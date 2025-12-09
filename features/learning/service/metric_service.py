from datetime import datetime
import json
from pathlib import Path
from typing import List, Optional
from app.config import config as con


class MetricService:
    def __init__(self):
        self.base_path = Path(con.LEARNING_DIR)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.total_metrics_path = self.base_path / "metrics_total.json"

    def create_metrics(self, history_obj, module_id: str) -> dict:
        acc = float(history_obj.history["accuracy"][-1])
        loss = float(history_obj.history["loss"][-1])
        return {
            "module_id": module_id,
            "accuracy": acc,
            "loss": loss,
            "timestamp": datetime.now().isoformat()
        }

    def create_history(self, history_obj, config, module_id: str) -> dict:
        return {
            "module_id": module_id,
            "epochs": len(history_obj.history["loss"]),
            "loss": history_obj.history["loss"],
            "accuracy": history_obj.history.get("accuracy", []),
            "feature_cols": config.feature_cols,
            "window_size": config.window_size,
            "note": config.note
        }

    def _load_total_metrics_raw(self) -> List[dict]:
        if not self.total_metrics_path.exists():
            return []
        try:
            with open(self.total_metrics_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                # If file malformed, return empty list
                return []
        except Exception:
            return []

    def load_total_metrics(self) -> List[dict]:
        return self._load_total_metrics_raw()

    def append_total_metrics(self, module_id: str, accuracy: float, timeframe: str):
        data = self._load_total_metrics_raw()
        entry = {
            "module_id": module_id,
            "accuracy": float(accuracy),
        }
        data.append(entry)
        with open(self.total_metrics_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def get_best_module(self, timeframe: Optional[str] = None) -> Optional[str]:
        data = self._load_total_metrics_raw()
        if not data:
            return None
        if timeframe is not None:
            data = [d for d in data if str(d.get("timeframe")) == str(timeframe)]
            if not data:
                return None
        best = max(data, key=lambda x: x.get("accuracy", -1))
        return best.get("module_id")
