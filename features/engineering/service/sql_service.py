from __future__ import annotations
import json
import sqlite3
from datetime import datetime
import pandas as pd  # <--- Thêm dòng này
from dataclasses import asdict # <--- Thêm dòng này
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
                if isinstance(v, dict) or hasattr(v, '__dataclass_fields__'):
                    # Tự động convert dict hoặc dataclass thành chuỗi JSON để lưu
                    if hasattr(v, '__dataclass_fields__'):
                        v = asdict(v)
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
                # Lưu ý: Vì có import future annotations, logic check type có thể cần điều chỉnh
                # ở đây mình giữ nguyên logic cũ của bạn, chỉ bổ sung try-catch cho json
                if "datetime" in str(ann):
                    if isinstance(v, str) and v.startswith('"') and v.endswith('"'):
                        v = v.strip('"')
                    try:
                        v = datetime.fromisoformat(v)
                    except:
                        pass
                elif "dict" in str(ann) or "Values" in str(ann):
                    try:
                        v = json.loads(v)
                        # Nếu class đích cần object (IndicatorValues), code này trả về dict
                        # Engineering sẽ nhận dict và hoạt động bình thường nếu là TypedDict
                    except:
                        pass
                kwargs[f] = v
            results.append(self.entity(**kwargs))
        return results

    # --- HÀM MỚI THÊM ---
    def get_all_as_df(self, timeframe: str = "1M") -> pd.DataFrame:
        """Load dữ liệu và chuyển đổi sang DataFrame phẳng cho Machine Learning"""
        items = self.load(timeframe)
        if not items:
            return pd.DataFrame()
        
        flat_data = []
        for item in items:
            row = {
                "timestamp": item.timestamp,
                "timeframe": item.timeframe
            }
            # Phẳng hóa (Flatten) Indicator
            if isinstance(item.indicator, dict):
                row.update(item.indicator)
            
            # Phẳng hóa Temporal (nếu là dataclass thì dùng asdict, nếu dict thì update luôn)
            if hasattr(item.temporal, '__dataclass_fields__'):
                row.update(asdict(item.temporal))
            elif isinstance(item.temporal, dict):
                row.update(item.temporal)
                
            flat_data.append(row)
            
        return pd.DataFrame(flat_data)