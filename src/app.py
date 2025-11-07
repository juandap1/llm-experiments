from transformers import pipeline
import torch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import math
import ffmpeg

from faster_whisper import WhisperModel
import praw
from pydub import AudioSegment
from gtts import gTTS
from bs4 import BeautifulSoup
import sec_parser as sp
from sec_downloader import Downloader
import pandas as pd
from io import StringIO

import requests

# Activate the virtual environment
# venv\Scripts\activate.bat

# Run fastapi server
# fastapi dev src\app.py

api_key="LFDXCQ8GX4AGGWDU"

class Query(BaseModel):
    question: str

# modelPath = "C:\\Users\\mhb90\\OneDrive\\Documents\\GitHub\\llama\\"

# pipe = pipeline(
#     "text-generation",
#     model=modelPath,
#     torch_dtype=torch.bfloat16,
#     device=0
# )

dl = Downloader("MatthewBranning", "juanpabby@gmail.com")
# messageStructure = [
#     # {"role": "system", "content": "You are an "},
#     {"role": "user", "content": "What is machine learning?"}
# ]

# response = pipe(
#     messageStructure,
#     max_new_tokens=500
# )

# outputResponse=response[0]["generated_text"][-1]

# print(outputResponse['content'])

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:9001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query/")
async def ask_question(query: Query):
    print(query)
    messageStructure = [
        {"role": "user", "content": query.question}
    ]
    response = pipe(
        messageStructure,
        max_new_tokens=500
    )
    output = response[0]["generated_text"][-1]
    return output['content']

    video_input_stream = ffmpeg.input("background_video.mp4")
    subtitle_input_stream = ffmpeg.input(subtitle_file)
    output_video = f"output/reddit_test.mp4"
    subtitle_track_title = subtitle_file.replace(".srt", "")

    if soft_subtitle:
        stream = ffmpeg.output(
            video_input_stream, subtitle_input_stream, output_video, **{"c": "copy", "c:s": "mov_text"},
            **{"metadata:s:s:0": f"language={subtitle_language}",
            "metadata:s:s:0": f"title={subtitle_track_title}"}
        )
        ffmpeg.run(stream, overwrite_output=True)
    else:
        stream = ffmpeg.output(video_input_stream, output_video,
                               vf=f"subtitles={subtitle_file}")
        ffmpeg.run(stream, overwrite_output=True)

@app.get("/stock")
async def stock_info(query: Query):
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol=GOOG&apikey={api_key}"
    r = requests.get(url)
    data = r.json()
    return data


@app.get("/stock/history/{symbol}")
async def stock_history(symbol: str):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={api_key}"
    r = requests.get(url)
    data = r.json()
    return data

@app.get("/stock/earnings/{symbol}")
async def stock_earnings(symbol: str):
    url = f"https://www.alphavantage.co/query?function=EARNINGS&symbol={symbol}&apikey={api_key}"
    r = requests.get(url)
    data = r.json()
    return data

@app.get("/stock/cashflow/{symbol}")
async def stock_cashflow(symbol: str):
    url = f"https://www.alphavantage.co/query?function=CASH_FLOW&symbol={symbol}&apikey={api_key}"
    r = requests.get(url)
    data = r.json()
    return data

@app.get("/stock/dividends/{symbol}")
async def stock_dividends(symbol: str):
    url = f"https://www.alphavantage.co/query?function=DIVIDENDS&symbol={symbol}&apikey={api_key}"
    r = requests.get(url)
    data = r.json()
    return data

@app.get("/stock/income/{symbol}")
async def stock_earnings(symbol: str):
    url = f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={api_key}"
    r = requests.get(url)
    data = r.json()
    return data

def get_cik(ticker):
    url = f"https://www.sec.gov/files/company_tickers.json"
    r = requests.get(url, headers={"User-Agent": "MatthewBranning juanpabby@gmail.com"})
    data = r.json()
    for item in data.values():
        if item["ticker"].lower() == ticker.lower():
            return str(item["cik_str"]).zfill(10)
    return None

@app.get("/sec/filings/{ticker}")
async def sec_filings(ticker: str):
    cik = get_cik(ticker)
    if not cik:
        return {"error": "Ticker not found"}
    
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {
        "User-Agent": "MatthewBranning",
    }
    r = requests.get(url, headers=headers)
    data = r.json()
    filings = data["filings"]["recent"]
    urls = []
    form_type="10-K"
    count=5
    for i, ftype in enumerate(filings["form"]):
        if ftype == form_type and len(urls) < count:
            acc_no = filings["accessionNumber"][i].replace("-", "")
            url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_no}/{filings['primaryDocument'][i]}"
            urls.append(url)
    txt = get_clean_text_from_filing(urls[0])
    return txt
    # messageStructure = [
    #     {"role": "user", "content": f"Extract the breakdown of revenues and expenses in a json format from the following: {txt}"}
    # ]
    # response = pipe(
    #     messageStructure,
    #     max_new_tokens=500
    # )
    # output = response[0]["generated_text"][-1]
    # return output['content']


def print_first_n_lines(text: str, *, n: int):
    print("\n".join(text.split("\n")[:n]), "...", sep="\n")

def get_clean_text_from_filing(url):
    # r = requests.get(url, headers={"User-Agent": "MatthewBranning juanpabby@gmail.com"})
    # soup = BeautifulSoup(r.content, "lxml")
    # text = soup.get_text(separator="\n")
    
    # Financial Results
    # Cost of Revenues
    # Sales and Marketing
    # General and Administrative
    # Segment Profitability
    html = dl.download_filing(url=url).decode()
    elements: list = sp.Edgar10QParser().parse(html)
    tree = sp.TreeBuilder().build(elements)
    # demo_output: str = sp.render(tree)
    # print_first_n_lines(demo_output, n=7)
    extracted = {}
    prev_node = None
    for node in tree.nodes:
        extracted = extract_table_data(extracted, node, "Revenues", prev_node, "Financial Results")
        extracted = extract_table_data(extracted, node, "Cost of Revenues", prev_node, "Costs and Expenses")
        extracted = extract_table_data(extracted, node, "Research and Development")
        extracted = extract_table_data(extracted, node, "Sales and Marketing")
        extracted = extract_table_data(extracted, node, "General and Administrative")
        prev_node = node
    # print(node.text)
    # print_first_n_lines(sp.render(node), n=25)

    return extracted

def extract_table_data(acc, node, table_name, previous_node=None, prev_node_check=None):
    extracted = {}
    if node.text == table_name:
        if previous_node is None or check_prev_node(previous_node, prev_node_check):
                for child in node.children:
                    if isinstance(child.semantic_element, sp.TableElement):
                        # print("FOUND" + table_name)
                        pd.set_option('display.max_columns', None)
                        extracted_tbl = pd.read_html(StringIO(str(child.semantic_element.html_tag._bs4)))[0]
                        # Keep only relevant columns
                        subset = extracted_tbl.iloc[:, [2, 4, 10]]
                        for i, row in subset.iterrows():
                            if pd.notna(row[2]):
                                extracted[row[2]] = {
                                    "2023": row[4],
                                    "2024": row[10]
                                }
                        acc[table_name] = extracted
    return acc


def check_prev_node(node, name):
    if node is None:
        return False
    if node.text == name:
        return True
    return False