import os
from readability import Document
import requests
from newspaper import Article
from dotenv import load_dotenv
load_dotenv()
from dateutil import parser
import json
import re
import ollama
import httpx
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

client = ollama.Client(host='http://localhost:11434')

from clients.qdrant_server import QdrantServerClient

news_api_token = os.getenv("NEWS_API")
vector_db = QdrantServerClient()

def is_retryable_exception(exception):
    # Retry only on network issues or server errors (5xx)
    if isinstance(exception, httpx.HTTPStatusError):
        status = exception.response.status_code
        return 500 <= status < 600  # server errors
    elif isinstance(exception, (httpx.RequestError, httpx.TimeoutException)):
        return True  # network-level issues
    return False  # do NOT retry 4xx errors like 403

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=1, max=4),
    retry=retry_if_exception(is_retryable_exception)
)
async def fetch_html(url):
    async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
        resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()  # raises HTTPStatusError for 4xx/5xx
        return resp.text

def store_articles_locally(articles):
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

def open_local_articles(filename="data.json"):
    """Open and read articles data from a local JSON file."""
    try:
        with open(filename, 'r') as f:
            # json.load(file_object)
            articles = json.load(f)
        return articles
    except IOError as e:
        print(f"An error occurred while reading the file: {e}")
        return []

def nano_to_sec(nano):
    # Converts nanoseconds to seconds for readability
    return round(nano / 1_000_000_000, 4)

def chunk_text(text, max_words=200):
    """
    Splits text into chunks prioritizing line breaks (paragraphs),
    but ensures no chunk exceeds max_words.
    """
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    current_chunk = []

    current_count = 0
    for para in paragraphs:
        para_words = para.split()
        if current_count + len(para_words) <= max_words:
            # Add paragraph to current chunk
            current_chunk.append(para)
            current_count += len(para_words)
        else:
            # Save current chunk
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            # Start new chunk
            current_chunk = [para]
            current_count = len(para_words)

    # Add the last chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def clean_json_response(response_text):
    """
    Cleans the model response to extract valid JSON.
    Removes any markdown formatting or extraneous text.
    """
    return re.sub(r"^```json\s*|\s*```$", "", response_text, flags=re.MULTILINE).strip()

def process_chunks(chunks):
    processed = []
    for chunk_text in chunks:
        prompt = f"""
        You are a financial analyst. Summarize the following news article chunk in 1-3 sentences.
        Also provide a sentiment analysis (positive, negative, neutral) and rate the importance of this chunk on a scale of 1-10 for an investor considering Microsoft stock.
        Chunk:
        {chunk_text}

        Output as JSON with keys without any Markdown formatting or additional commentary:
        "summary", "sentiment", "importance"
        """
        response = client.generate(model="gemma3:1b", prompt=prompt)
        clean_text = clean_json_response(response['response'])
        data = json.loads(clean_text)
        processed.append(data)
    return processed

async def scrape_news_async(article_meta, ticker):
    """Fetch and parse a news article asynchronously."""
    try:
        # --- Process NewsApi.org Metadata ---
        source = article_meta.get("source", {}).get("name", "unknown")
        iso_str = article_meta.get("publishedAt")
        dt = parser.isoparse(iso_str) if iso_str else None
        url = article_meta.get("url", "unknown")
        print(f"Scraping article: {url}")

        # --- Fetch HTML ---
        html = await fetch_html(url)

        # --- Extract main content ---
        doc = Document(html)
        clean_html = doc.summary()
        article = Article(url)
        article.set_html(clean_html)
        article.parse()
        content = article.text.strip()

        # --- Chunk text ---
        chunks = chunk_text(content)
        
        # --- Encode chunks ---
        vectors = await vector_db.encode_texts(chunks)

        # --- Preprocess chunks (summary/sentiment/importance) ---
        processed = process_chunks(chunks)

        # --- Build payloads for Qdrant ---
        payloads = []
        for i in range(len(processed)):
            payloads.append({
                "text": chunks[i],
                "summary": processed[i]["summary"],
                "sentiment": processed[i]["sentiment"],
                "importance": processed[i]["importance"],
                "ticker": ticker,
                "timestamp": dt.isoformat(),
                "source": source,
                "url": url
            })
        print(f"Scraped and processed {len(chunks)} chunks from {url}")
        return vectors, payloads
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None, None

async def scrape_many(urls: list[str]) -> list[str]:
    """Scrape all URLs concurrently."""
    tasks = [asyncio.create_task(scrape_news_async(url)) for url in urls]
    return await asyncio.gather(*tasks)


async def ingest_many_articles_async(
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
            vectors, payloads = await scrape_news_async(article_meta, ticker)
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

    # --- Batched Upsert ---
    async def insert_batch(start):
        end = min(start + batch_size, len(all_vectors))
        # await vector_db.upsert_vectors(
        #     collection_name=collection_name,
        #     vectors=all_vectors[start:end],
        #     payloads=all_payloads[start:end]
        # )
        await asyncio.to_thread(
            vector_db.upsert_vectors,
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

def generate_analysis():
    points = vector_db.fetch_relevant_chunks(query="Major financially impactful news events for Microsoft (MSFT)", sort=True)
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

    prompt = f"""
    You are a financial analyst. Using the following preprocessed article summaries (which include importance, sentiment, and key datapoints), generate a structured report:

    1. General major headline summarizing the main events or trends across all articles.
    2. Individual event headlines:
       - Headline
       - Short summary
       - Market impact
       - Key datapoints/numbers
    3. Broader market summary

    Group information in a maximum of 4 individual events
    Only use the information provided. Organize output in JSON:

    {{
      "general_headline": "...",
      "events": [
        {{
          "headline": "...",
          "summary": "...",
          "market_impact": "...",
          "datapoints": "..."
        }}
      ],
      "market_summary": "..."
    }}

    Summaries:
    {summaries_text}
    """
    stream = client.generate(
        model='gemma3:1b',
        prompt=prompt,
        stream=True
    )
    token_count = 0
    full_response = ""
    final_chunk = None

    for chunk in stream:
        # Get the new content
        content = chunk.get('response', '')
        
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
        tokens_per_second = round(eval_count / nano_to_sec(eval_duration_ns), 2) if eval_duration_ns else 0

        print(f"✅ **Generation Complete.**")
        print(f"* Output Tokens Generated: {eval_count}")
        print(f"* **Total Duration:** {nano_to_sec(total_duration_ns)} seconds")
        print(f"* Load Duration: {nano_to_sec(load_duration_ns)} seconds")
        print(f"* Prompt Eval Duration: {nano_to_sec(prompt_eval_duration_ns)} seconds")
        print(f"* **Output Generation Duration:** {nano_to_sec(eval_duration_ns)} seconds")
        print(f"* **Inference Rate (Tokens/s):** {tokens_per_second}")
    clean_text = clean_json_response(full_response)
    return clean_text

# query = "+Microsoft AND (investment OR earnings OR revenue OR stock OR shares OR profit OR loss OR forecast OR guidance OR outlook)"
# # domains = "bloomber.com,wsj.com,reuters.com,ft.com,cnbc.com,economist.com,forbes.com,marketwatch.com,finance.yahoo.com,investopedia.com,barrons.com"
# article_response = requests.get(f"https://newsapi.org/v2/everything?q={query}&apiKey={news_api_token}")
# # all_articles = requests.get(f"https://newsapi.org/v2/everything?q={query}&apiKey={news_api_token}&domains={domains}")
# # all_articles = requests.get(f"https://newsapi.org/v2/top-headlines?q={query}&apiKey={news_api_token}&category=business")
# all_articles = article_response.json()["articles"]
# store_articles_locally(all_articles)

articles = open_local_articles()
asyncio.run(ingest_many_articles_async(
    articles=articles,
    ticker="MSFT",
    batch_size=50,
    concurrency=10,
    collection_name="news_articles"
))