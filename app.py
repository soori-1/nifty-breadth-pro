import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(layout="wide", page_title="Nifty 500 Pro Dashboard")
st.title("📊 Right Horizons Nifty 500 Market Breadth")
# --- HIDE STREAMLIT BRANDING ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
def load_data():
    if not os.path.exists("Nifty500_Master_Data.csv"):
        return pd.DataFrame()
    
    df = pd.read_csv("Nifty500_Master_Data.csv")
    df['DATE'] = pd.to_datetime(df['DATE'])
    
    # Calculate Net Highs
    df['Net_Highs'] = df['52W_HIGH'] - df['52W_LOW']
    
    # Add a 10-Day Exponential Moving Average (EMA)
    df['Net_Highs_EMA'] = df['Net_Highs'].ewm(span=10, adjust=False).mean()
    
    df = df.sort_values(by='DATE')
    return df

df = load_data()
# The ttl=3600 tells it to clear the cache every 1 hour, ensuring today's new data always shows up
@st.cache_data(ttl=3600) 
def load_data():
    if not os.path.exists("Nifty500_Master_Data.csv"):
        return pd.DataFrame()
    
    df = pd.read_csv("Nifty500_Master_Data.csv")
    df['DATE'] = pd.to_datetime(df['DATE'])
    
    # Calculate Net Highs
    df['Net_Highs'] = df['52W_HIGH'] - df['52W_LOW']
    
    # Add a 10-Day Exponential Moving Average (EMA)
    df['Net_Highs_EMA'] = df['Net_Highs'].ewm(span=10, adjust=False).mean()
    
    df = df.sort_values(by='DATE')
    return df
 # --- STYLED DATA TABLE ---
    st.subheader("Latest Market Data (Color-Coded)")
    
    # 1. Format the data
    display_df = df.sort_values(by='DATE', ascending=False).head(20).copy()
    display_df['DATE'] = display_df['DATE'].dt.strftime('%d %b %Y') 
    
    display_df = display_df[['DATE', 'NIFTY_500_CLOSE', '52W_HIGH', '52W_LOW', 'Net_Highs', 'PCT_HIGH']]
    
    display_df.rename(columns={
        'DATE': 'Date',
        'NIFTY_500_CLOSE': 'Index Close',
        '52W_HIGH': 'New Highs',
        '52W_LOW': 'New Lows',
        'Net_Highs': 'Net Highs (H-L)',
        'PCT_HIGH': '% Stocks at High'
    }, inplace=True)

    # 2. Use Streamlit's built-in column configuration for foolproof styling
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Index Close": st.column_config.NumberColumn(
                "Index Close",
                format="%.2f"
            ),
            "New Highs": st.column_config.NumberColumn(
                "New Highs",
                help="Number of stocks hitting 52-week highs"
            ),
            "New Lows": st.column_config.NumberColumn(
                "New Lows",
                help="Number of stocks hitting 52-week lows"
            ),
            "Net Highs (H-L)": st.column_config.NumberColumn(
                "Net Highs (H-L)",
                help="Positive = Bullish, Negative = Bearish"
            ),
            "% Stocks at High": st.column_config.NumberColumn(
                "% Stocks at High",
                format="%.1f%%"
            )
        }
    )
