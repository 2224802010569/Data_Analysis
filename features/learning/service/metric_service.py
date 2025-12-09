from datetime import datetime

class MetricService:

    def create_metrics(self, history_obj, module_id):
        acc = float(history_obj.history["accuracy"][-1])
        loss = float(history_obj.history["loss"][-1])

        return {
            "module_id": module_id,
            "accuracy": acc,
            "loss": loss,
            "timestamp": datetime.now().isoformat()
        }

    def create_history(self, history_obj, config, module_id):
        return {
            "module_id": module_id,
            "epochs": len(history_obj.history["loss"]),
            "loss": history_obj.history["loss"],
            "accuracy": history_obj.history.get("accuracy", []),
            "feature_cols": config.feature_cols,
            "window_size": config.window_size,
            "note": config.note
        }
