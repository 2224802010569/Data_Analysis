# run_eng.py
import sys
import os

# Thêm thư mục hiện tại vào path để import được các module
sys.path.append(os.getcwd())

from features.engineering.usecase.fetch_and_save import FetchAndSaveDataUseCase

def main():
    print("🚀 Bắt đầu tính toán chỉ số kỹ thuật (Feature Engineering)...")
    
    # Chạy tính toán cho 1h và 1M
    # Lưu ý: Quá trình này có thể mất 1-2 phút tùy lượng dữ liệu
    FetchAndSaveDataUseCase().execute(timeframes=["1h", "1M"])
    
    print("✅ HOÀN TẤT! Bây giờ Web đã có dữ liệu để chạy AI cho 1H và 1M.")

if __name__ == "__main__":
    main()