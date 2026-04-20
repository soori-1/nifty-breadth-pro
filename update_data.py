import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import os

# Configuration
FILE_NAME = "Nifty500_Master_Data.csv"
INDEX_TICKER = "^CNX500" 
URL = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"

def get_tickers():
    df = pd.read_csv(URL)
    return [s + ".NS" for s in df['Symbol'].tolist()]

def run_update():
    tickers = get_tickers()
    start_date = "1999-01-01" 
    end_date = datetime.now().strftime('%Y-%m-%d')

    print(f"Starting Data Engine... Targeting {end_date}")
    all_highs = pd.DataFrame()
    all_lows = pd.DataFrame()
    batch_size = 30
    
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        try:
            # IMPORTANT: Removed auto_adjust to avoid data gaps
            data = yf.download(batch, start=start_date, end=end_date, progress=False)
            all_highs = pd.concat([all_highs, data['High']], axis=1)
            all_lows = pd.concat([all_lows, data['Low']], axis=1)
            print(f"Downloaded {min(i+batch_size, 500)}/500 stocks...")
            time.sleep(1)
        except:
            continue

    # NEW: Specific download for Adjusted Close for consistency
    print("Downloading Nifty 500 Index Price (Adj Close)...")
    idx_raw = yf.download(INDEX_TICKER, start=start_date, end=end_date, progress=False)
    # Extract just the Adj Close column
    idx_close = idx_raw['Adj Close'].reindex(all_highs.index)

    # 52-Week High/Low Logic (252 trading days)
    rolling_h = all_highs.shift(1).rolling(window=252).max()
    rolling_l = all_lows.shift(1).rolling(window=252).min()
    
    high_count = (all_highs >= rolling_h).sum(axis=1)
    low_count = (all_lows <= rolling_l).sum(axis=1)
    active = all_highs.notna().sum(axis=1)

    # Combine into Master Table
    final_df = pd.DataFrame({
        'DATE': high_count.index,
        'NIFTY_500_CLOSE': idx_close.values,
        '52W_HIGH': high_count.values.astype(int),
        '52W_LOW': low_count.values.astype(int),
        'PCT_HIGH': ((high_count / active) * 100).fillna(0).round(1)
    })

    # Filter to start from 2000 onwards and save
    final_df = final_df[final_df['DATE'] >= '2000-01-01']
    final_df.to_csv(FILE_NAME, index=False)
    print("SUCCESS: Master Data Updated with complete Nifty 500 Index.")

if __name__ == "__main__":
    run_update()
