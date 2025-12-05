import pandas as pd
from app.config import config
from features.engineering.usecase.fetch_and_save import FetchAndSaveUseCase
from features.engineering.usecase.load import LoadUseCase
class EngineeringWorkflow:
    def run(self, timeframe: str = "1M"):
        # Logic lấy timeframe từ config nếu cần
        tf = timeframe
        print(f"🚀 Engineering đang chạy cho timeframe: {tf}")
        print("⚙️ Đang tính toán lại toàn bộ chỉ số kỹ thuật...")
        FetchAndSaveUseCase().execute(timeframes=[tf])
        
        data = LoadUseCase().load(timeframe=tf)

        if isinstance(data, list) and len(data) > 0:
            # Chuyển đổi sang DataFrame để in ra cho đẹp
            
            print(f"✅ Engineering hoàn tất. Đã xử lý {len(data)} dòng dữ liệu.")
        else:
            print("⚠️ Engineering chạy xong nhưng không có dữ liệu trả về.")
            
        return data

if __name__ == "__main__":
    # Test chạy với khung ngày (1d)
    EngineeringWorkflow().run(timeframe="1h")