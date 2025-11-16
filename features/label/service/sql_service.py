import sqlite3
import json
from discord import datetime
from app.config import config as con
from features.label.domain.entities.window import Window

class SQLService:

    def __init__(self):
        self.db_path = con.STORAGE_DIR
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_table()

    def _ensure_table(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS label (
                timeframe TEXT,
                t0: TEXT,
                t1: TEXT,
                class_label INTEGER,
                extra TEXT,
            )
            """)

    def save(self, window: list[Window]):
        if not window: return
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany("""
            INSERT OR IGNORE INTO label (timeframe, t0, t1, class_label, extra)
            VALUES (?, ?, ?, ?, ?)
            """, [(w.timestamp.isoformat(), w.t0, w.t1, w.class_label, json.dumps(w.extra)) for w in window])

    def load(self,timerange:list[datetime, datetime] , timeframe: str = "1M") -> list[Window]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT timestamp, open, high, low, close, volume, timeframe\
                FROM label \
                WHERE timeframe = ?", (timeframe,))
        rows = cur.fetchall()
        conn.close()

        db = [
            Window(
                timestamp=datetime.fromtimestamp(ts / 1000) if isinstance(ts, (int, float)) else ts,
                open=o, high=h, low=l, close=c, volume=v, timeframe=tf
            )
            for ts, o, h, l, c, v, tf in rows
        ]
        return db
