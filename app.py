"""Punto de entrada. Ejecutar con:  python app.py"""
import os

from flask import Flask, g, request

import db
from config import COMPETITIONS, Config
from routes import bp
from utils import fecha_corta


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(os.path.dirname(app.config["DATABASE"]), exist_ok=True)
    db.init_app(app)
    app.register_blueprint(bp)
    app.jinja_env.filters["fecha_corta"] = fecha_corta

    @app.context_processor
    def inject_globals():
        """Variables disponibles en TODAS las plantillas."""
        view_args = request.view_args or {}
        return {
            "all_comps": COMPETITIONS,
            "active_code": (view_args.get("code") or "").upper(),
            "api_warning": g.get("api_warning"),
        }

    with app.app_context():
        db.init_db()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
