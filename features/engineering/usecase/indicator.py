# features/feature_engineering/usecase/generate_indicator_usecase.py

import pandas as pd
from features.engineering.domain.entities.indicator import Indicator
from features.engineering.service.indicator_service import IndicatorService
from features.engineering.input.data_input import DataInput

class IndicatorUseCase:
    """
    UseCase: Sinh các chỉ báo kỹ thuật từ dữ liệu giá.
    Input:  DataFrame (timestamp, open, high, low, close, volume, timeframe)
    Output: DataFrame có thêm các cột chỉ báo (SMA, EMA, RSI, MACD, BBANDS, v.v.)
    """

    def __init__(self):
        self.service = IndicatorService()
        self.input_adapter = DataInput()

    def execute(self, timeframe: str = "1M") -> list[Indicator]:
        df = self.input_adapter.load(timeframe=timeframe)
        indi = self.service.generate(df)
        return indi