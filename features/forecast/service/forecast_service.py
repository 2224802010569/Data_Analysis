import numpy as np
import pandas as pd
import tensorflow as tf
import joblib
import os
from datetime import datetime
from features.forecast.domain.entities.forecast import ForecastResult

class ForecastService:
    def __init__(self, model_path="models/lstm_v1.keras", scaler_path="models/scaler.pkl"):
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.window_size = 30
        self.label_map_reverse = {
            0: 'NONE',
            1: 'BUY',
            2: 'SELL',
            3: 'STRONG',
            4: 'WEAK'
        }

    def predict_next(self, df_engineering: pd.DataFrame) -> ForecastResult:
        """
        Dự đoán hành động cho cây nến tiếp theo dựa trên dữ liệu quá khứ
        """
        # 1. Kiểm tra file model và scaler
        if not os.path.exists(self.model_path) or not os.path.exists(self.scaler_path):
            raise FileNotFoundError("Chưa tìm thấy Model hoặc Scaler. Hãy chạy Learning Workflow trước!")

        # 2. Load Model và Scaler
        model = tf.keras.models.load_model(self.model_path)
        scaler = joblib.load(self.scaler_path)

        # 3. Lấy đúng 30 dòng dữ liệu mới nhất
        if len(df_engineering) < self.window_size:
            raise ValueError(f"Không đủ dữ liệu! Cần ít nhất {self.window_size} dòng, hiện có {len(df_engineering)}.")
        
        # Sắp xếp theo thời gian và lấy 30 dòng cuối
        df_recent = df_engineering.sort_values('timestamp').tail(self.window_size)
        
        # 4. Lọc cột Features (Giống hệt lúc train)
        # Loại bỏ các cột không phải số liệu kỹ thuật
        exclude_cols = ['timestamp', 'timeframe', 'label', 't0', 't1', 'id', 'created_at']
        feature_cols = [c for c in df_recent.columns if c not in exclude_cols]
        
        # Chuyển sang mảng numpy
        data_raw = df_recent[feature_cols].values
        
        # 5. Chuẩn hóa dữ liệu (Scaling)
        # dùng transform để giữ nguyên tỉ lệ cũ
        data_scaled = scaler.transform(data_raw)
        
        # 6. Reshape thành 3D (1, 30, 22) để đưa vào LSTM
        input_data = np.array([data_scaled])
        
        # 7. Dự đoán
        prediction_probs = model.predict(input_data)[0] # Trả về mảng xác suất, ví dụ [0.1, 0.8, 0.1]
        
        # 8. Giải mã kết quả
        predicted_index = np.argmax(prediction_probs) # Lấy vị trí có xác suất cao nhất
        action = self.label_map_reverse.get(predicted_index, "UNKNOWN")
        confidence = float(prediction_probs[predicted_index])
        
        # Tạo dict chi tiết xác suất
        probs_detail = {self.label_map_reverse[i]: float(p) for i, p in enumerate(prediction_probs)}

        return ForecastResult(
            timestamp=datetime.now(),
            timeframe=df_recent.iloc[-1]['timeframe'], # Lấy timeframe của dòng cuối
            action=action,
            confidence=confidence,
            raw_probs=probs_detail
        )