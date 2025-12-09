import json
import os
from app.config import config as con

class HistoryService:

    def __init__(self):
        self.base_path = con.LEARNING_DIR

    def load_history(self, module_id: str):
        file_path = os.path.join(self.base_path, module_id, "history.json")
        if not os.path.exists(file_path):
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_history(self, module_id: str, history: dict):
        folder = os.path.join(self.base_path, module_id)
        os.makedirs(folder, exist_ok=True)

        file_path = os.path.join(folder, "history.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)

    def load_best_module(self, timeframe: str):
        best_module = None
        best_acc = -1
        for module_id in os.listdir(self.base_path):
            metrics_path = os.path.join(self.base_path, module_id, "metrics.json")
            if not os.path.exists(metrics_path):
                continue
            try:
                with open(metrics_path, "r") as f:
                    m = json.load(f)
                if str(m.get("timeframe")) != str(timeframe):
                    continue
                if m["accuracy"] > best_acc:
                    best_acc = m["accuracy"]
                    best_module = module_id
            except Exception:
                continue
        return best_module
