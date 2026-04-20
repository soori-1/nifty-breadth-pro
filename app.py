import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(layout="wide", page_title="Nifty 500 Pro Dashboard")
st.title("📊 Nifty 500 Market Breadth Dashboard")

# 1. Load Data with Safety Check
@st.cache_data
def load_data():
    if not os.path.exists("Nifty500_Master_Data.csv"):
        return pd.DataFrame()
    
    df = pd.read_csv("Nifty500_Master_Data.csv")
    df['DATE'] = pd.to_datetime(df['DATE'])
    # Net New Highs (NNH) Oscillator
    df['Net_Highs'] = df['52W_HIGH'] - df['52W_LOW']
    return df

df = load_data()

if df.empty:
    st.error("⚠️ Data file not found. Please run your GitHub Action first to generate the CSV.")
else:
    # 2. Setup 3 Subplots
    fig = make_subplots(
        rows=3, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.04,
        subplot_titles=("Nifty 500 Index Price", "New 52W Highs (+) and Lows (-)", "Net New Highs Oscillator (H - L)"),
        row_heights=[0.5, 0.25, 0.25]
    )

    # --- Row 1: Nifty 500 Close (Line) ---
    fig.add_trace(go.Scatter(
        x=df['DATE'], y=df['NIFTY_500_CLOSE'], 
        name="Nifty 500", line=dict(color='#00F2FF', width=2)
    ), row=1, col=1)

    # --- Row 2: High/Low Counts (Bars) ---
    fig.add_trace(go.Bar(
        x=df['DATE'], y=df['52W_HIGH'], 
        name="Highs", marker_color='#26A69A'
    ), row=2, col=1)
    
    fig.add_trace(go.Bar(
        x=df['DATE'], y=-df['52W_LOW'], 
        name="Lows", marker_color='#EF5350'
    ), row=2, col=1)

    # --- Row 3: Net Highs Oscillator (Line) ---
    fig.add_trace(go.Scatter(
        x=df['DATE'], y=df['Net_Highs'], 
        name="Net Highs", line=dict(color='white', width=1),
        fill='tozeroy', fillcolor='rgba(255, 255, 255, 0.1)'
    ), row=3, col=1)

    # 3. Global Styling
    fig.update_layout(
        height=900, 
        template="plotly_dark", 
        hovermode="x unified", 
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    
    st.plotly_chart(fig, use_container_width=True)

    # 4. Recent Data Table
    st.subheader("Recent Market Pulse")
    st.dataframe(
        df.tail(20).sort_values(by='DATE', ascending=False), 
        use_container_width=True, 
        hide_index=True
    )
