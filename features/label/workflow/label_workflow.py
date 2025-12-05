print("🔍 DEBUG 1: Bắt đầu Label Workflow")
import pandas as pd
print("✅ DEBUG 2: Import pandas xong")

# --- Đặt bẫy tại các dòng import ---
try:
    print("🔍 DEBUG 3: Đang import các UseCase...")
    from features.label.usecase.fetch_and_save import FetchAndSaveUseCase
    from features.label.usecase.load import LoadUseCase
    print("✅ DEBUG 4: Import thành công!")
except Exception as e:
    print(f"❌ DEBUG ERROR: Lỗi khi import UseCase: {e}")

class LabelWorkflow:
    def run(self, timeframe: str = "1M"):
        # Logic lấy timeframe chuẩn từ config nếu cần
        print(f"🚀 Label Workflow đang chạy cho timeframe: {timeframe}")
        
        # --- LOGIC CŨ (Có thể đang bị ẩn lệnh chạy) ---
        # data = LoadUseCase().load(timeframe=timeframe)
        # if not data:
        
        # --- LOGIC MỚI (Ép chạy) ---
        print("🏷️ Đang thực hiện gán nhãn lại từ đầu...")
        try:
            # Gọi usecase để tính toán và lưu nhãn
            FetchAndSaveUseCase().execute(timeframes=[timeframe])
            
            # Load lại để kiểm tra
            data = LoadUseCase().load(timeframe=timeframe)
            
            if isinstance(data, list) and len(data) > 0:
                print(f"✅ Labeling hoàn tất. Đã gán nhãn cho {len(data)} dòng dữ liệu.")
            else:
                print("⚠️ Labeling chạy xong nhưng không có dữ liệu trả về.")
                
            return data
            
        except Exception as e:
            print(f"❌ Lỗi trong quá trình xử lý: {e}")
            import traceback
            traceback.print_exc()
            return []

if __name__ == "__main__":
    # Chạy thử với khung ngày (1d)
    LabelWorkflow().run(timeframe="1d")