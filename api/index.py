from flask import Flask, request
import yfinance as yf
import os
import requests

# Bot Config
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8905985212:AAHGD1pDMkavJ2_Pk6Ewx2hCN9RuDkKEoB4")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = Flask(__name__)

def send_telegram_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def get_gold_signal():
    try:
        data = yf.download("GC=F", period="1d", interval="15m", progress=False, auto_adjust=True)
        if data.empty:
            return "Market closed now. Try during London session (11AM-2PM EAT) - best for Gold."
        
        close = data['Close']
        price = float(close.iloc[-1])
        ema20 = float(close.ewm(span=20).mean().iloc[-1])
        ema50 = float(close.ewm(span=50).mean().iloc[-1])
        
        if price > ema20 and ema20 > ema50:
            action = "BUY 🟢"
            sl = price * 0.997
            tp = price * 1.003
        elif price < ema20 and ema20 < ema50:
            action = "SELL 🔴"
            sl = price * 1.003
            tp = price * 0.997
        else:
            action = "WAIT ⚪ (No clear trend)"
            sl = price * 0.998
            tp = price * 1.002

        return f"""🔥 FOREX SNIPER - FREE DEMO

Pair: XAU/USD (Gold)
Price: {price:.2f}
EMA20: {ema20:.2f} | EMA50: {ema50:.2f}

ACTION: {action}
Entry: {price:.2f}
SL: {sl:.2f}
TP1: {tp:.2f}

How to use: Open MT5 -> {action} Gold at {price:.2f}
"""
    except Exception as e:
        return f"Error fetching market data: {e}"

@app.route('/', methods=['GET'])
def home():
    return "Forex Sniper KE Bot is running!"

@app.route('/api', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        return "Webhook endpoint active"

    try:
        update = request.get_json()
        if update and "message" in update:
            chat_id = update["message"]["chat"]["id"]
            text = update["message"].get("text", "")
            
            if text.startswith("/start"):
                send_telegram_message(chat_id, "Welcome to Forex Sniper KE Bot 🎯\n\nUse /gold to get live XAU/USD signals.")
            elif "/gold" in text or "/signal" in text:
                signal = get_gold_signal()
                send_telegram_message(chat_id, signal)
            else:
                send_telegram_message(chat_id, "Send /gold to get live Gold signals.")
    except Exception as e:
        print(f"Webhook error: {e}")

    return "ok", 200
