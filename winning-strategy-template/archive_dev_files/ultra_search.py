"""
Ultra-aggressive search for 30%+ returns
Focus on parameters that maximize upside capture
"""
from optimize_parameters import ParameterOptimizer

def ultra_aggressive_search():
    """Test ultra-aggressive parameters aiming for 30%+ returns"""
    optimizer = ParameterOptimizer()
    
    # Based on analysis: need to capture more upside
    # Key insights:
    # - Very high position size (0.98-0.99)
    # - Very high take profit targets (60-80%)
    # - Moderate stop loss for volatility
    # - Very long holding periods
    # - Extreme RSI thresholds
    
    test_sets = [
        # Baseline extreme
        {
            'max_position_size': 0.99,
            'stop_loss_pct': 15.0,
            'take_profit_pct': 80.0,
            'rsi_oversold': 20,
            'rsi_overbought': 90,
            'min_time_between_trades': 4320
        },
        # Slightly less extreme
        {
            'max_position_size': 0.98,
            'stop_loss_pct': 12.0,
            'take_profit_pct': 75.0,
            'rsi_oversold': 22,
            'rsi_overbought': 88,
            'min_time_between_trades': 3900
        },
        # Balanced extreme
        {
            'max_position_size': 0.97,
            'stop_loss_pct': 14.0,
            'take_profit_pct': 70.0,
            'rsi_oversold': 23,
            'rsi_overbought': 87,
            'min_time_between_trades': 4000
        },
        # High frequency extreme
        {
            'max_position_size': 0.99,
            'stop_loss_pct': 13.0,
            'take_profit_pct': 65.0,
            'rsi_oversold': 25,
            'rsi_overbought': 85,
            'min_time_between_trades': 2880
        },
        # Conservative stop, aggressive target
        {
            'max_position_size': 0.98,
            'stop_loss_pct': 10.0,
            'take_profit_pct': 75.0,
            'rsi_oversold': 24,
            'rsi_overbought': 86,
            'min_time_between_trades': 3600
        },
        # Maximum allocation
        {
            'max_position_size': 1.0,
            'stop_loss_pct': 15.0,
            'take_profit_pct': 80.0,
            'rsi_oversold': 20,
            'rsi_overbought': 90,
            'min_time_between_trades': 4800
        },
        # Extreme patience
        {
            'max_position_size': 0.99,
            'stop_loss_pct': 18.0,
            'take_profit_pct': 90.0,
            'rsi_oversold': 18,
            'rsi_overbought': 92,
            'min_time_between_trades': 5400
        },
        # Balanced but aggressive
        {
            'max_position_size': 0.96,
            'stop_loss_pct': 12.0,
            'take_profit_pct': 68.0,
            'rsi_oversold': 23,
            'rsi_overbought': 87,
            'min_time_between_trades': 3300
        },
        # High risk, high reward
        {
            'max_position_size': 0.99,
            'stop_loss_pct': 20.0,
            'take_profit_pct': 85.0,
            'rsi_oversold': 19,
            'rsi_overbought': 91,
            'min_time_between_trades': 4500
        },
        # Frequent but large positions
        {
            'max_position_size': 0.98,
            'stop_loss_pct': 11.0,
            'take_profit_pct': 72.0,
            'rsi_oversold': 24,
            'rsi_overbought': 88,
            'min_time_between_trades': 3000
        }
    ]
    
    print("\n" + "="*70)
    print("ULTRA-AGGRESSIVE SEARCH FOR 30%+ RETURNS")
    print("="*70)
    print("Testing 10 extreme parameter combinations...")
    print("="*70)
    
    best_return = 0
    best_config = None
    
    for i, params in enumerate(test_sets, 1):
        print(f"\n[{i}/{len(test_sets)}] Testing ultra-aggressive combination...")
        success = optimizer.test_parameter_set(params, f"Ultra-aggressive test {i}")
        
        if success:
            # Check if we reached 30%
            from optimization_db import OptimizationDB
            db = OptimizationDB()
            top = db.get_top_results(1)
            if top and top[0]['combined_return'] >= 30.0:
                print(f"\n{'='*70}")
                print(f"🎉 SUCCESS! Found configuration with 30%+ return!")
                print(f"{'='*70}")
                print(f"Return: {top[0]['combined_return']:.2f}%")
                print(f"Drawdown: {top[0]['avg_drawdown']:.2f}%")
                print(f"Trades: {top[0]['total_trades']}")
                print(f"\nParameters:")
                for key, value in params.items():
                    print(f"  {key}: {value}")
                db.close()
                optimizer.close()
                return True
            
            if top and top[0]['combined_return'] > best_return:
                best_return = top[0]['combined_return']
                best_config = params
            db.close()
    
    print(f"\n{'='*70}")
    print(f"SEARCH COMPLETE - Best return: {best_return:.2f}%")
    print(f"{'='*70}")
    if best_config:
        print("Best configuration:")
        for key, value in best_config.items():
            print(f"  {key}: {value}")
    
    optimizer.show_top_results(5)
    optimizer.close()
    return False


if __name__ == "__main__":
    success = ultra_aggressive_search()
    if not success:
        print("\n⚠️  Did not reach 30% target. Try adjusting strategy logic or using real market data.")
