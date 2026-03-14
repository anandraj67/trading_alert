import requests
import os
import time
import pandas as pd
from datetime import datetime, timedelta, time as datetime_time

ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiIzTkM5OFciLCJqdGkiOiI2ODJiOWM2ZDc4YWQ1ODc1MDU3OTJhNjUiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc0NzY4ODU1NywiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzQ3NjkyMDAwfQ.JukyDlLmc_qioitlRepx9BuhyAWQLxQ7_vAANQzHg9A"

NIFTY_SYMBOL = "NSE_INDEX|Nifty 50"
INTERVAL=1
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

def fetch_candles():
    url = f"https://api.upstox.com/v3/historical-candle/intraday/{NIFTY_SYMBOL}/minutes/{INTERVAL}"
    resp = requests.get(url, headers=headers)
    data = resp.json()
    #print(data)
    candles = data["data"]["candles"]
    df = pd.DataFrame(candles, columns=["time", "open", "high", "low", "close", "volume", "oi"])
    return df

def check_breakout(df):
    if len(df) < 6:
        return None

    latest_candle = df.iloc[0]
    past_five = df.iloc[1:6]

    past_high = past_five["high"].max()
    past_low = past_five["low"].min()

    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          "|", "Range", past_low, "-", past_high,
          "|",  "Last close:", latest_candle["close"])
    
    if latest_candle["close"] > past_high:
        return f"Breakout UP ^^^^^^^^^ | Close={latest_candle['close']} > PastHigh={past_high}", "/System/Library/Sounds/Blow.aiff"
    elif latest_candle["close"] < past_low:
        return f"Breakout DOWN vvvvvvvvv | Close={latest_candle['close']} < PastLow={past_low}", "/System/Library/Sounds/Bottle.aiff"
    
    return None

def alert(text, sound_path):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), " | alert", text)
    #os.system(f"say '{text}'")
    os.system(f'afplay "{sound_path}"')
    os.system(f'afplay "{sound_path}"')

def run_once():
    try:
        df = fetch_candles()
        text, sound_path = check_breakout(df)
        if text:
            alert(text, sound_path)
    except requests.exceptions.RequestException as e:
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "| Exception fetching data:", str(e))
    except Exception as e:
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "| General Exception:", str(e))

def is_market_open():
    now = datetime.now()
    current_time = now.time()
    current_day = now.weekday()  # Monday = 0, Sunday = 6
    
    market_start = datetime_time(9, 0)    # 9:00 AM
    market_end = datetime_time(15, 45)    # 3:45 PM

    if current_day >= 0 and current_day <= 4:
        return market_start <= current_time <= market_end
    else:
        return False

while True:
    if is_market_open():
        run_once()
    else:
        print("Market is Close right now")
    time.sleep(60*INTERVAL)

