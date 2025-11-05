"""
Automated Parameter Optimization Runner
Systematically tests different parameter combinations and saves results to database
"""
import json
import sys
import subprocess
from typing import Dict, List, Tuple
from itertools import product
from optimization_db import OptimizationDB
import re

class ParameterOptimizer:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.base_config = self.load_config()
        self.db = OptimizationDB()
        
    def load_config(self) -> Dict:
        """Load base configuration"""
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def save_config(self, config: Dict):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def run_backtest(self) -> Tuple[Dict, Dict, Dict]:
        """
        Run backtest and parse results
        Returns: (btc_results, eth_results, combined_results)
        """
        try:
            # Run backtest script
            result = subprocess.run(
                ['python', 'backtest_historical.py'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            output = result.stdout + result.stderr
            
            # Parse BTC results
            btc_return = self._extract_value(output, r'BTC-USD.*?Total Return:\s+([+-]?\d+\.\d+)%')
            btc_drawdown = self._extract_value(output, r'BTC-USD.*?Max Drawdown:\s+(\d+\.\d+)%')
            btc_trades = int(self._extract_value(output, r'BTC-USD.*?Total Trades:\s+(\d+)', default='0'))
            btc_win_rate = self._extract_value(output, r'BTC-USD.*?Win Rate:\s+(\d+\.\d+)%')
            btc_final_value = self._extract_value(output, r'BTC-USD.*?Final Value:\s+\$([0-9,]+\.\d+)')
            
            # Parse ETH results
            eth_return = self._extract_value(output, r'ETH-USD.*?Total Return:\s+([+-]?\d+\.\d+)%')
            eth_drawdown = self._extract_value(output, r'ETH-USD.*?Max Drawdown:\s+(\d+\.\d+)%')
            eth_trades = int(self._extract_value(output, r'ETH-USD.*?Total Trades:\s+(\d+)', default='0'))
            eth_win_rate = self._extract_value(output, r'ETH-USD.*?Win Rate:\s+(\d+\.\d+)%')
            eth_final_value = self._extract_value(output, r'ETH-USD.*?Final Value:\s+\$([0-9,]+\.\d+)')
            
            # Parse combined results
            combined_return = self._extract_value(output, r'Combined Return:\s+([+-]?\d+\.\d+)%')
            avg_drawdown = self._extract_value(output, r'Average Max Drawdown:\s+(\d+\.\d+)%')
            total_trades = int(self._extract_value(output, r'Total Trades:\s+(\d+)', default='0'))
            
            btc_results = {
                'return': btc_return,
                'drawdown': btc_drawdown,
                'trades': btc_trades,
                'win_rate': btc_win_rate,
                'final_value': btc_final_value
            }
            
            eth_results = {
                'return': eth_return,
                'drawdown': eth_drawdown,
                'trades': eth_trades,
                'win_rate': eth_win_rate,
                'final_value': eth_final_value
            }
            
            combined_results = {
                'return': combined_return,
                'avg_drawdown': avg_drawdown,
                'total_trades': total_trades
            }
            
            return btc_results, eth_results, combined_results
            
        except Exception as e:
            print(f"Error running backtest: {e}")
            return None, None, None
    
    def _extract_value(self, text: str, pattern: str, default: str = '0') -> float:
        """Extract numeric value from text using regex"""
        match = re.search(pattern, text, re.DOTALL)
        if match:
            value = match.group(1).replace(',', '')
            return float(value)
        return float(default)
    
    def test_parameter_set(self, params: Dict, notes: str = "") -> bool:
        """Test a specific parameter combination"""
        # Check if already tested
        if self.db.parameter_exists(params):
            print(f"⏭️  Skipping (already tested): {params}")
            return False
        
        # Update config
        config = self.base_config.copy()
        config.update(params)
        self.save_config(config)
        
        print(f"\n{'='*70}")
        print(f"Testing: {json.dumps(params, indent=2)}")
        print(f"{'='*70}")
        
        # Run backtest
        btc_results, eth_results, combined_results = self.run_backtest()
        
        if combined_results:
            # Save to database
            result_id = self.db.save_result(params, btc_results, eth_results, 
                                           combined_results, notes)
            
            print(f"\n✅ Results saved (ID: {result_id})")
            print(f"   Return: {combined_results['return']:.2f}%")
            print(f"   Drawdown: {combined_results['avg_drawdown']:.2f}%")
            print(f"   Trades: {combined_results['total_trades']}")
            
            return True
        else:
            print("❌ Backtest failed")
            return False
    
    def grid_search(self, param_grid: Dict[str, List]):
        """
        Perform grid search over parameter space
        
        Example:
        param_grid = {
            'max_position_size': [0.7, 0.8, 0.9],
            'stop_loss_pct': [6.0, 8.0, 10.0],
            'take_profit_pct': [30.0, 40.0, 50.0],
            'min_time_between_trades': [1440, 2880, 4320]
        }
        """
        # Generate all combinations
        keys = list(param_grid.keys())
        values = list(param_grid.values())
        combinations = list(product(*values))
        
        total = len(combinations)
        print(f"\n🔍 Starting grid search with {total} combinations...")
        
        for i, combo in enumerate(combinations, 1):
            params = dict(zip(keys, combo))
            print(f"\n[{i}/{total}] Testing combination {i}...")
            self.test_parameter_set(params, f"Grid search {i}/{total}")
        
        print(f"\n✅ Grid search complete! Tested {total} combinations")
        self.show_top_results()
    
    def random_search(self, param_ranges: Dict[str, Tuple], n_iterations: int = 50):
        """
        Random search over parameter space
        
        Example:
        param_ranges = {
            'max_position_size': (0.7, 0.95),
            'stop_loss_pct': (5.0, 12.0),
            'take_profit_pct': (25.0, 60.0),
            'min_time_between_trades': (720, 4320)
        }
        """
        import random
        
        print(f"\n🎲 Starting random search with {n_iterations} iterations...")
        
        for i in range(n_iterations):
            params = {}
            for param, (min_val, max_val) in param_ranges.items():
                if isinstance(min_val, int):
                    params[param] = random.randint(min_val, max_val)
                else:
                    params[param] = round(random.uniform(min_val, max_val), 2)
            
            print(f"\n[{i+1}/{n_iterations}] Testing random combination...")
            self.test_parameter_set(params, f"Random search {i+1}/{n_iterations}")
        
        print(f"\n✅ Random search complete! Tested {n_iterations} combinations")
        self.show_top_results()
    
    def show_top_results(self, n: int = 10):
        """Display top performing parameter sets"""
        print(f"\n{'='*70}")
        print(f"TOP {n} RESULTS BY SCORE")
        print(f"{'='*70}")
        
        results = self.db.get_top_results(n)
        
        for i, result in enumerate(results, 1):
            print(f"\n#{i} - Score: {result['score']:.2f}")
            print(f"   Return: {result['combined_return']:.2f}% | Drawdown: {result['avg_drawdown']:.2f}% | Trades: {result['total_trades']}")
            print(f"   Position: {result['max_position_size']} | Stop: {result['stop_loss_pct']}% | Target: {result['take_profit_pct']}%")
            print(f"   RSI: {result['rsi_oversold']}/{result['rsi_overbought']} | Trade Interval: {result['min_time_between_trades']}min")
            if result['meets_requirements']:
                print(f"   ✅ Meets contest requirements!")
    
    def close(self):
        """Clean up"""
        self.db.close()


def quick_test_suite():
    """Run a quick test suite with promising parameter combinations"""
    optimizer = ParameterOptimizer()
    
    # Test combinations based on previous observations
    test_sets = [
        # Original best performer baseline
        {
            'max_position_size': 0.90,
            'stop_loss_pct': 8.0,
            'take_profit_pct': 40.0,
            'rsi_oversold': 35,
            'rsi_overbought': 75,
            'min_time_between_trades': 2880
        },
        # Higher position, higher target
        {
            'max_position_size': 0.95,
            'stop_loss_pct': 10.0,
            'take_profit_pct': 50.0,
            'rsi_oversold': 30,
            'rsi_overbought': 80,
            'min_time_between_trades': 2880
        },
        # More frequent trading
        {
            'max_position_size': 0.85,
            'stop_loss_pct': 7.0,
            'take_profit_pct': 35.0,
            'rsi_oversold': 32,
            'rsi_overbought': 78,
            'min_time_between_trades': 1440
        },
        # Conservative approach
        {
            'max_position_size': 0.75,
            'stop_loss_pct': 6.0,
            'take_profit_pct': 30.0,
            'rsi_oversold': 28,
            'rsi_overbought': 72,
            'min_time_between_trades': 2160
        },
        # Aggressive growth
        {
            'max_position_size': 0.98,
            'stop_loss_pct': 12.0,
            'take_profit_pct': 60.0,
            'rsi_oversold': 25,
            'rsi_overbought': 85,
            'min_time_between_trades': 3600
        }
    ]
    
    for i, params in enumerate(test_sets, 1):
        print(f"\n{'='*70}")
        print(f"QUICK TEST {i}/{len(test_sets)}")
        print(f"{'='*70}")
        optimizer.test_parameter_set(params, f"Quick test {i}")
    
    optimizer.show_top_results(5)
    optimizer.close()


def full_grid_search():
    """Run comprehensive grid search"""
    optimizer = ParameterOptimizer()
    
    param_grid = {
        'max_position_size': [0.80, 0.85, 0.90, 0.95],
        'stop_loss_pct': [6.0, 8.0, 10.0],
        'take_profit_pct': [35.0, 40.0, 45.0, 50.0],
        'rsi_oversold': [30, 35],
        'rsi_overbought': [75, 80],
        'min_time_between_trades': [1440, 2160, 2880, 3600]
    }
    
    optimizer.grid_search(param_grid)
    optimizer.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "grid":
            print("Starting full grid search...")
            full_grid_search()
        elif sys.argv[1] == "quick":
            print("Starting quick test suite...")
            quick_test_suite()
        else:
            print("Usage: python optimize_parameters.py [quick|grid]")
    else:
        # Default: run quick test suite
        quick_test_suite()
