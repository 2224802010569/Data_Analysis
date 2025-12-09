#File này sẽ đóng vai trò là "Cổng" (Gateway), chịu trách nhiệm đọc file JSON và truyền xuống Workflow.
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
from features.engineering.workflow.engineering_workflow import DataWorkflow
class EngineeringOutput:
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.workflow = DataWorkflow(config=self.config)
    def _load_config(self, path: str) -> Dict[str, Any]:
        """
        Tìm và đọc file config.json.
        Ưu tiên tìm ở thư mục gốc dự án để tránh lỗi đường dẫn.
        """
        file_path = Path(path)
        if not file_path.exists():
            root_path = Path(__file__).resolve().parents[3] / path 
            if root_path.exists():
                file_path = root_path       
        if not file_path.exists():
            return {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ [EngineeringOutput] Lỗi đọc config: {e}")
            return {}

    def get(self, timeframe: str = "1M") -> pd.DataFrame:
        """
        Lấy dữ liệu Engineering features.
        """
        return self.workflow.run(timeframe=timeframe)