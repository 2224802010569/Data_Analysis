from features.label.domain.entities.label import Label
from features.label.input.data_input import DataInput
from features.label.service.strength_service import StrengthService
from features.label.service.trend_service import TrendService


class LabelUsecase:
    def __init__(self):
        self.ts = TrendService()
        self.ss = StrengthService()

    def execute(self, tf: str = "1M") -> list[Label]:
        data = DataInput().load(timeframe=tf)
        df_t = self.ts.execute(data)
        df_s = self.ss.execute(data)
        df = df_t + df_s
        return df