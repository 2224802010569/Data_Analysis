from flask import Blueprint, render_template, request, jsonify
from app.service.data_service import DataService

main_router = Blueprint("main_router", __name__)
service = DataService()

@main_router.route("/")
def index():
    return render_template("main/main.html")

@main_router.get("/api/data")
def api_get_candle_data():
    tf = request.args.get("tf", "1M")
    df = service.get_candle_data(tf)
    if df is None or df.empty:
        return jsonify({"status": "empty", "data": []})

    return jsonify({
        "status": "ok",
        "data": df.to_dict(orient="records")
    })
