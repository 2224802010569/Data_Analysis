from datetime import datetime
from typing import List
from features.engineering.domain.entities.engineering import Engineering
from features.engineering.service.sql_service import SQLService
from app.config import config as con

class LoadUseCase:
    def __init__(self):
        self.sql = SQLService()
        self.path = con.STORAGE_DIR
    
    def load(self,timerange:list[datetime, datetime], timeframe: str = "1M") -> List[Engineering]:
        return self.sql.load(timerange, timeframe)