import pandas as pd
import numpy as np
from typing import List
from ta.trend import EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator, ROCIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, VolumeWeightedAveragePrice
from features.engineering.domain.entities.indicator import Indicator, IndicatorValues


class IndicatorService:

    def generate(self, df: pd.DataFrame) -> List[Indicator]:
        if df is None or df.empty:
            raise ValueError("Input DataFrame is empty.")
        df = df.copy()
        df = df.sort_values("timestamp").reset_index(drop=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Clean numeric fields
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=["close", "high", "low", "volume"])

        # Compute indicators
        df = self._add_trend(df)
        df = self._add_momentum(df)
        df = self._add_volatility(df)
        df = self._add_volume(df)
        df = self._add_regime(df)

        # Final cleanup
        df = df.fillna(method="bfill").fillna(method="ffill").reset_index(drop=True)

        timeframe = df["timeframe"].iloc[0] if "timeframe" in df.columns else "unknown"

        indicators: List[Indicator] = []

        for _, row in df.iterrows():
            values: IndicatorValues = {
                "ema_20": row["ema_20"],
                "ema_50": row["ema_50"],
                "macd": row["macd"],
                "macd_signal": row["macd_signal"],
                "adx_14": row["adx_14"],
                "rsi_14": row["rsi_14"],
                "stoch_k": row["stoch_k"],
                "roc_10": row["roc_10"],
                "bb_upper": row["bb_upper"],
                "bb_lower": row["bb_lower"],
                "bb_width": row["bb_width"],
                "atr_14": row["atr_14"],
                "obv": row["obv"],
                "vwap": row["vwap"],
                "vol_ma_20": row["vol_ma_20"],
                "ema_slope_20": row["ema_slope_20"],
                "rsi_regime": row["rsi_regime"],
                "volatility_state": row["volatility_state"],
            }
            indicators.append(
                Indicator(
                    timestamp=row["timestamp"],
                    timeframe=timeframe,
                    values=values,
                )
            )
        return indicators


    def _add_trend(self, df: pd.DataFrame) -> pd.DataFrame:
        df["ema_20"] = EMAIndicator(df["close"], window=20).ema_indicator()
        df["ema_50"] = EMAIndicator(df["close"], window=50).ema_indicator()
        macd = MACD(df["close"])
        df["macd"] = macd.macd()
        df["macd_signal"] = macd.macd_signal()
        adx = ADXIndicator(df["high"], df["low"], df["close"], window=14)
        df["adx_14"] = adx.adx()
        return df

    def _add_momentum(self, df: pd.DataFrame) -> pd.DataFrame:
        df["rsi_14"] = RSIIndicator(df["close"], window=14).rsi()
        df["stoch_k"] = StochasticOscillator(df["high"], df["low"], df["close"]).stoch()
        df["roc_10"] = ROCIndicator(df["close"], window=10).roc()
        return df

    def _add_volatility(self, df: pd.DataFrame) -> pd.DataFrame:
        bb = BollingerBands(df["close"], window=20, window_dev=2)
        df["bb_upper"] = bb.bollinger_hband()
        df["bb_lower"] = bb.bollinger_lband()
        df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["close"]

        atr = AverageTrueRange(df["high"], df["low"], df["close"], window=14)
        df["atr_14"] = atr.average_true_range()
        return df

    def _add_volume(self, df: pd.DataFrame) -> pd.DataFrame:
        df["obv"] = OnBalanceVolumeIndicator(df["close"], df["volume"]).on_balance_volume()
        df["vwap"] = VolumeWeightedAveragePrice(
            df["high"], df["low"], df["close"], df["volume"]
        ).volume_weighted_average_price()
        df["vol_ma_20"] = df["volume"].rolling(20).mean()
        return df

    def _add_regime(self, df: pd.DataFrame) -> pd.DataFrame:
        df["ema_slope_20"] = df["ema_20"].diff()
        df["rsi_regime"] = np.select(
            [df["rsi_14"] > 60, df["rsi_14"] < 40],
            [1, -1],
            default=0,
        )
        df["volatility_state"] = df["atr_14"] / df["close"]
        return df
