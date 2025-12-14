import json
from pathlib import Path
from app.config import config as con


class HistoryService:

    def __init__(self):
        self.base_dir = con.LEARNING_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.base_dir / "history.json"

    def load(self) -> dict:
        if not self.history_path.exists():
            return {"by_timeframe": {}, "stable": []}
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                data.setdefault("by_timeframe", {})
                data.setdefault("stable", [])
                return data
        except Exception:
            return {"by_timeframe": {}, "stable": []}

    def save(self, history: dict) -> None:
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)

    def update_timeframe(
        self,
        timeframe: str,
        module,
        accuracy: float,
    ) -> None:
        history = self.load()
        history["by_timeframe"][timeframe] = {
            "module_id": module.module_id,
            "accuracy": float(accuracy),
            "module": module.to_dict(),
        }
        self.save(history)

    def update_stable_modules(self, stable_modules: list):
        history = self.load()
        history["stable"] = [
            {
                "module_id": m["module_id"],
                "stability": float(m["stability"]),
                "module": m["module"],
            }
            for m in stable_modules
        ]
        self.save(history)

    def get_stable_modules(self) -> list:
        history = self.load()
        return history.get("stable", [])

    def remove_timeframe(self, timeframe: str) -> None:
        history = self.load()
        history["by_timeframe"].pop(timeframe, None)
        self.save(history)

    def get_all_modules(self) -> list:
        history = self.load()
        seen = {}
        for tf, entry in history["by_timeframe"].items():
            mid = entry["module_id"]
            if mid not in seen:
                seen[mid] = entry["module"]
        return list(seen.values())
    
    def append(self, module, metrics_by_timeframe: dict) -> None:
        entry = {
            "module_id": module.module_id,
            "metrics": {
                tf: {"accuracy": float(m["accuracy"])}
                for tf, m in metrics_by_timeframe.items()
            },
            "module": module.to_dict()
        }
        data = self.load()
        data.append(entry)
        self.save(data)

    def get_next_module_id(self) -> str:
        history = self.load()
        if not history:
            return "00000"
        ids = []
        for h in history:
            try:
                ids.append(int(h["module_id"]))
            except Exception:
                continue
        if not ids:
            return "00000"
        next_id = max(ids) + 1
        return f"{next_id:05d}"
    
    def _get_best_module_id(self, timeframe: str) -> str | None:
        return (
            self.load()
            .get("by_timeframe", {})
            .get(timeframe, {})
            .get("module_id")
        )
