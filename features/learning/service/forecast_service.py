import os
import numpy as np
import pandas as pd
from datetime import timedelta
from app.config import config as con
from features.learning.domain.entities.forecast import ForecastData
from features.learning.service.data_service import DataService


class ForecastService:
    def __init__(self):
        self.data_service = DataService()
        self.output_dir = con.LEARNING_DIR
    
    def _next_timestamp(self, ts, timeframe):
        if timeframe == "1h":
            return ts + timedelta(hours=1)
        if timeframe == "1d":
            return ts + timedelta(days=1)
        if timeframe == "1M":
            return ts + pd.DateOffset(months=1)
        return ts + timedelta(days=1)

    def _safe_ret(self, r, timeframe):
        r = float(np.clip(r, -0.3, 0.3))
        return r * 1.2 if r > 0 else r
    
    def forecast(
        self,
        model,
        df_candle,
        df_engineering,
        module,
        timeframe,
    ):
        output_dir = f"{self.output_dir}/{module.module_id}"
        os.makedirs(output_dir, exist_ok=True)

        # -------------------------------------------------
        # 1. Build forecast window (ONE-STEP ML INPUT)
        # -------------------------------------------------
        X, last_candle, last_ts = self.data_service.build_forecast_window(
            df_candle=df_candle,
            df_engineering=df_engineering,
            module=module,
        )

        # -------------------------------------------------
        # 2. ONE ML prediction (đúng bản chất model)
        # -------------------------------------------------
        y_pred = model.predict(X, batch_size=64, verbose=1)[0]
        # y_pred shape: (5,) -> O H L C V returns

        # -------------------------------------------------
        # 3. Chuẩn bị thông tin ban đầu
        # -------------------------------------------------
        rows = []

        current_ts = max(
            con.START_FORE,
            self._next_timestamp(last_ts, timeframe)
        )

        last_close = float(last_candle[3])
        last_vol = float(last_candle[4])

        MIN_VOL_RATIO = 0.05
        base_vol = df_candle["volume"].tail(100).mean()
        min_vol = base_vol * MIN_VOL_RATIO

        base_ret = np.clip(y_pred, -0.03, 0.03)

        decay = 0.92
        base_mean_strength = 0.10
        vol_scale = 8.0
        mean_price = df_candle["close"].tail(100).mean()
        mean_vol = df_candle["volume"].tail(100).mean()
        returns = df_candle["close"].pct_change().dropna()
        volatility = returns.tail(50).std()

        mean_strength = base_mean_strength / (1 + vol_scale * volatility)

        step = 0


        while current_ts <= con.END_FORE:
            alpha = decay ** step

            # ---- Close price (mean reversion) ----
            delta_ml = alpha * base_ret[3] * last_close
            delta_mean = mean_strength * (mean_price - last_close)
            c = last_close + delta_ml + delta_mean

            # ---- OHLC từ close ----
            o = last_close
            h = max(o, c) * (1 + abs(base_ret[1]) * alpha)
            l = min(o, c) * (1 - abs(base_ret[2]) * alpha)

            # ---- Volume ----
            delta_vol = alpha * base_ret[4] * last_vol
            delta_vol_mean = mean_strength * (mean_vol - last_vol)
            v = last_vol + delta_vol + delta_vol_mean

            # ---- Sanity ----
            c = max(c, 0)
            o = max(o, 0)
            h = max(h, o, c)
            l = max(min(l, o, c), 0)
            v = max(v, min_vol)

            rows.append(
                ForecastData(
                    module_id=module.module_id,
                    timestamp=current_ts,
                    open=o,
                    high=h,
                    low=l,
                    close=c,
                    volume=v,
                    timeframe=timeframe,
                )
            )

            last_close = c
            last_vol = v
            current_ts = self._next_timestamp(current_ts, timeframe)
            step += 1

        return rows

