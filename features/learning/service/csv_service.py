from pathlib import Path
from typing import List
import pandas as pd

from features.learning.domain.entities.forecast import ForecastData


class CSVService:

    def write_forecast(self,forecasts: List[object], path: str | Path,) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not forecasts:
            raise ValueError("Forecast list is empty")
        rows = [f.__dict__ for f in forecasts]
        df = pd.DataFrame(rows)
        df.to_csv(path, index=False, encoding="utf-8")
        return path

    def read_dataframe(self, path: str | Path) -> pd.DataFrame:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"CSV not found: {path}")
        return pd.read_csv(path)
