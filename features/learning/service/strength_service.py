import pandas as pd
import numpy as np
from features.label.domain.entities.label import Label
from features.label.service.edit_service import EditService as edit


class StrengthService:
    def __init__(self,
                vol_window: int = 20,
                atr_window: int = 14,
                strong_th: float = 1.2,
                weak_th: float = 0.8):
        self.vol_window = vol_window
        self.atr_window = atr_window
        self.strong_th = strong_th
        self.weak_th = weak_th

    def compute_atr(self, df: pd.DataFrame) -> pd.Series:
        high_low = df["high"] - df["low"]
        high_close = (df["high"] - df["close"].shift()).abs()
        low_close = (df["low"] - df["close"].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(self.atr_window).mean().fillna(method="bfill")
        return atr

    def compute_volume_stability(self, df: pd.DataFrame) -> pd.Series:
        vol_ma = df["volume"].rolling(self.vol_window).mean()
        vol_std = df["volume"].rolling(self.vol_window).std()
        stability = (vol_ma / vol_std).fillna(0)
        return stability
    
    def compute_volatility_stability(self, df: pd.DataFrame, atr: pd.Series) -> pd.Series:
        atr_ma = atr.rolling(self.vol_window).mean()
        stability = (atr_ma / atr).fillna(0)
        return stability

    def execute(self, df: pd.DataFrame) -> list[Label]:
        df = df.copy()
        df["atr"] = self.compute_atr(df)
        df["vol_stab"] = self.compute_volume_stability(df)
        df["volatility_stab"] = self.compute_volatility_stability(df, df["atr"])
        df["liquidity_score"] = df["vol_stab"] * df["volatility_stab"]
        df["label"] = np.where(
            df["liquidity_score"] > self.strong_th, "strong",
            np.where(df["liquidity_score"] < self.weak_th, "weak", "normal")
        )
        return edit().merge(edit().convert(df))