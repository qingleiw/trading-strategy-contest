"""
Optimization Results Analyzer
Visualize and analyze parameter optimization results
"""
from optimization_db import OptimizationDB
import json

def analyze_results():
    """Comprehensive analysis of optimization results"""
    db = OptimizationDB()
    
    print("\n" + "="*70)
    print("PARAMETER OPTIMIZATION ANALYSIS")
    print("="*70)
    
    # Overall summary
    db.print_summary()
    
    # Top results by score
    print("\n" + "="*70)
    print("TOP 10 RESULTS BY SCORE")
    print("="*70)
    top_results = db.get_top_results(10)
    
    for i, result in enumerate(top_results, 1):
        print(f"\n#{i} - Score: {result['score']:.2f} {'[MEETS REQUIREMENTS]' if result['meets_requirements'] else ''}")
        print("-"*70)
        print(f"Performance:")
        print(f"  Combined Return:  {result['combined_return']:>7.2f}%")
        print(f"  Avg Drawdown:     {result['avg_drawdown']:>7.2f}%")
        print(f"  Total Trades:     {result['total_trades']:>7}")
        print(f"  BTC: {result['btc_return']:>6.2f}% return, {result['btc_drawdown']:>5.2f}% DD, {result['btc_trades']:>3} trades, {result['btc_win_rate']:>5.1f}% WR")
        print(f"  ETH: {result['eth_return']:>6.2f}% return, {result['eth_drawdown']:>5.2f}% DD, {result['eth_trades']:>3} trades, {result['eth_win_rate']:>5.1f}% WR")
        print(f"\nParameters:")
        print(f"  Position Size:    {result['max_position_size']}")
        print(f"  Stop Loss:        {result['stop_loss_pct']}%")
        print(f"  Take Profit:      {result['take_profit_pct']}%")
        print(f"  RSI Thresholds:   {result['rsi_oversold']}/{result['rsi_overbought']}")
        print(f"  Trade Interval:   {result['min_time_between_trades']} minutes ({result['min_time_between_trades']/60:.1f} hours)")
        print(f"  Max DD Limit:     {result['max_drawdown_limit']}%")
        if result['notes']:
            print(f"  Notes: {result['notes']}")
    
    # Best by return
    print("\n" + "="*70)
    print("TOP 5 BY RETURN (regardless of score)")
    print("="*70)
    best_return = db.get_best_by_return(5)
    
    for i, result in enumerate(best_return, 1):
        print(f"\n#{i} - Return: {result['combined_return']:.2f}% (Score: {result['score']:.2f})")
        print(f"  Drawdown: {result['avg_drawdown']:.2f}% | Trades: {result['total_trades']}")
        print(f"  Position: {result['max_position_size']}, Stop: {result['stop_loss_pct']}%, Target: {result['take_profit_pct']}%")
        print(f"  Interval: {result['min_time_between_trades']}min, RSI: {result['rsi_oversold']}/{result['rsi_overbought']}")
    
    # Parameter impact analysis
    print("\n" + "="*70)
    print("PARAMETER IMPACT ANALYSIS")
    print("="*70)
    
    parameters = [
        'max_position_size',
        'stop_loss_pct', 
        'take_profit_pct',
        'min_time_between_trades'
    ]
    
    for param in parameters:
        print(f"\n{param}:")
        print("-"*70)
        stats = db.get_parameter_statistics(param)
        
        for stat in stats[:5]:  # Top 5 values
            print(f"  {stat[param]:>8} → Avg Return: {stat['avg_return']:>6.2f}%, "
                  f"Avg DD: {stat['avg_drawdown']:>5.2f}%, Score: {stat['avg_score']:>6.2f} "
                  f"(n={stat['count']})")
    
    # Export results
    print("\n" + "="*70)
    print("EXPORTING RESULTS")
    print("="*70)
    db.export_to_csv()
    
    # Generate config for best result
    if top_results:
        best = top_results[0]
        best_config = {
            "max_position_size": best['max_position_size'],
            "stop_loss_pct": best['stop_loss_pct'],
            "take_profit_pct": best['take_profit_pct'],
            "rsi_oversold": best['rsi_oversold'],
            "rsi_overbought": best['rsi_overbought'],
            "min_time_between_trades": best['min_time_between_trades'],
            "max_drawdown_limit": best['max_drawdown_limit']
        }
        
        with open('best_config.json', 'w') as f:
            json.dump(best_config, f, indent=2)
        
        print(f"✅ Best configuration saved to best_config.json")
        print(f"\nTo use this configuration:")
        print(f"  1. Review the parameters above")
        print(f"  2. Update config.json with these values")
        print(f"  3. Run backtest_historical.py to verify")
    
    db.close()


def show_meeting_requirements():
    """Show only results that meet contest requirements"""
    db = OptimizationDB()
    
    results = db.get_top_results(100, require_contest_criteria=True)
    
    print("\n" + "="*70)
    print(f"RESULTS MEETING CONTEST REQUIREMENTS ({len(results)} found)")
    print("="*70)
    
    if not results:
        print("\n⚠️  No results meet contest requirements yet:")
        print("   - Return > 30%")
        print("   - Drawdown < 50%")
        print("   - Trades ≥ 10")
        print("\nContinue testing more parameter combinations!")
    else:
        for i, result in enumerate(results[:20], 1):  # Show top 20
            print(f"\n#{i} - Score: {result['score']:.2f}")
            print(f"  Return: {result['combined_return']:.2f}% | DD: {result['avg_drawdown']:.2f}% | Trades: {result['total_trades']}")
            print(f"  Position: {result['max_position_size']}, Stop: {result['stop_loss_pct']}%, Target: {result['take_profit_pct']}%")
    
    db.close()


def compare_parameters(param_name: str):
    """Compare different values of a specific parameter"""
    db = OptimizationDB()
    
    print(f"\n" + "="*70)
    print(f"COMPARISON: {param_name}")
    print("="*70)
    
    stats = db.get_parameter_statistics(param_name)
    
    print(f"\n{'Value':<12} {'Avg Return':<12} {'Avg DD':<10} {'Avg Score':<12} {'Tests'}")
    print("-"*70)
    
    for stat in stats:
        value = stat[param_name]
        print(f"{value:<12} {stat['avg_return']:>10.2f}% {stat['avg_drawdown']:>8.2f}% "
              f"{stat['avg_score']:>10.2f} {stat['count']:>7}")
    
    db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "requirements":
            show_meeting_requirements()
        elif sys.argv[1] == "compare" and len(sys.argv) > 2:
            compare_parameters(sys.argv[2])
        else:
            print("Usage:")
            print("  python analyze_results.py                    # Full analysis")
            print("  python analyze_results.py requirements       # Show results meeting contest criteria")
            print("  python analyze_results.py compare <param>    # Compare parameter values")
    else:
        analyze_results()
