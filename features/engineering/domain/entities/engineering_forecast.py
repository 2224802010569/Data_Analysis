from dataclasses import dataclass
from datetime import datetime
from features.engineering.domain.entities.indicator import IndicatorValues
from features.engineering.domain.entities.temporal import TemporalValues


@dataclass
class Engineering_Forecast:
    timestamp: datetime
    timeframe: str
    indicator: IndicatorValues
    temporal: TemporalValues