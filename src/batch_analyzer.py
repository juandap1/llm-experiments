from readability import Document
import requests
from newspaper import Article

url = "https://finance.yahoo.com/news/google-invest-40-billion-data-210300462.html"
response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text

doc = Document(response)
clean_html = doc.summary()

article = Article(url)
article.set_html(clean_html)
article.parse()

print(article.text)
