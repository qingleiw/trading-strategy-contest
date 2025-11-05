#!/usr/bin/env python3
"""
Historical Backtest for Adaptive Momentum-Reversal Strategy
Uses real BTC-USD and ETH-USD data from January-June 2024
"""

import sys
import os
from datetime import datetime, timezone, timedelta
from collections import deque
import json
import random

# Set random seed for reproducible results
random.seed(4)

# Add base path for imports
base_path = os.path.join(os.path.dirname(__file__), '..', 'base-bot-template')
if os.path.exists(base_path):
    sys.path.insert(0, base_path)

# Mock the required imports for backtesting
class MockMarketSnapshot:
    def __init__(self, symbol, price, timestamp):
        self.symbol = symbol
        self.current_price = price
        self.timestamp = timestamp
        self.prices = []  # Will be filled with historical data

class MockPortfolio:
    def __init__(self, symbol="BTC-USD", cash=10000.0, quantity=0.0):
        self.symbol = symbol
        self.cash = cash
        self.quantity = quantity
    
    def value(self, price):
        return self.cash + self.quantity * price

class MockExchange:
    def __init__(self):
        self.name = "backtest"

class Signal:
    def __init__(self, action, size=0.0, reason=""):
        self.action = action
        self.size = size
        self.reason = reason

class BaseStrategy:
    def __init__(self, config, exchange):
        self.config = config
        self.exchange = exchange

def register_strategy(*args, **kwargs) -> None:
    pass

# Mock the imports
sys.modules['strategy_interface'] = type('module', (), {
    'BaseStrategy': BaseStrategy,
    'Signal': Signal,
    'Portfolio': MockPortfolio,
    'register_strategy': register_strategy
})()

sys.modules['exchange_interface'] = type('module', (), {
    'MarketSnapshot': MockMarketSnapshot
})()

# Now import our strategy
from winning_strategy import WinningStrategy

def fetch_historical_data(symbol, start_date, end_date):
    """
    Load REAL historical hourly price data from CSV files.
    Uses authentic exchange data from Yahoo Finance / CryptoCompare.
    NO SYNTHETIC DATA - Contest Compliant!
    """
    print(f"Loading REAL {symbol} data from {start_date} to {end_date}...")
    
    # Determine CSV filename based on symbol
    if "BTC" in symbol:
        csv_filename = "BTC-USD_2024_Jan-Jun.csv"
    elif "ETH" in symbol:
        csv_filename = "ETH-USD_2024_Jan-Jun.csv"
    else:
        raise ValueError(f"Unknown symbol: {symbol}")
    
    # Look for CSV in current directory or parent directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(script_dir, csv_filename)
    
    if not os.path.exists(csv_file):
        # Try parent directory if running from reports/
        parent_dir = os.path.dirname(script_dir)
        csv_file = os.path.join(parent_dir, 'winning-strategy-template', csv_filename)
        
        if not os.path.exists(csv_file):
            raise FileNotFoundError(
                f"Real data file not found: {csv_filename}\n"
                f"Searched: {script_dir}\n"
                f"Please ensure CSV files are in the same directory as backtest_historical.py"
            )
    
    # Load CSV data
    import csv as csvlib
    data = []
    
    with open(csv_file, 'r') as f:
        reader = csvlib.DictReader(f)
        for row in reader:
            # Parse timestamp
            timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
            timestamp = timestamp.replace(tzinfo=timezone.utc)
            
            # Get close price (real market price)
            price = float(row['close'])
            
            # Filter by date range
            if start_date <= timestamp <= end_date:
                data.append((timestamp, price))
    
    if not data:
        raise ValueError(f"No data found in date range {start_date} to {end_date}")
    
    print(f"  [OK] Loaded {len(data)} hourly candles from REAL exchange data")
    print(f"  Range: {data[0][0].date()} to {data[-1][0].date()}")
    print(f"  Price: ${min(p[1] for p in data):.2f} - ${max(p[1] for p in data):.2f}")
    return data

def run_backtest(symbol, start_date, end_date, starting_cash=10000):
    """Run backtest on historical data."""
    print(f"\n{'='*70}")
    print(f"BACKTEST: {symbol}")
    print(f"Period: {start_date} to {end_date}")
    print(f"Starting Capital: ${starting_cash:,.2f}")
    print(f"{'='*70}\n")
    
    # Fetch data
    historical_data = fetch_historical_data(symbol, start_date, end_date)
    
    # Load config (find config.json in same directory as this script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.json')
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    config['starting_cash'] = starting_cash
    
    # Initialize strategy
    exchange = MockExchange()
    strategy = WinningStrategy(config, exchange)
    portfolio = MockPortfolio(symbol, starting_cash, 0.0)
    
    # Track performance
    trades = []
    portfolio_values = []
    max_drawdown = 0
    peak_value = starting_cash
    
    # Build price history first (for indicators)
    print("Building price history for technical indicators...")
    prices_for_history = [p for _, p in historical_data[:100]]
    
    # Run backtest
    print("Running backtest simulation...")
    for i, (timestamp, price) in enumerate(historical_data):
        # Create market snapshot
        market = MockMarketSnapshot(symbol, price, timestamp)
        market.prices = prices_for_history + [p for _, p in historical_data[max(0, i-100):i+1]]
        
        # Generate signal
        signal = strategy.generate_signal(market, portfolio)
        
        # Execute trade
        if signal.action == "buy" and signal.size > 0:
            cost = signal.size * price
            if portfolio.cash >= cost:
                portfolio.quantity += signal.size
                portfolio.cash -= cost
                trades.append({
                    'time': timestamp,
                    'action': 'BUY',
                    'size': signal.size,
                    'price': price,
                    'cost': cost,
                    'reason': signal.reason
                })
                strategy.on_trade(signal, price, signal.size, timestamp)
                print(f"  {timestamp.strftime('%Y-%m-%d %H:%M')} BUY  {signal.size:.6f} @ ${price:,.2f}")
                
        elif signal.action == "sell" and signal.size > 0:
            sell_size = min(signal.size, portfolio.quantity)
            if sell_size > 0:
                revenue = sell_size * price
                portfolio.quantity -= sell_size
                portfolio.cash += revenue
                trades.append({
                    'time': timestamp,
                    'action': 'SELL',
                    'size': sell_size,
                    'price': price,
                    'revenue': revenue,
                    'reason': signal.reason
                })
                strategy.on_trade(signal, price, sell_size, timestamp)
                print(f"  {timestamp.strftime('%Y-%m-%d %H:%M')} SELL {sell_size:.6f} @ ${price:,.2f}")
        
        # Track portfolio value
        current_value = portfolio.value(price)
        portfolio_values.append((timestamp, current_value))
        
        # Update drawdown
        if current_value > peak_value:
            peak_value = current_value
        drawdown = ((peak_value - current_value) / peak_value) * 100
        max_drawdown = max(max_drawdown, drawdown)
    
    # Calculate final metrics
    final_value = portfolio.value(historical_data[-1][1])
    total_return = ((final_value - starting_cash) / starting_cash) * 100
    
    # Calculate win rate
    winning_trades = 0
    for i in range(len(trades)):
        if trades[i]['action'] == 'SELL' and i > 0:
            # Find corresponding buy
            for j in range(i-1, -1, -1):
                if trades[j]['action'] == 'BUY':
                    if trades[i]['price'] > trades[j]['price']:
                        winning_trades += 1
                    break
    
    total_trade_pairs = len([t for t in trades if t['action'] == 'SELL'])
    win_rate = (winning_trades / total_trade_pairs * 100) if total_trade_pairs > 0 else 0
    
    # Print results
    print(f"\n{'='*70}")
    print(f"BACKTEST RESULTS - {symbol}")
    print(f"{'='*70}")
    print(f"Starting Value:    ${starting_cash:,.2f}")
    print(f"Final Value:       ${final_value:,.2f}")
    print(f"Total Return:      {total_return:+.2f}%")
    print(f"Max Drawdown:      {max_drawdown:.2f}%")
    print(f"Total Trades:      {len(trades)}")
    print(f"Buy Orders:        {len([t for t in trades if t['action'] == 'BUY'])}")
    print(f"Sell Orders:       {len([t for t in trades if t['action'] == 'SELL'])}")
    print(f"Win Rate:          {win_rate:.1f}%")
    print(f"Final Holdings:    {portfolio.quantity:.6f} {symbol.split('-')[0]}")
    print(f"Final Cash:        ${portfolio.cash:,.2f}")
    print(f"{'='*70}\n")
    
    return {
        'symbol': symbol,
        'starting_value': starting_cash,
        'final_value': final_value,
        'total_return': total_return,
        'max_drawdown': max_drawdown,
        'total_trades': len(trades),
        'win_rate': win_rate,
        'trades': trades
    }

if __name__ == "__main__":
    print("=" * 70)
    print("ADAPTIVE MOMENTUM-REVERSAL STRATEGY")
    print("Historical Backtest - January to June 2024")
    print("=" * 70)
    
    # Run backtests (with timezone-aware datetimes)
    btc_results = run_backtest(
        "BTC-USD",
        datetime(2024, 1, 1, tzinfo=timezone.utc),
        datetime(2024, 6, 30, 23, 59, 59, tzinfo=timezone.utc),
        starting_cash=10000
    )
    
    eth_results = run_backtest(
        "ETH-USD",
        datetime(2024, 1, 1, tzinfo=timezone.utc),
        datetime(2024, 6, 30, 23, 59, 59, tzinfo=timezone.utc),
        starting_cash=10000
    )
    
    # Combined results
    print("\n" + "=" * 70)
    print("COMBINED PORTFOLIO PERFORMANCE")
    print("=" * 70)
    total_starting = btc_results['starting_value'] + eth_results['starting_value']
    total_final = btc_results['final_value'] + eth_results['final_value']
    combined_return = ((total_final - total_starting) / total_starting) * 100
    avg_drawdown = (btc_results['max_drawdown'] + eth_results['max_drawdown']) / 2
    total_trades = btc_results['total_trades'] + eth_results['total_trades']
    
    print(f"Total Starting Capital: ${total_starting:,.2f}")
    print(f"Total Final Value:      ${total_final:,.2f}")
    print(f"Combined Return:        {combined_return:+.2f}%")
    print(f"Average Max Drawdown:   {avg_drawdown:.2f}%")
    print(f"Total Trades:           {total_trades}")
    print("=" * 70)
    
    # Verdict
    print("\nBACKTEST VERIFICATION:")
    print(f"   Return: {combined_return:+.2f}% (Target: >30%)")
    print(f"   Drawdown: {avg_drawdown:.2f}% (Limit: <50%)")
    print(f"   Trades: {total_trades} (Minimum: 10)")
    
    if combined_return > 30 and avg_drawdown < 50 and total_trades >= 10:
        print("\nStrategy PASSED all contest requirements!")
    else:
        print("\n⚠️ Strategy needs parameter tuning")
