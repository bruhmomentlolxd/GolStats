"""Cliente de football-data.org (API v4) con caché en SQLite.

Documentación: https://www.football-data.org/documentation/quickstart
"""
import json
import time
from datetime import timedelta
from urllib.parse import urlencode

import requests
from flask import current_app, g

from db import get_db

BASE_URL = "https://api.football-data.org/v4"


class ApiError(Exception):
    """Error al consultar la API. 'kind' indica el tipo para mostrar un mensaje claro."""

    def __init__(self, message, kind="error"):
        super().__init__(message)
        self.message = message
        self.kind = kind  # no_key | network | rate_limit | forbidden | not_found | error


def _request(path, params):
    key = current_app.config.get("FOOTBALL_API_KEY")
    if not key:
        raise ApiError("Falta la API key. Creá el archivo .env con FOOTBALL_API_KEY=tu_token.", "no_key")
    try:
        r = requests.get(BASE_URL + path, params=params, headers={"X-Auth-Token": key}, timeout=12)
    except requests.RequestException:
        raise ApiError("No se pudo conectar con football-data.org. ¿Tenés internet?", "network")

    if r.status_code == 200:
        return r.json()
    if r.status_code == 429:
        raise ApiError("Se superó el límite de consultas (10 por minuto). Esperá un momento y recargá.", "rate_limit")
    if r.status_code == 403:
        raise ApiError("Tu plan gratuito no incluye este dato.", "forbidden")
    if r.status_code == 404:
        raise ApiError("No se encontró lo que buscabas.", "not_found")
    if r.status_code in (401,):
        raise ApiError("La API key es incorrecta o fue revocada.", "no_key")
    raise ApiError(f"La API respondió con un error ({r.status_code}).", "error")


def cached_get(path, params=None, ttl=300):
    """GET con caché. 'ttl' son los segundos que una respuesta se considera "fresca"
    (o una función que recibe los datos y devuelve los segundos)."""
    params = params or {}
    cache_key = path + "?" + urlencode(sorted(params.items()))
    db = get_db()
    row = db.execute("SELECT payload, fetched_at FROM api_cache WHERE cache_key = ?", (cache_key,)).fetchone()
    now = time.time()

    if row:
        data = json.loads(row["payload"])
        seconds = ttl(data) if callable(ttl) else ttl
        if now - row["fetched_at"] < seconds:
            return data

    try:
        data = _request(path, params)
    except ApiError as e:
        # Si hay algo guardado, lo mostramos igual (aunque esté viejo) y avisamos.
        if row and e.kind not in ("not_found", "forbidden"):
            g.api_warning = f"{e.message} Mostrando los últimos datos guardados."
            return json.loads(row["payload"])
        raise

    db.execute("INSERT OR REPLACE INTO api_cache (cache_key, payload, fetched_at) VALUES (?, ?, ?)",
               (cache_key, json.dumps(data), now))
    db.commit()
    return data


# ---------- Funciones concretas (una por tipo de dato) ----------

def matches_for_day(day, today):
    """Partidos de un día. Se pide día y día siguiente (la API usa hora UTC) y se filtra después."""
    if day == today:
        ttl = 60            # hoy: puede haber partidos en vivo
    elif day < today:
        ttl = 3600
    else:
        ttl = 900
    params = {"dateFrom": day.isoformat(), "dateTo": (day + timedelta(days=1)).isoformat()}
    return cached_get("/matches", params, ttl).get("matches", [])


def standings(code):
    return cached_get(f"/competitions/{code}/standings", ttl=600)


def scorers(code):
    return cached_get(f"/competitions/{code}/scorers", {"limit": 50}, ttl=1800).get("scorers", [])


def competition_matches(code):
    return cached_get(f"/competitions/{code}/matches", ttl=600).get("matches", [])


def match_detail(match_id):
    # Partido terminado: casi no cambia. Partido en curso o futuro: se refresca seguido.
    ttl = lambda d: 6 * 3600 if d.get("status") == "FINISHED" else 60
    return cached_get(f"/matches/{match_id}", ttl=ttl)
