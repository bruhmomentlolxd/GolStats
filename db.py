"""Conexión a SQLite (se usa como caché de la API)."""
import os
import sqlite3

from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Crea las tablas si no existen (no borra nada)."""
    db = get_db()
    with open(os.path.join(current_app.root_path, "schema.sql"), encoding="utf-8") as f:
        db.executescript(f.read())
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)

    @app.cli.command("clear-cache")
    def clear_cache_command():
        """Borra los datos guardados de la API: flask --app app clear-cache"""
        get_db().execute("DELETE FROM api_cache")
        get_db().commit()
        print("Caché borrada.")
