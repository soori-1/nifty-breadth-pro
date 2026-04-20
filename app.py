import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# 1. Page Configuration MUST be the first Streamlit command
st.set_page_config(layout="wide", page_title="Nifty 500 Pro Dashboard")

# 2. Hide all Streamlit Branding (Boss-Ready Mode)
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("📊 Right Horizons Nifty 500 Market Breadth")

# 3. Fast Loading Data Engine (1-Hour Cache)
@st.cache_data(ttl=3600) 
def load_data():
    if not os.path.exists("Nifty500_Master_Data.csv"):
        return pd.DataFrame()
    
    df = pd.read_csv("Nifty500_Master_Data.csv")
    df['DATE'] = pd.to_datetime(df['DATE'])
    
    # Calculate Net Highs and EMA Trend
    df['Net_Highs'] = df['52W_HIGH'] - df['52W_LOW']
    df['Net_Highs_EMA'] = df['Net_Highs'].ewm(span=10, adjust=False).mean()
    
    df = df.sort_values(by='DATE')
    return df

df = load_data()

# 4. Dashboard UI
if df.empty:
    st.warning("⚠️ CSV is currently empty or not found. Please wait for the GitHub Action to finish.")
else:
    # --- CHARTS ---
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04,
        subplot_titles=("Nifty 500 Index Price", "New Highs (+) and Lows (-)", "Net High-Low Oscillator & 10-Day Trend (EMA)"),
        row_heights=[0.4, 0.3, 0.3] 
    )

    # Top: Nifty Line
    fig.add_trace(go.Scatter(
        x=df['DATE'], y=df['NIFTY_500_CLOSE'], 
        name="Index", line=dict(color='#00d4ff', width=2)
    ), row=1, col=1)

    # Middle: High/Low Bars
    fig.add_trace(go.Bar(
        x=df['DATE'], y=df['52W_HIGH'], 
        name="Highs", marker_color='#26a69a'
    ), row=2, col=1)
    
    fig.add_trace(go.Bar(
        x=df['DATE'], y=-df['52W_LOW'], 
        name="Lows", marker_color='#ef5350'
    ), row=2, col=1)

    # Bottom: Net Highs Line Graph
    fig.add_trace(go.Scatter(
        x=df['DATE'], y=df['Net_Highs'], 
        name="Daily Net", mode='lines', line=dict(color='rgba(255, 255, 255, 0.4)', width=1)
    ), row=3, col=1)
    
    fig.add_trace(go.Scatter(
        x=df['DATE'], y=df['Net_Highs_EMA'], 
        name="10-Day Trend", mode='lines', line=dict(color='#ffeb3b', width=2)
    ), row=3, col=1)

    fig.add_hline(y=0, line_dash="dash", line_color="#ff5252", line_width=1.5, row=3, col=1)

    fig.update_layout(height=1000, template="plotly_dark", hovermode="x unified", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # --- DATA TABLE ---
    st.subheader("Latest Market Data")
    
    # Format the data cleanly
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

    # Streamlit Native Configuration for rendering without
