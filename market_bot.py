import os
import requests
import yfinance as yf
import pandas as pd

# Get secrets from GitHub
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

# Download 90 days of BTC data
data = yf.download("BTC-USD", period="90d")

# Calculate moving averages
data["MA20"] = data["Close"].rolling(20).mean()
data["MA50"] = data["Close"].rolling(50).mean()

# Calculate daily returns
data["Returns"] = data["Close"].pct_change()

# Calculate annualized volatility
volatility = data["Returns"].std() * (252 ** 0.5)
volatility_percent = float(volatility * 100)

# Get latest values safely
current_price = float(data["Close"].iloc[-1])
ma20 = float(data["MA20"].iloc[-1])
ma50 = float(data["MA50"].iloc[-1])

# Determine trend
if current_price > ma20 and ma20 > ma50:
    trend = "📈 Bullish"
elif current_price < ma20 and ma20 < ma50:
    trend = "📉 Bearish"
else:
    trend = "⚖️ Sideways"

# Determine risk level
if volatility_percent > 60:
    risk = "🔴 High Risk"
elif volatility_percent > 30:
    risk = "🟡 Medium Risk"
else:
    risk = "🟢 Low Risk"

# Final message
message = f"""
📊 BTC Market Report

Price: ${round(current_price,2)}
MA20: ${round(ma20,2)}
MA50: ${round(ma50,2)}

Trend: {trend}
Volatility: {round(volatility_percent,2)}%
Risk Level: {risk}
"""

send_message(message)
