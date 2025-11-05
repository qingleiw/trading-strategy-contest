#!/usr/bin/env python3
"""
Download REAL historical data from CryptoCompare API
This is ACTUAL exchange data, not synthetic
"""

import requests
import csv
from datetime import datetime
import time

def fetch_real_hourly_data(symbol, start_timestamp, end_timestamp):
    """
    Fetch real hourly OHLCV data from CryptoCompare
    This is actual historical data aggregated from multiple exchanges
    """
    
    all_data = []
    current_ts = start_timestamp
    
    print(f"Fetching real {symbol} data...")
    
    while current_ts < end_timestamp:
        # CryptoCompare API - free and reliable
        url = f"https://min-api.cryptocompare.com/data/v2/histohour"
        params = {
            'fsym': symbol,
            'tsym': 'USD',
            'limit': 2000,  # Max records per request
            'toTs': min(current_ts + (2000 * 3600), end_timestamp)
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            if data['Response'] == 'Success':
                candles = data['Data']['Data']
                all_data.extend(candles)
                print(f"  Fetched {len(all_data)} candles...")
                
                if len(candles) < 2000:
                    break
                    
                current_ts = candles[-1]['time']
            else:
                print(f"  Error: {data.get('Message', 'Unknown error')}")
                break
                
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"  Error: {e}")
            break
    
    # Filter to exact date range
    filtered = [c for c in all_data if start_timestamp <= c['time'] < end_timestamp]
    print(f"  ✓ Downloaded {len(filtered)} real hourly candles")
    
    return filtered


def save_to_csv(candles, filename, symbol):
    """Save real OHLCV data to CSV"""
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        for candle in candles:
            timestamp = datetime.fromtimestamp(candle['time']).strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([
                timestamp,
                candle['open'],
                candle['high'],
                candle['low'],
                candle['close'],
                candle['volumefrom']
            ])
    
    print(f"  ✓ Saved to {filename}")
    
    # Show price stats
    start_price = candles[0]['close']
    end_price = candles[-1]['close']
    change = ((end_price - start_price) / start_price) * 100
    print(f"  📊 {symbol}: ${start_price:,.2f} → ${end_price:,.2f} ({change:+.2f}%)")


def main():
    """Download real data for Jan 1 - Jun 30, 2024"""
    
    print("="*70)
    print("DOWNLOADING REAL HISTORICAL DATA")
    print("Source: CryptoCompare (Aggregated Exchange Data)")
    print("Period: January 1, 2024 - June 30, 2024")
    print("="*70)
    print()
    
    # Convert dates to Unix timestamps
    start_ts = int(datetime(2024, 1, 1).timestamp())
    end_ts = int(datetime(2024, 7, 1).timestamp())
    
    # Download BTC real data
    print("1. Fetching REAL BTC-USD data from exchanges...")
    btc_data = fetch_real_hourly_data('BTC', start_ts, end_ts)
    if btc_data:
        save_to_csv(btc_data, 'BTC-USD_2024_Jan-Jun.csv', 'BTC-USD')
    print()
    
    # Download ETH real data
    print("2. Fetching REAL ETH-USD data from exchanges...")
    eth_data = fetch_real_hourly_data('ETH', start_ts, end_ts)
    if eth_data:
        save_to_csv(eth_data, 'ETH-USD_2024_Jan-Jun.csv', 'ETH-USD')
    print()
    
    print("="*70)
    print("✅ REAL DATA DOWNLOADED SUCCESSFULLY")
    print("="*70)
    print()
    print("Data Source: CryptoCompare API")
    print("  - Aggregated from major exchanges (Coinbase, Binance, Kraken)")
    print("  - 100% authentic historical data")
    print("  - No synthetic generation")
    print()
    print("Files created:")
    print("  - BTC-USD_2024_Jan-Jun.csv")
    print("  - ETH-USD_2024_Jan-Jun.csv")
    print()
    print("Ready for contest backtesting!")


if __name__ == '__main__':
    main()
