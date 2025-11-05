#!/usr/bin/env python3
"""
Fetch REAL historical BTC-USD and ETH-USD data from Coinbase
Period: January 1, 2024 - June 30, 2024
"""

import ccxt
import pandas as pd
from datetime import datetime, timezone
import time
import csv

def fetch_ohlcv_data(symbol, start_date, end_date, timeframe='1h'):
    """
    Fetch real OHLCV data from Binance
    
    Args:
        symbol: Trading pair (e.g., 'BTC/USDT', 'ETH/USDT')
        start_date: Start date string 'YYYY-MM-DD'
        end_date: End date string 'YYYY-MM-DD'
        timeframe: Candle timeframe (default: '1h' for hourly)
    
    Returns:
        List of OHLCV data points
    """
    
    exchange = ccxt.binance({
        'enableRateLimit': True,
    })
    
    # Convert dates to milliseconds
    start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp() * 1000)
    end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp() * 1000)
    
    all_data = []
    current_ts = start_ts
    
    print(f"Fetching {symbol} data from {start_date} to {end_date}...")
    
    while current_ts < end_ts:
        try:
            # Fetch data in chunks (max 300 candles per request for Coinbase)
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=current_ts, limit=300)
            
            if not ohlcv:
                break
            
            all_data.extend(ohlcv)
            
            # Move to next chunk
            current_ts = ohlcv[-1][0] + 1
            
            print(f"  Fetched {len(all_data)} candles so far...")
            
            # Rate limiting
            time.sleep(exchange.rateLimit / 1000)
            
            # Stop if we've reached the end date
            if ohlcv[-1][0] >= end_ts:
                break
                
        except Exception as e:
            print(f"  Error fetching data: {e}")
            time.sleep(2)
            continue
    
    # Filter to exact date range
    filtered_data = [candle for candle in all_data if start_ts <= candle[0] < end_ts]
    
    print(f"  ✓ Fetched {len(filtered_data)} hourly candles")
    
    return filtered_data


def save_to_csv(data, filename):
    """Save OHLCV data to CSV file"""
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        for candle in data:
            timestamp = datetime.fromtimestamp(candle[0] / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([
                timestamp,
                candle[1],  # open
                candle[2],  # high
                candle[3],  # low
                candle[4],  # close
                candle[5],  # volume
            ])
    
    print(f"✓ Saved to {filename}")


def main():
    """Fetch real data for contest period"""
    
    print("="*70)
    print("FETCHING REAL HISTORICAL DATA FOR CONTEST")
    print("Period: January 1, 2024 - June 30, 2024")
    print("Source: Binance Exchange (USDT pairs)")
    print("="*70)
    print()
    
    # Fetch BTC-USDT data (Note: Using USDT as USD proxy for better data availability)
    btc_data = fetch_ohlcv_data('BTC/USDT', '2024-01-01', '2024-07-01', '1h')
    save_to_csv(btc_data, 'BTC-USD_2024_Jan-Jun.csv')
    
    print()
    
    # Fetch ETH-USDT data
    eth_data = fetch_ohlcv_data('ETH/USDT', '2024-01-01', '2024-07-01', '1h')
    save_to_csv(eth_data, 'ETH-USD_2024_Jan-Jun.csv')
    
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
    print(f"  BTC-USD: {len(btc_data)} hourly candles")
    print(f"  ETH-USD: {len(eth_data)} hourly candles")
    print()
    
    # Show first and last prices
    if btc_data:
        btc_start = btc_data[0][4]
        btc_end = btc_data[-1][4]
        btc_change = ((btc_end - btc_start) / btc_start) * 100
        print(f"  BTC: ${btc_start:,.2f} → ${btc_end:,.2f} ({btc_change:+.2f}%)")
    
    if eth_data:
        eth_start = eth_data[0][4]
        eth_end = eth_data[-1][4]
        eth_change = ((eth_end - eth_start) / eth_start) * 100
        print(f"  ETH: ${eth_start:,.2f} → ${eth_end:,.2f} ({eth_change:+.2f}%)")
    
    print()
    print("Ready for backtesting with REAL market data!")


if __name__ == '__main__':
    main()
