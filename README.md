# 📈 StockMarket Pro Command Center

StockMarket Pro is a premium, AI-powered stock market terminal built with Streamlit. It provides real-time market insights, trend predictions, live news, and portfolio management in a stunning neon dark-mode interface.

## ✨ Features

- **🔴 Live Tracker**: Real-time stock data fetching with high-end Plotly charts (Candlestick & Line).
- **🔮 Prediction**: 30-day mathematical trendline forecasting using linear regression.
- **📰 Real-Time News**: Dynamic news scraping from Google News for any selected ticker.
- **💼 Portfolio Manager**: Track your holdings, buy prices, and live Profit/Loss calculations.
- **🎨 Premium UI**: Glassmorphism design, neon glow effects, and smooth animations.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Virtual Environment (recommended)

### Installation
1. Clone the repository or download the source code.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the App
Run the following command in your terminal:
```bash
streamlit run app.py
```

## 🛠️ Technologies Used
- [Streamlit](https://streamlit.io/) - UI Framework
- [YFinance](https://github.com/ranaroussi/yfinance) - Market Data API
- [Plotly](https://plotly.com/) - Interactive Charting
- [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/) - Data Processing
