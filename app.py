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

    # --- TERMINAL CONTROLS ---
    ctrl_col1, ctrl_col2 = st.columns([1, 1])
    
    with ctrl_col1:
        chart_choice = st.radio(
            "Select Lower Indicator:",
            ["Net Highs (H-L)", "52-Week Highs", "52-Week Lows"],
            horizontal=True
        )
        
    with ctrl_col2:
        split_ratio = st.slider(
            "Adjust Chart Split (Price Area %)", 
            min_value=40, max_value=90, value=70, step=5
        )

    top_height = split_ratio / 100.0
    bottom_height = 1.0 - top_height

    # --- SYNCHRONIZED CHART (FIXED) ---
    # We remove shared_xaxes=True to bypass the Plotly bug
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=False, 
        row_heights=[top_height, bottom_height], 
        vertical_spacing=0.03
    )

    # TOP CHART: Nifty 500 
    fig.add_trace(go.Scatter(
        x=df['DATE'], y=df['NIFTY_500_CLOSE'], 
        name="Nifty 500", 
        line=dict(color='#FFFFFF', width=2), 
        fill='tozeroy', fillcolor='rgba(255, 255, 255, 0.05)' 
    ), row=1, col=1)

    # BOTTOM CHART: Indicator
    if chart_choice == "Net Highs (H-L)":
        fig.add_trace(go.Scatter(
            x=df['DATE'], y=df['Net_Highs'], name="Net Highs", 
            line=dict(color='#E0E0E0', width=1.5), fill='tozeroy', fillcolor='rgba(255, 255, 255, 0.05)'
        ), row=2, col=1)
        fig.add_hline(y=0, line_dash="dash", line_color="#F44336", line_width=1, row=2, col=1)

    elif chart_choice == "52-Week Highs":
        fig.add_trace(go.Scatter(
            x=df['DATE'], y=df['52W_HIGH'], name="Highs", 
            line=dict(color='#00E676', width=1.5), fill='tozeroy', fillcolor='rgba(0, 230, 118, 0.1)'
        ), row=2, col=1)

    elif chart_choice == "52-Week Lows":
        fig.add_trace(go.Scatter(
            x=df['DATE'], y=df['52W_LOW'], name="Lows", 
            line=dict(color='#FF5252', width=1.5), fill='tozeroy', fillcolor='rgba(255, 82, 82, 0.1)'
        ), row=2, col=1)

    # --- UI & INTERACTIVITY ---
    fig.update_layout(
        height=700, 
        plot_bgcolor="#131722", 
        paper_bgcolor="#131722",
        font=dict(color="#d1d4dc"),
        hovermode="x unified",
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        dragmode="pan"
    )

    # NEW FIX: Manually link the X-axes so zooming one zooms both perfectly
    fig.update_xaxes(matches='x')
    
    # Hide the date labels on the top chart to make it look seamless
    fig.update_xaxes(showticklabels=False, row=1, col=1)

    # Apply Range Selectors to the Top Chart
    fig.update_xaxes(
        type="date",
        rangeselector=dict(
            buttons=list([
                dict(count=7, label="1W", step="day", stepmode="backward"),
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(count=2, label="2Y", step="year", stepmode="backward"),
                dict(step="all", label="All")
            ]),
            bgcolor="#2A2E39",
            activecolor="#4C525E",
            font=dict(color="white"),
            y=1.05,
            x=0
        ),
        row=1, col=1
    )

    fig.update_yaxes(rangemode="nonnegative", fixedrange=False, row=1, col=1)
    fig.update_yaxes(fixedrange=False, row=2, col=1)

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#2B2B43', showspikes=True, spikecolor="#787B86", spikesnap="cursor", spikemode="across")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#2B2B43', showspikes=True, spikecolor="#787B86", spikethickness=1)

    st.plotly_chart(
        fig, 
        use_container_width=True, 
        config={'scrollZoom': True, 'displayModeBar': False}
    )

    # --- DATA TABLE ---
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
