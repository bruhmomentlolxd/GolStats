"""Rutas (páginas) de la aplicación."""
from datetime import date, timedelta

from flask import Blueprint, abort, g, render_template, request

import api
from api import ApiError
from config import COMPETITIONS
from utils import (build_rounds, build_stats, default_round, group_by_date, fecha_corta, fecha_larga, normalize_match,
                   normalize_match_detail, today_ar, to_local)

bp = Blueprint("main", __name__)

COMP_BY_CODE = {c["code"]: c for c in COMPETITIONS}
COMP_ORDER = {c["code"]: i for i, c in enumerate(COMPETITIONS)}


def _error_page(e):
    """Pantalla amigable cuando la API falla y no hay datos guardados."""
    return render_template("error.html", error=e), 503


@bp.route("/")
def index():
    today = today_ar()
    try:
        day = date.fromisoformat(request.args.get("fecha", ""))
    except ValueError:
        day = today
    filtro = request.args.get("ver", "todos")

    try:
        raw = api.matches_for_day(day, today)
    except ApiError as e:
        return _error_page(e)

    # La API trabaja en UTC: dejamos solo los partidos que caen en este día en hora argentina
    matches = [normalize_match(m) for m in raw]
    matches = [m for m in matches if m["date"] == day and m["code"] in COMP_BY_CODE]
    matches.sort(key=lambda m: (COMP_ORDER[m["code"]], m["hour"]))

    n_live = sum(1 for m in matches if m["state"] == "live")
    if filtro == "vivo":
        shown = [m for m in matches if m["state"] == "live"]
    else:
        shown = matches

    groups = []
    for m in shown:
        if not groups or groups[-1][0]["code"] != m["code"]:
            groups.append((COMP_BY_CODE[m["code"]], []))
        groups[-1][1].append(m)

    if day == today:
        title = "Partidos de hoy"
    elif day == today - timedelta(days=1):
        title = "Partidos de ayer"
    elif day == today + timedelta(days=1):
        title = "Partidos de mañana"
    else:
        title = "Partidos del " + fecha_corta(day)

    return render_template(
        "index.html", groups=groups, day=day, title=title, subtitle=fecha_larga(day),
        prev_day=day - timedelta(days=1), next_day=day + timedelta(days=1), today=today,
        filtro=filtro, n_total=len(matches), n_live=n_live, has_live=n_live > 0 and day == today,
    )


@bp.route("/competiciones")
def competitions():
    return render_template("competitions.html")


@bp.route("/competiciones/<code>")
def competition_detail(code):
    code = code.upper()
    comp = COMP_BY_CODE.get(code)
    if comp is None:
        abort(404)

    errors = {}  # si una parte falla, el resto de la página igual se muestra

    # --- Tabla de posiciones ---
    tables, season = [], {}
    try:
        data = api.standings(code)
        season = data.get("season") or {}
        for s in data.get("standings", []):
            if s.get("type") != "TOTAL":
                continue
            group = s.get("group")
            title = ("Grupo " + group.replace("GROUP_", "")) if group and group.startswith("GROUP_") else None
            tables.append({"title": title, "rows": s.get("table", [])})
    except ApiError as e:
        errors["tabla"] = e

    # --- Partidos por fecha / ronda ---
    rounds, selected, current = [], 0, 0
    try:
        items = [{"utc": m.get("utcDate") or "", "n": normalize_match(m)} for m in api.competition_matches(code)]
        rounds = build_rounds(items)
        current = default_round(rounds)
        try:
            selected = int(request.args.get("ronda", current))
        except ValueError:
            selected = current
        selected = min(max(selected, 0), max(len(rounds) - 1, 0))
    except ApiError as e:
        errors["partidos"] = e

    # --- Estadísticas personales ---
    stats = []
    try:
        stats = build_stats(api.scorers(code))
    except ApiError as e:
        errors["stats"] = e

    if len(errors) == 3:  # no se pudo cargar nada
        return _error_page(next(iter(errors.values())))

    day_groups = group_by_date(rounds[selected]["matches"]) if rounds else []
    return render_template(
        "competition.html", comp=comp, tables=tables, season=season, stats=stats, errors=errors,
        rounds=rounds, selected=selected, current=current, day_groups=day_groups,
    )


@bp.route("/partido/<int:match_id>")
def match_detail(match_id):
    tab = request.args.get("tab", "resumen")
    if tab not in ("resumen", "alineaciones"):
        tab = "resumen"
    try:
        raw = api.match_detail(match_id)
    except ApiError as e:
        if e.kind == "not_found":
            abort(404)
        return _error_page(e)

    m = normalize_match_detail(raw)
    comp = COMP_BY_CODE.get(m["code"], {"code": m["code"], "name": m["comp_name"], "accent": "#22e07a"})
    return render_template("match.html", m=m, comp=comp, tab=tab, has_live=m["state"] == "live")


@bp.app_errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404
