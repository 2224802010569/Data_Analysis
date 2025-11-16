import pandas as pd
from features.engineering.domain.entities.engineering import Engineering
from features.engineering.usecase.indicator import IndicatorUseCase
from features.engineering.usecase.temporal import TemporalUseCase


class CombineUseCase:

    def __init__(self):
        self.indicator_uc = IndicatorUseCase()
        self.temporal_uc = TemporalUseCase()

    def execute(self, timeframe: str = "1M") -> list[Engineering]:

        # Lấy list entity
        indicators = self.indicator_uc.execute(timeframe)
        temporals = self.temporal_uc.execute(timeframe)

        # Map theo timestamp
        indicator_map = {i.timestamp: i for i in indicators}
        temporal_map = {t.timestamp: t for t in temporals}

        # Thu tất cả timestamps
        all_timestamps = sorted(set(indicator_map.keys()) | set(temporal_map.keys()))
        e_list: list[Engineering] = []
        for ts in all_timestamps:
            ind = indicator_map.get(ts)
            tmp = temporal_map.get(ts)
            e_list.append(
                Engineering(
                    timestamp=ts,
                    timeframe=timeframe,
                    indicator=ind.values if ind else {},
                    temporal=tmp.values if tmp else {},
                )
            )
        return e_list
