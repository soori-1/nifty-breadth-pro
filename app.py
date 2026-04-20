import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide", page_title="Nifty 500 Pro Dashboard")
st.title("📊 Nifty 500 Market Breadth Dashboard")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("Nifty500_Master_Data.csv")
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['Net_Highs'] = df['52W_HIGH'] - df['52W_LOW']
    return df

try:
    df = load_data()

    # Layout with 3 subplots
    fig = make_subplots(
        rows=3, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.04,
        subplot_titles=("Nifty 500 Index Price", "New Highs (+) and New Lows (-)", "Net New Highs Line (H - L)"),
        row_heights=[0.5, 0.25, 0.25]
    )

    # 1. Nifty 500 Line (Top)
    fig.add_trace(go.Scatter(x=df['DATE'], y=df['NIFTY_500_CLOSE'], name="Nifty 500", 
                             line=dict(color='#00CCFF', width=2)), row=1, col=1)

    # 2. Highs and Lows Bars (Middle)
    fig.add_trace(go.Bar(x=df['DATE'], y=df['52W_HIGH'], name="New Highs", marker_color='green'), row=2, col=1)
    fig.add_trace(go.Bar(x=df['DATE'], y=-df['52W_LOW'], name="New Lows", marker_color='red'), row=2, col=1)

    # 3. Net Highs Line (Bottom)
    fig.add_trace(go.Scatter(x=df['DATE'], y=df['Net_Highs'], name="Net Highs", 
                             line=dict(color='white', width=1.5), fill='tozeroy', 
                             fillcolor='rgba(255, 255, 255, 0.1)'), row=3, col=1)

    # Formatting
    fig.update_layout(height=900, template="plotly_dark", hovermode="x unified", showlegend=False)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    
    st.plotly_chart(fig, use_container_width=True)

    # Data Table
    st.subheader("Recent Data Points")
    st.dataframe(df.tail(20).sort_values(by='DATE', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Waiting for data... Please ensure your GitHub Action has finished. Error: {e}")
