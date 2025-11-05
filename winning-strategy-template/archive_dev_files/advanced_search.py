"""
Targeted Grid Search - Focus on high-performing parameter ranges
Based on initial quick test results
"""
from optimize_parameters import ParameterOptimizer

def targeted_search():
    """Run targeted grid search around best performers"""
    optimizer = ParameterOptimizer()
    
    # Based on quick tests, these ranges showed promise:
    # - Very high position sizes (0.95-0.98) performed well
    # - High take profit targets (50-60%) were effective
    # - Wider stop losses (10-12%) gave room for volatility
    # - Longer intervals (2160-3600min) had better returns
    # - More extreme RSI thresholds (25-30 / 80-85) worked better
    
    param_grid = {
        'max_position_size': [0.92, 0.95, 0.98],
        'stop_loss_pct': [10.0, 12.0, 15.0],
        'take_profit_pct': [50.0, 55.0, 60.0, 65.0],
        'rsi_oversold': [22, 25, 28],
        'rsi_overbought': [82, 85, 88],
        'min_time_between_trades': [2160, 2880, 3600, 4320]
    }
    
    print("\n" + "="*70)
    print("TARGETED GRID SEARCH")
    print("="*70)
    print(f"Testing parameter combinations optimized for high returns...")
    print(f"Total combinations: {3 * 3 * 4 * 3 * 3 * 4} = {3*3*4*3*3*4}")
    print("="*70)
    
    optimizer.grid_search(param_grid)
    optimizer.close()


def extreme_search():
    """Test extremely aggressive parameters"""
    optimizer = ParameterOptimizer()
    
    extreme_tests = [
        {
            'max_position_size': 0.99,
            'stop_loss_pct': 15.0,
            'take_profit_pct': 70.0,
            'rsi_oversold': 20,
            'rsi_overbought': 88,
            'min_time_between_trades': 4320
        },
        {
            'max_position_size': 0.98,
            'stop_loss_pct': 12.0,
            'take_profit_pct': 65.0,
            'rsi_oversold': 22,
            'rsi_overbought': 85,
            'min_time_between_trades': 3600
        },
        {
            'max_position_size': 0.95,
            'stop_loss_pct': 10.0,
            'take_profit_pct': 55.0,
            'rsi_oversold': 25,
            'rsi_overbought': 82,
            'min_time_between_trades': 3000
        },
        {
            'max_position_size': 0.97,
            'stop_loss_pct': 14.0,
            'take_profit_pct': 60.0,
            'rsi_oversold': 23,
            'rsi_overbought': 86,
            'min_time_between_trades': 3300
        },
        {
            'max_position_size': 0.96,
            'stop_loss_pct': 11.0,
            'take_profit_pct': 58.0,
            'rsi_oversold': 24,
            'rsi_overbought': 84,
            'min_time_between_trades': 3900
        }
    ]
    
    print("\n" + "="*70)
    print("EXTREME PARAMETER TESTS")
    print("="*70)
    print("Testing ultra-aggressive parameters for maximum returns...")
    print("="*70)
    
    for i, params in enumerate(extreme_tests, 1):
        print(f"\n[{i}/{len(extreme_tests)}] Testing extreme combination...")
        optimizer.test_parameter_set(params, f"Extreme test {i}")
    
    optimizer.show_top_results(10)
    optimizer.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "extreme":
            extreme_search()
        elif sys.argv[1] == "targeted":
            targeted_search()
        else:
            print("Usage: python advanced_search.py [extreme|targeted]")
    else:
        print("Running extreme search first, then you can run targeted grid search...")
        extreme_search()
