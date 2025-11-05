"""
Download real historical cryptocurrency data from Yahoo Finance
No API key or registration required - completely free!
"""

import yfinance as yf
import pandas as pd
from datetime import datetime

def download_crypto_data(ticker, start_date, end_date, output_file):
    """
    Download historical OHLCV data from Yahoo Finance
    
    Args:
        ticker: Yahoo Finance ticker (e.g., 'BTC-USD', 'ETH-USD')
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        output_file: Path to save CSV file
    """
    print(f"\nDownloading {ticker} data from {start_date} to {end_date}...")
    
    try:
        # Download data with 1-hour interval
        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            interval='1h',  # Hourly data
            progress=True
        )
        
        if data.empty:
            print(f"❌ No data returned for {ticker}")
            return False
        
        # Reset index to make datetime a column
        data.reset_index(inplace=True)
        
        # Rename columns to match our format
        data.columns = ['timestamp', 'open', 'high', 'low', 'close', 'adj_close', 'volume']
        
        # Keep only needed columns
        data = data[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        
        # Convert timestamp to ISO format
        data['timestamp'] = data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Save to CSV
        data.to_csv(output_file, index=False)
        
        print(f"✅ Successfully downloaded {len(data)} hourly candles")
        print(f"📁 Saved to: {output_file}")
        print(f"📊 Date range: {data['timestamp'].iloc[0]} to {data['timestamp'].iloc[-1]}")
        print(f"💰 Price range: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error downloading {ticker}: {e}")
        return False

def main():
    """Download BTC-USD and ETH-USD data for January-June 2024"""
    
    print("=" * 70)
    print("Yahoo Finance Data Downloader - NO REGISTRATION REQUIRED")
    print("=" * 70)
    
    # Contest period: January 1 - June 30, 2024
    start_date = "2024-01-01"
    end_date = "2024-07-01"  # End date is exclusive
    
    # Download BTC-USD
    btc_success = download_crypto_data(
        ticker="BTC-USD",
        start_date=start_date,
        end_date=end_date,
        output_file="BTC-USD_2024_Jan-Jun.csv"
    )
    
    # Download ETH-USD
    eth_success = download_crypto_data(
        ticker="ETH-USD",
        start_date=start_date,
        end_date=end_date,
        output_file="ETH-USD_2024_Jan-Jun.csv"
    )
    
    print("\n" + "=" * 70)
    if btc_success and eth_success:
        print("✅ SUCCESS! Both datasets downloaded successfully!")
        print("\nNext steps:")
        print("1. Update backtest_historical.py to load these CSV files")
        print("2. Remove all synthetic data generation code")
        print("3. Run backtest with REAL data")
    else:
        print("⚠️  Some downloads failed. Check errors above.")
    print("=" * 70)

if __name__ == "__main__":
    main()
