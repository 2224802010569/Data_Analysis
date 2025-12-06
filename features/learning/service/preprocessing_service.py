import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import joblib
import os

class PreprocessingService:
    def __init__(self, window_size=30):
        self.window_size = window_size
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        
        # Ánh xạ nhãn từ chữ sang số
        self.label_mapping = {
            'none': 0,
            'buy': 1,
            'sell': 2,
            'strong': 3,
            'weak': 4
        }

    def execute(self, df_engineering: pd.DataFrame, df_label: pd.DataFrame):
        """
        Hàm chính để biến đổi dữ liệu thô thành dữ liệu train cho LSTM
        Input: 2 DataFrames (Engineering và Label)
        Output: X_train, X_test, y_train, y_test
        """
        print("🔄 Đang xử lý dữ liệu...")

        # 1. Merge dữ liệu (Ghép chỉ báo kỹ thuật với nhãn đáp án)
        merged_df = pd.merge(df_engineering, df_label[['timestamp', 'label']], on='timestamp', how='inner')
        merged_df = merged_df.sort_values('timestamp')
        # 2. Lọc cột Features (Đầu vào) và Target (Đầu ra)
        exclude_cols = ['timestamp', 'timeframe', 'label', 't0', 't1', 'id', 'created_at']
        feature_cols = [c for c in merged_df.columns if c not in exclude_cols]
        
        print(f"📊 Số lượng Features tìm thấy: {len(feature_cols)} ({feature_cols})")
        
        # Lấy dữ liệu thô ra
        data_x = merged_df[feature_cols].values
        
        # Chuyển nhãn text sang số (Ví dụ: 'buy' -> 1)
        data_y = merged_df['label'].apply(lambda x: self.label_mapping.get(str(x).lower(), 0)).values

        # 3. Chuẩn hóa dữ liệu (Scaling) về khoảng [0, 1]
        data_x_scaled = self.scaler.fit_transform(data_x)

        # 4. Tạo cửa sổ trượt (Sliding Window)
        # Biến đổi bảng 2D thành khối 3D: (Số lượng mẫu, 30 ngày, Số features)
        X, y = [], []
        for i in range(self.window_size, len(data_x_scaled)):
            # Lấy 30 ngày quá khứ
            X.append(data_x_scaled[i-self.window_size:i])
            # Lấy nhãn của ngày hiện tại (mục tiêu dự đoán)
            y.append(data_y[i])
            
        X, y = np.array(X), np.array(y)

        # 5. Chia tập Train (80%) và Test (20%)
        # shuffle=False là BẮT BUỘC để không làm xáo trộn thứ tự thời gian
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        
        print(f"✅ Preprocessing hoàn tất!")
        print(f"   - Shape Train: {X_train.shape} (Dùng để học)")
        print(f"   - Shape Test:  {X_test.shape} (Dùng để thi)")
        
        return X_train, X_test, y_train, y_test

    def save_scaler(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.scaler, path)
        print(f"💾 Đã lưu Scaler tại: {path}")