"""Database utility for ROBOAi"""

import sqlite3
import aiosqlite
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import json


class Database:
    """SQLite database manager"""
    
    def __init__(self, db_path: str = "data/roboai.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.connection: Optional[sqlite3.Connection] = None
        self._create_tables()
    
    def connect(self) -> sqlite3.Connection:
        """Create database connection"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def _create_tables(self) -> None:
        """Create database tables if they don't exist"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE NOT NULL,
                symbol TEXT NOT NULL,
                segment TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                entry_time TEXT NOT NULL,
                exit_time TEXT,
                pnl REAL,
                status TEXT NOT NULL,
                strategy TEXT,
                reason TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE NOT NULL,
                trade_id TEXT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                order_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL,
                status TEXT NOT NULL,
                filled_quantity INTEGER DEFAULT 0,
                filled_price REAL,
                placed_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (trade_id) REFERENCES trades(trade_id)
            )
        ''')
        
        # Positions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                avg_price REAL NOT NULL,
                current_price REAL,
                pnl REAL,
                status TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Market data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                ltp REAL,
                metadata TEXT
            )
        ''')
        
        # Sentiment data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sentiment_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                sentiment_score REAL,
                sentiment_label TEXT,
                sources TEXT,
                reasoning TEXT,
                metadata TEXT
            )
        ''')
        
        # RCA logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rca_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT NOT NULL,
                analysis TEXT NOT NULL,
                recommendations TEXT,
                adjustments TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (trade_id) REFERENCES trades(trade_id)
            )
        ''')
        
        # Configuration history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parameter TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                reason TEXT,
                changed_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
    
    def insert_trade(self, trade_data: Dict[str, Any]) -> int:
        """Insert a new trade"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (
                trade_id, symbol, segment, side, quantity, entry_price,
                entry_time, status, strategy, reason, metadata, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade_data['trade_id'],
            trade_data['symbol'],
            trade_data.get('segment', 'EQ'),
            trade_data['side'],
            trade_data['quantity'],
            trade_data['entry_price'],
            trade_data['entry_time'],
            trade_data.get('status', 'OPEN'),
            trade_data.get('strategy'),
            trade_data.get('reason'),
            json.dumps(trade_data.get('metadata', {})),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def update_trade(self, trade_id: str, updates: Dict[str, Any]) -> None:
        """Update an existing trade"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Build dynamic update query
        set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values()) + [trade_id]
        
        cursor.execute(f'''
            UPDATE trades SET {set_clause} WHERE trade_id = ?
        ''', values)
        
        conn.commit()
    
    def get_trades(self, status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get trades, optionally filtered by status"""
        conn = self.connect()
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT * FROM trades WHERE status = ? ORDER BY created_at DESC LIMIT ?
            ''', (status, limit))
        else:
            cursor.execute('''
                SELECT * FROM trades ORDER BY created_at DESC LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def insert_order(self, order_data: Dict[str, Any]) -> int:
        """Insert a new order"""
        conn = self.connect()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO orders (
                order_id, trade_id, symbol, side, order_type, quantity,
                price, status, placed_at, updated_at, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_data['order_id'],
            order_data.get('trade_id'),
            order_data['symbol'],
            order_data['side'],
            order_data['order_type'],
            order_data['quantity'],
            order_data.get('price'),
            order_data.get('status', 'PENDING'),
            now,
            now,
            json.dumps(order_data.get('metadata', {}))
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def insert_market_data(self, symbol: str, data: Dict[str, Any]) -> int:
        """Insert market data"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO market_data (
                symbol, timestamp, open, high, low, close, volume, ltp, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            symbol,
            data.get('timestamp', datetime.now().isoformat()),
            data.get('open'),
            data.get('high'),
            data.get('low'),
            data.get('close'),
            data.get('volume'),
            data.get('ltp'),
            json.dumps(data.get('metadata', {}))
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def insert_rca_log(self, trade_id: str, analysis: Dict[str, Any]) -> int:
        """Insert RCA analysis log"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO rca_logs (
                trade_id, analysis, recommendations, adjustments, created_at
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            trade_id,
            json.dumps(analysis.get('analysis', {})),
            json.dumps(analysis.get('recommendations', [])),
            json.dumps(analysis.get('adjustments', [])),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def get_pnl_summary(self) -> Dict[str, Any]:
        """Get PnL summary"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                SUM(pnl) as total_pnl,
                AVG(pnl) as avg_pnl,
                MAX(pnl) as max_profit,
                MIN(pnl) as max_loss
            FROM trades
            WHERE status = 'CLOSED' AND pnl IS NOT NULL
        ''')
        
        row = cursor.fetchone()
        return dict(row) if row else {}
    
    def close(self) -> None:
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Global database instance
_database: Optional[Database] = None


def get_database(db_path: str = "data/roboai.db") -> Database:
    """Get or create global database instance"""
    global _database
    if _database is None:
        _database = Database(db_path)
    return _database
