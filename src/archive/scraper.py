from readability import Document
import requests
from newspaper import Article

from sentence_transformers import SentenceTransformer

url = "https://www.fool.com/investing/2025/11/14/big-tech-earnings-and-reckless-predictions/"
response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text

doc = Document(response)
clean_html = doc.summary()

article = Article(url)
article.set_html(clean_html)
article.parse()

print(article.publish_date)
print(article.text)

model = SentenceTransformer("all-MiniLM-L6-v2")

# def scrape_news(url):
#     try:
#         response = requests.get(
#             url, 
#             headers={"User-Agent": "Mozilla/5.0"}, 
#             timeout=10
#         ).text
#         response.raise_for_status()
#         doc = Document(response)
#         clean_html = doc.summary()

#         article = Article(url)
#         article.set_html(clean_html)
#         article.parse()
#         return article.text
#     except Exception as e:
#         print(f"Error scraping {url}: {e}")
#         return None

# def fetch_and_process_article(article, ticker="MSFT"):
#     source = article["source"]["name"]
#     iso_str = article["publishedAt"]
#     dt = parser.isoparse(iso_str)
#     url = article["url"]
#     content = scrape_news(url)
#     if not content:
#         return None
#     chunks = chunk_text(content)
#     encoded_chunks = vector_db.encode_texts(chunks)
#     processed = process_chunks(chunks)
#     payloads = []
#     for i in range(len(processed)):
#         payloads.append({
#             "text": chunks[i],
#             "summary": processed[i]["summary"],
#             "sentiment": processed[i]["sentiment"],
#             "importance": processed[i]["importance"],
#             "ticker": ticker,
#             "timestamp": dt.isoformat(),
#             "source": source,
#             "url": url
#         })
#     return encoded_chunks, processed



# test_article = all_articles[0]
# print(test_article)
# filename = "data.json"

# try:
#     # 'w' mode means write (or overwrite)
#     with open(filename, 'w') as f:
#         # json.dump(data, file_object, optional_arguments)
#         json.dump(test_article, f, indent=4) # indent=4 makes the file human-readable
#     print(f"Successfully saved data to {filename}")
# except IOError as e:
#     print(f"An error occurred while writing the file: {e}")

# with open(filename, 'r') as f:
#         # json.load(file_object)
#         vector_db = QdrantServerClient()
#         test_article = json.load(f)
#         ticker="MSFT"

#         iso_str = test_article["publishedAt"]
#         dt = parser.isoparse(iso_str)
#         # print(f"Published at: {dt}")
#         url = test_article["url"]
#         content = scrape_news(url)
#         source = test_article["source"]["name"]
#         chunks = chunk_text(content)
#         processed = process_chunks(chunks)
#         encoded_chunks = vector_db.encode_texts(chunks)

#         # print(chunks)
#         # print(len(chunks), "text chunks")
#         # print(len(encoded_chunks), "encoded vectors")
#         payloads = []
#         for i in range(len(processed)):
#             payloads.append({
#                 "text": chunks[i],
#                 "summary": processed[i]["summary"],
#                 "sentiment": processed[i]["sentiment"],
#                 "importance": processed[i]["importance"],
#                 "ticker": ticker,
#                 "timestamp": dt.isoformat(),
#                 "source": source,
#                 "url": url
#             })
#         vector_db.upsert_vectors(
#             collection_name="news_articles", 
#             vectors=encoded_chunks,
#             payloads=payloads
#         )

# vector_db = QdrantServerClient()
# hits = vector_db.query(
#     collection_name="news_articles", 
#     query_text="How much money is Microsoft Investing", 
#     limit=5
# )
# print(hits)