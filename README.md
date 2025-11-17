# 📈 Stock Bot - Discord Stock Market Data Bot

> A powerful Discord bot for real-time stock market data, candlestick charts, and gap analysis powered by Polygon.io API

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![py-cord](https://img.shields.io/badge/py--cord-2.2.2-blueviolet.svg)](https://github.com/Pycord-Development/pycord)
[![Polygon API](https://img.shields.io/badge/API-Polygon.io-green.svg)](https://polygon.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🌟 Features

### Stock Data & Analytics

- **📊 OHLC Data**: Get detailed open, high, low, close data with volume and market metrics
- **📉 Candlestick Charts**: Generate professional candlestick charts for any time range
- **📈 Gap Analysis**: Analyze opening gaps and statistics for stocks
- **💹 Market Metrics**: Access market cap, outstanding shares, and intraday extremes
- **📅 Historical Data**: Query stock data for specific dates and time ranges
- **📑 Excel Export**: Receive data in organized Excel format for further analysis

## 🎮 Bot Commands

### `/stock_data <tickers> [date]`
Get comprehensive OHLC data and market metrics for one or more stocks.

**Parameters**:
- `tickers` (required): Space-separated stock tickers (e.g., "AAPL MSFT GOOGL")
- `date` (optional): Date in YYYY-MM-DD format (defaults to current/last trading day)

**Returns**:
- Open, Close, High, Low prices
- Volume
- Time of high/low
- Market capitalization
- Outstanding shares
- Data up to 7 days

**Example**:
```
/stock_data AAPL TSLA 2024-01-15
```

### `/daily_candle_stick_chart <ticker> <date>`
Generate a daily candlestick chart for a specific stock and date.

**Parameters**:
- `ticker`: Stock symbol (e.g., "AAPL")
- `date`: Date in YYYY-MM-DD format

**Returns**: PNG image of candlestick chart

### `/timerange_candle_stick_chart <ticker> <date> <start_time> <end_time>`
Generate a candlestick chart for a specific intraday time range.

**Parameters**:
- `ticker`: Stock symbol
- `date`: Date in YYYY-MM-DD format
- `start_time`: Start time in HH:MM format (e.g., "09:30")
- `end_time`: End time in HH:MM format (e.g., "16:00")

**Returns**: PNG image of candlestick chart for specified time range

### `/chart <ticker> [params]`
Generate general stock charts with various configurations.

### `/gap_stats <ticker> [date]`
Analyze opening gap statistics for a stock.

**Returns**: Gap analysis data including:
- Gap percentage
- Pre-market vs. open comparison
- Gap fill analysis

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Discord Bot Token ([create one here](https://discord.com/developers/applications))
- Polygon.io API Key ([sign up here](https://polygon.io/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/chuk1123/stock_bot.git
   cd stock_bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   Create a `.env` file:
   ```env
   DISCORD_TOKEN=your-discord-bot-token-here
   POLYGON_API_KEY=your-polygon-api-key-here
   ```

4. **Configure bot permissions**

   In the Discord Developer Portal:
   - Enable required intents (if needed)
   - Generate invite link with appropriate permissions
   - Invite bot to your server

5. **Run the bot**
   ```bash
   python main.py
   ```

## 📁 Project Structure

```
stock_bot/
├── main.py                    # Main bot entry point and command handlers
├── stock_data.py              # Polygon API integration for stock data
├── candle_chart.py            # Candlestick chart generation with Plotly
├── gap_data.py                # Gap statistics analysis
├── scrape_data.py             # Web scraping utilities
├── requirements.txt           # Python dependencies
├── Procfile                   # Heroku deployment config
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
└── LICENSE                    # MIT License
```

## 🛠️ Technical Stack

### Core Technologies
- **[py-cord](https://github.com/Pycord-Development/pycord)** v2.2.2 - Modern Discord API wrapper
- **[Polygon.io API](https://polygon.io/)** v1.4.0 - Real-time and historical stock market data
- **[Plotly](https://plotly.com/)** v5.11.0 - Interactive candlestick chart generation
- **[Pandas](https://pandas.pydata.org/)** v1.5.1 - Data manipulation and analysis
- **[Kaleido](https://github.com/plotly/Kaleido)** v0.2.1 - Chart export to PNG/SVG

### Additional Libraries
- **aiohttp** - Async HTTP client
- **requests** - HTTP library
- **numpy** - Numerical computing
- **websockets** - WebSocket support
- **pytz** - Timezone handling
- **tabulate** - Table formatting

## 🌐 Deployment

### Heroku Deployment

This bot is pre-configured for Heroku:

1. **Create a Heroku app**
   ```bash
   heroku create your-stock-bot
   ```

2. **Set environment variables**
   ```bash
   heroku config:set DISCORD_TOKEN=your-token
   heroku config:set POLYGON_API_KEY=your-api-key
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

4. **Scale the worker**
   ```bash
   heroku ps:scale worker=1
   ```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DISCORD_TOKEN` | Your Discord bot token | Yes |
| `POLYGON_API_KEY` | Polygon.io API key for stock data | Yes |

## 📊 Data Sources

### Polygon.io API

The bot uses Polygon.io's REST API for:
- Real-time and historical stock prices
- Intraday OHLCV (Open, High, Low, Close, Volume) data
- Market statistics and fundamentals
- Time-series data for charting

**API Limits**: Free tier includes limited requests. Consider upgrading for production use.

### Chart Generation

Charts are generated using Plotly with:
- Candlestick visualization for price action
- Volume bars
- Customizable time ranges
- High-quality PNG export via Kaleido

## ⚙️ Configuration

### Market Hours

The bot respects market hours and will handle:
- Pre-market data (4:00 AM - 9:30 AM ET)
- Regular hours (9:30 AM - 4:00 PM ET)
- After-hours data (4:00 PM - 8:00 PM ET)

### Data Limitations

- Maximum 7-day historical data per request
- Time ranges must be within market hours
- Some features require paid Polygon.io subscription

## 🔒 Security Notes

**Important**: Never commit your API keys or tokens!

- Use environment variables for sensitive data
- Add `.env` to `.gitignore`
- Rotate keys if accidentally exposed
- Use Heroku Config Vars for deployed bots

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional chart types (line charts, indicators)
- Options data integration
- Fundamental analysis features
- Portfolio tracking
- Alert notifications

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Created by [Kevin Chu](https://github.com/chuk1123)
- Powered by [Polygon.io](https://polygon.io/) stock market data API
- Built with [py-cord](https://github.com/Pycord-Development/pycord)
- Charts generated with [Plotly](https://plotly.com/)

## ⚠️ Disclaimer

This bot provides stock market data for informational purposes only. Not financial advice. Always do your own research and consult with financial professionals before making investment decisions.

---

**Made with 📈 by chuk1123**

*Stock Bot - Your Discord trading companion!*
