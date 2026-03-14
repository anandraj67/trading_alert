import json
import os
from datetime import datetime
from upstox_client import UpstoxClient, WebSocketClient
from collections import deque

ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
API_KEY = "YOUR_API_KEY"
NIFTY_SYMBOL = "NSE_INDEX|Nifty 50"

# Store last 6 candles (rolling 5 + current)
candles = deque(maxlen=6)

def alert(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")
    os.system(f"say '{msg}'")  # You can replace with a beep or notification

def on_candle(candle):
    candles.append(candle)

    if len(candles) < 6:
        return

    past_five = list(candles)[:-1]
    last = candles[-1]

    past_high = max(c["high"] for c in past_five)
    past_low = min(c["low"] for c in past_five)

    if last["close"] > past_high:
        alert(f"Breakout UP: Close {last['close']} > Past High {past_high}")
    elif last["close"] < past_low:
        alert(f"Breakout DOWN: Close {last['close']} < Past Low {past_low}")

def start_websocket():
    client = UpstoxClient(api_key=API_KEY, access_token=ACCESS_TOKEN)
    ws = WebSocketClient(client)

    def handle_message(message):
        if message["type"] == "candle":
            c = message["data"]
            on_candle({
                "time": c["timestamp"],
                "open": c["open"],
                "high": c["high"],
                "low": c["low"],
                "close": c["close"],
                "volume": c["volume"]
            })

    ws.set_on_message(handle_message)
    ws.connect()
    ws.subscribe_candles(NIFTY_SYMBOL, interval="5minute")

start_websocket()
