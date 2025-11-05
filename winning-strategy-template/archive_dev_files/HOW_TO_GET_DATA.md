# How to Get Real Historical Data (5 Minutes)

## EASIEST METHOD: Manual Yahoo Finance Download

### Step 1: Download BTC-USD Data
1. Open: https://finance.yahoo.com/quote/BTC-USD/history/
2. Click "Time Period" dropdown
3. Select "Custom" and enter:
   - Start Date: **01/01/2024**
   - End Date: **06/30/2024**
4. Click "Download" button
5. Save as: `BTC-USD_2024_Jan-Jun.csv`

### Step 2: Download ETH-USD Data
1. Open: https://finance.yahoo.com/quote/ETH-USD/history/
2. Click "Time Period" dropdown
3. Select "Custom" and enter:
   - Start Date: **01/01/2024**
   - End Date: **06/30/2024**
4. Click "Download" button
5. Save as: `ETH-USD_2024_Jan-Jun.csv`

### Step 3: Move Files
Move both CSV files to:
```
c:\project\strategy-contest\winning-strategy-template\
```

## ALTERNATIVE: CoinGecko Manual Download

### For BTC:
1. Visit: https://www.coingecko.com/en/coins/bitcoin/historical_data
2. Set date range: 2024-01-01 to 2024-06-30
3. Export to CSV

### For ETH:
1. Visit: https://www.coingecko.com/en/coins/ethereum/historical_data
2. Set date range: 2024-01-01 to 2024-06-30
3. Export to CSV

## Why APIs Are Failing

All free crypto APIs now require:
- Rate limiting / throttling
- API keys / registration
- Premium accounts for historical data

**Manual download is FASTEST and most reliable!**

## Next Steps After Download

Once you have the CSV files:
1. Place them in `winning-strategy-template/` folder
2. I'll update `backtest_historical.py` to load real data
3. Remove all synthetic data generation
4. Run backtest with REAL data
5. Get realistic results for contest submission

---

**Time Estimate:** 5 minutes to download both files manually
**Zero registration, zero API keys, 100% free**
