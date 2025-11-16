from readability import Document
from newspaper import Article
from dateutil import parser
import re
import httpx
import asyncio
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
from services.utils import clean_json_response

class ScraperService:
    def __init__(self, vector_db, ollama_client):
        self.vector_db = vector_db
        self.client = ollama_client

    @staticmethod
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
    async def fetch_html(self, url):
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()  # raises HTTPStatusError for 4xx/5xx
            return resp.text
        
    def chunk_text(self, text, max_words=200):
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

    def process_chunks(self, chunks):
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
            response = self.client.generate(model="gemma3:1b", prompt=prompt)
            clean_text = clean_json_response(response['response'])
            data = json.loads(clean_text)
            processed.append(data)
        return processed

    async def scrape_news_async(self, article_meta, ticker):
        """Fetch and parse a news article asynchronously."""
        try:
            # --- Process NewsApi.org Metadata ---
            source = article_meta.get("source", {}).get("name", "unknown")
            iso_str = article_meta.get("publishedAt")
            dt = parser.isoparse(iso_str) if iso_str else None
            url = article_meta.get("url", "unknown")
            print(f"Scraping article: {url}")

            # --- Fetch HTML ---
            html = await self.fetch_html(url)
            html = re.sub(
                r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', 
                '', 
                html
            )
            html = html.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')

            # --- Extract main content ---
            doc = Document(html)
            clean_html = doc.summary()
            article = Article(url)
            article.set_html(clean_html)
            article.parse()
            content = article.text.strip()

            # --- Chunk text ---
            chunks = self.chunk_text(content)
            
            # --- Encode chunks ---
            vectors = await self.vector_db.encode_texts(chunks)

            # --- Preprocess chunks (summary/sentiment/importance) ---
            processed = self.process_chunks(chunks)

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
        
    async def scrape_many(self, urls: list[str]) -> list[str]:
        """Scrape all URLs concurrently."""
        tasks = [asyncio.create_task(self.scrape_news_async(url)) for url in urls]
        return await asyncio.gather(*tasks)