from massive import RESTClient
from dotenv import load_dotenv
load_dotenv()
import os
import datetime

massive_token = os.getenv("MASSIVE_TOKEN")
print(massive_token)
client = RESTClient(massive_token)

aggs = []
for a in client.list_aggs("MSFT", 1, "day", "2023-12-01", datetime.datetime.now().strftime("%Y-%m-%d")):
    aggs.append(a)
print(len(aggs))
print(aggs[0])
print(datetime.datetime.fromtimestamp(aggs[-1].timestamp / 1000).strftime('%Y-%m-%d'))