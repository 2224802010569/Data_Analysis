# features/engineering/workflow/engineering_workflow.py
# File này sẽ nhận config và áp dụng bộ lọc cột (feature_cols) lên DataFrame kết quả trước khi trả về.
import pandas as pd
from typing import Dict, Any, Optional
from features.engineering.usecase.fetch_and_save import FetchAndSaveDataUseCase
from features.engineering.usecase.load import LoadUseCase
class DataWorkflow:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.feature_cols = self.config.get(
            "feature_cols", 
            ["timestamp", "timeframe", "indicator", "temporal"]
        )
    def run(self, timeframe: str = "1M") -> pd.DataFrame:
        data = LoadUseCase().load(timeframe=timeframe)
        if not data:
            print(f"⚡ [Engineering] Fetching new data for {timeframe}...")
            FetchAndSaveDataUseCase().execute(timeframes=[timeframe])
            data = LoadUseCase().load(timeframe=timeframe)
        if isinstance(data, list) and len(data) > 0:
            df = pd.DataFrame([{
                "timestamp": e.timestamp,
                "timeframe": e.timeframe,
                "indicator": e.indicator, # Dict json
                "temporal": e.temporal    # Dict json
            } for e in data])
            available_cols = [c for c in self.feature_cols if c in df.columns]
            if available_cols:
                df = df[available_cols]
                
        else:
            df = pd.DataFrame(columns=self.feature_cols)

        return df