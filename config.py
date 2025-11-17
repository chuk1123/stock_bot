"""
Stock Bot Configuration
Centralized configuration for API keys and bot settings
"""
import os

# Discord Bot Configuration
DISCORD_TOKEN = os.getenv("TOKEN")

# Polygon API Configuration
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

# Discord Guild IDs (servers where bot is active)
GUILD_IDS = [
    985331377698385950,
    981996746475462656,
    959419758560804894,
    905562370326274068,
    959872581270388766
]

# Timezone Configuration
TIMEZONE = 'EST'

# Data Limits
MAX_DAYS_HISTORICAL = 7  # Maximum days in the past for stock data

# File Outputs
EXCEL_OUTPUT_FILE = 'stock_data.xlsx'
CHART_OUTPUT_FILE = 'timeframe_chart.jpeg'
DAILY_CHART_OUTPUT_FILE = 'daily_chart.jpeg'
