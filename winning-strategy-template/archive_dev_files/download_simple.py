"""
Simple data downloader using only standard library + requests
Downloads real historical crypto data from CoinGecko (no auth required)
"""

import requests
import csv
from datetime import datetime, timezone
import time

def download_coingecko_data(coin_id, vs_currency, days, output_file):
    """
    Download historical data from CoinGecko public API
    
    Args:
        coin_id: 'bitcoin' or 'ethereum'
        vs_currency: 'usd'
        days: number of days (180 for Jan-Jun 2024)
        output_file: path to save CSV
    """
    print(f"\n📥 Downloading {coin_id.upper()} data...")
    
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        'vs_currency': vs_currency,
        'days': days,
        'interval': 'hourly'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        prices = data['prices']
        
        if not prices:
            print(f"❌ No data received for {coin_id}")
            return False
        
        # Write to CSV
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'price', 'unix_timestamp'])
            
            for timestamp_ms, price in prices:
                dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
                timestamp_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                writer.writerow([timestamp_str, price, timestamp_ms])
        
        print(f"✅ Downloaded {len(prices)} hourly data points")
        print(f"📁 Saved to: {output_file}")
        print(f"📊 Price range: ${min(p[1] for p in prices):.2f} - ${max(p[1] for p in prices):.2f}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading {coin_id}: {e}")
        return False

def main():
    print("=" * 70)
    print("CoinGecko Data Downloader - NO REGISTRATION REQUIRED")
    print("=" * 70)
    
    # Download last 180 days (roughly Jan-Jun 2024 to current)
    # Note: CoinGecko free API gives last N days from current date
    
    print("\n⚠️  Note: CoinGecko free API provides data from current date backwards")
    print("For Jan-Jun 2024 historical data, use 'days=max' or manual download\n")
    
    # Download Bitcoin
    btc_success = download_coingecko_data(
        coin_id='bitcoin',
        vs_currency='usd',
        days=180,  # Last 180 days
        output_file='BTC-USD_coingecko.csv'
    )
    
    time.sleep(2)  # Rate limiting
    
    # Download Ethereum
    eth_success = download_coingecko_data(
        coin_id='ethereum',
        vs_currency='usd',
        days=180,
        output_file='ETH-USD_coingecko.csv'
    )
    
    print("\n" + "=" * 70)
    if btc_success and eth_success:
        print("✅ Downloads complete!")
        print("\n📝 MANUAL ALTERNATIVE (Recommended):")
        print("1. Visit: https://www.coingecko.com/en/coins/bitcoin/historical_data")
        print("2. Set date range: Jan 1, 2024 - Jun 30, 2024")
        print("3. Download CSV")
        print("4. Repeat for Ethereum")
    else:
        print("⚠️  Some downloads may have failed")
    print("=" * 70)

if __name__ == "__main__":
    main()
