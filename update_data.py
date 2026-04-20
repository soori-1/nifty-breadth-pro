import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. Configuration
FILE_NAME = "Nifty500_Master_Data.csv"
INDEX_TICKER = "^CNX500" 
URL = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"

def run_update():
    # Load Tickers
    df_tickers = pd.read_csv(URL)
    tickers = [s + ".NS" for s in df_tickers['Symbol'].tolist()]
    
    start_date = "1999-01-01" 
    end_date = datetime.now().strftime('%Y-%m-%d')
    print(f"Fetching data from {start_date} to {end_date}...")

    # Download Nifty 500 Index first to establish the master timeline
    idx_raw = yf.download(INDEX_TICKER, start=start_date, end=end_date, progress=False)
    
    # Flatten MultiIndex if present
    if isinstance(idx_raw.columns, pd.MultiIndex):
        nifty_series = idx_raw['Adj Close'].iloc[:, 0]
    else:
        nifty_series = idx_raw['Adj Close'] if 'Adj Close' in idx_raw.columns else idx_raw['Close']
    
    nifty_series = nifty_series.squeeze() # Ensure 1D

    # Download 500 stocks in batches
    all_highs = pd.DataFrame(index=nifty_series.index)
    all_lows = pd.DataFrame(index=nifty_series.index)
    batch_size = 40
    
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        data = yf.download(batch, start=start_date, end=end_date, progress=False)
        
        if not data.empty:
            # Safely extract High/Low
            if 'High' in data.columns:
                h = data['High']
                all_highs = all_highs.join(h, how='left', rsuffix='_high')
            if 'Low' in data.columns:
                l = data['Low']
                all_lows = all_lows.join(l, how='left', rsuffix='_low')
                
        print(f"Progress: {min(i+batch_size, 500)}/500 stocks...")
        time.sleep(1)

    print("Calculating metrics...")
    # 52-Week Logic
    rolling_h = all_highs.shift(1).rolling(window=252).max()
    rolling_l = all_lows.shift(1).rolling(window=252).min()
    
    high_count = (all_highs >= rolling_h).sum(axis=1)
    low_count = (all_lows <= rolling_l).sum(axis=1)
    active = all_highs.notna().sum(axis=1)

    # Build Final DataFrame
    final_df = pd.DataFrame({
        'DATE': nifty_series.index,
        'NIFTY_500_CLOSE': nifty_series.values,
        '52W_HIGH': high_count.values,
        '52W_LOW': low_count.values,
        'PCT_HIGH': ((high_count / active) * 100).fillna(0).round(1).values
    })

    # Start from 2000 and save
    final_df = final_df[final_df['DATE'] >= '2000-01-01']
    final_df.to_csv(FILE_NAME, index=False)
    print(f"SUCCESS: {FILE_NAME} generated with {len(final_df)} rows.")

if __name__ == "__main__":
    run_update()
