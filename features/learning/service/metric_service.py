import numpy as np
from features.learning.service.data_service import DataService


class MetricService:
    def __init__(self):
        self.data_service = DataService()

    def _mae(self, y_true, y_pred):
        return float(np.mean(np.abs(y_true - y_pred)))

    def _rmse(self, y_true, y_pred):
        return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

    def _accuracy_from_mae(self, mae):
        return max(0.0, 100.0 - mae)

    def evaluate(
        self,
        model,
        df_candle,
        df_engineering,
        module,
    ) -> dict:
        """
        Evaluate model and return metric snapshot
        """
        X, y_true = self.data_service.build_training_set(
            df_candle=df_candle,
            df_engineering=df_engineering,
            module=module,
        )

        if len(X) < 20:
            raise ValueError("Not enough data for metric evaluation")
        n = len(X)
        test_size = max(10, int(n * 0.1))
        X_test = X[-test_size:]
        y_test = y_true[-test_size:]
        y_pred = model.predict(X_test, verbose=0)
        mae = self._mae(y_test, y_pred)
        return {
            "accuracy": self._accuracy_from_mae(mae),
            "mae": mae,
            "rmse": self._rmse(y_test, y_pred),
        }
