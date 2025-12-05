from dataclasses import dataclass
from datetime import datetime

@dataclass
class ForecastResult:
    timestamp: datetime  # Thời điểm dự báo
    timeframe: str       # Khung thời gian (1M, 1H...)
    action: str          # Hành động gợi ý: BUY, SELL, HOLD
    confidence: float    # Độ tin cậy (VD: 0.85 tức là chắc chắn 85%)
    raw_probs: dict      # Xác suất chi tiết từng hành động