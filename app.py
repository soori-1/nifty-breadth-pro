import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide", page_title="Nifty 500 Breadth")
st.title("📊 Nifty 500 Market Breadth Dashboard")

# Load Data
df = pd.read_csv("Nifty500_Master_Data.csv")
df['DATE'] = pd.to_datetime(df['DATE'])

# Layout
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                    subplot_titles=("Nifty 500 Index Price", "New Highs vs New Lows"),
                    row_heights=[0.7, 0.3])

# Top: Index Close
fig.add_trace(go.Scatter(x=df['DATE'], y=df['NIFTY_500_CLOSE'], name="Nifty 500", line=dict(color='white')), row=1, col=1)

# Bottom: Highs/Lows
fig.add_trace(go.Bar(x=df['DATE'], y=df['52W_HIGH'], name="Highs", marker_color='green'), row=2, col=1)
fig.add_trace(go.Bar(x=df['DATE'], y=-df['52W_LOW'], name="Lows", marker_color='red'), row=2, col=1)

fig.update_layout(height=800, template="plotly_dark", hovermode="x unified", showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# Latest Data Table
st.subheader("Recent Market Activity")
st.table(df.tail(15).sort_values(by='DATE', ascending=False))
