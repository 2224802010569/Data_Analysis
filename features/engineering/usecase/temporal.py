# features/feature_engineering/usecase/generate_temporal_feature_usecase.py

import pandas as pd
from features.engineering.domain.entities.temporal import Temporal
from features.engineering.input.data_input import DataInput
from features.engineering.service.temporal_service import TemporalService

class TemporalUseCase:
    """Biến timestamp → hành vi thị trường."""

    def __init__(self):
        self.adapter = DataInput()
        self.service = TemporalService()

    def execute(self, timeframe: str = "1M") -> list[Temporal]:
        df = self.adapter.load(timeframe=timeframe)
        temporals = self.service.generate(df, timeframe=timeframe)
        return temporals
