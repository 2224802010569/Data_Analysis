from typing import List
from features.data.domain.entities.candle import Candle
from features.data.service.csv_service import CSVService
from features.data.service.sql_service import SQLService
from app.config import config as con

class LoadUseCase:
    def __init__(self):
        self.csv = CSVService()
        self.sql = SQLService()
        self.path = con.STORAGE_DIR
    
    def load(self, type: str ="sql", timeframe: str = "1M") -> List[Candle]:
        match type:
            case "sql":
                return self.sql.load(timeframe)
            case "csv":
                return self.csv.load(timeframe)
            case _:  
                raise ValueError(f"Unknown load type: {type}")  