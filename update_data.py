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
        # Downloading data for the batch
        data = yf.download(batch, start=start_date, end=end_date, auto_adjust=True, progress=False)
        
        # We ensure we are selecting the 'High' and 'Low' columns properly
        if 'High' in data.columns:
            all_highs = pd.concat([all_highs, data['High']], axis=1)
        if 'Low' in data.columns:
            all_lows = pd.concat([all_lows, data['Low']], axis=1)
            
        print(f"Downloaded {min(i+batch_size, 500)}/500 stocks...")
        time.sleep(1)

    # Download Nifty 500 Index Price - We force it to be a 1D Series using .squeeze()
    print("Downloading Index Price...")
    idx_data = yf.download(INDEX_TICKER, start=start_date, end=end_date, progress=False)
    # Extract just the Close column and flatten it
    if isinstance(idx_data.columns, pd.MultiIndex):
        nifty_close = idx_data['Close'].iloc[:, 0]
    else:
        nifty_close = idx_data['Close']
        
    # Logic for 52-Week Highs/Lows
    rolling_h = all_highs.shift(1).rolling(window=252).max()
    rolling_l = all_lows.shift(1).rolling(window=252).min()
    
    high_count = (all_highs >= rolling_h).sum(axis=1)
    low_count = (all_lows <= rolling_l).sum(axis=1)
    active = all_highs.notna().sum(axis=1)

    # Build the DataFrame using Series directly (safer than .values)
    final_df = pd.DataFrame({
        'NIFTY_500_CLOSE': nifty_close,
        '52W_HIGH': high_count,
        '52W_LOW': low_count,
        'PCT_HIGH': ((high_count / active) * 100).fillna(0).round(1)
    }).reset_index() # This moves the Date from the index to a column

    # Rename the date column to match our requirements
    final_df.rename(columns={'Date': 'DATE', 'index': 'DATE'}, inplace=True)
    
    # Final cleanup: Start from 2000 and save
    final_df = final_df[final_df['DATE'] >= '2000-01-01']
    final_df.to_csv(FILE_NAME, index=False)
    print(f"SUCCESS: {FILE_NAME} generated with {len(final_df)} rows.")

if __name__ == "__main__":
    run_update()
