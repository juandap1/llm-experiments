# from sec_edgar_downloader import Downloader
# import os

# BASE_DIR = os.path.join(os.getcwd(), "sec_filings")
# TICKER = "MSFT"
# FILING_TYPE = "10-K"
# ticker_dir = os.path.join(BASE_DIR, FILING_TYPE, TICKER)

# dl = Downloader("llm-experiments", "juanpabby@gmail.com", BASE_DIR)

# # Get the latest 10-K filing for Microsoft
# dl.get("10-K", "MSFT", limit=1)

# -------------------------------
# CONFIG
# -------------------------------
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup

from llm_model import LocalLLM

# Initialize your model once
model_path = r"../model"
llm = LocalLLM(max_new_tokens=500)

FILE_PATH = "/Users/mbranni03/Documents/GitHub/llm-experiments/sec_filings/sec-edgar-filings/MSFT/10-K/0000950170-25-100235/full-submission.txt"
MAX_CHARS = 2000  # Adjust chunk size depending on your LLM

with open(FILE_PATH, "r", encoding="utf-8") as f:
    raw_html = f.read()

soup = BeautifulSoup(raw_html, "html.parser")

for tag in soup(["script", "style", "meta", "noscript", "iframe"]):
    tag.extract()

clean_text = soup.get_text(separator="\n")

# Normalize whitespace
clean_text = re.sub(r"\n\s*\n", "\n\n", clean_text)  # remove multiple blank lines
clean_text = re.sub(r"[ \t]+", " ", clean_text)      # replace multiple spaces/tabs

large_paragraphs = []
for p in soup.find_all("p"):
    text = p.get_text(" ", strip=True)  # replaces tags with space
    # Remove multiple spaces/newlines
    text = " ".join(text.split())
    if len(text) >= 200:
        large_paragraphs.append(text)

# print(f"Found {len(large_paragraphs)} clean large paragraphs")
# print(large_paragraphs[0][:1000])
        
# Initialize aggregation containers
aggregated_summaries = []
aggregated_risks = []
aggregated_metrics = {
    "revenue": [],
    "net_income": [],
    "eps": [],
    "cash_flow": [],
    "assets": [],
    "liabilities": []
}

# Loop through each chunk and analyze
for i, chunk in enumerate(large_paragraphs[0:1]):
    context = f"Paragraph {i+1}"
    prompt = f"""
    You are a financial analyst. Analyze the following section of a 10-Q filing.

    Section Context: {context}
    Text:
    {chunk}

    Tasks:
    1. Summarize key points in bullet form.
    2. Extract key financial metrics: revenue, net income, EPS, cash flow, assets, liabilities.
    3. Highlight any new or unusual risks or events.

    Return results as JSON with the following keys:
    {{
    "summary": [ ... ],
    "metrics": {{ "revenue": ..., "net_income": ..., "eps": ..., "cash_flow": ..., "assets": ..., "liabilities": ... }},
    "risks": [ ... ]
    }}
    """

    # Generate output from LLM
    output_text = llm.generate(prompt)

    # Attempt to parse JSON from LLM output
    try:
        data = json.loads(output_text)
    except json.JSONDecodeError:
        print(f"Warning: Could not parse JSON for chunk {i+1}. Skipping...")
        continue

    # Aggregate results
    aggregated_summaries.extend(data.get("summary", []))
    aggregated_risks.extend(data.get("risks", []))
    metrics = data.get("metrics", {})
    for key in aggregated_metrics:
        if metrics.get(key) is not None:
            aggregated_metrics[key].append(metrics[key])

# Display aggregated results
print("\n=== AGGREGATED SUMMARIES ===")
for s in aggregated_summaries:
    print("-", s)

print("\n=== AGGREGATED METRICS ===")
for k, v in aggregated_metrics.items():
    print(f"{k}: {v}")

print("\n=== AGGREGATED RISKS ===")
for risk in aggregated_risks:
    print("-", risk)