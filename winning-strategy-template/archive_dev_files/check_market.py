#!/usr/bin/env python3
"""Simple Buy and Hold test to see market performance"""

# BTC: Jan $42k -> Jun $62k = +47.6%
# ETH: Jan $2.3k -> Jun $3.4k = +47.8%

btc_start = 42000
btc_end = 62000
btc_return = ((btc_end - btc_start) / btc_start) * 100

eth_start = 2300
eth_end = 3400
eth_return = ((eth_end - eth_start) / eth_start) * 100

print(f"BTC Buy & Hold: {btc_return:+.2f}%")
print(f"ETH Buy & Hold: {eth_return:+.2f}%")
print(f"Average: {(btc_return + eth_return) / 2:+.2f}%")
