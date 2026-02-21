import os
import requests
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ----------- TELEGRAM FUNCTIONS -----------

def send_media_group(images):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup"

    media = []
    files = {}

    for i, image in enumerate(images):
        files[f"photo{i}"] = open(image, "rb")
        media.append({
            "type": "photo",
            "media": f"attach://photo{i}"
        })

    requests.post(
        url,
        data={"chat_id": CHAT_ID, "media": str(media).replace("'", '"')},
        files=files
    )

    for f in files.values():
        f.close()


def send_photo(photo_path, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(photo_path, "rb") as photo:
        requests.post(
            url,
            data={"chat_id": CHAT_ID, "caption": caption},
            files={"photo": photo}
        )

# ----------- ANALYSIS FUNCTION -----------

def analyze_asset(symbol, name):
    data = yf.download(symbol, period="120d")

    data["MA20"] = data["Close"].rolling(20).mean()
    data["MA50"] = data["Close"].rolling(50).mean()
    data["Returns"] = data["Close"].pct_change()

    volatility = data["Returns"].std() * (252 ** 0.5)
    volatility_percent = float(volatility * 100)

    current_price = float(data["Close"].iloc[-1])
    ma20 = float(data["MA20"].iloc[-1])
    ma50 = float(data["MA50"].iloc[-1])

    if current_price > ma20 and ma20 > ma50:
        trend = "📈 Bullish"
        trend_score = 1
    elif current_price < ma20 and ma20 < ma50:
        trend = "📉 Bearish"
        trend_score = -1
    else:
        trend = "⚖️ Sideways"
        trend_score = 0

    if volatility_percent > 60:
        risk = "🔴 High Risk"
        risk_score = -1
    elif volatility_percent > 30:
        risk = "🟡 Medium Risk"
        risk_score = 0
    else:
        risk = "🟢 Low Risk"
        risk_score = 1

    confidence = (trend_score * 50) + (risk_score * 25) + 50
    confidence = max(0, min(100, confidence))

    # Generate chart
    plt.figure()
    plt.plot(data["Close"])
    plt.title(f"{name} Price Chart")
    plt.xlabel("Days")
    plt.ylabel("Price")
    filename = f"{symbol}.png"
    plt.savefig(filename)
    plt.close()

    caption = f"""
📊 {name} Report

Price: {round(current_price,2)}
Trend: {trend}
Volatility: {round(volatility_percent,2)}%
Risk: {risk}
Confidence Score: {confidence}%
"""

    return filename, caption


# ----------- MAIN EXECUTION -----------

# First group (single message)
group_assets = [
    ("BTC-USD", "Bitcoin"),
    ("ETH-USD", "Ethereum"),
    ("^NSEI", "NIFTY 50")
]

group_images = []

for symbol, name in group_assets:
    image, caption = analyze_asset(symbol, name)
    group_images.append(image)

send_media_group(group_images)


# QQQ separate message
qqq_image, qqq_caption = analyze_asset("QQQ", "Invesco QQQ Trust")
send_photo(qqq_image, qqq_caption)


# QQQM separate message
qqqm_image, qqqm_caption = analyze_asset("QQQM", "Invesco NASDAQ 100 ETF")
send_photo(qqqm_image, qqqm_caption)
