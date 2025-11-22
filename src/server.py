from fastapi import FastAPI, Request, HTTPException, Depends, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import requests
import json
import asyncio
import aiohttp
import ollama

from clients.sql_server import MySQLClient
from clients.qdrant_server import QdrantServerClient
from batch_analyzer import BatchAnalyzer

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:9000",
        "http://127.0.0.1:9000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONTAINER_ROOT = '/app'

# SECRETS
logo_dev_token = os.getenv("LOGO_DEV_TOKEN")
stock_token = os.getenv("ALPHAVANTAGE_TOKEN")

# Initialize clients
# Note: In FastAPI, it's often better to initialize these in a startup event or as dependencies if they need to be closed.
# For now, keeping them global as in the original script.
client = ollama.Client(host='http://ollama:11434')
vector_db = QdrantServerClient(host="qdrant")
analyzer = BatchAnalyzer(vector_db, client)

# Dependency
def get_db():
    db = MySQLClient()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class TransactionCreate(BaseModel):
    ticker: str
    share_count: float
    share_price: float
    transaction_date: str
    buying: bool

class BatchStockRequest(BaseModel):
    tickers: List[str]

@app.get("/")
def hello_world():
    return Response(content="<p>HOT RELOAD 4!</p>", media_type="text/html")

@app.get("/transactions")
def sql(db: MySQLClient = Depends(get_db)):
    transactions = db.fetch_all("SELECT * FROM transactions ORDER BY transaction_date DESC, id DESC")
    return transactions

@app.post("/transaction", status_code=201)
def add_transaction(transaction: TransactionCreate, db: MySQLClient = Depends(get_db)):
    try:
        id = db.insert_transaction(
            transaction.ticker, 
            transaction.share_count, 
            transaction.share_price, 
            transaction.transaction_date, 
            transaction.buying
        )
        return {"message": f"Transaction {id} added successfully", "new_id": id}
    except Exception as e:
        print(f"❌ Error inserting transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock/{ticker}")
def get_stock_info(ticker: str, db: MySQLClient = Depends(get_db)):
    ticker = ticker.upper()
    try:
        row = db.fetch_one("SELECT ticker, name, description, latest_price, sector, industry, analysis, is_etf FROM tickers WHERE ticker = %s", (ticker,))
        
        if row and row["name"] and row["latest_price"]:
            return {
                "ticker": ticker,
                "name": row["name"],
                "description": row["description"],
                "latest_price": row["latest_price"],
                "sector": row["sector"],
                "industry": row["industry"],
                "analysis": row["analysis"],
                "is_etf": row["is_etf"]
            }
        else:
            latest_price = row["latest_price"] if row else None
            if not row or not latest_price:
                url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={stock_token}'
                r = requests.get(url)
                data = r.json()
                # Handle potential API errors or empty responses
                if "Global Quote" in data and "05. price" in data["Global Quote"]:
                    latest_price = float(data["Global Quote"]["05. price"])
                    latest_date = data["Global Quote"]["07. latest trading day"]
                    db.update_stock_price(ticker, latest_price, latest_date)
                else:
                    # Fallback or error handling if price not found
                    pass 

            if not row or not row["name"]:
                url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={stock_token}'
                r = requests.get(url)
                data = r.json()
                # Check if data is valid
                if "Name" in data:
                    db.update_company_data(ticker, data["Name"], data["Description"], data["Sector"], data["Industry"])
                    return {
                        "ticker": ticker,
                        "name": data["Name"],
                        "description": data["Description"],
                        "latest_price": latest_price,
                        "sector": data["Sector"],
                        "industry": data["Industry"]
                    }
                else:
                     # Return what we have if API fails
                    return {
                        "ticker": ticker,
                        "name": row["name"] if row else "",
                        "description": row["description"] if row else "",
                        "latest_price": latest_price,
                        "sector": row["sector"] if row else "",
                        "industry": row["industry"] if row else ""
                    }
            else:
                return {
                    "ticker": ticker,
                    "name": row["name"],
                    "description": row["description"],
                    "latest_price": latest_price,
                    "sector": row["sector"],
                    "industry": row["industry"]
                }
    except Exception as e:
        print(f"Error pulling stock data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stock/batch")
def get_stock_info_batch(req: BatchStockRequest, db: MySQLClient = Depends(get_db)):
    tickers = [t.upper() for t in req.tickers]

    if not tickers:
        raise HTTPException(status_code=400, detail="tickers required")

    # --- 1. Load existing rows in a single query ---
    placeholders = ",".join(["%s"] * len(tickers))
    # Note: MySQLClient.fetch_all might need adjustment if it doesn't support dynamic placeholders easily with list
    # But assuming it handles the tuple correctly as per original code.
    rows = db.fetch_all(
        f"""
        SELECT ticker, name, description, latest_price, latest_date,
               sector, industry, analysis, is_etf
        FROM tickers
        WHERE ticker IN ({placeholders})
        """,
        tuple(tickers),
    )

    rows_by_ticker = {r["ticker"]: r for r in rows}

    # --- 2. Identify missing info ---
    need_price = []
    need_overview = []

    for t in tickers:
        row = rows_by_ticker.get(t)

        if not row or not row["latest_price"]:
            need_price.append(t)

        if not row or not row["name"]:
            need_overview.append(t)

    # --- 3. Fetch missing info concurrently ---
    async def fetch_missing():
        tasks = []
        async with aiohttp.ClientSession() as session:

            # Missing prices
            for t in need_price:
                url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={t}&apikey={stock_token}'
                tasks.append(("price", t, session.get(url)))

            # Missing overview
            for t in need_overview:
                url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={t}&apikey={stock_token}'
                tasks.append(("overview", t, session.get(url)))

            results = []
            for kind, ticker, coro in tasks:
                try:
                    resp = await coro
                    data = await resp.json()
                    results.append((kind, ticker, data))
                except:
                    results.append((kind, ticker, None))
            return results

    # Since we are in a sync route, we use asyncio.run. 
    # Ideally, the whole route should be async, but db calls are sync.
    # We can keep it this way for now or make the route async and wrap db calls.
    results = asyncio.run(fetch_missing())

    # --- 4. Write updates to DB & merge results ---
    for kind, ticker, data in results:
        if not data:
            continue

        if kind == "price" and "Global Quote" in data:
            price = data["Global Quote"].get("05. price")
            date = data["Global Quote"].get("07. latest trading day")
            if price:
                price = float(price)
                db.update_stock_price(ticker, price, date)
                if ticker not in rows_by_ticker:
                    rows_by_ticker[ticker] = {"ticker": ticker}
                rows_by_ticker[ticker]["latest_price"] = price

        elif kind == "overview" and "Name" in data:
            db.update_company_data(
                ticker,
                data["Name"],
                data["Description"],
                data["Sector"],
                data["Industry"],
            )
            if ticker not in rows_by_ticker:
                rows_by_ticker[ticker] = {"ticker": ticker}
            rows_by_ticker[ticker].update({
                "name": data["Name"],
                "description": data["Description"],
                "sector": data["Sector"],
                "industry": data["Industry"]
            })

    # --- 5. Build final response ---
    final = {}

    for t in tickers:
        row = rows_by_ticker.get(t)
        if not row:
            continue

        final[t] = {
            "ticker": t,
            "name": row.get("name", ""),
            "description": row.get("description", ""),
            "latest_price": row.get("latest_price", -1),
            "sector": row.get("sector", ""),
            "industry": row.get("industry", ""),
            "analysis": row.get("analysis", ""),
            "is_etf": row.get("is_etf", 0)
        }

    return final

@app.get("/stock/history/{ticker}")
def get_stock_history(ticker: str, db: MySQLClient = Depends(get_db)):
    ticker = ticker.upper()
    try:
        history = db.fetch_all("""
            SELECT date, open_price, close_price, low, high 
            FROM price_history 
            WHERE ticker = %s 
            ORDER BY date ASC
        """, (ticker,)) # Pass as tuple
        if history:
            return history

        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={stock_token}&outputsize=full'
        r = requests.get(url)
        data = r.json()
        price_history = data.get("Time Series (Daily)", {})
        records_to_insert = []
        for date_str, daily_data in price_history.items():
            try:
                record = (
                    ticker,
                    float(daily_data['1. open']), 
                    float(daily_data['4. close']), 
                    float(daily_data['3. low']), 
                    float(daily_data['2. high']), 
                    date_str 
                )
                records_to_insert.append(record)
            except (KeyError, ValueError) as e:
                print(f"Skipping record for {date_str}: {e}")
                continue
        if records_to_insert:
            rows_inserted = db.insert_many_prices(ticker, records_to_insert)
            print(f"✅ Successfully inserted {rows_inserted} price records for {ticker}.")
            # Convert tuples back to dicts or list of lists for JSON response if needed, 
            # but returning list of tuples is also valid JSON (list of lists)
            return records_to_insert
        return []
    except Exception as e:
        print(f"Error pulling stock history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logo/{ticker}")
def get_logo(ticker: str, db: MySQLClient = Depends(get_db)):
    ticker = ticker.upper()
    try:
        row = db.fetch_one("SELECT logo FROM tickers WHERE ticker = %s", (ticker,))
        if row and row['logo']:
            db_path = row['logo']
            if not os.path.isabs(db_path):
                logo_path = os.path.join(CONTAINER_ROOT, db_path)
            else:
                logo_path = db_path
            print(f"Database entry found for {ticker}. Logo path is: {logo_path}")
            if os.path.exists(logo_path):
                print(f"Serving local file: {logo_path}")
                return FileResponse(logo_path, media_type='image/jpeg')
            print(f"Warning: File missing on disk, proceeding to download.")
    except Exception as e:
        print(f"Database/Check failure for {ticker}: {e}. Attempting download.")

    try:
        save_directory = os.path.join(CONTAINER_ROOT, "logos")
        filename = f"{ticker}.jpg"
        full_path = os.path.join(save_directory, filename)
        os.makedirs(save_directory, exist_ok=True)
        
        response = requests.get(f"https://img.logo.dev/ticker/{ticker}?token={logo_dev_token}", stream=True)
        response.raise_for_status()
        
        with open(full_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk: 
                    file.write(chunk)
        
        db.update_logo(ticker, full_path)
        print(f"✅ Image successfully saved and DB updated for {ticker} at: {full_path}")
        return FileResponse(full_path, media_type='image/jpeg')
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download logo for {ticker}: {e}")
        raise HTTPException(status_code=404, detail=f"Logo not found or download failed for {ticker}.")
    except Exception as e:
        print(f"❌ An unexpected error occurred for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock/analysis")
def get_stock_analysis(ticker: str = "", company: str = "", db: MySQLClient = Depends(get_db)):
    try:
        ticker = ticker.upper()
        analysis = analyzer.generate_analysis(ticker, company)
        db.update_analysis(ticker, analysis)
        j = json.loads(analysis)
        return j
    except Exception as e:
        print(f"❌ An unexpected error occurred for getting analysis for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)