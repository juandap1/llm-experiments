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
client = ollama.Client(host='http://localhost:11434')

from clients.qdrant_server import QdrantServerClient

news_api_token = os.getenv("NEWS_API")


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

def process_chunks(chunks):
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
        clean_text = re.sub(r"^```json\s*|\s*```$", "", response["response"], flags=re.MULTILINE).strip()
        data = json.loads(clean_text)
        return data

def scrape_news(url):
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
    doc = Document(response)
    clean_html = doc.summary()

    article = Article(url)
    article.set_html(clean_html)
    article.parse()
    return article.text

# query = "+Microsoft AND (investment OR earnings OR revenue OR stock OR shares OR profit OR loss OR forecast OR guidance OR outlook)"
# # domains = "bloomber.com,wsj.com,reuters.com,ft.com,cnbc.com,economist.com,forbes.com,marketwatch.com,finance.yahoo.com,investopedia.com,barrons.com"
# article_response = requests.get(f"https://newsapi.org/v2/everything?q={query}&apiKey={news_api_token}")
# # all_articles = requests.get(f"https://newsapi.org/v2/everything?q={query}&apiKey={news_api_token}&domains={domains}")
# # all_articles = requests.get(f"https://newsapi.org/v2/top-headlines?q={query}&apiKey={news_api_token}&category=business")
# all_articles = article_response.json()["articles"]

# test_article = all_articles[0]
# print(test_article)
filename = "data.json"

# try:
#     # 'w' mode means write (or overwrite)
#     with open(filename, 'w') as f:
#         # json.dump(data, file_object, optional_arguments)
#         json.dump(test_article, f, indent=4) # indent=4 makes the file human-readable
#     print(f"Successfully saved data to {filename}")
# except IOError as e:
#     print(f"An error occurred while writing the file: {e}")

with open(filename, 'r') as f:
        # json.load(file_object)
        test_article = json.load(f)

        iso_str = test_article["publishedAt"]
        dt = parser.isoparse(iso_str)
        # print(f"Published at: {dt}")
        url = test_article["url"]
        content = scrape_news(url)
        chunks = chunk_text(content)
        process_chunks(chunks)
        source = test_article["source"]["name"]

        # vector_db = QdrantServerClient()
        # encoded_chunks = vector_db.encode_texts(chunks)
        # print(chunks)
        # print(len(chunks), "text chunks")
        # print(len(encoded_chunks), "encoded vectors")
        # vector_db.upsert_vectors(
        #     collection_name="news_articles", 
        #     vectors=encoded_chunks,
        #     chunks=chunks,
        #     ticker="MSFT", 
        #     timestamp=iso_str,
        #     source=source,
        #     url=url
        # )

# stream = client.generate(
#     model='gemma3:1b',
#     prompt='Write a haiku about Python.',
#     stream=True
# )

# final_chunk = None
# def nano_to_sec(nano):
#     # Converts nanoseconds to seconds for readability
#     return round(nano / 1_000_000_000, 4)

# token_count = 0
# full_response = ""

# for chunk in stream:
#     # Get the new content
#     content = chunk.get('response', '')
    
#     # Append the content to the full response
#     full_response += content
    
#     # Count the number of tokens (this is only a proxy count, as it uses python's built-in len)
#     # Ollama returns accurate count in the *final* chunk's 'eval_count', but we use this for the live display
#     token_count += len(content.split()) # Simple word count proxy
    
#     # --- Live Progress Bar/Display Logic ---
#     # Print the last token received immediately
#     print(content, end='', flush=True) 
#     final_chunk = chunk

# Get the timing metrics
# total_duration_ns = final_chunk.get('total_duration')
# load_duration_ns = final_chunk.get('load_duration', 0)
# prompt_eval_duration_ns = final_chunk.get('prompt_eval_duration')
# eval_duration_ns = final_chunk.get('eval_duration')
# eval_count = final_chunk.get('eval_count', 0)
# tokens_per_second = round(eval_count / nano_to_sec(eval_duration_ns), 2) if eval_duration_ns else 0

# print(f"✅ **Generation Complete.**")
# print(f"* Output Tokens Generated: {eval_count}")
# print(f"* **Total Duration:** {nano_to_sec(total_duration_ns)} seconds")
# print(f"* Load Duration: {nano_to_sec(load_duration_ns)} seconds")
# print(f"* Prompt Eval Duration: {nano_to_sec(prompt_eval_duration_ns)} seconds")
# print(f"* **Output Generation Duration:** {nano_to_sec(eval_duration_ns)} seconds")
# print(f"* **Inference Rate (Tokens/s):** {tokens_per_second}")

# vector_db = QdrantServerClient()
# hits = vector_db.query(
#     collection_name="news_articles", 
#     query_text="How much money is Microsoft Investing", 
#     limit=5
# )
# print(hits)