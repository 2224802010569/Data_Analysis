from features.learning.service.history_service import HistoryService
from features.learning.service.storage_service import StorageService

class MetaService:

    def __init__(self):
        self.history_service = HistoryService()

    def suggest_from_history(self) -> dict | None:
        history = self.history_service.load()
        if not history:
            return None
        by_tf = history.get("by_timeframe", {})
        if not by_tf:
            return None
        scores = {}
        used_ids = set()
        for tf, h in by_tf.items():
            module = h.get("module")
            acc = h.get("accuracy", 0)
            mid = h.get("module_id")
            if not module or not mid:
                continue
            used_ids.add(mid)
            if mid not in scores:
                scores[mid] = {
                    "module": module,
                    "accs": [],
                }
            scores[mid]["accs"].append(acc)
        if not scores:
            return None
        ranked = []
        for mid, v in scores.items():
            accs = v["accs"]
            avg_acc = sum(accs) / len(accs)
            ranked.append((avg_acc, mid, v["module"]))
        ranked.sort(key=lambda x: x[0], reverse=True)
        nums = []
        for mid in used_ids:
            if mid.isdigit():
                nums.append(int(mid))
        next_id = max(nums) + 1 if nums else 0
        if next_id > 99999:
            raise ValueError("module_id overflow (>99999)")
        new_module_id = f"{next_id:05d}"
        best_module = ranked[0][2]
        return {
            "module_id": new_module_id,
            **best_module,
        }

    def default_module_config(self) -> dict:
        return {
            "module_id": "00000",
            "window_size": 30,
            "feature_cols": [],
            "seed": 42,
            "note": "auto baseline",
        }

    def update_by_timeframe(self, module, metrics_by_timeframe: dict):
        history = self.history_service.load()
        by_tf = history["by_timeframe"]
        for tf, m in metrics_by_timeframe.items():
            acc_new = float(m.get("accuracy", 0))
            if tf not in by_tf:
                self.history_service.update_timeframe(tf, module, acc_new)
                continue
            acc_old = by_tf[tf].get("accuracy", 0)
            if acc_new > acc_old:
                self.history_service.update_timeframe(tf, module, acc_new)

    def update_stable_modules(self, module, metrics_by_timeframe: dict):
        history = self.history_service.load()
        stable = history.get("stable", [])
        pool = {}
        for s in stable:
            mid = s["module_id"]
            pool[mid] = {
                "module_id": mid,
                "module": s["module"],
                "scores": [s["stability"]],
            }
        mid = module.module_id
        pool[mid] = {
            "module_id": mid,
            "module": module.to_dict(),
            "scores": [
                float(m.get("accuracy", 0))
                for m in metrics_by_timeframe.values()
            ],
        }
        scored = []
        for p in pool.values():
            scores = p["scores"]
            if not scores:
                continue
            stability = sum(scores) / len(scores)
            scored.append(
                {
                    "module_id": p["module_id"],
                    "module": p["module"],
                    "stability": stability,
                }
            )
        scored.sort(key=lambda x: x["stability"], reverse=True)
        top2 = scored[:2]
        self.history_service.update_stable_modules(top2)

    def update_learning_history(self, module, metrics_by_timeframe: dict):
        self.update_by_timeframe(module, metrics_by_timeframe)
        self.update_stable_modules(module, metrics_by_timeframe)