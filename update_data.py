import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import os

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

    # A. Download Index Price & Flatten it immediately
    idx_raw = yf.download(INDEX_TICKER, start=start_date, end=end_date, progress=False)
    
    # Logic to handle both MultiIndex and Single Index responses
    if isinstance(idx_raw.columns, pd.MultiIndex):
        nifty_series = idx_raw['Adj Close'].iloc[:, 0]
    else:
        nifty_series = idx_raw['Adj Close'] if 'Adj Close' in idx_raw.columns else idx_raw['Close']
    
    # B. Download 500 stocks in batches
    # We use the nifty_series index as our master timeline
    all_highs = pd.DataFrame(index=nifty_series.index)
    all_lows = pd.DataFrame(index=nifty_series.index)
    batch_size = 40
    
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        data = yf.download(batch, start=start_date, end=end_date, progress=False)
        
        if not data.empty:
            # Extract High/Low correctly for MultiIndex
            if 'High' in data.columns:
                h = data['High']
                all_highs = all_highs.join(h, how='left', rsuffix='_h')
            if 'Low' in data.columns:
                l = data['Low']
                all_lows = all_lows.join(l, how='left', rsuffix='_l')
        
        print(f"Progress: {min(i+batch_size, 500)}/500 stocks...")
        time.sleep(1)

    print("Calculating Metrics...")
    # C. Calculate 52-Week Breadth
    # shift(1) ensures we don't include today's high in the "prev 52-week" calc
    rolling_h = all_highs.shift(1).rolling(window=252).max()
    rolling_l = all_lows.shift(1).rolling(window=252).min()
    
    high_count = (all_highs >= rolling_h).sum(axis=1)
    low_count = (all_lows <= rolling_l).sum(axis=1)
    active = all_highs.notna().sum(axis=1)

    # D. Build Final CSV Table
    final_df = pd.DataFrame({
        'DATE': nifty_series.index,
        'NIFTY_500_CLOSE': nifty_series.values.flatten(),
        '52W_HIGH': high_count.values.flatten(),
        '52W_LOW': low_count.values.flatten(),
        'PCT_HIGH': ((high_count / active) * 100).fillna(0).round(1).values.flatten()
    })

    # Filter for 2000 onwards and save
    final_df = final_df[final_df['DATE'] >= '2000-01-01']
    final_df.to_csv(FILE_NAME, index=False)
    print(f"SUCCESS: {FILE_NAME} saved with {len(final_df)} days of data.")

if __name__ == "__main__":
    run_update()
