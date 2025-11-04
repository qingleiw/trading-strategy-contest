#!/usr/bin/env python3
"""Adaptive Momentum-Reversal Trading Bot

This strategy combines multiple technical indicators for robust trading:
1. RSI for momentum detection and oversold/overbought conditions
2. MACD for trend direction and momentum confirmation 
3. Bollinger Bands for mean reversion opportunities
4. Dynamic position sizing based on volatility
5. Advanced risk management with stop-losses and drawdown protection

Optimized for cryptocurrency markets with adaptive risk management.
"""

from __future__ import annotations

import sys
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Deque
from collections import deque
from statistics import mean, pstdev
import logging

# Import base infrastructure from base-bot-template
base_path = os.path.join(os.path.dirname(__file__), '..', 'base-bot-template')
if not os.path.exists(base_path):
    base_path = '/app/base'

sys.path.insert(0, base_path)

from strategy_interface import BaseStrategy, Signal, Portfolio, register_strategy
from exchange_interface import MarketSnapshot


class WinningStrategy(BaseStrategy):
    """Adaptive Momentum-Reversal Strategy for cryptocurrency trading.
    
    This strategy uses multiple technical indicators:
    - RSI: Relative Strength Index for momentum
    - MACD: Moving Average Convergence Divergence for trend
    - Bollinger Bands: For mean reversion opportunities
    - Dynamic position sizing based on volatility
    - Advanced risk management with stop-losses
    """

    def __init__(self, config: Dict[str, Any], exchange):
        super().__init__(config=config, exchange=exchange)
        
        # Strategy parameters (optimized for Jan-Jun 2024 crypto data)
        self.rsi_period = int(config.get("rsi_period", 14))
        self.rsi_oversold = float(config.get("rsi_oversold", 25))
        self.rsi_overbought = float(config.get("rsi_overbought", 75))
        
        self.macd_fast = int(config.get("macd_fast", 12))
        self.macd_slow = int(config.get("macd_slow", 26))
        self.macd_signal = int(config.get("macd_signal", 9))
        
        self.bb_period = int(config.get("bb_period", 20))
        self.bb_std_dev = float(config.get("bb_std_dev", 2.0))
        
        # Risk management
        self.max_position_size = float(config.get("max_position_size", 0.3))  # 30% max position
        self.stop_loss_pct = float(config.get("stop_loss_pct", 8.0))
        self.take_profit_pct = float(config.get("take_profit_pct", 15.0))
        self.trailing_stop_pct = float(config.get("trailing_stop_pct", 5.0))
        self.max_drawdown_limit = float(config.get("max_drawdown_limit", 45.0))  # Stay under 50%
        
        # Position tracking
        self.positions: Deque[Dict[str, Any]] = deque()
        self.peak_portfolio_value = float(config.get("starting_cash", 10000.0))
        self.last_trade_time: Optional[datetime] = None
        self.min_time_between_trades = int(config.get("min_time_between_trades", 30))  # minutes
        
        # Technical indicator state
        self.price_history: Deque[float] = deque(maxlen=100)
        self.ema_fast_history: Deque[float] = deque(maxlen=50)
        self.ema_slow_history: Deque[float] = deque(maxlen=50)
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.total_pnl = 0.0
        
        self.logger = logging.getLogger("winning_strategy")

    def _calculate_rsi(self, prices: List[float], period: int = 14) -> Optional[float]:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return None
            
        deltas = []
        for i in range(1, len(prices)):
            deltas.append(prices[i] - prices[i-1])
            
        if len(deltas) < period:
            return None
            
        gains = [d for d in deltas[-period:] if d > 0]
        losses = [-d for d in deltas[-period:] if d < 0]
        
        avg_gain = mean(gains) if gains else 0
        avg_loss = mean(losses) if losses else 0
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_ema(self, prices: List[float], period: int) -> Optional[float]:
        """Calculate Exponential Moving Average."""
        if len(prices) < period:
            return None
            
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
            
        return ema

    def _calculate_macd(self, prices: List[float]) -> tuple[Optional[float], Optional[float], Optional[float]]:
        """Calculate MACD line, signal line, and histogram."""
        ema_fast = self._calculate_ema(prices, self.macd_fast)
        ema_slow = self._calculate_ema(prices, self.macd_slow)
        
        if ema_fast is None or ema_slow is None:
            return None, None, None
            
        macd_line = ema_fast - ema_slow
        
        # For signal line, we need MACD history
        if len(self.ema_fast_history) >= self.macd_signal:
            macd_history = []
            for i in range(len(self.ema_fast_history)):
                if i < len(self.ema_slow_history):
                    macd_history.append(self.ema_fast_history[i] - self.ema_slow_history[i])
            
            signal_line = self._calculate_ema(macd_history, self.macd_signal)
            histogram = macd_line - signal_line if signal_line else None
        else:
            signal_line = None
            histogram = None
            
        return macd_line, signal_line, histogram

    def _calculate_bollinger_bands(self, prices: List[float]) -> tuple[Optional[float], Optional[float], Optional[float]]:
        """Calculate Bollinger Bands: upper, middle (SMA), lower."""
        if len(prices) < self.bb_period:
            return None, None, None
            
        recent_prices = prices[-self.bb_period:]
        sma = mean(recent_prices)
        std_dev = pstdev(recent_prices)
        
        upper_band = sma + (self.bb_std_dev * std_dev)
        lower_band = sma - (self.bb_std_dev * std_dev)
        
        return upper_band, sma, lower_band

    def _calculate_volatility(self, prices: List[float], period: int = 20) -> float:
        """Calculate price volatility as standard deviation of returns."""
        if len(prices) < period + 1:
            return 0.02  # Default 2% volatility
            
        returns = []
        for i in range(1, min(len(prices), period + 1)):
            returns.append((prices[-i] - prices[-i-1]) / prices[-i-1])
            
        return pstdev(returns) if len(returns) > 1 else 0.02

    def _calculate_position_size(self, current_price: float, portfolio: Portfolio, volatility: float) -> float:
        """Calculate position size based on volatility and available cash."""
        # Base position size as percentage of portfolio
        portfolio_value = portfolio.value(current_price)
        base_size = portfolio_value * self.max_position_size
        
        # Adjust for volatility (reduce size in high volatility)
        volatility_factor = max(0.5, 1 - (volatility * 10))  # Scale volatility impact
        adjusted_size = base_size * volatility_factor
        
        # Ensure we don't exceed available cash
        max_cash_size = portfolio.cash * 0.95  # Leave 5% buffer
        final_size = min(adjusted_size, max_cash_size)
        
        return final_size / current_price  # Return quantity, not notional

    def _check_risk_limits(self, portfolio: Portfolio, current_price: float) -> bool:
        """Check if we're within risk limits (drawdown, etc.)."""
        current_value = portfolio.value(current_price)
        
        # Initialize peak value on first call (fixes test scenarios with varied starting values)
        if self.total_trades == 0 and current_value > 0:
            self.peak_portfolio_value = max(self.peak_portfolio_value, current_value)
        
        # Update peak value
        if current_value > self.peak_portfolio_value:
            self.peak_portfolio_value = current_value
            
        # Check drawdown (avoid division by zero)
        if self.peak_portfolio_value <= 0:
            return True  # No drawdown check if no peak established
            
        drawdown_pct = ((self.peak_portfolio_value - current_value) / self.peak_portfolio_value) * 100
        
        if drawdown_pct >= self.max_drawdown_limit:
            self.logger.warning(f"Drawdown limit exceeded: {drawdown_pct:.2f}% >= {self.max_drawdown_limit}%")
            return False
            
        return True

    def _should_stop_loss(self, portfolio: Portfolio, current_price: float) -> bool:
        """Check if we should trigger stop loss on existing positions."""
        if not self.positions or portfolio.quantity <= 0:
            return False
            
        # Calculate average entry price
        total_cost = sum(pos['price'] * pos['size'] for pos in self.positions)
        total_size = sum(pos['size'] for pos in self.positions)
        avg_entry = total_cost / total_size if total_size > 0 else current_price
        
        # Check stop loss
        loss_pct = ((avg_entry - current_price) / avg_entry) * 100
        return loss_pct >= self.stop_loss_pct

    def _should_take_profit(self, portfolio: Portfolio, current_price: float) -> bool:
        """Check if we should take profit on existing positions."""
        if not self.positions or portfolio.quantity <= 0:
            return False
            
        # Calculate average entry price
        total_cost = sum(pos['price'] * pos['size'] for pos in self.positions)
        total_size = sum(pos['size'] for pos in self.positions)
        avg_entry = total_cost / total_size if total_size > 0 else current_price
        
        # Check take profit
        profit_pct = ((current_price - avg_entry) / avg_entry) * 100
        return profit_pct >= self.take_profit_pct

    def _can_trade(self, now: datetime) -> bool:
        """Check if enough time has passed since last trade."""
        if self.last_trade_time is None:
            return True
            
        time_since_last = now - self.last_trade_time
        return time_since_last >= timedelta(minutes=self.min_time_between_trades)

    def generate_signal(self, market: MarketSnapshot, portfolio: Portfolio) -> Signal:
        """Generate trading signal based on technical indicators."""
        current_price = market.current_price
        # Use market timestamp if available, otherwise current time
        if hasattr(market, 'timestamp') and market.timestamp:
            # Ensure timestamp is timezone-aware
            now = market.timestamp.replace(tzinfo=timezone.utc) if market.timestamp.tzinfo is None else market.timestamp
        else:
            now = datetime.now(timezone.utc)
        
        # Update price history
        self.price_history.append(current_price)
        
        # Check risk limits first
        if not self._check_risk_limits(portfolio, current_price):
            return Signal("hold", reason="Risk limits exceeded")
            
        # Check if we can trade (time-based throttling)
        if not self._can_trade(now):
            return Signal("hold", reason="Time throttling active")
            
        # Get enough price data for indicators
        prices = list(self.price_history)
        if len(prices) < max(self.rsi_period, self.bb_period, self.macd_slow):
            return Signal("hold", reason="Insufficient price history")
            
        # Calculate technical indicators
        rsi = self._calculate_rsi(prices, self.rsi_period)
        macd_line, macd_signal, macd_histogram = self._calculate_macd(prices)
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(prices)
        volatility = self._calculate_volatility(prices)
        
        # Update EMA history for MACD calculation
        ema_fast = self._calculate_ema(prices, self.macd_fast)
        ema_slow = self._calculate_ema(prices, self.macd_slow)
        if ema_fast:
            self.ema_fast_history.append(ema_fast)
        if ema_slow:
            self.ema_slow_history.append(ema_slow)
            
        # Check exit conditions first
        if portfolio.quantity > 0:
            # Calculate current position P&L
            total_cost = sum(pos['price'] * pos['size'] for pos in self.positions)
            total_size = sum(pos['size'] for pos in self.positions)
            avg_entry = total_cost / total_size if total_size > 0 else current_price
            current_pnl_pct = ((current_price - avg_entry) / avg_entry) * 100
            
            # Stop loss check (higher priority)
            if self._should_stop_loss(portfolio, current_price):
                return Signal("sell", size=portfolio.quantity, reason="Stop loss triggered")
                
            # BALANCED STRATEGY: Hold winners longer, but still exit when appropriate
            # Exit conditions (in priority order):
            # 1. Take profit target reached -> Sell 80%
            # 2. Strong overbought + bearish signals -> Sell 60%  
            # 3. Moderate profit + reversal signals -> Sell 40%
            
            # Take profit at target - sell most but keep 20% riding
            if self._should_take_profit(portfolio, current_price):
                sell_size = portfolio.quantity * 0.8
                return Signal("sell", size=sell_size, reason=f"Take profit (80%): +{current_pnl_pct:.1f}%")
                
            # Strong technical weakness indicators
            overbought = rsi and rsi >= self.rsi_overbought
            bearish_macd = (macd_line and macd_signal and 
                           macd_line < macd_signal and 
                           macd_histogram and macd_histogram < -1.0)
            bb_breach = bb_upper and current_price >= bb_upper * 1.03  # 3% above upper band
            
            # Trend reversal check
            reversal_signal = False
            if len(prices) >= 20:
                recent_high = max(prices[-20:])
                drop_from_high = ((recent_high - current_price) / recent_high) * 100
                if drop_from_high >= 5.0 and current_pnl_pct > 0:
                    reversal_signal = True
            
            # Exit on strong combined weakness (sell majority)
            if overbought and bearish_macd:
                sell_size = portfolio.quantity * 0.6
                return Signal("sell", size=sell_size, reason=f"Strong weakness (60%): RSI {rsi:.1f} + MACD bearish")
            
            if overbought and bb_breach:
                sell_size = portfolio.quantity * 0.6
                return Signal("sell", size=sell_size, reason=f"Extreme extension (60%): RSI {rsi:.1f} + BB +3%")
            
            # Exit on moderate profit + any weakness signal (sell some)
            if current_pnl_pct >= 20 and (overbought or bearish_macd or reversal_signal):
                sell_size = portfolio.quantity * 0.4
                return Signal("sell", size=sell_size, reason=f"Defensive exit (40%): +{current_pnl_pct:.1f}% + weakness")
                
        # Entry conditions - aim to stay invested in uptrend markets
        current_position_value = portfolio.quantity * current_price
        total_portfolio_value = portfolio.cash + current_position_value
        position_pct = current_position_value / total_portfolio_value if total_portfolio_value > 0 else 0
        
        # In uptrend markets, aim for high allocation (80-90%)
        target_allocation = 0.85
        if portfolio.cash > 100 and position_pct < target_allocation:
            buy_signals = 0
            buy_reasons = []
            
            # Check market trend - strongly favor uptrends
            if len(prices) >= 20:
                short_trend = (prices[-1] - prices[-5]) / prices[-5]
                medium_trend = (prices[-1] - prices[-20]) / prices[-20]
                long_trend = (prices[-1] - prices[-50]) / prices[-50] if len(prices) >= 50 else medium_trend
                
                # Only avoid buying in severe downtrends
                if medium_trend < -0.10:  # Down 10%+ 
                    return Signal("hold", reason="Severe downtrend")
                
                # Strong uptrend - add multiple signals
                if long_trend > 0.05:  # Up 5%+ over long term
                    buy_signals += 2
                    buy_reasons.append("Strong long-term uptrend")
                elif medium_trend > 0.02:
                    buy_signals += 1
                    buy_reasons.append("Medium uptrend")
            
            # RSI recovery from oversold (better timing than pure oversold)
            if rsi and 30 < rsi <= self.rsi_oversold + 5:  # Just recovering from oversold
                buy_signals += 2  # Stronger weight
                buy_reasons.append(f"RSI recovering: {rsi:.1f}")
                
            # MACD bullish crossover with strong momentum
            if macd_line and macd_signal and macd_line > macd_signal and macd_histogram and macd_histogram > 0:
                buy_signals += 1
                buy_reasons.append("MACD bullish")
                
            # Bollinger Band lower breach (mean reversion opportunity)
            if bb_lower and current_price <= bb_lower * 1.01:  # Within 1% of lower band
                buy_signals += 2  # Strong signal
                buy_reasons.append("Price at lower Bollinger Band")
                
            # Strong momentum breakout
            if len(prices) >= 10:
                recent_low = min(prices[-10:])
                bounce = ((current_price - recent_low) / recent_low) * 100
                
                # Early in uptrend (bounced 2-5%)
                if 2.0 <= bounce <= 5.0:
                    buy_signals += 2
                    buy_reasons.append(f"Momentum breakout: +{bounce:.1f}%")
                # Small dip buying opportunity  
                elif -1.0 <= bounce < 0:
                    buy_signals += 1
                    buy_reasons.append(f"Dip buy opportunity")
                    
            # Need at least 2 confirming signals (easier to enter in uptrends)
            if buy_signals >= 2:
                position_size = self._calculate_position_size(current_price, portfolio, volatility)
                if position_size > 0:
                    reason = f"Buy signals: {', '.join(buy_reasons[:2])}"
                    return Signal("buy", size=position_size, reason=reason)
                    
        return Signal("hold", reason="No clear signals")

    def on_trade(self, signal: Signal, execution_price: float, execution_size: float, timestamp: datetime) -> None:
        """Update strategy state after trade execution."""
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
            
        self.last_trade_time = timestamp
        self.total_trades += 1
        
        if signal.action == "buy" and execution_size > 0:
            # Record new position
            position = {
                "price": execution_price,
                "size": execution_size,
                "timestamp": timestamp.isoformat(),
                "type": "buy"
            }
            self.positions.append(position)
            
            self.logger.info(f"BUY: {execution_size:.6f} @ ${execution_price:,.2f} = ${execution_size * execution_price:,.2f}")
            
        elif signal.action == "sell" and execution_size > 0:
            # Calculate P&L for this trade
            if self.positions:
                # FIFO: remove from oldest positions first
                remaining_size = execution_size
                trade_pnl = 0.0
                
                while self.positions and remaining_size > 0:
                    position = self.positions[0]
                    if position["size"] <= remaining_size:
                        # Sell entire position
                        pnl = (execution_price - position["price"]) * position["size"]
                        trade_pnl += pnl
                        remaining_size -= position["size"]
                        self.positions.popleft()
                    else:
                        # Partial sell
                        pnl = (execution_price - position["price"]) * remaining_size
                        trade_pnl += pnl
                        position["size"] -= remaining_size
                        remaining_size = 0
                        
                self.total_pnl += trade_pnl
                if trade_pnl > 0:
                    self.winning_trades += 1
                    
                self.logger.info(f"SELL: {execution_size:.6f} @ ${execution_price:,.2f} = ${execution_size * execution_price:,.2f}, PnL: ${trade_pnl:,.2f}")

    def get_state(self) -> Dict[str, Any]:
        """Get serializable strategy state."""
        return {
            "positions": list(self.positions),
            "peak_portfolio_value": self.peak_portfolio_value,
            "last_trade_time": self.last_trade_time.isoformat() if self.last_trade_time else None,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "total_pnl": self.total_pnl,
            "price_history": list(self.price_history),
            "ema_fast_history": list(self.ema_fast_history),
            "ema_slow_history": list(self.ema_slow_history)
        }

    def set_state(self, state: Dict[str, Any]) -> None:
        """Restore strategy state."""
        self.positions = deque(state.get("positions", []))
        self.peak_portfolio_value = state.get("peak_portfolio_value", 10000.0)
        self.total_trades = state.get("total_trades", 0)
        self.winning_trades = state.get("winning_trades", 0)
        self.total_pnl = state.get("total_pnl", 0.0)
        
        last_trade = state.get("last_trade_time")
        if last_trade:
            self.last_trade_time = datetime.fromisoformat(last_trade)
            
        price_history = state.get("price_history", [])
        self.price_history = deque(price_history, maxlen=100)
        
        ema_fast = state.get("ema_fast_history", [])
        self.ema_fast_history = deque(ema_fast, maxlen=50)
        
        ema_slow = state.get("ema_slow_history", [])
        self.ema_slow_history = deque(ema_slow, maxlen=50)


# Register the momentum-reversal strategy
register_strategy("adaptive_momentum", WinningStrategy)
register_strategy("momentum_reversal", WinningStrategy)  # Alternative name