# Max future price
# Min future price
# simple forward return 
# Peak-to-trough drawdown
# Rule-based classification

from features.label.domain.entities.window import Window


class LabelService:
    def __init__(self):
        pass

    def generate_labels(self, window: list[Window]) -> list[Window]:
        # tạo nhãn từ dữ liệu đã cho.
        pass

    def _calculate_window(self, window: Window) -> Window:
        # tính toán các giá trị window.
        pass
    
    def _high_return(self, window: Window) -> float:
        # tính toán tỉ lệ tăng cao nhất trong cửa sổ.
        pass

    def _low_return(self, window: Window) -> float:
        # tính toán tỉ lệ giảm thấp nhất trong cửa sổ.
        pass

    def _fwd_return(self, window: Window) -> float:
        # tính toán tỉ lệ tăng/giảm từ T0 đến hết cửa sổ.
        pass

    def _drawdown(self, window: Window) -> float:
        # tính toán mức giảm tối đa từ T0 đến hết cửa sổ.
        pass

    def _volatility(self, window: Window) -> float:
        # tính toán độ biến động trong cửa sổ.
        pass