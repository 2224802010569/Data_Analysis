from app.config import config
from features.label.service.sql_service import SQLService
from features.learning.service.storage_service import StorageService
class FetchAndSaveUseCase:
    def __init__(self):
        self.sql = SQLService()

    def execute(self):
        pass
