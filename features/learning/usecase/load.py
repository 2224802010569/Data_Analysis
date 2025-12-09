from features.learning.service.storage_service import StorageService
from features.learning.service.history_service import HistoryService

class LoadUseCase:

    def __init__(self):
        self.history_service = HistoryService()
        self.storage_service = StorageService()

    def load(self):
        history = self.history_service.load_global_history()
        best_module_id = history.get("best_module")
        if not best_module_id:
            return None
        module_entity = self.storage_service.load_model(best_module_id)
        return best_module_id, module_entity
