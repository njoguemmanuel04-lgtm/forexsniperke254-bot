from flask import Flask, request
import yfinance as yf
import os
from telegram import Bot

# Your bot token from BotFather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8905985212:AAHGD1pDMkavJ2_Pk6Ewx2hCN9RuDkKEoB4")
bot = Bot(token=BOT_TOKEN)

app = Flask(__name__)

def get_gold_signal():
    try:
        # Gold futures
        data = yf.download("GC=F", period="1d", interval="15m", progress=False, auto_adjust=True)
        if data.empty:
            return "Market closed now. Try during London session 11AM-2PM EAT - best for Gold."
        
        close = data['Close']
        price = float(close.iloc[-1])
        ema20 = float(close.ewm(span=20).mean().iloc[-1])
        ema50 = float(close.ewm(span=50).mean().iloc[-1])
        
        # Simple logic for FREE demo
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

        signal = f"""🔥 FOREX SNIPER - FREE DEMO

Pair: XAU/USD (Gold)
Price: {price:.2f}
EMA20: {ema20:.2f} | EMA50: {ema50:.2f}

ACTION: {action}
Entry: {price:.2f}
SL: {sl:.2f}
TP1: {tp:.2f}

How to use: Open MT5 -> {action} Gold at {price:.2f}

This is FREE demo. Premium gives auto TP/SL + M-Pesa alerts.
"""
        return signal
    except Exception as e:
        return f"Error fetching market: {e}. Market may be closed."

@app.route('/api', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        if not update:
            return "ok", 200
            
        # Handle messages
        if "message" in update:
            msg = update["message"]
            chat_id = msg["chat"]["id"]
            text = msg.get("text", "")
            
            if text.startswith("/start"):
                welcome = """Welcome to Forex Sniper KE Bot 🎯 FREE DEMO

Commands:
/gold - Live Gold signal
/signal - Latest signal
/eurusd - EUR/USD

Tap /gold to test the flow Chairman"""
                bot.send_message(chat_id=chat_id, text=welcome)
                
            elif "/gold" in text or "/signal" in text or "Gold" in text:
                signal = get_gold_signal()
                bot.send_message(chat_id=chat_id, text=signal)
                
            elif "/eurusd" in text:
                bot.send_message(chat_id=chat_id, text="EUR/USD feature coming in premium version. Use /gold for now.")
            else:
                bot.send_message(chat_id=chat_id, text="Send /gold for live Gold signal")

        # Handle button clicks
        if "callback_query" in update:
            chat_id = update["callback_query"]["message"]["chat"]["id"]
            bot.send_message(chat_id=chat_id, text=get_gold_signal())

    except Exception as e:
        print(f"Error: {e}")
    
    return "ok", 200

@app.route('/')
def home():
    return "Forex Sniper KE Bot @forexsniperke254_bot is LIVE - FREE DEMO active"

@app.route('/api', methods=['GET'])
def check():
    return "Webhook active - Bot is live"
