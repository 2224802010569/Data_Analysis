from flask import Blueprint, render_template, request, jsonify
from app.service.label_service import LabelService

recommend_router = Blueprint("recommend_router", __name__)
label_service = LabelService()

@recommend_router.get("/recommend")
def recommend_page():
    return render_template("main/recommend.html", current_page="recommend")


@recommend_router.get("/api/label")
def api_get_label_data():
    tf = request.args.get("tf", "1M")
    df = label_service.get_label_data(tf)
    if df is None or df.empty:
        return jsonify({"status": "empty", "data": []})

    return jsonify({
        "status": "ok",
        "data": df.to_dict(orient="records")
    })


@recommend_router.get("/api/recommendations")
def api_recommendations():
    tf = request.args.get("tf", "1M")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 20))
    result = label_service.get_page(tf=tf, page=page, page_size=page_size)
    return jsonify({
        "status": "ok",
        "page": result.get("page", page),
        "total_pages": result.get("total_pages", 1),
        "records": result.get("records", [])
    })
