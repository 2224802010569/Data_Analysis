from features.learning.service.sql_service import SQLService
from features.learning.domain.entities.module import Module

class LoadUseCase:
    def __init__(self):
        self.sql = SQLService()
    
    def load(self, module_id: str ) -> Module:
        return self.sql.load(module_id=module_id)[0]
    
    def load_best(self) -> Module:
        pass