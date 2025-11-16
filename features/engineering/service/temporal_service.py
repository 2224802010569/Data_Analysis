import pandas as pd
import numpy as np

from features.engineering.domain.entities.temporal import Temporal, TemporalValues

class TemporalService:

    def __init__(self):
        pass

    def generate(self, df: pd.DataFrame, timeframe: str = "1d") -> list[Temporal]:
        if df is None or df.empty:
            raise ValueError("⚠️ DataFrame trống, không thể tạo temporal feature.")

        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["timeframe"] = timeframe
        df["time_sin"], df["time_cos"] = self._encode_time(df["timestamp"], timeframe)
        df["return_1"] = df["close"].pct_change()
        df["time_volatility"] = df["return_1"].rolling(3).std()
        df = df.fillna(method="bfill").fillna(method="ffill")
        timeframe = df["timeframe"].iloc[0]
        temporals: list[Temporal] = []
        for _, row in df.iterrows():
            values: TemporalValues = {
                "time_sin": row["time_sin"],
                "time_cos": row["time_cos"],
                "return_1": row["return_1"],
                "time_volatility": row["time_volatility"]
            }
            temporals.append(
                Temporal(
                    timestamp = row["timestamp"],
                    timeframe = timeframe,
                    values = values
                )
            )
        return temporals

    # === Hàm encode chu kỳ thời gian ===
    def _encode_time(self, timestamps: pd.Series, timeframe: str):
        """
        Encode timestamp thành cặp (sin, cos) theo timeframe.
        - 1h: chu kỳ theo 24h
        - 1d: chu kỳ theo 7 ngày (tuần)
        - 1M: chu kỳ theo 12 tháng (năm)
        """
        dt = pd.to_datetime(timestamps)

        if timeframe == "1h":
            unit = dt.dt.hour + dt.dt.minute / 60.0
            period = 24.0
        elif timeframe == "1d":
            unit = dt.dt.dayofweek
            period = 7.0
        elif timeframe == "1M":
            unit = dt.dt.month
            period = 12.0
        else:
            unit = dt.dt.dayofyear
            period = 365.0

        time_sin = np.sin(2 * np.pi * unit / period)
        time_cos = np.cos(2 * np.pi * unit / period)
        return time_sin, time_cos
