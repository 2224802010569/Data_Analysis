import json
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

from features.learning.input.data_input import DataInput
from features.learning.input.engineering_input import EngineeringInput

class DataService:
    def load_data(self, timeframe: str):
        df_candle = DataInput().load(timeframe)
        df_engineering = EngineeringInput().load(timeframe)
        return df_candle, df_engineering

    def _safe_json(self, v):
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return {}
        return {}

    def _parse_engineering(self, df_eng: pd.DataFrame) -> pd.DataFrame:
        ind = df_eng["indicator"].map(self._safe_json)
        tmp = df_eng["temporal"].map(self._safe_json)
        ind_df = pd.DataFrame(ind.tolist()).fillna(0)
        tmp_df = pd.DataFrame(tmp.tolist()).fillna(0)
        base = df_eng[["timestamp", "timeframe"]].copy()
        return pd.concat([base, ind_df, tmp_df], axis=1)

    def _merge_with_candle(self, df_feat: pd.DataFrame, df_candle: pd.DataFrame) -> pd.DataFrame:
        df_feat["timestamp"] = pd.to_datetime(df_feat["timestamp"])
        df_candle["timestamp"] = pd.to_datetime(df_candle["timestamp"])
        merged = df_feat.merge(
            df_candle[["timestamp", "timeframe", "open", "high", "low", "close", "volume"]],
            on=["timestamp", "timeframe"],
            how="left"
        )
        merged[["open", "high", "low", "close", "volume"]] = (
            merged[["open", "high", "low", "close", "volume"]]
            .fillna(method="ffill")
            .fillna(0)
        )
        return merged

    def build_training_set(self, df_candle, df_engineering, module):
        window = module.window_size
        feat_df = self._parse_engineering(df_engineering)
        merged = self._merge_with_candle(feat_df, df_candle)
        feature_cols = [c for c in merged.columns if c not in ("timestamp", "timeframe")]
        features = merged[feature_cols].to_numpy(dtype=np.float32)
        candles = merged[["open", "high", "low", "close", "volume"]].to_numpy(dtype=np.float32)
        if len(features) <= window:
            return (
                np.zeros((0, window, features.shape[1]), dtype=np.float32),
                np.zeros((0, 5), dtype=np.float32),
            )
        X_view = sliding_window_view(features, (window, features.shape[1]))
        X = X_view[:, 0]
        y_next = candles[window:]
        X = X[:-1]
        y_next = y_next[: len(X)]
        prev_close = candles[window - 1 : window - 1 + len(X), 3:4]
        prev_vol = candles[window - 1 : window - 1 + len(X), 4:5]
        prev_close = np.where(prev_close == 0, 1e-8, prev_close)
        prev_vol = np.where(prev_vol == 0, 1e-8, prev_vol)
        ohlc_ret = (y_next[:, :4] - prev_close) / prev_close
        vol_ret = (y_next[:, 4:5] - prev_vol) / prev_vol
        y = np.concatenate([ohlc_ret, vol_ret], axis=1)
        y = np.nan_to_num(y, nan=0.0, posinf=1.0, neginf=-1.0)
        return X, y

    def build_forecast_window(self, df_candle, df_engineering, module):
        window = module.window_size
        feat_df = self._parse_engineering(df_engineering)
        merged = self._merge_with_candle(feat_df, df_candle)
        merged = merged.sort_values("timestamp")
        feature_cols = [c for c in merged.columns if c not in ("timestamp", "timeframe")]
        features = merged[feature_cols].to_numpy(dtype=np.float32)
        candles = merged[["open", "high", "low", "close", "volume"]].to_numpy(dtype=np.float32)
        if len(features) < window:
            raise ValueError("Không đủ dữ liệu để build forecast window")
        X_last = features[-window:].reshape(1, window, -1)
        last_candle = candles[-1]
        last_timestamp = merged.iloc[-1]["timestamp"]

        return X_last, last_candle, last_timestamp

    def build_feature_row_from_prediction(self, last_feature_row, predicted_ohlcv):
        next_row = last_feature_row.copy()
        next_row[-5:] = np.array(predicted_ohlcv, dtype=np.float32)
        return next_row
