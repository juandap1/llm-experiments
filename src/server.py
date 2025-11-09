from flask import Flask, request, jsonify
from clients.sql_server import MySQLClient
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
db = MySQLClient()

@app.route("/")
def hello_world():
    return "<p>HOT RELOAD 2!</p>"

@app.route("/transactions")
def sql():
    transactions = db.fetch_all("SELECT * FROM transactions")
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

        return jsonify({"message": f"Transaction {id} added successfully"}), 201
    except Exception as e:
        print(f"❌ Error inserting transaction: {e}")
        return jsonify({"error": str(e)}), 500