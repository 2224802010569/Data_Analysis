from typing import Protocol, List
from features.engineering.domain.entities.indicator import Indicator

class IndicatorRepositoryPort(Protocol):
    def compute(self, df, name: str, params: dict) -> Indicator:
        """Tính chỉ báo và trả về đối tượng Indicator"""
        pass
