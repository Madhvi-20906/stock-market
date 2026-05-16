import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, timedelta

# Set page configuration
st.set_page_config(page_title="StockMarket Pro", page_icon="📈", layout="wide")

# Initialize Session State for Portfolio
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = [
        {'Ticker': 'AAPL', 'Shares': 15, 'Buy Price': 145.00},
        {'Ticker': 'TSLA', 'Shares': 5, 'Buy Price': 180.50},
        {'Ticker': 'NVDA', 'Shares': 8, 'Buy Price': 420.00},
        {'Ticker': 'MSFT', 'Shares': 12, 'Buy Price': 310.25}
    ]

# Custom CSS for Premium Dark Mode & Glassmorphism
st.markdown("""
<style>
    /* Main Background */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top left, rgba(255, 0, 255, 0.35) 0%, rgba(18, 12, 24, 1) 40%, rgba(10, 6, 14, 1) 100%);
        color: #e2d9eb;
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #120b18;
        border-right: 1px solid rgba(255, 0, 255, 0.1);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(255, 0, 255, 0.3);
    }

    /* Metric Cards (Glassmorphism + Neon Glow) */
    [data-testid="stMetricValue"] {
        color: #ffffff;
        font-size: 2.2rem;
        text-shadow: 0 0 8px rgba(255, 0, 255, 0.5);
    }
    [data-testid="stMetricDelta"] {
        font-size: 1.2rem;
        color: #ffb8ff !important;
    }
    div.css-1r6slb0.e1tzin5v2, div[data-testid="metric-container"] {
        background: rgba(20, 10, 30, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 0, 255, 0.2);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4), inset 0 0 10px rgba(255, 0, 255, 0.05);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    /* Animated Gradient Border for Metric Cards */
    div.css-1r6slb0.e1tzin5v2:hover, div[data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        border: 1px solid rgba(255, 0, 255, 0.5);
        box-shadow: 0 4px 15px rgba(0,0,0,0.4), 0 0 20px rgba(255, 0, 255, 0.4);
    }
    
    /* Button */
    .stButton>button {
        background: linear-gradient(90deg, #ff00ff 0%, #8a2be2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 700;
        box-shadow: 0 0 15px rgba(255, 0, 255, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 0 25px rgba(255, 0, 255, 0.7);
        transform: scale(1.02);
        color: white;
    }
    
    /* Inputs */
    .stTextInput input, .stDateInput input, .stSelectbox > div[data-baseweb="select"] {
        background-color: rgba(20, 10, 30, 0.8) !important;
        border: 1px solid rgba(255, 0, 255, 0.3) !important;
        color: white !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus, .stDateInput input:focus {
        border: 1px solid rgba(255, 0, 255, 0.8) !important;
        box-shadow: 0 0 10px rgba(255, 0, 255, 0.3) !important;
    }
    
    /* --- ANIMATIONS --- */
    
    /* Pulsing Dot */
    .live-indicator {
        display: inline-block;
        width: 14px;
        height: 14px;
        background-color: #ff00ff;
        border-radius: 50%;
        margin-right: 12px;
        box-shadow: 0 0 10px #ff00ff;
        animation: pulse 1.5s infinite;
        vertical-align: middle;
    }
    
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 0, 255, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(255, 0, 255, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 0, 255, 0); }
    }

    /* Ticker Tape */
    .ticker-wrap {
        width: 100%;
        overflow: hidden;
        background-color: rgba(18, 11, 24, 0.6);
        border-bottom: 1px solid rgba(255, 0, 255, 0.2);
        border-top: 1px solid rgba(255, 0, 255, 0.2);
        padding: 8px 0;
        margin-bottom: 20px;
        box-shadow: 0 2px 15px rgba(255, 0, 255, 0.1);
    }
    .ticker {
        display: inline-block;
        white-space: nowrap;
        animation: ticker 30s linear infinite;
    }
    .ticker-item {
        display: inline-block;
        padding: 0 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        color: #e2d9eb;
    }
    .up { color: #00ff88; text-shadow: 0 0 8px rgba(0, 255, 136, 0.5); }
    .down { color: #ff3366; text-shadow: 0 0 8px rgba(255, 51, 102, 0.5); }
    
    @keyframes ticker {
        0% { transform: translate3d(50vw, 0, 0); }
        100% { transform: translate3d(-100%, 0, 0); }
    }

    /* Animated Grid Background */
    .grid-bg {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background-image: 
            linear-gradient(rgba(255, 0, 255, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 0, 255, 0.05) 1px, transparent 1px);
        background-size: 50px 50px;
        z-index: -2;
        animation: moveGrid 15s linear infinite;
        pointer-events: none;
    }
    
    @keyframes moveGrid {
        0% { transform: translateY(0); }
        100% { transform: translateY(50px); }
    }

    /* Style Tabs to ensure visibility in dark theme */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        color: #e2d9eb !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ff00ff !important;
        border-bottom: 2px solid #ff00ff !important;
    }
    div[data-baseweb="tab-highlight"] {
        background-color: #ff00ff !important;
    }
</style>
""", unsafe_allow_html=True)

# Insert Background Grid
st.markdown("<div class='grid-bg'></div>", unsafe_allow_html=True)

# Insert Ticker Tape
st.markdown("""
<div class="ticker-wrap">
    <div class="ticker">
        <div class="ticker-item">AAPL <span class="up">▲ +1.2%</span></div>
        <div class="ticker-item">TSLA <span class="down">▼ -0.5%</span></div>
        <div class="ticker-item">MSFT <span class="up">▲ +0.8%</span></div>
        <div class="ticker-item">NVDA <span class="up">▲ +2.1%</span></div>
        <div class="ticker-item">AMZN <span class="down">▼ -1.1%</span></div>
        <div class="ticker-item">GOOGL <span class="up">▲ +0.4%</span></div>
        <div class="ticker-item">META <span class="up">▲ +1.5%</span></div>
        <div class="ticker-item">NFLX <span class="down">▼ -0.8%</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<h1><span class='live-indicator'></span> StockMarket Pro Command Center</h1>", unsafe_allow_html=True)
st.markdown("Advanced AI-powered terminal for real-time market insights.")

# Sidebar Controls
st.sidebar.header("Navigation & Settings")
ticker = st.sidebar.text_input("Ticker Symbol", value="AAPL").strip().upper()

# Date range selection
col1, col2 = st.sidebar.columns(2)
start_date = col1.date_input("Start", date.today() - timedelta(days=365))
end_date = col2.date_input("End", date.today())

chart_type = st.sidebar.selectbox("Chart Type", ["Candlestick", "Line"])

fetch_button = st.sidebar.button("Fetch Data")

@st.cache_data
def get_data(ticker, start, end):
    try:
        # Use Ticker object for more robust fetching
        t = yf.Ticker(ticker)
        df = t.history(start=start, end=end)
        
        # If specific range fails, try period as fallback
        if df.empty:
            df = t.history(period="1y")
            
        return df
    except Exception as e:
        st.sidebar.error(f"Ticker Error: {e}")
        return pd.DataFrame()

if fetch_button or ticker:
    try:
        with st.spinner("Fetching market data..."):
            df = get_data(ticker, start_date, end_date)
            
            if df is None or df.empty:
                st.error(f"No data found for ticker '{ticker}' and the selected date range.")
                st.info("💡 **Tips:** \n- Check if the ticker symbol is correct (e.g., AAPL, TSLA).\n- Verify your internet connection.\n- Markets are closed on weekends and holidays.")
            else:
                # Top Metrics
                latest = df.iloc[-1]
                prev = df.iloc[-2]
                
                # Handle multi-index columns from yf.download
                if isinstance(df.columns, pd.MultiIndex):
                    close_val = latest['Close'].iloc[0]
                    prev_close = prev['Close'].iloc[0]
                    volume_val = latest['Volume'].iloc[0]
                    high_val = latest['High'].iloc[0]
                else:
                    close_val = latest['Close']
                    prev_close = prev['Close']
                    volume_val = latest['Volume']
                    high_val = latest['High']

                change = close_val - prev_close
                pct_change = (change / prev_close) * 100

                # --- APP TABS ---
                tab1, tab2, tab3, tab4 = st.tabs(["🔴 Live Tracker", "🔮 Prediction", "📰 News", "💼 Portfolio"])
                
                with tab1:
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Current Price", f"${close_val:.2f}", f"{change:.2f} ({pct_change:.2f}%)")
                    m2.metric("24h Volume", f"{int(volume_val):,}")
                    m3.metric("Daily High", f"${high_val:.2f}")
                    m4.metric("Ticker", ticker.upper())

                    # Charting
                    st.markdown("### Market Trends")
                    
                    fig = go.Figure()

                    if chart_type == "Candlestick":
                        if isinstance(df.columns, pd.MultiIndex):
                            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'].iloc[:,0], high=df['High'].iloc[:,0], low=df['Low'].iloc[:,0], close=df['Close'].iloc[:,0], increasing_line_color='#ff00ff', decreasing_line_color='#8a2be2', name='Market Data'))
                        else:
                            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], increasing_line_color='#ff00ff', decreasing_line_color='#8a2be2', name='Market Data'))
                    else:
                        if isinstance(df.columns, pd.MultiIndex):
                            fig.add_trace(go.Scatter(x=df.index, y=df['Close'].iloc[:,0], mode='lines', line=dict(color='#ff00ff', width=3), name='Close Price'))
                        else:
                            fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', line=dict(color='#ff00ff', width=3), name='Close Price'))
                    
                    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=30, b=0), xaxis_rangeslider_visible=False, hovermode='x unified')

                    st.plotly_chart(fig, width='stretch')

                    with st.expander("View Raw Data"):
                        st.dataframe(df.tail(10), width='stretch')
                
                with tab2:
                    st.markdown("### 30-Day Trendline Prediction")
                    st.markdown("Mathematical linear regression based on the selected date range.")
                    if len(df) > 10:
                        if isinstance(df.columns, pd.MultiIndex):
                            closes = df['Close'].iloc[:,0].values
                        else:
                            closes = df['Close'].values
                        
                        x = np.arange(len(closes))
                        z = np.polyfit(x, closes, 1)
                        p = np.poly1d(z)
                        
                        future_x = np.arange(len(closes), len(closes) + 30)
                        future_y = p(future_x)
                        
                        last_date = df.index[-1]
                        if hasattr(last_date, 'date'):
                            last_date = last_date.date()
                        future_dates = [last_date + timedelta(days=int(i)) for i in range(1, 31)]
                        
                        fig_pred = go.Figure()
                        fig_pred.add_trace(go.Scatter(x=df.index, y=closes, mode='lines', line=dict(color='rgba(255, 0, 255, 0.5)', width=2), name='Historical'))
                        fig_pred.add_trace(go.Scatter(x=df.index, y=p(x), mode='lines', line=dict(color='#8a2be2', width=2, dash='dash'), name='Trendline'))
                        fig_pred.add_trace(go.Scatter(x=future_dates, y=future_y, mode='lines', line=dict(color='#00ff88', width=3), name='30-Day Forecast'))
                        
                        fig_pred.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=30, b=0), hovermode='x unified')
                        st.plotly_chart(fig_pred, width='stretch')
                    else:
                        st.warning("Not enough data to calculate a trend. Select a wider date range.")

                with tab3:
                    st.markdown(f"### Latest News for {ticker.upper()}")
                    
                    def get_real_time_news(t):
                        try:
                            url = f'https://news.google.com/rss/search?q={t}+stock&hl=en-US&gl=US&ceid=US:en'
                            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(req) as response:
                                xml_data = response.read()
                            root = ET.fromstring(xml_data)
                            items = []
                            for item in root.findall('.//item')[:10]:
                                title = item.find('title').text
                                link = item.find('link').text
                                pubDate = item.find('pubDate').text
                                if ' - ' in title:
                                    title, publisher = title.rsplit(' - ', 1)
                                else:
                                    publisher = 'Google News'
                                items.append({'title': title, 'link': link, 'publisher': publisher, 'pubDate': pubDate})
                            return items
                        except:
                            return []

                    news = get_real_time_news(ticker)

                    if not news:
                        st.info("No recent news found for this ticker.")
                    else:
                        for article in news:
                            st.markdown(f"**[{article.get('title', 'No Title')}]({article.get('link', '#')})**")
                            try:
                                pub_str = pd.to_datetime(article.get('pubDate')).strftime('%Y-%m-%d %H:%M')
                            except:
                                pub_str = article.get('pubDate', 'Unknown Time')
                            st.markdown(f"<small style='color: #a9a9a9;'>{article.get('publisher', 'News Provider')} | {pub_str} </small>", unsafe_allow_html=True)
                            st.markdown("---")

                with tab4:
                    st.markdown("### Portfolio Manager")
                    col_add1, col_add2, col_add3, col_add4 = st.columns([2, 2, 2, 1])
                    with col_add1:
                        new_ticker = st.text_input("Ticker", key="p_tick", value="AAPL").upper()
                    with col_add2:
                        new_shares = st.number_input("Shares", min_value=1, value=10, key="p_shares")
                    with col_add3:
                        new_price = st.number_input("Avg Buy Price ($)", min_value=0.01, value=150.0, key="p_price")
                    with col_add4:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("Add", width='stretch'):
                            st.session_state.portfolio.append({
                                'Ticker': new_ticker,
                                'Shares': new_shares,
                                'Buy Price': new_price
                            })
                            # Removed st.rerun() so it updates naturally without flashing

                    if st.session_state.portfolio:
                        st.markdown("#### Current Holdings")
                        port_df = pd.DataFrame(st.session_state.portfolio)
                        
                        # Fetch live prices for portfolio
                        live_prices = {}
                        for t in port_df['Ticker'].unique():
                            try:
                                t_data = yf.Ticker(t).history(period="1d")
                                live_prices[t] = t_data['Close'].iloc[-1] if not t_data.empty else 0
                            except:
                                live_prices[t] = 0
                                
                        port_df['Live Price'] = port_df['Ticker'].map(live_prices)
                        port_df['Total Value'] = port_df['Shares'] * port_df['Live Price']
                        port_df['Total Cost'] = port_df['Shares'] * port_df['Buy Price']
                        port_df['P/L ($)'] = port_df['Total Value'] - port_df['Total Cost']
                        port_df['P/L (%)'] = (port_df['P/L ($)'] / port_df['Total Cost']) * 100
                        
                        st.dataframe(port_df.style.format({
                            'Buy Price': '${:.2f}',
                            'Live Price': '${:.2f}',
                            'Total Value': '${:.2f}',
                            'Total Cost': '${:.2f}',
                            'P/L ($)': '${:.2f}',
                            'P/L (%)': '{:.2f}%'
                        }), width='stretch')
                        
                        total_val = port_df['Total Value'].sum()
                        total_pl = port_df['P/L ($)'].sum()
                        st.metric("Total Portfolio Value", f"${total_val:,.2f}", f"${total_pl:,.2f} Total P/L")
                        
                        if st.button("Clear Portfolio"):
                            st.session_state.portfolio = []
                            st.rerun()
                    else:
                        st.info("Your portfolio is empty. Add some stocks above!")
                    
    except Exception as e:
        st.error(f"Error fetching data: {e}")
