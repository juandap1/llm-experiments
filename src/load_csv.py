import pandas as pd
from sqlalchemy import create_engine

def clean_money(x):
    if pd.isna(x):
        return None
    x = str(x)
    x = x.replace("$", "")
    x = x.replace("(", "-")
    x = x.replace(")", "")
    x = x.replace(",", "")
    return float(x)

df = pd.read_csv("csv/cleaned_etfs.csv", quotechar='"', escapechar='\\', engine="python")
df = df[df["Trans Code"].isin(["Buy", "Sell"])]
df["Activity Date"] = pd.to_datetime(df["Activity Date"], format="%m/%d/%Y")

df = df.rename(columns={
    "Instrument": "ticker",
    "Quantity": "share_count",
    "Price": "share_price",
    "Activity Date": "transaction_date",
    "Trans Code": "buying"
})

# Convert Buy/Sell into boolean 1/0
df["buying"] = df["buying"].map({"Buy": 1, "Sell": 0})

# Select only the columns your SQL table has
df = df[["ticker", "share_count", "share_price", "transaction_date", "buying"]]
df["share_price"] = df["share_price"].apply(clean_money)
df["share_count"] = pd.to_numeric(df["share_count"], errors="coerce")

engine = create_engine("mysql+pymysql://my_user:my_password@localhost/my_database")

df.to_sql("transactions", engine, if_exists="append", index=False)

# input_path = "csv/65633315-02fa-5ce1-bfc5-52777a202ae3.csv"
# output_path = "csv/cleaned_etfs.csv"

# cleaned_lines = []
# buffer = ""

# with open(input_path, "r", encoding="utf-8") as f:
#     for line in f:
#         line = line.rstrip("\n")

#         # Append the line
#         buffer += line

#         # Count quotes to know if this row is complete
#         if buffer.count('"') % 2 == 0:
#             cleaned_lines.append(buffer)
#             buffer = ""
#         else:
#             buffer += " "  # Replace newline with a space inside fields

# # Write cleaned CSV
# with open(output_path, "w", encoding="utf-8") as f:
#     for line in cleaned_lines:
#         f.write(line + "\n")

# print("Cleaned CSV written to:", output_path)


### MARK ETFS IN TABLE ###
# SET SQL_SAFE_UPDATES = 0;

# UPDATE tickers
# SET is_etf = 1
# WHERE UPPER(ticker) IN ('SCHD', 'VOO', 'QQQM', 'FDVV', 'SPMO');