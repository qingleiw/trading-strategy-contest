"""
Parameter Optimization Database
Tracks all backtest runs with different parameter combinations
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os

class OptimizationDB:
    def __init__(self, db_path: str = "optimization_results.db"):
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # Main results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                
                -- Strategy Parameters
                max_position_size REAL,
                stop_loss_pct REAL,
                take_profit_pct REAL,
                rsi_oversold INTEGER,
                rsi_overbought INTEGER,
                min_time_between_trades INTEGER,
                max_drawdown_limit REAL,
                rsi_period INTEGER,
                macd_fast INTEGER,
                macd_slow INTEGER,
                macd_signal INTEGER,
                bb_period INTEGER,
                bb_std_dev REAL,
                
                -- BTC Results
                btc_return REAL,
                btc_drawdown REAL,
                btc_trades INTEGER,
                btc_win_rate REAL,
                btc_final_value REAL,
                
                -- ETH Results
                eth_return REAL,
                eth_drawdown REAL,
                eth_trades INTEGER,
                eth_win_rate REAL,
                eth_final_value REAL,
                
                -- Combined Results
                combined_return REAL,
                avg_drawdown REAL,
                total_trades INTEGER,
                
                -- Scoring
                score REAL,
                meets_requirements BOOLEAN,
                notes TEXT
            )
        """)
        
        # Index for quick lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_score ON backtest_results(score DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_return ON backtest_results(combined_return DESC)
        """)
        
        self.conn.commit()
    
    def calculate_score(self, combined_return: float, avg_drawdown: float, 
                       total_trades: int) -> float:
        """
        Calculate overall score for parameter combination
        Higher score = better performance
        
        Scoring factors:
        - Return (weighted 60%)
        - Low drawdown (weighted 30%)  
        - Trade count in reasonable range (weighted 10%)
        """
        # Return score (0-60 points)
        return_score = min(combined_return * 2, 60)  # 30% return = 60 points
        
        # Drawdown score (0-30 points) - lower is better
        drawdown_score = max(0, 30 - avg_drawdown * 3)  # 10% drawdown = 0 points
        
        # Trade count score (0-10 points) - optimal range 50-200 trades
        if 50 <= total_trades <= 200:
            trade_score = 10
        elif 20 <= total_trades < 50:
            trade_score = 5 + (total_trades - 20) / 30 * 5
        elif 200 < total_trades <= 400:
            trade_score = 10 - (total_trades - 200) / 200 * 5
        else:
            trade_score = 0
        
        return return_score + drawdown_score + trade_score
    
    def save_result(self, config: Dict, btc_results: Dict, eth_results: Dict, 
                   combined_results: Dict, notes: str = "") -> int:
        """Save backtest result to database"""
        cursor = self.conn.cursor()
        
        combined_return = combined_results['return']
        avg_drawdown = combined_results['avg_drawdown']
        total_trades = combined_results['total_trades']
        
        score = self.calculate_score(combined_return, avg_drawdown, total_trades)
        
        # Check if meets contest requirements
        meets_requirements = (
            combined_return > 30 and 
            avg_drawdown < 50 and 
            total_trades >= 10
        )
        
        cursor.execute("""
            INSERT INTO backtest_results (
                timestamp,
                max_position_size, stop_loss_pct, take_profit_pct,
                rsi_oversold, rsi_overbought, min_time_between_trades,
                max_drawdown_limit, rsi_period, macd_fast, macd_slow,
                macd_signal, bb_period, bb_std_dev,
                btc_return, btc_drawdown, btc_trades, btc_win_rate, btc_final_value,
                eth_return, eth_drawdown, eth_trades, eth_win_rate, eth_final_value,
                combined_return, avg_drawdown, total_trades,
                score, meets_requirements, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            config.get('max_position_size'), config.get('stop_loss_pct'), 
            config.get('take_profit_pct'), config.get('rsi_oversold'),
            config.get('rsi_overbought'), config.get('min_time_between_trades'),
            config.get('max_drawdown_limit'), config.get('rsi_period'),
            config.get('macd_fast'), config.get('macd_slow'), config.get('macd_signal'),
            config.get('bb_period'), config.get('bb_std_dev'),
            btc_results['return'], btc_results['drawdown'], btc_results['trades'],
            btc_results['win_rate'], btc_results['final_value'],
            eth_results['return'], eth_results['drawdown'], eth_results['trades'],
            eth_results['win_rate'], eth_results['final_value'],
            combined_return, avg_drawdown, total_trades,
            score, meets_requirements, notes
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_top_results(self, limit: int = 10, 
                       require_contest_criteria: bool = False) -> List[Dict]:
        """Get top performing parameter combinations"""
        cursor = self.conn.cursor()
        
        query = """
            SELECT * FROM backtest_results
            {}
            ORDER BY score DESC
            LIMIT ?
        """.format("WHERE meets_requirements = 1" if require_contest_criteria else "")
        
        cursor.execute(query, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results
    
    def get_best_by_return(self, limit: int = 10) -> List[Dict]:
        """Get results sorted by return"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM backtest_results
            ORDER BY combined_return DESC
            LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_parameter_statistics(self, parameter: str) -> Dict:
        """Analyze how a specific parameter affects results"""
        cursor = self.conn.cursor()
        cursor.execute(f"""
            SELECT 
                {parameter},
                AVG(combined_return) as avg_return,
                AVG(avg_drawdown) as avg_drawdown,
                AVG(score) as avg_score,
                COUNT(*) as count
            FROM backtest_results
            GROUP BY {parameter}
            ORDER BY avg_score DESC
        """)
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def parameter_exists(self, config: Dict) -> Optional[int]:
        """Check if this exact parameter combination was already tested"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id FROM backtest_results
            WHERE 
                max_position_size = ? AND
                stop_loss_pct = ? AND
                take_profit_pct = ? AND
                rsi_oversold = ? AND
                rsi_overbought = ? AND
                min_time_between_trades = ?
            LIMIT 1
        """, (
            config.get('max_position_size'),
            config.get('stop_loss_pct'),
            config.get('take_profit_pct'),
            config.get('rsi_oversold'),
            config.get('rsi_overbought'),
            config.get('min_time_between_trades')
        ))
        
        result = cursor.fetchone()
        return result[0] if result else None
    
    def export_to_csv(self, filepath: str = "optimization_results.csv"):
        """Export all results to CSV for analysis"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM backtest_results ORDER BY score DESC")
        
        import csv
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow([desc[0] for desc in cursor.description])
            # Write data
            writer.writerows(cursor.fetchall())
        
        print(f"✅ Exported to {filepath}")
    
    def print_summary(self):
        """Print database summary"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM backtest_results")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM backtest_results WHERE meets_requirements = 1")
        meeting_req = cursor.fetchone()[0]
        
        cursor.execute("SELECT MAX(combined_return), MAX(score) FROM backtest_results")
        max_return, max_score = cursor.fetchone()
        
        print("=" * 70)
        print("OPTIMIZATION DATABASE SUMMARY")
        print("=" * 70)
        print(f"Total test runs: {total}")
        print(f"Meeting contest requirements: {meeting_req}")
        print(f"Best return: {max_return:.2f}%" if max_return else "Best return: N/A")
        print(f"Best score: {max_score:.2f}" if max_score else "Best score: N/A")
        print("=" * 70)
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    # Test the database
    with OptimizationDB() as db:
        db.print_summary()
