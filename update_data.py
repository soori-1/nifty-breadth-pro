import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import os

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
    all_highs = pd.DataFrame()
    all_lows = pd.DataFrame()
    batch_size = 30
    
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        data = yf.download(batch, start=start_date, end=end_date, progress=False)
        
        # Pull Highs and Lows
        if 'High' in data.columns:
            all_highs = pd.concat([all_highs, data['High']], axis=1)
        if 'Low' in data.columns:
            all_lows = pd.concat([all_lows, data['Low']], axis=1)
            
        print(f"Downloaded {min(i+batch_size, 500)}/500 stocks...")
        time.sleep(1)

    # --- THE FIX FOR THE VALUEERROR ---
    print("Downloading Index Price...")
    idx_raw = yf.download(INDEX_TICKER, start=start_date, end=end_date, progress=False)
    
    # We force the Index data to be 1D by selecting just the 'Adj Close' 
    # and using .iloc[:, 0] to grab the first available column
    if 'Adj Close' in idx_raw.columns:
        nifty_series = idx_raw['Adj Close']
    else:
        nifty_series = idx_raw['Close']
    
    # If it's still a DataFrame (MultiIndex), grab the first column only
    if isinstance(nifty_series, pd.DataFrame):
        nifty_series = nifty_series.iloc[:, 0]

    # Align the index price with our breadth dates (important for holidays)
    nifty_final = nifty_series.reindex(all_highs.index).ffill()
    
    # Breadth Logic
    rolling_h = all_highs.shift(1).rolling(window=252).max()
    rolling_l = all_lows.shift(1).rolling(window=252).min()
    
    high_count = (all_highs >= rolling_h).sum(axis=1)
    low_count = (all_lows <= rolling_l).sum(axis=1)
    active = all_highs.notna().sum(axis=1)

    # Constructing final DataFrame safely
    final_df = pd.DataFrame({
        'NIFTY_500_CLOSE': nifty_final,
        '52W_HIGH': high_count,
        '52W_LOW': low_count,
        'PCT_HIGH': ((high_count / active) * 100).fillna(0).round(1)
    }).reset_index()

    final_df.rename(columns={'Date': 'DATE', 'index': 'DATE'}, inplace=True)
    
    # Filter for year 2000 onwards
    final_df = final_df[final_df['DATE'] >= '2000-01-01']
    final_df.to_csv(FILE_NAME, index=False)
    print(f"SUCCESS: {FILE_NAME} generated.")

if __name__ == "__main__":
    run_update()
