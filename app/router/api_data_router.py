from flask import Blueprint, request, jsonify
from app.service.data_service import DataService

api_data_router = Blueprint("api_data_router", __name__)
service = DataService()

@api_data_router.get("/data")
def get_data():
    tf = request.args.get("tf", "1M")
    df = service.get_candle_data(tf)
    if df is None or df.empty:
        return jsonify({"status": "empty", "data": []})

    return jsonify({
        "status": "ok",
        "data": df.to_dict(orient="records")
    })
