from datetime import datetime
import sqlite3
import json
from app.config import config as con
from features.engineering.domain.entities.engineering import Engineering


class SQLService:

    def __init__(self):
        self.db_path = con.STORAGE_DIR
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_table()

    def _ensure_table(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS engineering (
                timestamp TEXT,
                timeframe TEXT,
                indicator_json TEXT,
                temporal_json TEXT
            );
            """)

    def save(self, entities: list[Engineering]):
        if not entities: return
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany("""
            INSERT INTO engineering (timestamp, timeframe, indicator_json, temporal_json)
            VALUES (?, ?, ?, ?)
            """,[(
                e.timestamp.isoformat(), 
                e.timeframe, 
                json.dumps(e.indicator), 
                json.dumps(e.temporal)
                ) 
                for e in entities])

    def load(self, timeframe: str = "1M") -> list[Engineering]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * \
                FROM engineering \
                WHERE timeframe=?", (timeframe,))
        rows = cur.fetchall()
        conn.close()
        db = [
            Engineering(
                timestamp=datetime.fromtimestamp(ts / 1000) if isinstance(ts, (int, float)) else ts,
                timeframe=tf,
                indicator=json.loads(ind_json),
                temporal=json.loads(temp_json)
            )
            for ts, tf, ind_json, temp_json in rows
        ]
        return db
