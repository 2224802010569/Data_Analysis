# features/feature_engineering/usecase/generate_indicator_usecase.py

import pandas as pd
from features.engineering.domain.entities.indicator import Indicator
from features.engineering.service.indicator_service import IndicatorService
from features.engineering.input.data_input import DataInput

class IndicatorUseCase:
    def __init__(self):
        self.service = IndicatorService()

    def execute(self, df: pd.DataFrame) -> list[Indicator]:
        print("indicator\n", df.head())
        indi = self.service.generate(df)
        return indi