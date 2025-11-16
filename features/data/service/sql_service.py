import datetime
import sqlite3
from app.config import config as con
from features.data.domain.entities.candle import Candle

class SQLService:
    def __init__(self):
        self.db_path = con.STORAGE_DIR
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_table()

    def _ensure_table(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS candle (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                timeframe TEXT,
                timestamp DATETIME,
                open REAL, high REAL, low REAL, close REAL, volume REAL,
                UNIQUE(symbol, timeframe, timestamp)
            )""")

    def get_last_timestamp(self, symbol, tf):
        query = "SELECT MAX(timestamp) FROM candle WHERE symbol=? AND timeframe=?"
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(query, (symbol, tf)).fetchone()
            return row[0] if row and row[0] else None

    def save(self, tf, candles: list[Candle]):
        if not candles: return
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany("""
            INSERT OR IGNORE INTO candle(symbol, timeframe, timestamp, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [(con.SYMBOL, tf, c.timestamp, c.open, c.high, c.low, c.close, c.volume) for c in candles])

    def load(self, timeframe: str = "1M") -> list[Candle]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT timestamp, open, high, low, close, volume, timeframe\
                FROM candle \
                WHERE timeframe = ?", (timeframe,))
        rows = cur.fetchall()
        conn.close()

        db = [
            Candle(
                timestamp=datetime.fromtimestamp(ts / 1000) if isinstance(ts, (int, float)) else ts,
                open=o, high=h, low=l, close=c, volume=v, timeframe=tf
            )
            for ts, o, h, l, c, v, tf in rows
        ]
        print(f"✅ Loaded {len(db)} rows from SQLite ({timeframe})")
        return db