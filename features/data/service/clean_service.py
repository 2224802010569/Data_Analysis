from typing import List
from datetime import datetime
import math

from features.data.domain.entities.candle import Candle

class CleanService:
    """
    CleanUseCase:
        - ensure timestamps are datetime (bỏ candle khác loại)
        - deduplicate by timestamp (if same timestamp AND same timeframe -> keep last)
        If same timestamp but different timeframe -> keep both
        - replace invalid numeric (None or NaN) with fallback value
    """

    def __init__(self, fallback_numeric: float = 0.0):
        self.fallback_numeric = float(fallback_numeric)

    # 1) Ensure timestamp is datetime
    @staticmethod
    def _ensure_datetime(candles: List[Candle]) -> List[Candle]:
        result: List[Candle] = []
        for c in candles:
            if c is None:
                continue
            if isinstance(c.timestamp, datetime):
                result.append(c)
            else:
                # skip if timestamp is not datetime
                # you can log here if needed
                continue
        return result

    @staticmethod
    def _is_valid_number(x) -> bool:
        if x is None:
            return False
        try:
            xf = float(x)
        except Exception:
            return False
        if math.isnan(xf):
            return False
        return True

    # 2) Fill invalid numeric fields with fallback value
    def _fill_numeric(self, candles: List[Candle]) -> List[Candle]:
        out: List[Candle] = []
        for c in candles:
            o = c.open if self._is_valid_number(c.open) else self.fallback_numeric
            h = c.high if self._is_valid_number(c.high) else self.fallback_numeric
            l = c.low if self._is_valid_number(c.low) else self.fallback_numeric
            cl = c.close if self._is_valid_number(c.close) else self.fallback_numeric
            v = c.volume if self._is_valid_number(c.volume) else self.fallback_numeric

            # create new Candle (or you can modify in-place)
            out.append(Candle(
                timestamp=c.timestamp,
                open=float(o),
                high=float(h),
                low=float(l),
                close=float(cl),
                volume=float(v),
                timeframe=c.timeframe
            ))
        return out

    # 3) Deduplicate: remove duplicates where timestamp and timeframe both match.
    # Keep the last seen candle for that (preserve input order).
    # If same timestamp but different timeframe -> keep both.
    def _deduplicate(self, candles: List[Candle]) -> List[Candle]:
        seen = {}  # key: (timestamp, timeframe) -> index in output
        out: List[Candle] = []

        for c in candles:
            key = (c.timestamp, c.timeframe)
            if key in seen:
                idx = seen[key]
                out[idx] = c
            else:
                seen[key] = len(out)
                out.append(c)
        return out

    # Public method: perform cleaning pipeline
    def execute(self, candles: List[Candle]) -> List[Candle]:
        if not candles:
            return []
        step1 = self._ensure_datetime(candles)
        step2 = self._fill_numeric(step1)
        step3 = self._deduplicate(step2)
        step3.sort(key=lambda c: (c.timestamp, c.timeframe))
        return step3