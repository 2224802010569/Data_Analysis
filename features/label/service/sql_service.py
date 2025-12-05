from __future__ import annotations
import json
import sqlite3
from datetime import datetime
import pandas as pd # <--- Thêm dòng này
from app.config import config as con
from features.label.domain.entities.label import Label

entities = Label

class SQLService:

    def __init__(self):
        self.entity = entities
        self.table = self.entity.__name__.lower()
        self.db_path = con.STORAGE_DIR
        self.fields = list(self.entity.__annotations__.keys())
        self._ensure_table()

    def schema(self):
        cols = []
        for name, typ in self.entity.__annotations__.items():
            if typ is str:
                sql = "TEXT"
            elif typ is int:
                sql = "INTEGER"
            elif typ is float:
                sql = "REAL"
            elif typ is datetime:
                sql = "TEXT"
            else:
                sql = "TEXT"
            cols.append(f"{name} {sql}")
        return ", ".join(cols)

    def _ensure_table(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f"CREATE TABLE IF NOT EXISTS {self.table} ({self.schema()})")

    def save(self, items: list[entities]):
        if not items:
            return
        rows = []
        for it in items:
            row = []
            for f in self.fields:
                v = getattr(it, f)
                if isinstance(v, datetime):
                    v = json.dumps(v.isoformat())
                if isinstance(v, dict):
                    v = json.dumps(v)
                row.append(v)
            rows.append(tuple(row))
        placeholders = ",".join(["?"] * len(self.fields))
        columns = ",".join(self.fields)
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})",
                rows
            )

    def load(self, timeframe: str = "1M") -> list[entities]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                f"SELECT * FROM {self.table} WHERE timeframe = ?",
                (timeframe,)
            )
            rows = cur.fetchall()
        results = []
        for row in rows:
            kwargs = {}
            for idx, f in enumerate(self.fields):
                v = row[idx]
                ann = self.entity.__annotations__[f]
                # Logic check type đơn giản hóa
                if "datetime" in str(ann):
                    if isinstance(v, str) and v.startswith('"') and v.endswith('"'):
                        v = v.strip('"')
                    try:
                        v = datetime.fromisoformat(v)
                    except:
                        pass
                elif "dict" in str(ann):
                    try:
                        v = json.loads(v)
                    except:
                        pass
                kwargs[f] = v
            results.append(self.entity(**kwargs))
        return results

    # --- HÀM MỚI THÊM ---
    def get_all_as_df(self, timeframe: str = "1M") -> pd.DataFrame:
        """Load label và chuyển về DataFrame chuẩn"""
        items = self.load(timeframe)
        if not items:
            return pd.DataFrame()
        
        data = []
        for item in items:
            data.append({
                "timestamp": item.t0,  # Map t0 thành timestamp để khớp với Engineering
                "label": item.label,
                "timeframe": item.timeframe
            })
        
        return pd.DataFrame(data)