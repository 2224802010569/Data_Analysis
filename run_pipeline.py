import sys
import time

# Import các Workflow
from features.data.workflow.data_workflow import DataWorkflow
from features.engineering.workflow.engineering_workflow import EngineeringWorkflow
from features.label.workflow.label_workflow import LabelWorkflow
from features.learning.workflow.learning_workflow import LearningWorkflow

def run_full_pipeline():
    print("🚀 BẮT ĐẦU CHẠY TOÀN BỘ HỆ THỐNG...")
    start_time = time.time()

    # Danh sách các khung thời gian cần xử lý
    # 1d: Để train AI và vẽ biểu đồ ngày
    # 1h: Để vẽ biểu đồ giờ
    # 1M: Để vẽ biểu đồ tháng
    timeframes = ["1d", "1h", "1M"]

    # --- BƯỚC 1: TẢI DỮ LIỆU (DATA) ---
    print("\n" + "="*50)
    print("1️⃣  STEP 1: TẢI DỮ LIỆU TỪ SÀN (CRAWL DATA)")
    print("="*50)
    for tf in timeframes:
        print(f"   ⬇️ Đang tải dữ liệu khung {tf}...")
        try:
            DataWorkflow().run(timeframe=tf)
        except Exception as e:
            print(f"   ⚠️ Lỗi tải {tf}: {e}")

    # --- BƯỚC 2: TÍNH CHỈ SỐ (ENGINEERING) ---
    print("\n" + "="*50)
    print("2️⃣  STEP 2: TÍNH TOÁN CHỈ SỐ KỸ THUẬT (ENGINEERING)")
    print("="*50)
    for tf in timeframes:
        print(f"   ⚙️ Đang xử lý khung {tf}...")
        try:
            EngineeringWorkflow().run(timeframe=tf)
        except Exception as e:
            print(f"   ⚠️ Lỗi xử lý {tf}: {e}")

    # --- BƯỚC 3: GÁN NHÃN (LABEL) ---
    print("\n" + "="*50)
    print("3️⃣  STEP 3: GÁN NHÃN DỮ LIỆU (LABELING)")
    print("="*50)
    # Chỉ cần gán nhãn cho khung '1d' để train AI (các khung khác chỉ để xem)
    try:
        print("   🏷️ Đang gán nhãn cho khung 1d...")
        LabelWorkflow().run(timeframe="1d")
    except Exception as e:
        print(f"   ⚠️ Lỗi gán nhãn: {e}")

    # --- BƯỚC 4: HUẤN LUYỆN AI (LEARNING) ---
    print("\n" + "="*50)
    print("4️⃣  STEP 4: HUẤN LUYỆN MODEL AI (TRAINING)")
    print("="*50)
    try:
        print("   🧠 Đang train lại model (có thể mất vài phút)...")
        # Lưu ý: Train AI mặc định dùng khung 1d
        LearningWorkflow().run() 
    except Exception as e:
        print(f"   ⚠️ Lỗi train model: {e}")

    # --- TỔNG KẾT ---
    elapsed = time.time() - start_time
    print("\n" + "="*50)
    print(f"✅ HOÀN TẤT TOÀN BỘ QUY TRÌNH!")
    print(f"⏱️ Tổng thời gian: {elapsed:.2f} giây")
    print("👉 Bây giờ bạn có thể chạy 'python main.py' để mở Web.")
    print("="*50)

if __name__ == "__main__":
    run_full_pipeline()