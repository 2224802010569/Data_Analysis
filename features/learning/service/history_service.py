import json
from pathlib import Path
from app.config import config as con

class HistoryService:

    def __init__(self):
        self.base_path = Path(con.LEARNING_DIR)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.global_history_path = self.base_path / "history.json"

    def save_history(self, module_id: str, history: dict):
        module_dir = self.base_path / module_id
        module_dir.mkdir(parents=True, exist_ok=True)
        history_path = module_dir / "history.json"
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)

    def load_history(self, module_id: str):
        history_path = self.base_path / module_id / "history.json"
        if not history_path.exists():
            return None
        with open(history_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_global_history(self) -> dict:
        if not self.global_history_path.exists():
            return {
                "timeline": [],
                "meta_pool": [],
                "best_module": None,
                "train_counter": 0
            }
        with open(self.global_history_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_global_history(self, data: dict):
        with open(self.global_history_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def append_history_item(self, module_id: str, accuracy: float, config: dict):
        data = self.load_global_history()

        entry = {
            "train_index": data["train_counter"] + 1,
            "module_id": module_id,
            "accuracy": accuracy,
            "config": config
        }
        data["timeline"].append(entry)
        data["train_counter"] += 1
        self.save_global_history(data)

    def update_best(self):
        data = self.load_global_history()
        if not data["timeline"]:
            return
        best = max(data["timeline"], key=lambda x: x["accuracy"])
        data["best_module"] = best["module_id"]
        self.save_global_history(data)

    def config_diversity(self, cfg1, cfg2) -> float:
        score = 0
        score += abs(cfg1["window_size"] - cfg2["window_size"]) / 50.0
        if cfg1["seed"] != cfg2["seed"]:
            score += 0.2
        s1, s2 = set(cfg1["feature_cols"]), set(cfg2["feature_cols"])
        jaccard = 1 - (len(s1 & s2) / len(s1 | s2))
        score += jaccard * 0.5
        return score

    def compute_score(self, item, timeline, train_counter) -> float:
        accuracy = item["accuracy"]
        recency = item["train_index"] / train_counter
        div_sum = 0
        for other in timeline:
            if other["module_id"] == item["module_id"]:
                continue
            div_sum += self.config_diversity(item["config"], other["config"])
        diversity = div_sum / max(len(timeline) - 1, 1)
        return 0.6*accuracy + 0.25*diversity + 0.15*recency
    
    def update_meta_pool(self):
        data = self.load_global_history()
        timeline = data["timeline"]
        counter = data["train_counter"]
        if not timeline:
            return
        scored = [(self.compute_score(it, timeline, counter), it) for it in timeline]
        scored.sort(key=lambda x: x[0], reverse=True)
        pool = [it for score, it in scored[:5]]
        data["meta_pool"] = pool
        self.save_global_history(data)
