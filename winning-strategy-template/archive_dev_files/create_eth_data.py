"""
Generate ETH-USD data using cryptocompare API (fallback method)
This will create the missing ETH-USD CSV file
"""

import requests
import csv
from datetime import datetime, timezone
import time

def fetch_cryptocompare_hourly(symbol, limit=2000, to_timestamp=None):
    """Fetch hourly data from CryptoCompare public API"""
    url = "https://min-api.cryptocompare.com/data/v2/histohour"
    
    if to_timestamp is None:
        to_timestamp = int(datetime(2024, 7, 1).timestamp())
    
    params = {
        'fsym': symbol,
        'tsym': 'USD',
        'limit': limit,
        'toTs': to_timestamp
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        
        if data['Response'] == 'Success':
            return data['Data']['Data']
        else:
            print(f"API Response: {data.get('Message', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def create_eth_csv():
    """Create ETH-USD CSV matching the BTC format"""
    
    print("📥 Fetching ETH-USD data from CryptoCompare...")
    
    all_data = []
    
    # Fetch data in chunks (2000 hours at a time)
    # Jan 1 to Jun 30, 2024 = ~4320 hours, need 3 chunks
    end_ts = int(datetime(2024, 7, 1).timestamp())
    
    for chunk in range(3):
        print(f"   Fetching chunk {chunk + 1}/3...")
        
        # For each chunk, fetch backwards from the previous chunk's earliest time
        to_ts = end_ts if chunk == 0 else int(datetime.strptime(all_data[0]['timestamp'], '%Y-%m-%d %H:%M:%S').timestamp())
        
        data = fetch_cryptocompare_hourly('ETH', limit=2000, to_timestamp=to_ts)
        
        if data:
            # Convert and prepend to get chronological order
            for candle in reversed(data):
                dt = datetime.fromtimestamp(candle['time'], tz=timezone.utc)
                timestamp_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                all_data.insert(0, {
                    'timestamp': timestamp_str,
                    'open': candle['open'],
                    'high': candle['high'],
                    'low': candle['low'],
                    'close': candle['close'],
                    'volume': candle['volumeto'],
                    'time_unix': candle['time']
                })
            time.sleep(1.5)  # Rate limiting
        else:
            print("❌ Failed to fetch data")
            return False
    
    # Filter to Jan 1 - Jun 30, 2024 and remove duplicates
    start_str = '2024-01-01 00:00:00'
    end_str = '2024-07-01 00:00:00'
    
    # Remove duplicates by timestamp
    seen = set()
    unique_data = []
    for d in all_data:
        if d['timestamp'] not in seen and start_str <= d['timestamp'] < end_str:
            seen.add(d['timestamp'])
            unique_data.append(d)
    
    unique_data.sort(key=lambda x: x['timestamp'])
    
    # Write to CSV
    output_file = 'ETH-USD_2024_Jan-Jun.csv'
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        for candle in unique_data:
            writer.writerow([
                candle['timestamp'],
                candle['open'],
                candle['high'],
                candle['low'],
                candle['close'],
                candle['volume']
            ])
    
    print(f"✅ Created {output_file}")
    print(f"📊 {len(unique_data)} hourly candles")
    if unique_data:
        print(f"📅 Date range: {unique_data[0]['timestamp']} to {unique_data[-1]['timestamp']}")
    
    return True

if __name__ == "__main__":
    print("=" * 70)
    print("ETH-USD Data Generator")
    print("=" * 70)
    
    success = create_eth_csv()
    
    if success:
        print("\n✅ SUCCESS! ETH-USD data created")
        print("\nYou now have both:")
        print("  • BTC-USD_2024_Jan-Jun.csv")
        print("  • ETH-USD_2024_Jan-Jun.csv")
        print("\nNext: Update backtest_historical.py to use real data")
    else:
        print("\n❌ Failed. Try manual download from Yahoo Finance")
    
    print("=" * 70)
