from __future__ import annotations
import json
import sqlite3
from datetime import datetime
from app.config import config as con
from features.engineering.domain.entities.engineering import Engineering

entities = Engineering

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
                if ann is datetime:
                    if isinstance(v, str) and v.startswith('"') and v.endswith('"'):
                        v = v.strip('"')
                    v = datetime.fromisoformat(v)
                elif ann is dict:
                    v = json.loads(v)
                kwargs[f] = v
            results.append(self.entity(**kwargs))
        return results
