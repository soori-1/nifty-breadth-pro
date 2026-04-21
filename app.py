import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# 1. Clean Corporate Page Config
st.set_page_config(layout="wide", page_title="Market Breadth Terminal")

# 2. Hide all Streamlit Branding
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container {padding-top: 2rem;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Professional Header
st.title("Right Horizons - Nifty 500 Market Breadth Analysis")
st.markdown("<p style='color: gray;'>Internal Quantitative Tool | Daily 52-Week High/Low Ledger</p>", unsafe_allow_html=True)

# 3. High-Speed Data Loader (Fixes the Slowness)
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
    # Gets the latest day and the previous day to show daily changes
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Nifty 500 Index", f"{latest['NIFTY_500_CLOSE']:,.2f}", f"{latest['NIFTY_500_CLOSE'] - prev['NIFTY_500_CLOSE']:,.2f}")
    with col2:
        st.metric("New 52W Highs", int(latest['52W_HIGH']), int(latest['52W_HIGH'] - prev['52W_HIGH']))
    with col3:
        # Inverting the delta color for lows (more lows is bad, fewer is good)
        st.metric("New 52W Lows", int(latest['52W_LOW']), int(latest['52W_LOW'] - prev['52W_LOW']), delta_color="inverse")
    with col4:
        st.metric("Net Breadth (H-L)", int(latest['Net_Highs']), int(latest['Net_Highs'] - prev['Net_Highs']))

    st.divider()

    # --- TOP CHART: NIFTY 500 ---
    st.subheader("Index Performance")
    fig_idx = go.Figure()
    fig_idx.add_trace(go.Scatter(x=df['DATE'], y=df['NIFTY_500_CLOSE'], name="Nifty 500", line=dict(color='#2962FF', width=2)))
    fig_idx.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), hovermode="x unified")
    st.plotly_chart(fig_idx, use_container_width=True)

    st.divider()

    # --- BOTTOM CHART: INTERACTIVE BREADTH SELECTOR ---
    st.subheader("Breadth Indicators")
    
    # The Toggle Switch
    chart_choice = st.radio(
        "Select Metric to View:",
        ["52-Week Highs", "52-Week Lows", "Net Highs (Highs - Lows)"],
        horizontal=True
    )

    fig_breadth = go.Figure()

    # Display the correct line based on user choice
    if chart_choice == "52-Week Highs":
        fig_breadth.add_trace(go.Scatter(
            x=df['DATE'], y=df['52W_HIGH'], name="Highs", 
            line=dict(color='#00C853', width=2), fill='tozeroy', fillcolor='rgba(0, 200, 83, 0.1)'
        ))
    elif chart_choice == "52-Week Lows":
        fig_breadth.add_trace(go.Scatter(
            x=df['DATE'], y=df['52W_LOW'], name="Lows", 
            line=dict(color='#D50000', width=2), fill='tozeroy', fillcolor='rgba(213, 0, 0, 0.1)'
        ))
    else:
        fig_breadth.add_trace(go.Scatter(
            x=df['DATE'], y=df['Net_Highs'], name="Net Highs", 
            line=dict(color='#9C27B0', width=2), fill='tozeroy', fillcolor='rgba(156, 39, 176, 0.1)'
        ))
        # Add the Zero Line for Net Highs
        fig_breadth.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)

    fig_breadth.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0), hovermode="x unified")
    st.plotly_chart(fig_breadth, use_container_width=True)

    # --- PROFESSIONAL DATA TABLE ---
    st.subheader("Historical Ledger")
    
    display_df = df.sort_values(by='DATE', ascending=False).head(30).copy()
    display_df['DATE'] = display_df['DATE'].dt.strftime('%d %b %Y') 
    
    st.dataframe(
        display_df[['DATE', 'NIFTY_500_CLOSE', '52W_HIGH', '52W_LOW', 'Net_Highs', 'PCT_HIGH']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "DATE": "Trading Date",
            "NIFTY_500_CLOSE": st.column_config.NumberColumn("Index Close", format="%.2f"),
            "52W_HIGH": st.column_config.NumberColumn("Highs"),
            "52W_LOW": st.column_config.NumberColumn("Lows"),
            "Net_Highs": st.column_config.NumberColumn("Net (H-L)"),
            "PCT_HIGH": st.column_config.NumberColumn("% at High", format="%.1f%%")
        }
    )
