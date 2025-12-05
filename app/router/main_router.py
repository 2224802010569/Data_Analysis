from flask import Blueprint, render_template, request, jsonify
import pandas as pd
import numpy as np
import tensorflow as tf
import joblib
import os

from app.service.data_service import DataService
from features.engineering.service.sql_service import SQLService as EngineeringSqlService
from features.data.usecase.load import LoadUseCase

main_router = Blueprint("main_router", __name__)

MODEL_PATH = "models/lstm_v1.keras"
SCALER_PATH = "models/scaler.pkl"

# Biến global để cache model
ai_model = None
ai_scaler = None

def load_ai_resources():
    """Load model và scaler một lần duy nhất vào RAM"""
    global ai_model, ai_scaler
    try:
        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            if ai_model is None:
                ai_model = tf.keras.models.load_model(MODEL_PATH)
            if ai_scaler is None:
                ai_scaler = joblib.load(SCALER_PATH)
            return True
    except Exception as e:
        print(f"❌ Lỗi load AI Resources: {e}")
    return False

@main_router.route("/")
def index():
    return render_template("main/main.html")

@main_router.get("/api/data")
def api_get_data():
    tf = request.args.get("tf", "1d")
    
    # 1. Load Data (Engineering & Candle)
    eng_service = EngineeringSqlService()
    df_eng = eng_service.get_all_as_df(timeframe=tf)
    
    candles = LoadUseCase().load(type="sql", timeframe=tf)
    if not candles or df_eng.empty:
        return jsonify({"status": "empty", "data": []})

    df_price = pd.DataFrame([{
        "timestamp": c.timestamp,
        "open": c.open,
        "high": c.high,
        "low": c.low,
        "close": c.close,
        "volume": c.volume
    } for c in candles])

    # 2. Merge & Clean
    df_eng['timestamp'] = pd.to_datetime(df_eng['timestamp'])
    df_price['timestamp'] = pd.to_datetime(df_price['timestamp'])
    
    df_full = pd.merge(df_eng, df_price, on="timestamp", how="inner")
    df_full = df_full.sort_values('timestamp')

    # 3. Tối ưu hóa: Chỉ lấy 1000 nến gần nhất để xử lý
    # (Cộng thêm 30 nến quá khứ để đủ window cho nến đầu tiên)
    limit = 1000
    if len(df_full) > limit + 30:
        df_process = df_full.tail(limit + 30).copy().reset_index(drop=True)
    else:
        df_process = df_full.copy().reset_index(drop=True)

    # 4. Chạy AI Dự báo (Batch Processing - Siêu nhanh)
    has_ai = load_ai_resources()
    
    if has_ai:
        try:
            # Lọc features
            exclude_cols = ['timestamp', 'timeframe', 'label', 't0', 't1', 'id', 'created_at', 'open', 'high', 'low', 'close', 'volume', 'ai_action', 'ai_confidence']
            feature_cols = [c for c in df_eng.columns if c not in exclude_cols]
            
            data_raw = df_process[feature_cols].values
            data_scaled = ai_scaler.transform(data_raw)
            
            # Tạo Window (Vector hóa)
            X_batch = []
            valid_indices = []
            window_size = 30
            
            for i in range(window_size, len(data_scaled)):
                X_batch.append(data_scaled[i-window_size:i])
                valid_indices.append(i)
            
            # Khởi tạo cột kết quả mặc định
            df_process['ai_action'] = "NONE"
            df_process['ai_confidence'] = 0.0

            if X_batch:
                X_batch = np.array(X_batch)
                
                # Dự đoán 1 lần cho toàn bộ batch (Thay vì loop từng cái)
                predictions = ai_model.predict(X_batch, verbose=0)
                
                # Xử lý kết quả hàng loạt
                pred_classes = np.argmax(predictions, axis=1)
                pred_confs = np.max(predictions, axis=1)
                
                action_map = {0: 'NONE', 1: 'BUY', 2: 'SELL', 3: 'STRONG', 4: 'WEAK'}
                mapped_actions = [action_map.get(x, "NONE") for x in pred_classes]
                
                # Gán ngược lại DataFrame
                df_process.loc[valid_indices, 'ai_action'] = mapped_actions
                df_process.loc[valid_indices, 'ai_confidence'] = pred_confs.astype(float)

        except Exception as e:
            print(f"⚠️ Lỗi khi chạy AI: {e}")
            df_process['ai_action'] = "NONE"
            df_process['ai_confidence'] = 0.0
    else:
        df_process['ai_action'] = "NONE"
        df_process['ai_confidence'] = 0.0

    # 5. Trả về kết quả (Lấy đúng limit yêu cầu)
    df_final = df_process.tail(limit)
    
    return jsonify({
        "status": "ok",
        "data": df_final.to_dict(orient="records")
    })