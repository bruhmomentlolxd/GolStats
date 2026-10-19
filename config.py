"""Configuración de la aplicación."""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _load_env_file():
    """Lee el archivo .env (si existe) y carga sus variables. Así la API key no queda en el código."""
    path = os.path.join(BASE_DIR, ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file()

# Competiciones del plan gratuito de football-data.org (código, nombre, país, color)
COMPETITIONS = [
    {"code": "CL",  "name": "Champions League",    "country": "Europa",       "accent": "#22e07a"},
    {"code": "PL",  "name": "Premier League",      "country": "Inglaterra",   "accent": "#a855f7"},
    {"code": "PD",  "name": "LaLiga",              "country": "España",       "accent": "#f97316"},
    {"code": "SA",  "name": "Serie A",             "country": "Italia",       "accent": "#38bdf8"},
    {"code": "BL1", "name": "Bundesliga",          "country": "Alemania",     "accent": "#ef4444"},
    {"code": "FL1", "name": "Ligue 1",             "country": "Francia",      "accent": "#eab308"},
    {"code": "DED", "name": "Eredivisie",          "country": "Países Bajos", "accent": "#fb923c"},
    {"code": "PPL", "name": "Primeira Liga",       "country": "Portugal",     "accent": "#16a34a"},
    {"code": "ELC", "name": "Championship",        "country": "Inglaterra",   "accent": "#3b82f6"},
    {"code": "BSA", "name": "Brasileirão Série A", "country": "Brasil",       "accent": "#facc15"},
    {"code": "WC",  "name": "Copa del Mundo",      "country": "Mundo",        "accent": "#f43f5e"},
    {"code": "EC",  "name": "Eurocopa",            "country": "Europa",       "accent": "#6366f1"},
]


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-cambiar-en-produccion")
    DATABASE = os.path.join(BASE_DIR, "instance", "futbol.db")

    # Clave de football-data.org (se lee del archivo .env o de la variable de entorno)
    FOOTBALL_API_KEY = os.environ.get("FOOTBALL_API_KEY", "")
