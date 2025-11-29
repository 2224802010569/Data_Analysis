import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from flask import Flask
from app.router.main_router import main_router
from app.router.api_data_router import api_data_router

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main_router)
    app.register_blueprint(api_data_router, url_prefix="/api")
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
