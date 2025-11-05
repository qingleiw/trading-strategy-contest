"""
Ultimate parameter search - Test extreme hold configurations
Goal: Achieve 30%+ combined return by holding winners longer
"""
import subprocess
import re
from optimization_db import OptimizationDB
import itertools

db = OptimizationDB()

def test_parameter_set(params):
    """Test a single parameter configuration"""
    config = {
        "max_position_size": params['position'],
        "stop_loss_pct": params['stop_loss'],
        "take_profit_pct": params['take_profit'],
        "rsi_oversold": params['rsi_oversold'],
        "rsi_overbought": params['rsi_overbought'],
        "min_trade_interval_minutes": params['interval']
    }
    
    # Write config
    import json
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # Run backtest
    result = subprocess.run(
        ['python', 'backtest_historical.py'],
        capture_output=True,
        text=True
    )
    
    output = result.stdout + result.stderr
    
    # Parse results
    btc_return = eth_return = combined_return = 0.0
    btc_drawdown = eth_drawdown = max_drawdown = 0.0
    btc_trades = eth_trades = total_trades = 0
    btc_winrate = eth_winrate = 0.0
    
    # Extract metrics
    if match := re.search(r'BTC Return: ([-\d.]+)%', output):
        btc_return = float(match.group(1))
    if match := re.search(r'ETH Return: ([-\d.]+)%', output):
        eth_return = float(match.group(1))
    if match := re.search(r'Combined Return: ([-\d.]+)%', output):
        combined_return = float(match.group(1))
    if match := re.search(r'BTC Max Drawdown: ([-\d.]+)%', output):
        btc_drawdown = float(match.group(1))
    if match := re.search(r'ETH Max Drawdown: ([-\d.]+)%', output):
        eth_drawdown = float(match.group(1))
    if match := re.search(r'Max Drawdown: ([-\d.]+)%', output):
        max_drawdown = float(match.group(1))
    if match := re.search(r'BTC Trades: (\d+)', output):
        btc_trades = int(match.group(1))
    if match := re.search(r'ETH Trades: (\d+)', output):
        eth_trades = int(match.group(1))
    if match := re.search(r'Total Trades: (\d+)', output):
        total_trades = int(match.group(1))
    if match := re.search(r'BTC Win Rate: ([\d.]+)%', output):
        btc_winrate = float(match.group(1))
    if match := re.search(r'ETH Win Rate: ([\d.]+)%', output):
        eth_winrate = float(match.group(1))
    
    # Save to database
    db.save_result(
        config=config,
        btc_results={
            'return': btc_return,
            'drawdown': btc_drawdown,
            'trades': btc_trades,
            'win_rate': btc_winrate,
            'final_value': 0  # Not tracked in this script
        },
        eth_results={
            'return': eth_return,
            'drawdown': eth_drawdown,
            'trades': eth_trades,
            'win_rate': eth_winrate,
            'final_value': 0
        },
        combined_results={
            'return': combined_return,
            'avg_drawdown': max_drawdown,
            'total_trades': total_trades
        },
        notes=f"Ultimate search: {params}"
    )
    
    print(f"[Test {params}]")
    print(f"  Combined: {combined_return:.2f}% (BTC: {btc_return:.2f}%, ETH: {eth_return:.2f}%)")
    print(f"  Drawdown: {max_drawdown:.2f}%  Trades: {total_trades}")
    print()
    
    return combined_return >= 30.0

def ultimate_grid_search():
    """
    Test extreme configurations focused on holding winners longer
    Strategy: Remove partial profit taking, only exit at extreme conditions
    """
    print("=== ULTIMATE PARAMETER SEARCH ===")
    print("Testing extreme hold strategies for 30%+ combined return\n")
    
    # Extreme parameters - very high take_profit means we almost never exit on profit
    param_grid = {
        'position': [0.95, 0.98, 1.0],  # Very high allocation
        'stop_loss': [8, 10, 12, 15],  # Tight to loose stops
        'take_profit': [90, 100, 120, 150],  # Very high targets = hold longer
        'rsi_oversold': [20, 24, 28],
        'rsi_overbought': [75, 80, 85],  # Lower thresholds = exit sooner on weakness
        'interval': [2000, 2500, 3000, 3500]  # Various time throttles
    }
    
    # Generate all combinations
    keys = list(param_grid.keys())
    values = [param_grid[k] for k in keys]
    combinations = list(itertools.product(*values))
    
    total = len(combinations)
    print(f"Testing {total} parameter combinations...\n")
    
    success_count = 0
    for i, combo in enumerate(combinations, 1):
        params = dict(zip(keys, combo))
        print(f"Progress: {i}/{total} ({i*100//total}%)")
        
        if test_parameter_set(params):
            success_count += 1
            print(f"✓ SUCCESS! Found configuration with 30%+ combined return!")
            print(f"  Config: {params}\n")
    
    print(f"\n=== SEARCH COMPLETE ===")
    print(f"Tested: {total} combinations")
    print(f"Success: {success_count} configurations reached 30%+")
    
    # Show top results
    print("\n=== TOP 10 RESULTS ===")
    top_results = db.get_top_results(n=10, sort_by='combined_return')
    
    for i, result in enumerate(top_results, 1):
        print(f"\n{i}. Combined: {result['combined_return']:.2f}% (Score: {result['score']:.2f})")
        print(f"   BTC: {result['btc_return']:.2f}%  ETH: {result['eth_return']:.2f}%")
        print(f"   Drawdown: {result['max_drawdown']:.2f}%  Trades: {result['total_trades']}")
        print(f"   Config: pos={result['position']}, stop={result['stop_loss']}%, " 
              f"target={result['take_profit']}%, RSI={result['rsi_oversold']}/{result['rsi_overbought']}, "
              f"interval={result['interval']}min")

if __name__ == '__main__':
    ultimate_grid_search()
