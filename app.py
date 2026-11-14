"""Punto de entrada. Ejecutar con:  python app.py"""
import os

from flask import Flask, g, request

import api
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

    def emblem_url(code):
        """Logo de una competición (se consulta una vez por petición)."""
        if "emblems" not in g:
            g.emblems = api.competition_emblems()
        return g.emblems.get(code) or f"https://crests.football-data.org/{code}.png"

    app.jinja_env.globals["emblem_url"] = emblem_url

    @app.context_processor
    def inject_globals():
        """Variables disponibles en TODAS las plantillas."""
        view_args = request.view_args or {}
        return {
            "all_comps": COMPETITIONS,
            "active_code": (view_args.get("code") or "").upper(),
            "api_warning": g.get("api_warning"),
        }

    @app.after_request
    def security_headers(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        return resp

    with app.app_context():
        db.init_db()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
