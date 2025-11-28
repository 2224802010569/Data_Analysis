import pandas as pd
import numpy as np
from hmmlearn.hmm import GaussianHMM
from features.label.domain.entities.label import Label
from features.label.service.edit_service import EditService as edit


class TrendService:

    def __init__(self, n_regimes: int = 3,
                spike_threshold: float = 0.03,    # tăng/giảm > 6% là breakout
                min_trend_len: int = 3):          # ít nhất 3 nến liên tiếp
        self.n_regimes = n_regimes
        self.hmm_model = None
        self.spike_threshold = spike_threshold
        self.min_trend_len = min_trend_len

    def hmm_trend(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df["ret"] = df["close"].pct_change().fillna(0)
        df["vol"] = df["ret"].rolling(5).std().fillna(method="bfill")
        X = df[["ret", "vol"]].values
        self.hmm_model = GaussianHMM(
            n_components=self.n_regimes,
            covariance_type="full",
            n_iter=200
        )
        self.hmm_model.fit(X)
        df["regime"] = self.hmm_model.predict(X)
        means = df.groupby("regime")["ret"].mean().sort_values()
        mapping = {
            means.index[0]: "bear",
            means.index[1]: "neutral",
            means.index[2]: "bull"
        }
        df["regime_label"] = df["regime"].map(mapping)
        return df

    def detect_spikes(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["spike_up"] = df["ret"] > self.spike_threshold
        df["spike_down"] = df["ret"] < -self.spike_threshold
        return df

    def apply_trend_rule(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        labels = []
        streak = 1
        prev = df["regime_label"].iloc[0]
        for i in range(len(df)):
            curr = df["regime_label"].iloc[i]
            if df["spike_up"].iloc[i]:
                labels.append("buy")
                streak = 1
                prev = curr
                continue
            if df["spike_down"].iloc[i]:
                labels.append("sell")
                streak = 1
                prev = curr
                continue
            if curr == prev:
                streak += 1
            else:
                streak = 1
                prev = curr
            if curr == "bull" and streak >= self.min_trend_len:
                labels.append("buy")
            elif curr == "bear" and streak >= self.min_trend_len:
                labels.append("sell")
            else:
                labels.append("none")
        df["label"] = labels
        return df

    def execute(self, df: pd.DataFrame) -> list[Label]:
        df = self.hmm_trend(df)
        df = self.detect_spikes(df)
        df = self.apply_trend_rule(df)
        return edit().merge(edit().convert(df))
