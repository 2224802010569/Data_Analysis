import numpy as np
import pandas as pd
import json

LABEL_ORDER = ["none", "buy", "sell", "normal", "strong", "weak"]

class DataTrainService:

    def _label_to_onehot(self, label_str: str, num_classes: int):
        label_str = str(label_str).lower() if label_str else "none"
        try:
            idx = LABEL_ORDER.index(label_str)
        except ValueError:
            idx = 0

        vec = np.zeros(num_classes, dtype=np.float32)
        vec[idx] = 1.0
        return vec

    def _safe_json(self, s):
        try:
            if isinstance(s, str):
                return json.loads(s)
            if isinstance(s, dict):
                return s
            return {}
        except Exception:
            return {}

    def _normalize_df(self, df_data, df_eng, df_label):
        df_data = df_data.copy()
        df_eng = df_eng.copy()
        df_label = df_label.copy()
        df_data["timestamp"] = pd.to_datetime(df_data["timestamp"], errors="coerce")
        df_eng["timestamp"] = pd.to_datetime(df_eng["timestamp"], errors="coerce")
        df_label["t0"] = pd.to_datetime(df_label["t0"], errors="coerce")
        df_label["t1"] = pd.to_datetime(df_label["t1"], errors="coerce")
        df_data = df_data.sort_values("timestamp").reset_index(drop=True)
        df_eng = df_eng.sort_values("timestamp").reset_index(drop=True)
        return df_data, df_eng, df_label

    def _extract_indicator_temporal(self, df_eng):
        indicators = [self._safe_json(v) for v in df_eng["indicator"]]
        temporals = [self._safe_json(v) for v in df_eng["temporal"]]

        ind_df = pd.DataFrame(indicators).fillna(0.0)
        tmp_df = pd.DataFrame(temporals).fillna(0.0)
        return ind_df, tmp_df

    def _merge_candle(self, df_eng, df_data):
        merged = df_eng.merge(
            df_data[["timestamp", "open", "high", "low", "close", "volume"]],
            on="timestamp",
            how="left"
        )
        merged[["open","high","low","close","volume"]] = \
            merged[["open","high","low","close","volume"]].fillna(method="ffill").fillna(0.0)
        return merged

    def _align_labels(self, merged, df_label):
        labels = []
        for ts in merged["timestamp"]:
            row = df_label[(df_label["t0"] <= ts) & (ts < df_label["t1"])]
            lab = row.iloc[0]["label"] if not row.empty else "none"
            labels.append(lab)
        return labels

    def _build_window_xy(self, features_df, labels, config):
        window = config.window_size
        X_list, y_list = [], []

        for i in range(window, len(features_df)):
            X_list.append(features_df.iloc[i-window:i].values.astype(np.float32))
            y_list.append(self._label_to_onehot(labels[i], config.num_classes))

        if not X_list:
            return (
                np.zeros((0, window, features_df.shape[1]), dtype=np.float32),
                np.zeros((0, config.num_classes), dtype=np.float32)
            )

        X = np.stack(X_list, axis=0)
        y = np.stack(y_list, axis=0)
        return X, y

    def build_training_set(self, df_data, df_eng, df_label, config):
        df_data, df_eng, df_label = self._normalize_df(df_data, df_eng, df_label)
        ind_df, tmp_df = self._extract_indicator_temporal(df_eng)
        merged = self._merge_candle(df_eng, df_data)
        features_df = pd.concat([
            ind_df,
            tmp_df,
            merged[["open","high","low","close","volume"]]
        ], axis=1).fillna(0.0)
        labels = self._align_labels(merged, df_label)
        X, y = self._build_window_xy(features_df, labels, config)
        return X, y
