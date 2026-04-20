import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide", page_title="Nifty 500 Breadth")
st.title("📊 Nifty 500 Market Breadth Dashboard")

# 1. Load your master CSV
@st.cache_data # Faster reloading
def load_data():
    df = pd.read_csv("Nifty500_Master_Data.csv")
    df['DATE'] = pd.to_datetime(df['DATE'])
    # Calculate Net New Highs (NNH) Oscillator
    df['Net_Highs'] = df['52W_HIGH'] - df['52W_LOW']
    # Filter out empty index price rows (just in case)
    return df.dropna(subset=['NIFTY_500_CLOSE'])

df = load_data()

# 2. Create Subplots (Vertical stack)
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                    subplot_titles=("Nifty 500 Index Price", "New Highs vs New Lows (Bars)", "Net New Highs (Line)"),
                    row_heights=[0.5, 0.25, 0.25])

# --- Top Chart (Nifty 500 Line Graph) ---
fig.add_trace(go.Scatter(x=df['DATE'], y=df['NIFTY_500_CLOSE'], name="Nifty 500", line=dict(color='white', width=2)), row=1, col=1)

# --- Middle Chart (High/Low Bars) ---
fig.add_trace(go.Bar(x=df['DATE'], y=df['52W_HIGH'], name="New Highs", marker_color='green'), row=2, col=1)
fig.add_trace(go.Bar(x=df['DATE'], y=-df['52W_LOW'], name="New Lows", marker_color='red'), row=2, col=1)

# --- Bottom Chart (NEW: Net Highs Line Graph) ---
fig.add_trace(go.Scatter(x=df['DATE'], y=df['Net_Highs'], name="Net Highs (H-L)", line=dict(color='gray', width=1), fill='tozeroy', fillcolor='rgba(128, 128, 128, 0.2)'), row=3, col=1)

# Style the Layout
fig.update_layout(height=1000, template="plotly_dark", hovermode="x unified", showlegend=False)
fig.update_xaxes(rangeslider_visible=False) # Removes the messy bottom slider
st.plotly_chart(fig, use_container_width=True)

# Latest Data Table
st.subheader("Recent Market Activity")
# Sort descending by date to show latest on top
st.table(df.tail(15).sort_values(by='DATE', ascending=False))
