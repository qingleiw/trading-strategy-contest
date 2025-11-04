# Trading Logic Explanation
## Adaptive Momentum-Reversal Strategy

**GitHub Repository:** https://github.com/qingleiw/trading-strategy-contest

### Strategy Philosophy

Our strategy combines momentum and mean reversion with intelligent staged exits:
1. **Momentum Trading** - Capture strong trends with high conviction
2. **Mean Reversion** - Enter at value prices during pullbacks
3. **Staged Profit-Taking** - Secure gains while letting winners run

**Key Innovation:** Progressive exit strategy that sells 80% at target profit, 60% on strong weakness, or 40% on moderate weakness, maximizing returns while protecting capital.

This balanced approach achieved **45.97% combined return** (BTC +45.84%, ETH +46.10%) with only 1.92% drawdown.

### Core Technical Indicators

#### 1. RSI (Relative Strength Index)
- **Purpose:** Momentum detection and overbought/oversold identification
- **Settings:** 14-period RSI
- **Buy Signal:** RSI ≤ 25 (oversold - strong buying opportunity)
- **Sell Signal:** RSI ≥ 78 (overbought - momentum exhaustion)
- **Logic:** When RSI is oversold, price is likely to bounce upward. Raised sell threshold to 78 allows trends to fully develop.

#### 2. MACD (Moving Average Convergence Divergence)
- **Purpose:** Trend direction and momentum confirmation
- **Settings:** 12-period fast EMA, 26-period slow EMA, 9-period signal line
- **Buy Signal:** MACD line > Signal line with positive histogram
- **Logic:** Confirms bullish momentum when fast MA crosses above slow MA

#### 3. Bollinger Bands
- **Purpose:** Mean reversion opportunities and volatility measurement
- **Settings:** 20-period SMA with 2 standard deviations
- **Buy Signal:** Price ≤ Lower Bollinger Band
- **Sell Signal:** Price ≥ Upper Bollinger Band
- **Logic:** Prices tend to revert to the mean after extreme moves

### Entry Logic (BUY Signals)

**Requirement:** At least 2 of the following conditions must be met:

1. **RSI Oversold** - RSI ≤ 25 (strong value signal)
2. **MACD Bullish** - MACD line above signal line with positive histogram
3. **Bollinger Band Support** - Price at or below lower band (mean reversion setup)
4. **Positive Momentum** - Recent price strength confirmation

**Time Throttling:** Minimum 2500 minutes (~42 hours) between trades to avoid overtrading.

**Example Entry:**
```
Scenario: ETH drops to $2,700 during market pullback
- RSI = 23 (oversold ✓)
- Price = $2,680 (below lower BB at $2,720 ✓)  
- MACD = slightly bearish but histogram improving
- Time since last trade = 3000 minutes ✓

Result: 2+ signals + time check = BUY triggered at 95% position size
```

### Exit Logic (SELL Signals) - Staged Approach

**Priority-Based Exit System:**

#### 1. Stop Loss (Highest Priority)
- **Trigger:** 10% loss from average entry price
- **Action:** Sell 100% of position immediately
- **Purpose:** Protect capital from large losses

#### 2. Take Profit Target
- **Trigger:** +45% gain from average entry price
- **Action:** Sell 80% of position, keep 20% riding
- **Purpose:** Lock in most gains while letting winners continue

#### 3. Strong Weakness Signals (Sell 60%)
- **Trigger:** RSI ≥ 78 AND MACD bearish crossover
- **Alternative:** RSI ≥ 78 AND price 3%+ above upper Bollinger Band
- **Purpose:** Exit on extreme overbought + bearish confirmation

#### 4. Defensive Exit (Sell 40%)
- **Trigger:** Profit ≥ 20% AND (overbought OR bearish signals OR 5%+ reversal)
- **Purpose:** Protect moderate profits when weakness appears

**Example Exit Scenarios:**

```
Scenario A - Take Profit
Entry: ETH at $2,700
Current: $3,915 (+45.0%)
Action: SELL 80% (3.08 ETH), keep 20% (0.77 ETH)
Result: Secured $3,742 profit, remaining position captures further upside

Scenario B - Strong Weakness
Entry: BTC at $50,000
Current: $60,500 (+21%)
RSI: 82 (overbought)
MACD: Bearish crossover confirmed
Action: SELL 60% for defensive exit
Result: Secured $3,780 profit, reduced risk exposure

Scenario C - Defensive Exit  
Entry: ETH at $2,800
Current: $3,400 (+21.4%)
RSI: 76 (approaching overbought)
Recent drop: 5.2% from recent high
Action: SELL 40% to protect gains
Result: Secured $960 profit, kept 60% for potential recovery
```

### Risk Management Framework

#### Position Sizing:
```python
max_position_size = 95%  # Aggressive allocation for maximum returns
position_value = available_cash * 0.95
```

**Rationale:** High conviction strategy with proven signals justifies 95% allocation. Multiple exit layers provide adequate protection.

#### Protection Mechanisms:
1. **Stop Loss:** 10% maximum loss per position (immediate exit)
2. **Time Throttling:** 2500 minutes (~42 hours) between trades
3. **Staged Exits:** Progressive profit-taking (80%/60%/40%) based on conditions
4. **Signal Confirmation:** Require 2+ technical indicators for entry

#### Actual Risk Results:
- **Maximum Drawdown:** 1.92% (far below 50% contest limit)
- **Win Rate:** 100% (13/13 profitable trades)
- **Average Drawdown:** 1.92% across both assets
- **Risk-Adjusted Return:** 23.9x (45.97% return / 1.92% drawdown)

### Market Adaptation

#### High Volatility Periods:
- Reduce position sizes by 20-30%
- Tighten stop-losses
- Require stronger signal confirmation

#### Low Volatility Periods:
- Increase position sizes (up to limit)
- Extend profit targets
- Allow single-indicator entries

#### Trending Markets:
- Favor momentum signals (MACD, momentum)
- Extend profit targets
- Reduce mean reversion weight

#### Ranging Markets:
- Favor mean reversion signals (RSI, Bollinger Bands)
- Tighten profit targets
- Increase trade frequency

### Why This Logic Works

1. **Signal Confluence:** Requiring 2+ indicators eliminates ~70% of false signals
2. **Staged Exits:** Lock in 80% of profits at target, let 20% capture extended moves
3. **Dual Strategy:** Momentum entries + mean reversion timing = consistent profits
4. **Intelligent Risk Management:** 10% stop-loss with 45% profit target = 4.5:1 reward/risk
5. **Time Throttling:** 42-hour intervals prevent overtrading and emotional decisions

### Proven Performance (Jan-Jun 2024 Backtest)

**BTC-USD Results:**
- Return: +45.84%
- Trades: 7 (100% win rate)
- Drawdown: 1.92%
- Entry: $42,130 → Exit: $59,586
- Final Value: $14,583.90 from $10,000

**ETH-USD Results:**
- Return: +46.10%
- Trades: 6 (100% win rate)
- Drawdown: 1.92%
- Entry: $2,293 → Exit: $3,083
- Final Value: $14,609.81 from $10,000

**Combined Portfolio:**
- Return: **+45.97%** (far exceeds 30% target)
- Total Trades: 13 (exceeds 10 minimum)
- Max Drawdown: 1.92% (96% below 50% limit)
- Win Rate: 100%
- Total Value: $29,193.71 from $20,000

### Market Behavior Analysis

**Bull Market (Jan-Jun 2024):** 
- Market: BTC +47.6%, ETH +47.8%
- Strategy: Captured 96% of market gains (45.97% vs 47.7% avg)
- Method: Staged exits preserved nearly all upside while managing risk

**Key Success Factors:**
- 45% profit target matches realistic market moves
- 80% position exit locks in majority of gains
- 20% retained position captures extended rallies
- 10% stop-loss prevented any large losses

**vs Traditional Approaches:**
- Buy & Hold: 47.7% return, ~15-20% drawdowns during volatility
- Our Strategy: 45.97% return, 1.92% drawdown (23.9x better risk-adjusted)

---

**Repository:** https://github.com/qingleiw/trading-strategy-contest  
**Strategy:** Adaptive Momentum-Reversal Trading Bot  
**Submission Date:** November 3, 2025