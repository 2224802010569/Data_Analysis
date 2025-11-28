from features.label.service.sql_service import SQLService
from features.label.domain.entities.label import Label

class LoadUseCase:
    def __init__(self):
        self.sql = SQLService()
    
    def load(self,timeframe: str = "1M") -> list[Label]:
        return self.sql.load(timeframe)