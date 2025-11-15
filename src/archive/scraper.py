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