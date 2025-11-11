from flask import Flask, request, jsonify, send_file
from clients.sql_server import MySQLClient
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)
db = MySQLClient()

CONTAINER_ROOT = '/app'

# SECRETS
logo_dev_token = os.getenv("LOGO_DEV_TOKEN")


@app.route("/")
def hello_world():
    return "<p>HOT RELOAD 2!</p>"

@app.route("/transactions")
def sql():
    transactions = db.fetch_all("SELECT * FROM transactions ORDER BY transaction_date DESC")
    # print("All transactions:", transactions)
    return jsonify(transactions), 200

@app.route("/transaction", methods=["POST"])
def add_transaction():
    try:
        data = request.get_json()
        # print(data)
        ticker = data.get("ticker")
        share_count = data.get("share_count")
        share_price = data.get("share_price")
        transaction_date = data.get("transaction_date")
        buying = data.get("buying")

        id = db.insert_transaction(ticker, share_count, share_price, transaction_date, buying)

        return jsonify({"message": f"Transaction {id} added successfully", "new_id": id}), 201
    except Exception as e:
        print(f"❌ Error inserting transaction: {e}")
        return jsonify({"error": str(e)}), 500
    

@app.route("/logo/<ticker>")
def get_logo(ticker):
    ticker = ticker.upper()
    try:
        row = db.fetch_one("SELECT logo FROM tickers WHERE ticker = %s", (ticker,))
        # Check if row exists AND logo path is defined
        if row and row['logo']:
            db_path = row['logo']
            if not os.path.isabs(db_path):
                logo_path = os.path.join(CONTAINER_ROOT, db_path)
            else:
                logo_path = db_path
            print(f"Database entry found for {ticker}. Logo path is: {logo_path}")
            # Check if the file exists locally
            if os.path.exists(logo_path):
                print(f"Serving local file: {logo_path}")
                return send_file(logo_path, mimetype='image/jpeg')
            # If path is in DB but file is missing, we proceed to download
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
        # Update the database with the new path
        db.update_logo(ticker, full_path)
        print(f"✅ Image successfully saved and DB updated for {ticker} at: {full_path}")
        return send_file(full_path, mimetype='image/svg+xml')
    except requests.exceptions.RequestException as e:
        # Handle errors related to the HTTP request (network, 404, etc.)
        print(f"❌ Failed to download logo for {ticker}: {e}")
        return jsonify({"error": f"Logo not found or download failed for {ticker}."}), 404
    except Exception as e:
        # Catch any other general errors (e.g., file writing issues)
        print(f"❌ An unexpected error occurred for {ticker}: {e}")
        return jsonify({"error": str(e)}), 500