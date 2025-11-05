# Finding the Download Button on Yahoo Finance

## Visual Guide

### For BTC-USD:

1. **Open this exact URL in your browser:**
   ```
   https://finance.yahoo.com/quote/BTC-USD/history?period1=1704067200&period2=1719792000
   ```
   (This URL has the dates pre-set for Jan 1 - Jun 30, 2024)

2. **Look at the top right of the page** - you'll see:
   - A date range selector showing "Jan 01, 2024 - Jun 30, 2024"
   - Next to it: **"Download ↓"** link/button

3. **If you don't see the download button:**
   - Scroll up - it's in the header area
   - Look for the historical data table
   - Above the table on the right side is "Download"
   - It might say "Download Data" or just have a download icon ↓

4. **Click "Download"** and it will save as `BTC-USD.csv`

### For ETH-USD:

1. **Open this URL:**
   ```
   https://finance.yahoo.com/quote/ETH-USD/history?period1=1704067200&period2=1719792000
   ```

2. **Click "Download"** (same location as BTC)

3. Saves as `ETH-USD.csv`

---

## Alternative: Use Trading View

If Yahoo Finance download isn't working:

### TradingView Method:
1. Go to: https://www.tradingview.com/chart/
2. Search for "BTCUSD" in the search bar
3. Set timeframe to 1H (1 hour)
4. Set date range: Jan 1, 2024 - Jun 30, 2024
5. Click the "..." menu → Export chart data
6. Download CSV
7. Repeat for "ETHUSD"

---

## Alternative: Use CoinMarketCap

### CoinMarketCap Historical Data:
1. Go to: https://coinmarketcap.com/currencies/bitcoin/historical-data/
2. Set date range: 01/01/2024 to 06/30/2024
3. Click "Export Data" button
4. Save CSV
5. Repeat for Ethereum: https://coinmarketcap.com/currencies/ethereum/historical-data/

---

## Still Can't Find It?

### Option 1: I'll generate sample real data
I can create a Python script that generates data matching the ACTUAL price movements from Jan-Jun 2024 (not random, but based on known real prices).

### Option 2: Use my pre-prepared CSVs
If you tell me you want to proceed, I can prepare the backtest code to work with whatever format you manage to download.

### Option 3: Contest organizers may provide data
Check if the contest repository or rules mention official data sources.

---

**Which option would you like to try?**
1. I'll open Yahoo Finance page in browser for you
2. Try TradingView export
3. Try CoinMarketCap export
4. Use alternative data source
5. Generate realistic data based on known 2024 prices
