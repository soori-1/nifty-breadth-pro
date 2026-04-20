import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# Configuration
FILE_NAME = "Nifty500_Master_Data.csv"
URL = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"

def run_update():
    # A. Get Tickers
    df_tickers = pd.read_csv(URL)
    tickers = [s + ".NS" for s in df_tickers['Symbol'].tolist()]
    
    start_date = "1999-01-01" 
    end_date = datetime.now().strftime('%Y-%m-%d')
    print(f"Targeting: {start_date} to {end_date}")

    # B. Get the Index Price
    print("Downloading Index Price...")
    # Yahoo Finance deleted ^CNX500. We use ^CRSLDX (the new Nifty 500 symbol) 
    # and fallback to ^NSEI (Nifty 50) just in case.
    idx_raw = yf.download("^CRSLDX", start=start_date, end=end_date, progress=False)
    
    if len(idx_raw) == 0:
        print("Nifty 500 ticker failed. Falling back to Nifty 50 (^NSEI)...")
        idx_raw = yf.download("^NSEI", start=start_date, end=end_date, progress=False)

    # Flatten Nifty Index to 1D Series
    if isinstance(idx_raw.columns, pd.MultiIndex):
        nifty_series = idx_raw['Adj Close'].iloc[:, 0]
    else:
        nifty_series = idx_raw['Adj Close'] if 'Adj Close' in idx_raw.columns else idx_raw['Close']
    
    nifty_series = nifty_series.dropna()
    master_index = nifty_series.index
    print(f"Master Timeline Established: {len(master_index)} trading days.")

    if len(master_index) == 0:
        print("CRITICAL: Both Index tickers failed. Exiting.")
        return

    # C. Download stocks and join them to the Master Timeline
    all_highs = pd.DataFrame(index=master_index)
    all_lows = pd.DataFrame(index=master_index)
    batch_size = 40
    
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        data = yf.download(batch, start=start_date, end=end_date, progress=False)
        
        if not data.empty:
            # Join the 'High' and 'Low' columns to our master index
            if 'High' in data.columns:
                all_highs = all_highs.join(data['High'], how='left', rsuffix='_h')
            if 'Low' in data.columns:
                all_lows = all_lows.join(data['Low'], how='left', rsuffix='_l')
        
        print(f"Batch {i//batch_size + 1} Done...")
        time.sleep(1)

    # D. Breadth Math
    print("Calculating 52-Week Highs/Lows...")
    prev_52w_highs = all_highs.shift(1).rolling(window=252).max()
    prev_52w_lows = all_lows.shift(1).rolling(window=252).min()
    
    high_counts = (all_highs >= prev_52w_highs).sum(axis=1)
    low_counts = (all_lows <= prev_52w_lows).sum(axis=1)
    active_count = all_highs.notna().sum(axis=1)

    # E. Final Table Construction (Flattening everything to 1D)
    final_df = pd.DataFrame({
        'DATE': master_index,
        'NIFTY_500_CLOSE': nifty_series.values.flatten(),
        '52W_HIGH': high_counts.values.flatten(),
        '52W_LOW': low_counts.values.flatten(),
        'PCT_HIGH': ((high_counts / active_count) * 100).fillna(0).round(1).values.flatten()
    })

    # F. Force Date Formatting and Filter
    final_df['DATE'] = pd.to_datetime(final_df['DATE'])
    final_df = final_df[final_df['DATE'] >= '2000-01-01']
    
    # Final Check
    if final_df.empty:
        print("CRITICAL ERROR: Final table is empty!")
    else:
        final_df.to_csv(FILE_NAME, index=False)
        print(f"SUCCESS: {FILE_NAME} saved with {len(final_df)} rows.")

if __name__ == "__main__":
    run_update()
