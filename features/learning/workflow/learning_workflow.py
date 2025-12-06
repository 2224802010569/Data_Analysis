from datetime import datetime
import pandas as pd
import numpy as np
import os

from features.learning.service.preprocessing_service import PreprocessingService
from features.learning.domain.entities.model import CryptoLSTMModel
from features.engineering.service.sql_service import SQLService as EngineeringSqlService
from features.label.service.sql_service import SQLService as LabelSqlService

class LearningWorkflow:
    def __init__(self):
        self.preprocessing = PreprocessingService(window_size=30)
        self.model = CryptoLSTMModel(input_shape=(30, 22), num_classes=5) 
        self.engineering_service = EngineeringSqlService()
        self.label_service = LabelSqlService()

    def run(self, model_save_path="models/lstm_v1.keras"):
        print("🚀 Bắt đầu quy trình Training...")
        print("📥 Đang tải dữ liệu từ Database...")
        df_engineering = self.engineering_service.get_all_as_df()
        df_label = self.label_service.get_all_as_df()
        if df_engineering.empty:
            print("❌ Lỗi: Bảng Engineering trống! Bạn cần chạy 'features.engineering.workflow' trước.")
            return
        if df_label.empty:
            print("❌ Lỗi: Bảng Label trống! Bạn cần chạy 'features.label.workflow' trước.")
            return
        print(f"   - Tìm thấy {len(df_engineering)} dòng dữ liệu Engineering.")
        print(f"   - Tìm thấy {len(df_label)} dòng dữ liệu Label.")
        try:
            X_train, X_test, y_train, y_test = self.preprocessing.execute(df_engineering, df_label)
        except Exception as e:
            print(f"❌ Lỗi trong quá trình xử lý dữ liệu: {e}")
            return
        if len(X_train) == 0:
            print("❌ Không đủ dữ liệu để train sau khi cắt window (Window size=30).")
            return
        self.preprocessing.save_scaler("models/scaler.pkl")
        print(f"🏋️‍♀️ Bắt đầu train model với {len(X_train)} mẫu dữ liệu...")
        os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
        self.model.train(X_train, y_train, X_test, y_test, epochs=50, batch_size=32)
        self.model.save(model_save_path)
        print("🎉 Quy trình hoàn tất! Model đã được lưu.")
if __name__ == "__main__":
    workflow = LearningWorkflow()
    workflow.run()