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
st.markdown("<p style='color: #5f6368;'>Internal Quantitative Tool | Synchronized Price & Breadth Action</p>", unsafe_allow_html=True)

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

    # --- SYNCHRONIZED CHART (LIGHT MODE COLORS) ---
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=False, 
        row_heights=[top_height, bottom_height], 
        vertical_spacing=0.03
    )

    # TOP CHART: Nifty 500 (Now Corporate Blue)
    fig.add_trace(go.Scatter(
        x=df['DATE'], y=df['NIFTY_500_CLOSE'], 
        name="Nifty 500", 
        line=dict(color='#1A73E8', width=2), 
        fill='tozeroy', fillcolor='rgba(26, 115, 232, 0.05)' 
    ), row=1, col=1)

    # BOTTOM CHART: Indicator
    if chart_choice == "Net Highs (H-L)":
        fig.add_trace(go.Scatter(
            x=df['DATE'], y=df['Net_Highs'], name="Net Highs", 
            line=dict(color='#607D8B', width=1.5), fill='tozeroy', fillcolor='rgba(96, 125, 139, 0.05)'
        ), row=2, col=1)
        fig.add_hline(y=0, line_dash="dash", line_color="#D32F2F", line_width=1.5, row=2, col=1)

    elif chart_choice == "52-Week Highs":
        fig.add_trace(go.Scatter(
            x=df['DATE'], y=df['52W_HIGH'], name="Highs", 
            line=dict(color='#0F9D58', width=1.5), fill='tozeroy', fillcolor='rgba(15, 157, 88, 0.1)'
        ), row=2, col=1)

    elif chart_choice == "52-Week Lows":
        fig.add_trace(go.Scatter(
            x=df['DATE'], y=df['52W_LOW'], name="Lows", 
            line=dict(color='#DB4437', width=1.5), fill='tozeroy', fillcolor='rgba(219, 68, 55, 0.1)'
        ), row=2, col=1)

    # --- UI & INTERACTIVITY (PURE WHITE BACKGROUND) ---
    fig.update_layout(
        height=700, 
        plot_bgcolor="#FFFFFF", 
        paper_bgcolor="#FFFFFF",
        font=dict(color="#202124"), # Dark Gray text for readability
        hovermode="x unified",
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        dragmode="pan"
    )

    fig.update_xaxes(matches='x')
    fig.update_xaxes(showticklabels=False, row=1, col=1)

    # Range Selectors styled for Light Mode
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
            bgcolor="#F1F3F4",
            activecolor="#E8EAED",
            font=dict(color="#202124"),
            y=1.05,
            x=0
        ),
        row=1, col=1
    )

    fig.update_yaxes(rangemode="nonnegative", fixedrange=False, row=1, col=1)
    fig.update_yaxes(fixedrange=False, row=2, col=1)

    # Soft gray gridlines
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#F1F3F4', showspikes=True, spikecolor="#9AA0A6", spikesnap="cursor", spikemode="across")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#F1F3F4', showspikes=True, spikecolor="#9AA0A6", spikethickness=1)

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
