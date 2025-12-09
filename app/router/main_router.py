from flask import Blueprint, render_template, request, jsonify
import pandas as pd
import numpy as np
import tensorflow as tf
import joblib
import os

from features.engineering.service.sql_service import SQLService as EngineeringSqlService
from features.data.usecase.load import LoadUseCase

main_router = Blueprint("main_router", __name__)

MODEL_PATH = "models/lstm_v1.keras"
SCALER_PATH = "models/scaler.pkl"

ai_model = None
ai_scaler = None

def load_ai_resources():
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
    return render_template("main/main.html", current_page="home")

@main_router.get("/api/data")
def api_get_data():
    tf_req = request.args.get("tf", "1d")
    
    # 1. Load Data
    try:
        candles = LoadUseCase().load(type="sql", timeframe=tf_req)
        if not candles:
            return jsonify({"status": "empty", "data": []})

        eng_service = EngineeringSqlService()
        try:
            df_eng = eng_service.get_all_as_df(timeframe=tf_req)
        except:
            df_eng = pd.DataFrame()

    except Exception as e:
        print(f"⚠️ Lỗi Load Data: {e}")
        return jsonify({"status": "error", "data": []})

    # Convert Candles
    df_price = pd.DataFrame([{
        "timestamp": c.timestamp,
        "open": c.open,
        "high": c.high,
        "low": c.low,
        "close": c.close,
        "volume": c.volume
    } for c in candles])
    df_price['timestamp'] = pd.to_datetime(df_price['timestamp'])

    # 2. Merge Data
    if not df_eng.empty:
        try:
            df_eng['timestamp'] = pd.to_datetime(df_eng['timestamp'])
            # Left join để giữ nến
            df_full = pd.merge(df_price, df_eng, on="timestamp", how="left")
        except:
            df_full = df_price.copy()
    else:
        df_full = df_price.copy()
    
    df_full = df_full.sort_values('timestamp').reset_index(drop=True)
    
    # 3. Limit Data
    DISPLAY_LIMIT = 1000
    BUFFER = 100 
    
    if len(df_full) > (DISPLAY_LIMIT + BUFFER):
        df_process = df_full.tail(DISPLAY_LIMIT + BUFFER).copy().reset_index(drop=True)
    else:
        df_process = df_full.copy()

    # Init AI columns
    if 'ai_action' not in df_process.columns:
        df_process['ai_action'] = "NONE"
    if 'ai_confidence' not in df_process.columns:
        df_process['ai_confidence'] = 0.0

    # 4. Chạy AI
    has_ai = load_ai_resources()
    ignore_cols = ['timestamp', 'timeframe', 'label', 't0', 't1', 'id', 'created_at', 
                   'open', 'high', 'low', 'close', 'volume', 'ai_action', 'ai_confidence']
    potential_features = [c for c in df_process.columns if c not in ignore_cols]

    if has_ai and len(potential_features) > 0 and not df_process.empty:
        try:
            feature_cols = potential_features + ["open", "high", "low", "close", "volume"]
            # Chỉ lấy dòng không bị NaN
            mask_valid = df_process[potential_features].notna().all(axis=1)
            
            if mask_valid.any():
                data_subset = df_process.loc[mask_valid, feature_cols].values.astype(np.float32)
                expected_input = ai_scaler.n_features_in_
                n_features = data_subset.shape[1]
                
                if expected_input % n_features == 0:
                    window_size = expected_input // n_features
                    if len(data_subset) > window_size:
                        X_list = []
                        valid_indices_map = df_process.loc[mask_valid].index
                        batch_indices = []

                        for i in range(window_size, len(data_subset)):
                            window_data = data_subset[i-window_size : i]
                            X_list.append(window_data.reshape(1, -1))
                            batch_indices.append(valid_indices_map[i])
                        
                        if X_list:
                            X_batch = np.vstack(X_list)
                            X_final = ai_scaler.transform(X_batch).reshape(-1, window_size, n_features)
                            predictions = ai_model.predict(X_final, verbose=0)
                            
                            pred_classes = np.argmax(predictions, axis=1)
                            pred_confs = np.max(predictions, axis=1)
                            action_map = {0: 'NONE', 1: 'BUY', 2: 'SELL', 3: 'STRONG', 4: 'WEAK'}
                            
                            df_process.loc[batch_indices, 'ai_action'] = [action_map.get(x, "NONE") for x in pred_classes]
                            df_process.loc[batch_indices, 'ai_confidence'] = pred_confs
        except Exception as e:
            print(f"⚠️ AI Skip: {e}")

    # 5. Format Output (QUAN TRỌNG NHẤT)
    df_final = df_process.tail(DISPLAY_LIMIT).copy()
    df_final['timestamp'] = df_final['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')

    # --- FIX LỖI 1M ---
    # Thay thế toàn bộ NaN bằng None (thành null trong JSON) để JS không bị lỗi
    df_final = df_final.replace({np.nan: None})
    
    # Ép kiểu cho confidence để tránh lỗi numpy float
    df_final['ai_confidence'] = df_final['ai_confidence'].apply(lambda x: float(x) if x is not None else 0.0)

    return jsonify({
        "status": "ok",
        "data": df_final.to_dict(orient="records")
    })