import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import os

# Configuration
FILE_NAME = "Nifty500_Master_Data.csv"
URL = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"

def get_tickers():
    df = pd.read_csv(URL)
    return [s + ".NS" for s in df['Symbol'].tolist()]

def run_update():
    tickers = get_tickers()
    # If the file already exists, we can use a shorter lookback to save time
    # But for the first run, we need the full history
    start_date = "1999-01-01" 
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    all_highs = pd.DataFrame()
    all_lows = pd.DataFrame()
    batch_size = 20 # Smaller batches are safer for GitHub
    
    print(f"Downloading history for {len(tickers)} stocks...")
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        try:
            # Removed auto_adjust for better stability during initial massive pull
            data = yf.download(batch, start=start_date, end=end_date, progress=False)
            all_highs = pd.concat([all_highs, data['High']], axis=1)
            all_lows = pd.concat([all_lows, data['Low']], axis=1)
            print(f"Completed {i+batch_size} stocks...")
            time.sleep(2)
        except:
            continue

    idx_data = yf.download("^CNX500", start=start_date, end=end_date, progress=False)['Close']

    # Breadth Logic
    rolling_h = all_highs.shift(1).rolling(window=252).max()
    rolling_l = all_lows.shift(1).rolling(window=252).min()
    
    high_count = (all_highs >= rolling_h).sum(axis=1)
    low_count = (all_lows <= rolling_l).sum(axis=1)
    active = all_highs.notna().sum(axis=1)

    final_df = pd.DataFrame({
        'DATE': high_count.index,
        'NIFTY_500_CLOSE': idx_data.reindex(high_count.index).values,
        '52W_HIGH': high_count.values.astype(int),
        '52W_LOW': low_count.values.astype(int),
        'PCT_HIGH': ((high_count / active) * 100).fillna(0).round(1)
    })

    final_df = final_df[final_df['DATE'] >= '2000-01-01']
    final_df.to_csv(FILE_NAME, index=False)
    print("Database Updated Successfully!")

if __name__ == "__main__":
    run_update()
