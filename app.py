import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(layout="wide", page_title="Market Breadth Terminal")

# Hide Streamlit Branding
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container {padding-top: 2rem;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("Nifty 500 Breadth Terminal")
st.markdown("<p style='color: #8c919c;'>Internal Quantitative Tool | Synchronized Price & Breadth Action</p>", unsafe_allow_html=True)

@st.cache_data(ttl=3600) 
def load_data():
    if not os.path.exists("Nifty500_Master_Data.csv"):
        return pd.DataFrame()
    
    df = pd.read_csv("Nifty500_Master_Data.csv")
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['Net_Highs'] = df['52W_HIGH'] - df['52W_LOW']
    df = df.sort_values(by='DATE')
    return df

df = load_data()

if df.empty:
    st.error("System initializing. Please ensure data pipeline is complete.")
else:
    # --- EXECUTIVE KPI ROW ---
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Nifty 500 Index", f"{latest['NIFTY_500_CLOSE']:,.2f}", f"{latest['NIFTY_500_CLOSE'] - prev['NIFTY_500_CLOSE']:,.2f}")
    with col2:
        st.metric("New 52W Highs", int(latest['52W_HIGH']), int(latest['52W_HIGH'] - prev['52W_HIGH']))
    with col3:
        st.metric("New 52W Lows", int(latest['52W_LOW']), int(latest['52W_LOW'] - prev['52W_LOW']), delta_color="inverse")
    with col4:
        st.metric("Net Breadth (H-L)", int(latest['Net_Highs']), int(latest['Net_Highs'] - prev['Net_Highs']))

    st.divider()

    # --- INTERACTIVE INDICATOR SELECTOR ---
    chart_choice = st.radio(
        "Select Lower Indicator:",
        ["Net Highs (H-L)", "52-Week Highs", "52-Week Lows"],
        horizontal=True
    )

    # --- SYNCHRONIZED CHART ---
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        row_heights=[0.7,
