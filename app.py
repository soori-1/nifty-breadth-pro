import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(layout="wide", page_title="Right Horizons | Breadth Terminal")

# ─────────────────────────────────────────────────────
#  RIGHT HORIZONS TERMINAL THEME
#  Colors pulled from the brand logo: gold + dark
# ─────────────────────────────────────────────────────
RH_GOLD       = "#B8881A"
RH_GOLD_LIGHT = "#D4A830"
RH_GOLD_DIM   = "#7A5C10"
RH_RED        = "#E74C3C"
RH_GREEN      = "#2ECC71"
RH_BG         = "#0D0D0D"
RH_SURFACE    = "#161616"
RH_TEXT       = "#E8DFC8"
RH_MUTED      = "#7A7060"
RH_BORDER     = "rgba(184,136,26,0.2)"

CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@700;900&family=IBM+Plex+Mono:wght@300;400;500&display=swap');

#MainMenu, footer, header {{ visibility: hidden; }}

.stApp {{
    background: {RH_BG};
    color: {RH_TEXT};
    font-family: 'IBM Plex Mono', monospace;
}}

.block-container {{
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}}

/* ── BRAND HEADER ── */
.rh-header {{
    display: flex;
    align-items: baseline;
    gap: 14px;
    padding: 6px 0 14px;
    border-bottom: 1px solid {RH_BORDER};
    margin-bottom: 18px;
}}
.rh-brand {{
    font-family: 'Fraunces', serif;
    font-size: 22px;
    font-weight: 700;
    color: {RH_GOLD_LIGHT};
    letter-spacing: 0.06em;
}}
.rh-brand-sub {{
    font-size: 10px;
    color: {RH_MUTED};
    letter-spacing: 0.15em;
    text-transform: uppercase;
}}
.rh-live {{
    margin-left: auto;
    font-size: 10px;
    color: {RH_MUTED};
    letter-spacing: 0.1em;
    text-transform: uppercase;
}}
.rh-dot {{
    display: inline-block;
    width: 6px; height: 6px;
    background: {RH_GREEN};
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 2s ease-in-out infinite;
}}
@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.4; }}
}}

/* ── KPI METRIC CARDS ── */
[data-testid="stMetric"] {{
    background: {RH_SURFACE};
    border: 1px solid {RH_BORDER};
    padding: 14px 16px;
    border-radius: 0;
}}
[data-testid="stMetricLabel"] {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 9px !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase;
    color: {RH_MUTED} !important;
}}
[data-testid="stMetricValue"] {{
    font-family: 'Fraunces', serif !important;
    font-weight: 900 !important;
    color: {RH_TEXT} !important;
    font-size: 26px !important;
}}
[data-testid="stMetricDelta"] {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
}}

/* ── SECTION TITLES ── */
h1, h2, h3 {{
    font-family: 'IBM Plex Mono', monospace !important;
    color: {RH_GOLD_DIM} !important;
    font-size: 11px !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase;
    font-weight: 400 !important;
}}

/* ── CONTROLS ── */
.stRadio > label, .stSlider > label {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 10px !important;
    color: {RH_MUTED} !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}}
.stRadio [role="radiogroup"] label {{
    background: transparent;
    border: 1px solid {RH_BORDER};
    padding: 4px 10px !important;
    margin-right: 4px;
    transition: all 0.15s;
}}

/* ── DATAFRAME ── */
.stDataFrame {{
    border: 1px solid {RH_BORDER};
    background: {RH_SURFACE};
}}
.stDataFrame [data-testid="stDataFrameResizable"] {{
    background: {RH_SURFACE};
}}

hr, .stDivider {{
    border-color: {RH_BORDER} !important;
    margin: 12px 0 !important;
}}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
#  BRAND HEADER
# ─────────────────────────────────────────────────────
st.markdown(f"""
<div class="rh-header">
    <span class="rh-brand">RIGHT HORIZONS</span>
    <span class="rh-brand-sub">Market Breadth Terminal · Nifty 500</span>
    <span class="rh-live"><span class="rh-dot"></span>LIVE</span>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────
#  DATA LOAD
# ─────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    if not os.path.exists("Nifty500_Master_Data.csv"):
        return pd.DataFrame()

    df = pd.read_csv("Nifty500_Master_Data.csv")
    df['DATE'] = pd.to_datetime(df['DATE'])
    df = df.sort_values(by='DATE').reset_index(drop=True)
    df['NIFTY_500_CLOSE'] = df['NIFTY_500_CLOSE'].ffill()
    df['Net_Highs'] = df['52W_HIGH'] - df['52W_LOW']
    df['NIFTY_200_SMA'] = df['NIFTY_500_CLOSE'].rolling(window=200, min_periods=1).mean()

    if 'PCT_ABOVE_200SMA' not in df.columns:
        df['PCT_ABOVE_200SMA'] = 0.0
        df['ABOVE_200SMA'] = 0
    return df


df = load_data()

if df.empty:
    st.error("System initializing. Please ensure data pipeline is complete.")
else:
    latest, prev = df.iloc[-1], df.iloc[-2]

    # ── KPI ROW ──
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Nifty 500 Index", f"{latest['NIFTY_500_CLOSE']:,.2f}",
                  f"{latest['NIFTY_500_CLOSE'] - prev['NIFTY_500_CLOSE']:,.2f}")
    with c2:
        st.metric("New 52W Highs", int(latest['52W_HIGH']),
                  int(latest['52W_HIGH'] - prev['52W_HIGH']))
    with c3:
        st.metric("New 52W Lows", int(latest['52W_LOW']),
                  int(latest['52W_LOW'] - prev['52W_LOW']), delta_color="inverse")
    with c4:
        st.metric("Net Breadth (H−L)", int(latest['Net_Highs']),
                  int(latest['Net_Highs'] - prev['Net_Highs']))
    with c5:
        st.metric("Stocks > 200 SMA", f"{latest['PCT_ABOVE_200SMA']:.1f}%",
                  f"{latest['PCT_ABOVE_200SMA'] - prev['PCT_ABOVE_200SMA']:.1f}%")

    st.divider()

    # ── CONTROLS ──
    ctrl1, ctrl2 = st.columns([2, 1])
    with ctrl1:
        chart_choice = st.radio(
            "Lower Indicator",
            ["Net Highs (H-L)", "Stocks > 200 SMA (%)", "52-Week Highs", "52-Week Lows"],
            horizontal=True
        )
    with ctrl2:
        split_ratio = st.slider("Chart Split (Price Area %)", 40, 90, 65, 5)

    top_h = split_ratio / 100.0
    bot_h = 1.0 - top_h

    # ── SYNCHRONIZED CHART ──
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[top_h, bot_h], vertical_spacing=0.04
    )

    # PRICE
    fig.add_trace(go.Scatter(
        x=df['DATE'], y=df['NIFTY_500_CLOSE'], name="Nifty 500",
        line=dict(color=RH_GOLD_LIGHT, width=1.8),
        fill='tozeroy', fillcolor='rgba(184,136,26,0.06)'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df['DATE'], y=df['NIFTY_200_SMA'], name="200 SMA",
        line=dict(color=RH_RED, width=1.2, dash='dot')
    ), row=1, col=1)

    # INDICATOR
    if chart_choice == "Net Highs (H-L)":
        fig.add_trace(go.Scatter(
            x=df['DATE'], y=df['Net_Highs'], name="Net Highs",
            line=dict(color=RH_GOLD, width=1.5),
            fill='tozeroy', fillcolor='rgba(184,136,26,0.07)'
        ), row=2, col=1)
        fig.add_hline(y=0, line_dash="dash", line_color=RH_RED, line_width=1, row=2, col=1)

    elif chart_choice == "Stocks > 200 SMA (%)":
        fig.add_trace(go.Scatter(
            x=df['DATE'], y=df['PCT_ABOVE_200SMA'], name="% > 200 SMA",
            line=dict(color="#8E6FD8", width=1.5),
            fill='tozeroy', fillcolor='rgba(142,111,216,0.07)'
        ), row=2, col=1)
        fig.add_hline(y=50, line_dash="dash", line_color=RH_MUTED, line_width=1, row=2, col=1)

    elif chart_choice == "52-Week Highs":
        fig.add_trace(go.Scatter(
            x=df['DATE'], y=df['52W_HIGH'], name="Highs",
            line=dict(color=RH_GREEN, width=1.5),
            fill='tozeroy', fillcolor='rgba(46,204,113,0.07)'
        ), row=2, col=1)

    elif chart_choice == "52-Week Lows":
        fig.add_trace(go.Scatter(
            x=df['DATE'], y=df['52W_LOW'], name="Lows",
            line=dict(color=RH_RED, width=1.5),
            fill='tozeroy', fillcolor='rgba(231,76,60,0.07)'
        ), row=2, col=1)

    # ── LAYOUT (terminal aesthetic) ──
    fig.update_layout(
        height=700,
        plot_bgcolor=RH_BG,
        paper_bgcolor=RH_BG,
        font=dict(color=RH_TEXT, family="IBM Plex Mono", size=11),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=RH_SURFACE,
            bordercolor=RH_BORDER,
            font=dict(family="IBM Plex Mono", color=RH_TEXT, size=11)
        ),
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        dragmode="pan"
    )

    fig.update_xaxes(
        type="date",
        rangeselector=dict(
            buttons=[
                dict(count=7,  label="1W", step="day",   stepmode="backward"),
                dict(count=1,  label="1M", step="month", stepmode="backward"),
                dict(count=3,  label="3M", step="month", stepmode="backward"),
                dict(count=6,  label="6M", step="month", stepmode="backward"),
                dict(count=1,  label="1Y", step="year",  stepmode="backward"),
                dict(count=2,  label="2Y", step="year",  stepmode="backward"),
                dict(step="all", label="ALL")
            ],
            bgcolor=RH_SURFACE,
            activecolor=RH_GOLD,
            bordercolor=RH_GOLD_DIM,
            font=dict(color=RH_TEXT, family="IBM Plex Mono", size=10),
            y=1.08, x=0
        ),
        row=1, col=1
    )

    fig.update_xaxes(
        showgrid=True, gridwidth=0.5, gridcolor='rgba(58,53,48,0.5)',
        showspikes=True, spikecolor=RH_GOLD_DIM, spikesnap="cursor",
        spikemode="across", spikethickness=1,
        tickfont=dict(color=RH_MUTED, size=9),
        zeroline=False, linecolor=RH_BORDER
    )
    fig.update_yaxes(
        showgrid=True, gridwidth=0.5, gridcolor='rgba(58,53,48,0.5)',
        showspikes=True, spikecolor=RH_GOLD_DIM, spikethickness=1,
        tickfont=dict(color=RH_MUTED, size=9),
        zeroline=False, linecolor=RH_BORDER
    )
    fig.update_yaxes(rangemode="nonnegative", row=1, col=1)

    st.plotly_chart(fig, use_container_width=True,
                    config={'scrollZoom': True, 'displayModeBar': False})

    # ── HISTORICAL LEDGER ──
    st.subheader("Historical Ledger")
    display_df = df.sort_values(by='DATE', ascending=False).head(30).copy()
    display_df['DATE'] = display_df['DATE'].dt.strftime('%d %b %Y')

    st.dataframe(
        display_df[['DATE', 'NIFTY_500_CLOSE', '52W_HIGH', '52W_LOW',
                    'Net_Highs', 'PCT_ABOVE_200SMA']],
        use_container_width=True, hide_index=True,
        column_config={
            "DATE":            "Trading Date",
            "NIFTY_500_CLOSE": st.column_config.NumberColumn("Index Close",  format="%.2f"),
            "52W_HIGH":        st.column_config.NumberColumn("Highs"),
            "52W_LOW":         st.column_config.NumberColumn("Lows"),
            "Net_Highs":       st.column_config.NumberColumn("Net (H−L)"),
            "PCT_ABOVE_200SMA": st.column_config.NumberColumn("% > 200 SMA", format="%.1f%%")
        }
    )
