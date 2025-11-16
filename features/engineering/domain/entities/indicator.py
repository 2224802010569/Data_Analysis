from dataclasses import dataclass
from datetime import datetime
from typing import Optional, TypedDict


class IndicatorValues(TypedDict, total=False):
    ema_20: float
    ema_50: float
    macd: float
    macd_signal: float
    adx_14: float
    rsi_14: float
    stoch_k: float
    roc_10: float
    bb_upper: float
    bb_lower: float
    bb_width: float
    atr_14: float
    obv: float
    vwap: float
    vol_ma_20: float
    ema_slope_20: float
    rsi_regime: float
    volatility_state: float

@dataclass
class Indicator:
    timestamp: datetime
    timeframe: str
    values: IndicatorValues

    def get(self, key: str) -> Optional[float]:
        return self.values.get(key)
