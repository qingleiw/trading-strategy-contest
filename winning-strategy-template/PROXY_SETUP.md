# Proxy Setup Guide (Optional)

## Overview
By default, the backtest script will attempt to download data directly from Yahoo Finance. If you're behind a VPN or firewall that blocks access, you can configure a proxy.

## How to Enable Proxy

### Windows (PowerShell)
```powershell
# Set proxy for current session
$env:YFINANCE_PROXY = "http://127.0.0.1:10808"

# Run backtest
python backtest_historical.py

# Clear proxy (optional)
$env:YFINANCE_PROXY = $null
```

### Windows (Command Prompt)
```cmd
# Set proxy
set YFINANCE_PROXY=http://127.0.0.1:10808

# Run backtest
python backtest_historical.py
```

### Linux/Mac (Bash)
```bash
# Set proxy for current session
export YFINANCE_PROXY=http://127.0.0.1:10808

# Run backtest
python backtest_historical.py

# Clear proxy (optional)
unset YFINANCE_PROXY
```

## Proxy Configuration

Replace `127.0.0.1:10808` with your actual proxy address and port:
- **HTTP Proxy**: `http://host:port`
- **HTTPS Proxy**: `https://host:port`
- **Authenticated**: `http://user:pass@host:port`

## Important Notes

The backtest script **requires internet connection** to download data from Yahoo Finance API using yfinance. Make sure:
- You have a stable internet connection
- Yahoo Finance is accessible from your network
- If behind a firewall/VPN, configure the proxy as shown above

## Troubleshooting

### Issue: "Too Many Requests" error
**Solution**: Set up a proxy or wait a few minutes for the rate limit to reset.

### Issue: Proxy connection timeout
**Solution**: 
1. Check if your proxy is running
2. Verify the proxy address and port
3. Test proxy with: `curl -x http://127.0.0.1:10808 https://finance.yahoo.com`

### Issue: Data download still fails
**Solution**: 
1. Verify internet connection
2. Check if Yahoo Finance is accessible: visit https://finance.yahoo.com
3. Try using a proxy if behind a firewall
4. Check yfinance version: `pip install --upgrade yfinance`

## Notes

- The environment variable only needs to be set when you want to use a proxy
- Most users won't need this - yfinance works directly without proxy
- The proxy setting only affects the current terminal session
- **Internet connection is required** - the script downloads live data from Yahoo Finance
- Data is downloaded fresh each time the backtest runs (ensures up-to-date market data)
