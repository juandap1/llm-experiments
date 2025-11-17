import os
from dotenv import load_dotenv
load_dotenv()
import json
import ollama
import asyncio
from services.utils import clean_json_response
from services.scraper import ScraperService
import requests
from clients.qdrant_server import QdrantServerClient
# import time
# from datetime import timedelta

news_api_token = os.getenv("NEWS_API")

class BatchAnalyzer:
    def __init__(self, vector_db: QdrantServerClient, ollama_client: ollama.Client):
        self.vector_db = vector_db
        self.client = ollama_client
        self.scraper = ScraperService(vector_db, ollama_client)

    # Make a separate function to pull news based on query
    def pull_company_news(self, company):
        query = f"+{company} AND (investment OR earnings OR revenue OR stock OR shares OR profit OR loss OR forecast OR guidance OR outlook)"
        # domains = "bloomber.com,wsj.com,reuters.com,ft.com,cnbc.com,economist.com,forbes.com,marketwatch.com,finance.yahoo.com,investopedia.com,barrons.com"
        article_response = requests.get(f"https://newsapi.org/v2/everything?q={query}&apiKey={news_api_token}")
        # all_articles = requests.get(f"https://newsapi.org/v2/everything?q={query}&apiKey={news_api_token}&domains={domains}")
        # all_articles = requests.get(f"https://newsapi.org/v2/top-headlines?q={query}&apiKey={news_api_token}&category=business")
        all_articles = article_response.json()["articles"]
        # store_articles_locally(all_articles)
        return all_articles

    def store_articles_locally(self, articles):
        """Store articles data to a local JSON file."""
        filename = "data.json"
        try:
            # 'w' mode means write (or overwrite)
            with open(filename, 'w') as f:
                # json.dump(data, file_object, optional_arguments)
                json.dump(articles, f, indent=4) # indent=4 makes the file human-readable
            print(f"Successfully saved data to {filename}")
        except IOError as e:
            print(f"An error occurred while writing the file: {e}")

    def open_local_articles(self, filename="data.json"):
        """Open and read articles data from a local JSON file."""
        try:
            with open(filename, 'r') as f:
                # json.load(file_object)
                articles = json.load(f)
            return articles
        except IOError as e:
            print(f"An error occurred while reading the file: {e}")
            return []

    def nano_to_sec(self, nano):
        # Converts nanoseconds to seconds for readability
        return round(nano / 1_000_000_000, 4)

    async def ingest_many_articles_async(
        self,
        articles,
        ticker,
        batch_size=50,
        concurrency=10,
        collection_name="news_articles"
    ):
        """
        Fully async ingestion pipeline that:
        - Scrapes multiple articles in parallel
        - Chunks, encodes, preprocesses
        - Inserts into Qdrant in batches
        """

        semaphore = asyncio.Semaphore(concurrency)
        ingestion_results = []

        async def worker(article_meta):
            """Worker with semaphore limit."""
            async with semaphore:
                vectors, payloads = await self.scraper.scrape_news_async(article_meta, ticker)
                if vectors is not None:
                    ingestion_results.append((vectors, payloads))

        # --- Run all scraping tasks asynchronously ---
        tasks = [asyncio.create_task(worker(a)) for a in articles]

        # Let them run concurrently
        await asyncio.gather(*tasks, return_exceptions=True)

        if not ingestion_results:
            print("No data ingested — all scrapes failed.")
            return

        # --- Flatten results ---
        all_vectors = []
        all_payloads = []

        for vectors, payloads in ingestion_results:
            all_vectors.extend(vectors)
            all_payloads.extend(payloads)

        print(f"Preparing to insert {len(all_vectors)} vectors...")
        self.vector_db.create_collection(collection_name, len(all_vectors[0]))
        # --- Batched Upsert ---
        async def insert_batch(start):
            end = min(start + batch_size, len(all_vectors))
            # await vector_db.upsert_vectors(
            #     collection_name=collection_name,
            #     vectors=all_vectors[start:end],
            #     payloads=all_payloads[start:end]
            # )
            await asyncio.to_thread(
                self.vector_db.upsert_vectors,
                collection_name=collection_name,
                vectors=all_vectors[start:end],
                payloads=all_payloads[start:end]
            )
            print(f"Inserted {end}/{len(all_vectors)} vectors")

        # --- Create async tasks for each batch ---
        batches = [
            asyncio.create_task(insert_batch(i))
            for i in range(0, len(all_vectors), batch_size)
        ]

        await asyncio.gather(*batches)

        print("Batch ingestion completed!")

    def generate_analysis(self, ticker: str, company: str):
        points = self.vector_db.fetch_relevant_chunks(query=f"Major financially impactful news events for {company} ({ticker})", sort=True)
        if points is None or len(points) == 0:
            print("No relevant points found.")
            return None
        prepared = []

        for p in points:
            payload = p.payload

            prepared.append({
                "summary": payload.get("summary"),
                "sentiment": payload.get("sentiment"),
                "importance": payload.get("importance"),
                "ticker": payload.get("ticker"),
                "timestamp": payload.get("timestamp"),
            })
        summaries = [item["summary"] for item in prepared if item["summary"]]
        summaries_text = "\n\n".join(summaries)

        SYSTEM_MESSAGE = (
            f"You are a financial analyst analyzing the company {company} ({ticker})."
            f"Focus only on {company} and only mention other companies if they relate to the viability of {company} as an investment."
            "EMPHASIZE any numerical datapoints/statistics, like year over year growth and revenue, that emphasize the analysis"
            "Do NOT include any commentary, introduction, conclusion, or surrounding markdown fences (e.g., ```json). "
            "Your output MUST strictly adhere to the provided JSON template and MUST use the content from the summaries."
            "Your sole output MUST be a valid JSON object."
            f"Rewrite summaries from the perspective of an analyst, focusing fully on {company}"
        )

        USER_PROMPT = f"""
        Summaries to analyze (Use ONLY this data):
        ---
        {summaries_text}
        ---

        Fill the following JSON template using analysis for the company {company} based on the summaries above. 
        Ensure the 'events' array has a MAXIMUM of 4 elements.

        JSON TEMPLATE:
        {{
        "general_headline": "REPLACE_GENERAL_HEADLINE_HERE",
        "events": [
            {{
            "headline": "REPLACE_EVENT_HEADLINE_1_HERE",
            "summary": "REPLACE_EVENT_SUMMARY_1_HERE"
            }},
            {{
            "headline": "REPLACE_EVENT_HEADLINE_2_HERE",
            "summary": "REPLACE_EVENT_SUMMARY_2_HERE"
            }}
        ],
        "market_summary": "REPLACE_BROADER_MARKET_SUMMARY_HERE"
        }}

        BEGIN JSON OUTPUT NOW. Start with the opening curly brace
        """
        stream = self.client.chat(
            model='gemma3:1b',
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": USER_PROMPT}
            ],
            stream=True
        )
        token_count = 0
        full_response = ""
        final_chunk = None

        for chunk in stream:
            # Get the new content
            content = chunk['message']['content']
            
            # Append the content to the full response
            full_response += content
            
            # Count the number of tokens (this is only a proxy count, as it uses python's built-in len)
            # Ollama returns accurate count in the *final* chunk's 'eval_count', but we use this for the live display
            token_count += len(content.split()) # Simple word count proxy
            
            # --- Live Progress Bar/Display Logic ---
            # Print the last token received immediately
            print(content, end='', flush=True) 
            final_chunk = chunk
            # Get the timing metrics
        total_duration_ns = final_chunk.get('total_duration')
        load_duration_ns = final_chunk.get('load_duration', 0)
        prompt_eval_duration_ns = final_chunk.get('prompt_eval_duration')
        eval_duration_ns = final_chunk.get('eval_duration')
        eval_count = final_chunk.get('eval_count', 0)
        tokens_per_second = round(eval_count / self.nano_to_sec(eval_duration_ns), 2) if eval_duration_ns else 0

        print(f"✅ **Generation Complete.**")
        print(f"* Output Tokens Generated: {eval_count}")
        print(f"* **Total Duration:** {self.nano_to_sec(total_duration_ns)} seconds")
        print(f"* Load Duration: {self.nano_to_sec(load_duration_ns)} seconds")
        print(f"* Prompt Eval Duration: {self.nano_to_sec(prompt_eval_duration_ns)} seconds")
        print(f"* **Output Generation Duration:** {self.nano_to_sec(eval_duration_ns)} seconds")
        print(f"* **Inference Rate (Tokens/s):** {tokens_per_second}")
        clean_text = clean_json_response(full_response)
        return clean_text

# start_time = time.time()
# client = ollama.Client(host='http://localhost:11434')
# vector_db = QdrantServerClient()
# analyzer = BatchAnalyzer(vector_db, client)
# analyzer.generate_analysis("MSFT", "Microsoft Corporation")

# articles = analyzer.open_local_articles()
# asyncio.run(analyzer.ingest_many_articles_async(
#     articles=articles,
#     ticker="MSFT",
#     batch_size=50,
#     concurrency=10,
#     collection_name="news_articles"
# ))
# end_time = time.time()
# elapsed_time = end_time - start_time
# elapsed_time_readable = str(timedelta(seconds=elapsed_time))

# print(f"\nElapsed wall clock time: {elapsed_time:.4f} seconds")
# print(f"Readable time: {elapsed_time_readable}")