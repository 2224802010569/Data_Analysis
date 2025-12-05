from features.engineering.service.sql_service import SQLService as EngineeringSqlService
from features.forecast.service.forecast_service import ForecastService

class ForecastWorkflow:
    def __init__(self):
        self.engineering_service = EngineeringSqlService()
        self.forecast_service = ForecastService()

    def run(self):
        print("🔮 Đang phân tích thị trường để dự báo...")

        # 1. Lấy dữ liệu Engineering từ DB lên
        df = self.engineering_service.get_all_as_df()
        
        if df.empty:
            print("❌ Không có dữ liệu để dự báo.")
            return

        try:
            # 2. Gọi AI dự đoán
            result = self.forecast_service.predict_next(df)
            
            # 3. In kết quả ra màn hình 
            print("-" * 40)
            print(f"🕒 Thời gian: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🤖 AI Khuyến nghị: {result.action.upper()}") 
            print(f"🎯 Độ tin cậy: {result.confidence * 100:.2f}%")
            print("-" * 40)
            print("📊 Chi tiết xác suất:")
            for act, prob in result.raw_probs.items():
                print(f"   - {act}: {prob * 100:.2f}%")
            print("-" * 40)

        except Exception as e:
            print(f"❌ Có lỗi xảy ra: {e}")

if __name__ == "__main__":
    wf = ForecastWorkflow()
    wf.run()