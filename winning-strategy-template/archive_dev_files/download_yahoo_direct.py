"""
Direct download from Yahoo Finance API (no yfinance library needed)
Uses Yahoo's direct CSV download endpoint
"""

import requests
from datetime import datetime
import time

def download_yahoo_csv(ticker, start_date, end_date, output_file):
    """
    Download CSV directly from Yahoo Finance download endpoint
    
    Args:
        ticker: e.g., 'BTC-USD', 'ETH-USD'
        start_date: datetime object
        end_date: datetime object
        output_file: path to save CSV
    """
    print(f"\n📥 Downloading {ticker}...")
    
    # Convert dates to Unix timestamps
    period1 = int(start_date.timestamp())
    period2 = int(end_date.timestamp())
    
    # Yahoo Finance direct download URL
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}"
    params = {
        'period1': period1,
        'period2': period2,
        'interval': '1h',  # 1 hour intervals
        'events': 'history',
        'includeAdjustedClose': 'true'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Save the CSV content
        with open(output_file, 'wb') as f:
            f.write(response.content)
        
        # Count lines (data points)
        lines = response.content.decode('utf-8').strip().split('\n')
        data_points = len(lines) - 1  # Subtract header
        
        print(f"✅ Downloaded {data_points} hourly candles")
        print(f"📁 Saved to: {output_file}")
        
        # Show first few lines
        print(f"📊 Preview:")
        for line in lines[:3]:
            print(f"   {line}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        print(f"\n💡 Alternative: Manual download")
        print(f"   1. Visit: https://finance.yahoo.com/quote/{ticker}/history")
        print(f"   2. Set date range to Jan 1, 2024 - Jun 30, 2024")
        print(f"   3. Look for 'Download' link (top right area)")
        print(f"   4. Save as {output_file}")
        return False

def main():
    print("=" * 70)
    print("Yahoo Finance Direct CSV Downloader")
    print("=" * 70)
    
    # Contest period: Jan 1 - Jun 30, 2024
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 6, 30, 23, 59, 59)
    
    print(f"\n📅 Downloading data from {start_date.date()} to {end_date.date()}")
    
    # Download BTC-USD
    btc_success = download_yahoo_csv(
        ticker='BTC-USD',
        start_date=start_date,
        end_date=end_date,
        output_file='BTC-USD_2024_Jan-Jun.csv'
    )
    
    time.sleep(2)  # Be polite to Yahoo's servers
    
    # Download ETH-USD
    eth_success = download_yahoo_csv(
        ticker='ETH-USD',
        start_date=start_date,
        end_date=end_date,
        output_file='ETH-USD_2024_Jan-Jun.csv'
    )
    
    print("\n" + "=" * 70)
    if btc_success and eth_success:
        print("✅ SUCCESS! Both datasets downloaded!")
        print("\nNext steps:")
        print("1. Update backtest_historical.py to load these CSV files")
        print("2. Remove synthetic data generation code")
        print("3. Run backtest with REAL data")
    else:
        print("⚠️  Automated download may have failed")
        print("\n📝 MANUAL DOWNLOAD INSTRUCTIONS:")
        print("1. Open browser (Chrome/Firefox)")
        print("2. Go to: https://finance.yahoo.com/quote/BTC-USD/history")
        print("3. Click 'Time Period' dropdown near top")
        print("4. Select 'Custom' at bottom of dropdown")
        print("5. Enter: Start Date: 01/01/2024, End Date: 06/30/2024")
        print("6. Click 'Apply'")
        print("7. Look for 'Download' link (usually top right)")
        print("8. Click 'Download' - saves as BTC-USD.csv")
        print("9. Rename to: BTC-USD_2024_Jan-Jun.csv")
        print("10. Repeat for ETH-USD")
    print("=" * 70)

if __name__ == "__main__":
    main()
