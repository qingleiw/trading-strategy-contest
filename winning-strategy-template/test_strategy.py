#!/usr/bin/env python3
"""Quick test script for the Adaptive Momentum-Reversal Strategy."""

import sys
import os
from datetime import datetime, timezone
from collections import deque

# Add base path for imports
base_path = os.path.join(os.path.dirname(__file__), '..', 'base-bot-template')
if os.path.exists(base_path):
    sys.path.insert(0, base_path)

# Mock the required imports for testing
class MockMarketSnapshot:
    def __init__(self, symbol="BTC-USD", price=50000.0):
        self.symbol = symbol
        self.current_price = price
        # Generate 100 price points for sufficient indicator history
        base_price = price * 0.95  # Start 5% lower
        self.prices = []
        for i in range(100):
            # Create realistic price movement
            change = (i / 100) * 0.1 - 0.05  # Gradual change over time
            noise = (i % 7 - 3) * 0.005  # Add some noise
            price_point = base_price * (1 + change + noise)
            self.prices.append(max(1.0, price_point))  # Ensure positive price
        
        # Ensure last price matches current_price
        self.prices[-1] = price
        self.timestamp = datetime.now(timezone.utc)

class MockPortfolio:
    def __init__(self, cash=10000.0, quantity=0.0):
        self.symbol = "BTC-USD"
        self.cash = cash
        self.quantity = quantity
    
    def value(self, price):
        return self.cash + self.quantity * price

class MockExchange:
    def __init__(self):
        self.name = "mock"

# Mock the base strategy interface
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
    print(f"Register called with args: {args}, kwargs: {kwargs}")
    if len(args) >= 2:
        name, factory = args[0], args[1]
        print(f"Registered strategy: {name}")
        # Store the factory for testing
        global _test_factories
        if '_test_factories' not in globals():
            _test_factories = {}
        _test_factories[name] = factory

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

def test_strategy():
    """Test the momentum-reversal strategy with mock data."""
    print("Testing Momentum-Reversal Strategy...")
    
    # Create strategy config
    config = {
        "rsi_period": 14,
        "rsi_oversold": 25,
        "rsi_overbought": 75,
        "macd_fast": 12,
        "macd_slow": 26,
        "macd_signal": 9,
        "bb_period": 20,
        "bb_std_dev": 2.0,
        "max_position_size": 0.3,
        "stop_loss_pct": 8.0,
        "take_profit_pct": 15.0,
        "max_drawdown_limit": 45.0,
        "min_time_between_trades": 30,
        "starting_cash": 10000.0
    }
    
    # Create strategy instance
    exchange = MockExchange()
    strategy = WinningStrategy(config, exchange)
    
    # Test with different market conditions
    test_cases = [
        ("Normal market", 50000.0, 10000.0, 0.0),
        ("Oversold market (RSI)", 45000.0, 10000.0, 0.0),  # Lower price for oversold
        ("Overbought holding", 55000.0, 5000.0, 0.1),  # Higher price, holding position
        ("Low cash scenario", 50000.0, 100.0, 0.0),  # Very low cash
        ("Mean reversion buy", 47000.0, 8000.0, 0.0),  # Should trigger Bollinger Band signal
    ]
    
    for test_name, price, cash, quantity in test_cases:
        print(f"\nTest: {test_name}")
        print(f"   Price: ${price:,}")
        print(f"   Cash: ${cash:,}")
        print(f"   Quantity: {quantity}")
        
        # Create mock market and portfolio
        market = MockMarketSnapshot("BTC-USD", price)
        portfolio = MockPortfolio(cash, quantity)
        
        # Populate strategy's price history by calling generate_signal multiple times
        # This simulates the bot running and collecting price data over time
        for i, hist_price in enumerate(market.prices):
            # Update market to simulate time progression
            temp_market = MockMarketSnapshot("BTC-USD", hist_price)
            temp_market.prices = market.prices[:i+1]  # Progressive price history
            strategy.generate_signal(temp_market, portfolio)
        
        # Now generate the final signal with full history
        signal = strategy.generate_signal(market, portfolio)
        print(f"   Signal: {signal.action.upper()}")
        if signal.size > 0:
            print(f"   Size: {signal.size:.6f}")
        print(f"   Reason: {signal.reason}")
        
        # Test trade execution
        if signal.action == "buy" and signal.size > 0:
            strategy.on_trade(signal, price, signal.size, datetime.now(timezone.utc))
            print(f"   Trade executed: BUY {signal.size:.6f} @ ${price:,}")
        elif signal.action == "sell" and signal.size > 0:
            strategy.on_trade(signal, price, signal.size, datetime.now(timezone.utc))
            print(f"   Trade executed: SELL {signal.size:.6f} @ ${price:,}")

    # Test state management
    print(f"\nStrategy Statistics:")
    print(f"   Total trades: {strategy.total_trades}")
    print(f"   Winning trades: {strategy.winning_trades}")
    print(f"   Total PnL: ${strategy.total_pnl:,.2f}")
    print(f"   Positions: {len(strategy.positions)}")
    
    # Test state serialization
    state = strategy.get_state()
    print(f"\nState serialization: {len(state)} fields")
    
    print("\nAll tests completed successfully!")
    return True

if __name__ == "__main__":
    try:
        test_strategy()
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)