"""ガクモンのサーバー。起動:  python app.py  →  http://127.0.0.1:5000

- /api/...   : データ(API)
- それ以外   : ../frontend のHTML・CSS・JSをそのまま配る
"""

from flask import Flask, redirect, request, send_from_directory

import config
from api import bp
from db import close_db, init_db


def create_app(db_path=None):
    app = Flask(__name__, static_folder=None)
    app.config["DB_PATH"] = db_path or config.DB_PATH
    init_db(app.config["DB_PATH"])
    app.teardown_appcontext(close_db)
    app.register_blueprint(bp)

    @app.route("/")
    def index():
        return redirect("/pages/home.html")

    @app.route("/<path:path>")
    def frontend(path):
        return send_from_directory(config.FRONTEND_DIR, path)

    @app.after_request
    def allow_dev_origin(res):
        # Live Server(5500番)で画面を開いたままでも、APIを使えるようにする(開発用)
        origin = request.headers.get("Origin")
        if origin in config.DEV_ORIGINS:
            res.headers["Access-Control-Allow-Origin"] = origin
            res.headers["Access-Control-Allow-Headers"] = "Content-Type, X-User-Id"
            res.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, DELETE, OPTIONS"
        return res

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
