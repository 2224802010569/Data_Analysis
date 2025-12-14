from typing import List
from features.engineering.domain.entities.engineering import Engineering
from features.engineering.service.sql_service import SQLService
from app.config import config as con

class LoadUseCase:
    def __init__(self, e):
        self.sql = SQLService(e)
        self.path = con.STORAGE_DIR
    
    def load(self, timeframe: str = "1M") -> list[Engineering]:
        return self.sql.load(timeframe)