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

def clean_data_dictionary(data: dict) -> dict:
    """
    Iterates through ALL key-value pairs in the dictionary.
    If a value is a string that represents missing data (e.g., 'None', 'N/A'),
    it is converted to the Python None object.
    """
    cleaned_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            raw_value = value.strip()
            
            # Check for common missing value indicators (case-insensitive)
            if raw_value.lower() in ("none", "null", "n/a", ""):
                cleaned_data[key] = None  # Convert to the Python None object
            else:
                # OPTIONAL: Try to convert numeric-looking strings to float
                # ONLY do this if you are sure ALL non-string columns should be floats
                try:
                    cleaned_data[key] = float(raw_value)
                except ValueError:
                    cleaned_data[key] = raw_value  # Keep as string if conversion fails
        
        else:
            cleaned_data[key] = value # Keep non-string values as they are (e.g., int, None)
            
    return cleaned_data

@app.get("/stock/{ticker}")
def get_stock_info(ticker: str, db: MySQLClient = Depends(get_db)):
    ticker = ticker.upper()
    try:
        row = db.fetch_one("SELECT * FROM tickers WHERE ticker = %s", (ticker,))
        
        if row and row["name"] and row["latest_price"]:
            return {
                "ticker": ticker,
                "name": row["name"],
                "description": row["description"],
                "latest_price": row["latest_price"],
                "sector": row["sector"],
                "industry": row["industry"],
                "analysis": row["analysis"],
                "book_value": row["book_value"],
                "earnings_per_share": row["earnings_per_share"],
                "revenue_per_share": row["revenue_per_share"],
                "dividend_per_share": row["dividend_per_share"],
                "shares_outstanding": row["shares_outstanding"],
                "analyst_target_price": row["analyst_target_price"],
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

            if not row or not row["name"] or not row["earnings_per_share"]:
                url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={stock_token}'
                r = requests.get(url)
                data = r.json()
                # Check if data is valid
                if "Name" in data:
                    db.update_company_data(ticker, data["Name"], data["Description"], data["Sector"], data["Industry"], data["BookValue"], data["DilutedEPSTTM"], data["RevenuePerShareTTM"], data["DividendPerShare"], data["SharesOutstanding"], data["AnalystTargetPrice"], data["EBITDA"])
                    return {
                        "ticker": ticker,
                        "name": data["Name"],
                        "description": data["Description"],
                        "latest_price": latest_price,
                        "sector": data["Sector"],
                        "industry": data["Industry"],
                        "analysis": row["analysis"],
                        "book_value": data["BookValue"],
                        "earnings_per_share": data["DilutedEPSTTM"],
                        "revenue_per_share": data["RevenuePerShareTTM"],
                        "dividend_per_share": data["DividendPerShare"],
                        "shares_outstanding": data["SharesOutstanding"],
                        "analyst_target_price": data["AnalystTargetPrice"],
                        "ebitda": data["EBITDA"]
                    }
                else:
                     # Return what we have if API fails
                    return {
                        "ticker": ticker,
                        "name": row["name"] if row else "",
                        "description": row["description"] if row else "",
                        "latest_price": latest_price,
                        "sector": row["sector"] if row else "",
                        "industry": row["industry"] if row else "",
                        "analysis": row["analysis"] if row else "",
                        "book_value": row["book_value"] if row else "",
                        "earnings_per_share": row["earnings_per_share"] if row else "",
                        "revenue_per_share": row["revenue_per_share"] if row else "",
                        "dividend_per_share": row["dividend_per_share"] if row else "",
                        "shares_outstanding": row["shares_outstanding"] if row else "",
                        "analyst_target_price": row["analyst_target_price"] if row else "",
                        "ebitda": row["ebitda"] if row else ""
                    }
            else:
                return {
                    "ticker": ticker,
                    "name": row["name"],
                    "description": row["description"],
                    "latest_price": latest_price,
                    "sector": row["sector"],
                    "industry": row["industry"],
                    "analysis": row["analysis"],
                    "book_value": row["book_value"],
                    "earnings_per_share": row["earnings_per_share"],
                    "revenue_per_share": row["revenue_per_share"],
                    "dividend_per_share": row["dividend_per_share"],
                    "shares_outstanding": row["shares_outstanding"],
                    "analyst_target_price": row["analyst_target_price"],
                    "ebitda": row["ebitda"]
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
        SELECT *
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

        if not row or not row["name"] or not row["book_value"]:
            if not row["is_etf"]:
                need_overview.append(t)
        
        if not row or not row["dividend_per_share"]:
            if row["is_etf"]:
                dividend_per_share = get_etf_info(t)
                rows_by_ticker[t]["dividend_per_share"] = dividend_per_share
    # print(need_overview)
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
        if not data or "Note" in data:
            print(f"Failed to fetch {kind} for {ticker}: {data}")
            continue
        data = clean_data_dictionary(data)
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
            # print(data)
            db.update_company_data(
                ticker,
                data["Name"],
                data["Description"],
                data["Sector"],
                data["Industry"],
                data["BookValue"],
                data["DilutedEPSTTM"],
                data["RevenuePerShareTTM"],
                data["DividendPerShare"],
                data["SharesOutstanding"],
                data["AnalystTargetPrice"],
                data["EBITDA"]
            )
            if ticker not in rows_by_ticker:
                rows_by_ticker[ticker] = {"ticker": ticker}
            rows_by_ticker[ticker].update({
                "name": data["Name"],
                "description": data["Description"],
                "sector": data["Sector"],
                "industry": data["Industry"],
                "book_value": data["BookValue"],
                "earnings_per_share": data["DilutedEPSTTM"],
                "revenue_per_share": data["RevenuePerShareTTM"],
                "dividend_per_share": data["DividendPerShare"],
                "shares_outstanding": data["SharesOutstanding"],
                "analyst_target_price": data["AnalystTargetPrice"],
                "ebitda": data["EBITDA"]
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
            "book_value": row.get("book_value", -1),
            "earnings_per_share": row.get("earnings_per_share", -1),
            "revenue_per_share": row.get("revenue_per_share", -1),
            "dividend_per_share": row.get("dividend_per_share", -1),
            "shares_outstanding": row.get("shares_outstanding", -1),
            "analyst_target_price": row.get("analyst_target_price", -1),
            "ebitda": row.get("ebitda", -1),
            "is_etf": row.get("is_etf", 0)
        }

    return final

def get_dividend_history(ticker: str, db: MySQLClient = Depends(get_db)):
    ticker = ticker.upper()
    try:
        history = db.fetch_all("""
            SELECT declaration_date, amount 
            FROM dividend_history 
            WHERE ticker = %s 
            ORDER BY declaration_date ASC
        """, (ticker,)) # Pass as tuple
        if history:
            return history

        url = f'https://www.alphavantage.co/query?function=DIVIDEND&symbol={ticker}&apikey={stock_token}'
        r = requests.get(url)
        data = r.json()
        dividend_history = data.get("data", [])
        records_to_insert = []
        for d in dividend_history:
            try:
                record = (
                    ticker,
                    float(d['amount']), 
                    float(d['declaration_date']), 
                    float(d['ex_dividend_date']), 
                    float(d['payment_date'])
                )
                records_to_insert.append(record)
            except (KeyError, ValueError) as e:
                print(f"Skipping record for {date_str}: {e}")
                continue
        if records_to_insert:
            rows_inserted = db.insert_many_prices(ticker, records_to_insert)
            print(f"✅ Successfully inserted {rows_inserted} price records for {ticker}.")
    except Exception as e:
        print(f"Failed to fetch dividend history for {ticker}: {e}")

def get_etf_info(ticker: str, db: MySQLClient = Depends(get_db)):
    ticker = ticker.upper()
    try:
        url = f'https://www.alphavantage.co/query?function=ETF_PROFILE&symbol={ticker}&apikey={stock_token}'
        r = requests.get(url)
        data = r.json()
        db.update_etf_info(ticker, data.get("dividend_per_share", 0))
        return data.get("dividend_per_share", 0)
    except Exception as e:
        print(f"Failed to fetch etf info for {ticker}: {e}")

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