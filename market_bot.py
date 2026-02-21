import requests
import yfinance as yf
import pandas as pd

BOT_TOKEN = "8554800191:AAEiJKWEW7WbyaKEApx7CT9SHC38mHxEQkk"
CHAT_ID = "7847181691"

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=data)

# Download 60 days of BTC data
data = yf.download("BTC-USD", period="60d")

# Calculate moving averages
data["MA20"] = data["Close"].rolling(20).mean()
data["MA50"] = data["Close"].rolling(50).mean()

# Get latest values as numbers
current_price = float(data["Close"].iloc[-1])
ma20 = float(data["MA20"].iloc[-1])
ma50 = float(data["MA50"].iloc[-1])

# Trend logic
if current_price > ma20 and ma20 > ma50:
    trend = "📈 Bullish"
elif current_price < ma20 and ma20 < ma50:
    trend = "📉 Bearish"
else:
    trend = "⚖️ Sideways"

message = f"""
📊 BTC Analysis

Price: ${round(current_price,2)}
MA20: ${round(ma20,2)}
MA50: ${round(ma50,2)}

Trend: {trend}
"""

send_message(message)