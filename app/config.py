# backend/app/config.py
from pathlib import Path
from datetime import datetime

class Config:
    # ===== Project Paths =====
    BASE_DIR = Path(__file__).resolve().parents[1]
    DATA_DIR = BASE_DIR/ "features" / "data"
    STORAGE_DIR = DATA_DIR / "domain" / "storage" / "data.db"

    # ===== Data Source =====
    EXCHANGE = "binance"       # For ccxt
    SYMBOL = "BTC/USDT"        # Bitcoin
    TIMEFRAMES = ["1h", "1d", "1M"]

    # ===== Time Range =====
    START_DATE = datetime(2017, 1, 1)
    END_DATE = datetime(2024, 1, 1)

    # ===== API and Storage =====
    API_TIMEOUT = 10           # seconds
    CSV_ENCODING = "utf-8"
    AUTO_CREATE_DIRS = True

    # ===== Misc =====
    DEBUG = True


config = Config()
