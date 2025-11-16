import pandas as pd
from features.label.domain.entities.window import Window


class WindowService:
    def __init__(self):
        pass
    
    def sliding_window(self, e_data:pd.DataFrame = None, d_data:pd.DataFrame = None) -> list[Window]:
        self._find_window()
        pass

    def _find_window(self, data) -> Window:
        # tìm cửa sổ từ dữ liệu đã cho, đệ quy của sliding_window
        pass