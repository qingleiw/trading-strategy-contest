"""Quick grid search for 50%+ returns"""
import subprocess
import json

best_return = 0
best_config = None

# Test grid
test_configs = [
    # (take_profit, interval, rsi_low, rsi_high)
    (12, 120, 37, 63),
    (13, 150, 36, 64),
    (14, 180, 35, 65),
    (15, 180, 35, 65),  # Current best
    (16, 180, 34, 66),
    (16, 150, 35, 65),
    (17, 180, 33, 67),
    (18, 200, 34, 66),
    (20, 240, 32, 68),
]

for i, (tp, interval, rsi_low, rsi_high) in enumerate(test_configs, 1):
    config = {
        "max_position_size": 1.0,
        "stop_loss_pct": 12,
        "take_profit_pct": tp,
        "rsi_oversold": rsi_low,
        "rsi_overbought": rsi_high,
        "min_trade_interval_minutes": interval
    }
    
    # Write config
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # Run backtest
    result = subprocess.run(
        ['python', 'backtest_historical.py'],
        capture_output=True,
        text=True
    )
    
    output = result.stdout + result.stderr
    
    # Parse combined return
    import re
    match = re.search(r'Combined Return:\s+([-+]?\d+\.\d+)%', output)
    if match:
        ret = float(match.group(1))
        print(f"{i}/9: TP={tp}%, Int={interval}min, RSI={rsi_low}/{rsi_high} -> {ret:.2f}%")
        
        if ret > best_return:
            best_return = ret
            best_config = config
    else:
        print(f"{i}/9: FAILED")

print(f"\n=== BEST RESULT ===")
print(f"Return: {best_return:.2f}%")
print(f"Config: {best_config}")

# Save best
if best_config:
    with open('config_best.json', 'w') as f:
        json.dump(best_config, f, indent=2)
    print("Saved to config_best.json")
