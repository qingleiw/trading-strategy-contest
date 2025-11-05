from optimization_db import OptimizationDB

db = OptimizationDB()
cursor = db.conn.cursor()

print("Searching for configurations with 30%+ combined return...")
cursor.execute("""
    SELECT combined_return, btc_return, eth_return, 
           max_position_size, take_profit_pct, min_time_between_trades 
    FROM backtest_results 
    WHERE combined_return >= 30.0 
    ORDER BY combined_return DESC 
    LIMIT 5
""")

results = cursor.fetchall()
print(f"\nFound {len(results)} results with 30%+ combined return")

if results:
    for r in results:
        print(f"\nCombined: {r[0]:.2f}%, BTC: {r[1]:.2f}%, ETH: {r[2]:.2f}%")
        print(f"  Position: {r[3]}, TP: {r[4]}%, Interval: {r[5]}min")
else:
    print("\n❌ No configurations found with 30%+ combined return yet!")
    print("\nTop 5 results:")
    cursor.execute("""
        SELECT combined_return, btc_return, eth_return, 
               max_position_size, stop_loss_pct, take_profit_pct, 
               rsi_oversold, rsi_overbought, min_time_between_trades 
        FROM backtest_results 
        ORDER BY combined_return DESC 
        LIMIT 5
    """)
    top_results = cursor.fetchall()
    for i, r in enumerate(top_results, 1):
        print(f"\n#{i} Combined: {r[0]:.2f}%, BTC: {r[1]:.2f}%, ETH: {r[2]:.2f}%")
        print(f"   Pos: {r[3]}, Stop: {r[4]}%, TP: {r[5]}%")
        print(f"   RSI: {r[6]}/{r[7]}, Interval: {r[8]}min")

db.close()
