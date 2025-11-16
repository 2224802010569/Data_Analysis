from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict

class ExtraValues(TypedDict, total=False):
    high_return: float      #tỉ lệ tăng cao nhất
    low_return: float       #tỉ lệ giảm thấp nhất
    fwd_return: float       #tỉ lệ tăng/giảm từ T0 đến hết
    drawdown: float         #mức giảm tối đa từ T0 đến hết
    volatility: float       #độ biến động
    length: int             #độ dài cửa sổ, giảm thời gian tính toán
    
@dataclass
class Window:
    timeframe: str
    t0: datetime
    t1: datetime
    class_label: int
    extra: ExtraValues
