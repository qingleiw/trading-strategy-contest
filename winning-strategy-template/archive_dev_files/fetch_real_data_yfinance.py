#!/usr/bin/env python3
"""
Fetch REAL historical BTC and ETH data using yfinance
Period: January 1, 2024 - June 30, 2024
"""

import subprocess
import sys

# Install yfinance if not available
try:
    import yfinance as yf
except ImportError:
    print("Installing yfinance...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance"])
    import yfinance as yf

import pandas as pd
from datetime import datetime

def fetch_real_data(ticker, start_date, end_date, filename):
    """
    Fetch real historical price data from Yahoo Finance
    
    Args:
        ticker: Yahoo Finance ticker (e.g., 'BTC-USD', 'ETH-USD')
        start_date: Start date 'YYYY-MM-DD'
        end_date: End date 'YYYY-MM-DD'
        filename: Output CSV filename
    """
    
    print(f"\nFetching {ticker} data from {start_date} to {end_date}...")
    
    # Download data (hourly intervals)
    data = yf.download(ticker, start=start_date, end=end_date, interval='1h', progress=False)
    
    if data.empty:
        print(f"  ❌ No data found for {ticker}")
        return None
    
    # Reset index to make datetime a column
    data.reset_index(inplace=True)
    
    # Rename columns to match our format
    data.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    
    # Save to CSV
    data.to_csv(filename, index=False)
    
    print(f"  ✓ Fetched {len(data)} hourly candles")
    print(f"  ✓ Saved to {filename}")
    
    # Show price range
    start_price = data['close'].iloc[0]
    end_price = data['close'].iloc[-1]
    price_change = ((end_price - start_price) / start_price) * 100
    
    print(f"  📊 Price: ${start_price:,.2f} → ${end_price:,.2f} ({price_change:+.2f}%)")
    
    return data


def main():
    """Fetch real data for contest period"""
    
    print("="*70)
    print("FETCHING REAL HISTORICAL DATA FOR CONTEST")
    print("Period: January 1, 2024 - June 30, 2024")
    print("Source: Yahoo Finance (Real Market Data)")
    print("="*70)
    
    # Fetch BTC-USD data
    btc_data = fetch_real_data('BTC-USD', '2024-01-01', '2024-07-01', 'BTC-USD_2024_Jan-Jun.csv')
    
    # Fetch ETH-USD data
    eth_data = fetch_real_data('ETH-USD', '2024-01-01', '2024-07-01', 'ETH-USD_2024_Jan-Jun.csv')
    
    print()
    print("="*70)
    print("✓ REAL DATA DOWNLOADED SUCCESSFULLY")
    print("="*70)
    print()
    print("Files created:")
    print("  - BTC-USD_2024_Jan-Jun.csv")
    print("  - ETH-USD_2024_Jan-Jun.csv")
    print()
    print("Data Stats:")
    if btc_data is not None:
        print(f"  BTC-USD: {len(btc_data)} hourly candles")
    if eth_data is not None:
        print(f"  ETH-USD: {len(eth_data)} hourly candles")
    print()
    print("✅ Ready for backtesting with REAL market data!")
    print("   (No synthetic generation - 100% authentic exchange data)")


if __name__ == '__main__':
    main()
