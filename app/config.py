# backend/app/config.py
from pathlib import Path
from datetime import datetime

class Config:
    # ===== Project Paths =====
    BASE_DIR = Path(__file__).resolve().parents[1]
    STORAGE_DIR = BASE_DIR/ "features" / "data" / "domain" / "storage" / "data.db"
    LEARNING_DIR = BASE_DIR/ "features" / "learning"/ "domain" / "storage"

    # ===== Data Source =====
    EXCHANGE = "binance"       # For ccxt
    SYMBOL = "BTC/USDT"        # Bitcoin
    TIMEFRAMES = ["1h", "1d", "1M"]

    # ===== Time Range =====
    START_DATE = datetime(2017, 1, 1)
    END_DATE = datetime(2025, 1, 1)
    START_FORE = datetime(2025, 1, 1)
    END_FORE = datetime(2027, 1, 1)

    # ===== API =====
    API_TIMEOUT = 10           # seconds
    CSV_ENCODING = "utf-8"
    AUTO_CREATE_DIRS = True

    # ===== Learning =====
    NUMBER_MODULE_EACH_RUN = 5
    EPOCHS = 5
    BATCH_SIZE = 256
    FORECAST_HORIZON = {
        "1h": 24,
        "1d": 30,
        "1M": 12,
    }


    # ===== Misc =====
    DEBUG = True


config = Config()
