import yfinance as yf
import pandas as pd
import time
import os
from datetime import datetime

# 1. Configuration
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
    
    # Batch download to prevent Yahoo Finance from blocking us
    all_highs = pd.DataFrame()
    all_lows = pd.DataFrame()
    batch_size = 30
    
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        # auto_adjust=True handles stock splits/bonuses correctly
        data = yf.download(batch, start=start_date, end=end_date, auto_adjust=True, progress=False)
        all_highs = pd.concat([all_highs, data['High']], axis=1)
        all_lows = pd.concat([all_lows, data['Low']], axis=1)
        print(f"Downloaded {min(i+batch_size, 500)}/500 stocks...")
        time.sleep(1)

    # Download Nifty 500 Index Price
    idx_data = yf.download(INDEX_TICKER, start=start_date, end=end_date, progress=False)['Close']

    # 52-Week High/Low Logic (252 trading days)
    rolling_h = all_highs.shift(1).rolling(window=252).max()
    rolling_l = all_lows.shift(1).rolling(window=252).min()
    
    high_count = (all_highs >= rolling_h).sum(axis=1)
    low_count = (all_lows <= rolling_l).sum(axis=1)
    active = all_highs.notna().sum(axis=1)

    # Combine into Master Table
    final_df = pd.DataFrame({
        'DATE': high_count.index,
        'NIFTY_500_CLOSE': idx_data.reindex(high_count.index).values,
        '52W_HIGH': high_count.values.astype(int),
        '52W_LOW': low_count.values.astype(int),
        'PCT_HIGH': ((high_count / active) * 100).fillna(0).round(1)
    })

    # Start from Jan 1, 2000
    final_df = final_df[final_df['DATE'] >= '2000-01-01']
    final_df.to_csv(FILE_NAME, index=False)
    print("SUCCESS: Master Data Updated.")

if __name__ == "__main__":
    run_update()
    