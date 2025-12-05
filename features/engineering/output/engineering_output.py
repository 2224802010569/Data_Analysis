import pandas as pd
from dataclasses import asdict
# --- SỬA LỖI IMPORT TẠI ĐÂY ---
from features.engineering.workflow.engineering_workflow import EngineeringWorkflow

class EngineeringOutput:
    def __init__(self):
        # Khởi tạo đúng workflow
        self.workflow = EngineeringWorkflow()

    def get(self, timeframe: str = "1M") -> pd.DataFrame:
        # Gọi workflow để lấy dữ liệu (Trả về list các object Engineering)
        data = self.workflow.run(timeframe=timeframe)
        
        # Chuyển đổi List Object -> DataFrame (Để các bên khác dễ dùng)
        if data and isinstance(data, list):
            rows = []
            for item in data:
                # Tạo dòng cơ bản
                row = {
                    "timestamp": item.timestamp,
                    "timeframe": item.timeframe
                }
                
                # Bung lụa (Flatten) các chỉ số Indicator
                if item.indicator:
                    row.update(item.indicator)
                
                # Bung lụa (Flatten) các chỉ số Temporal
                if item.temporal:
                     # Kiểm tra nếu là dataclass thì chuyển sang dict
                     if hasattr(item.temporal, '__dataclass_fields__'):
                         row.update(asdict(item.temporal))
                     elif isinstance(item.temporal, dict):
                         row.update(item.temporal)
                         
                rows.append(row)
            
            return pd.DataFrame(rows)
            
        return pd.DataFrame()