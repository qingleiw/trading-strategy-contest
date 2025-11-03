#!/usr/bin/env python3
"""Winning Strategy Bot - Startup Script

Adaptive Momentum-Reversal Trading Bot designed to win the $1,000 trading contest.
Combines RSI, MACD, and Bollinger Bands with advanced risk management.
"""

from __future__ import annotations

import sys
import os

# Import base infrastructure from base-bot-template
base_path = os.path.join(os.path.dirname(__file__), '..', 'base-bot-template')
if not os.path.exists(base_path):
    # In Docker container, base template is at /app/base/
    base_path = '/app/base'

sys.path.insert(0, base_path)

# Import our winning strategy (this registers it)
import winning_strategy

# Import base bot infrastructure
from universal_bot import UniversalBot


def main() -> None:
    """Main entry point for Winning Strategy Bot."""
    config_path = sys.argv[1] if len(sys.argv) > 1 else None

    bot = UniversalBot(config_path)

    # Print startup info
    print("WINNING STRATEGY BOT - Contest Edition")
    print("=" * 60)
    print(f"Bot ID: {bot.config.bot_instance_id}")
    print(f"User ID: {bot.config.user_id}")
    print(f"Strategy: {bot.config.strategy}")
    print(f"Symbol: {bot.config.symbol}")
    print(f"Exchange: {bot.config.exchange}")
    print(f"Starting Cash: ${bot.config.starting_cash:,}")
    print()
    print("STRATEGY FEATURES:")
    print("   - RSI momentum detection (oversold/overbought)")
    print("   - MACD trend confirmation")
    print("   - Bollinger Bands mean reversion")
    print("   - Dynamic position sizing based on volatility")
    print("   - Stop-loss and take-profit automation")
    print("   - Maximum 45% drawdown protection")
    print("   - Trade throttling for optimal timing")
    print()
    print("TARGET: Maximize PnL while staying under 50% drawdown")
    print("GOAL: Win $1,000 USD prize!")
    print("=" * 60)

    try:
        bot.run()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"\nBot error: {e}")
        raise


if __name__ == "__main__":
    main()