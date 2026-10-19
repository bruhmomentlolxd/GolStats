"""Funciones auxiliares: horas, traducciones y conversión de las respuestas de la API
a diccionarios simples que usan las plantillas."""
from datetime import datetime, timedelta, timezone

AR_TZ = timezone(timedelta(hours=-3))  # Argentina (no usa horario de verano)

DIAS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
DIAS_LARGOS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
MESES_LARGOS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                "septiembre", "octubre", "noviembre", "diciembre"]

STAGES = {
    "REGULAR_SEASON": "Temporada regular", "LEAGUE_STAGE": "Fase de liga", "GROUP_STAGE": "Fase de grupos",
    "PLAYOFFS": "Playoffs", "LAST_64": "Ronda de 64", "LAST_32": "16avos de final", "LAST_16": "Octavos de final",
    "ROUND_OF_16": "Octavos de final", "QUARTER_FINALS": "Cuartos de final", "SEMI_FINALS": "Semifinales",
    "THIRD_PLACE": "Tercer puesto", "FINAL": "Final", "PRELIMINARY_ROUND": "Ronda preliminar",
    "QUALIFICATION": "Clasificación", "PRELIMINARY_SEMI_FINALS": "Semifinales preliminares",
}
LEAGUE_LIKE = ("REGULAR_SEASON", "LEAGUE_STAGE", "GROUP_STAGE")

POSITIONS_ES = {
    "Goalkeeper": "Arquero", "Defence": "Defensor", "Centre-Back": "Defensor central", "Left-Back": "Lateral izquierdo",
    "Right-Back": "Lateral derecho", "Midfield": "Mediocampista", "Defensive Midfield": "Mediocentro defensivo",
    "Central Midfield": "Mediocentro", "Attacking Midfield": "Mediapunta", "Left Midfield": "Volante izquierdo",
    "Right Midfield": "Volante derecho", "Offence": "Delantero", "Centre-Forward": "Delantero centro",
    "Left Winger": "Extremo izquierdo", "Right Winger": "Extremo derecho",
}


def stage_label(stage):
    if not stage:
        return ""
    return STAGES.get(stage, stage.replace("_", " ").capitalize())


def to_local(utc_str):
    """'2026-10-19T19:00:00Z' -> datetime en hora argentina."""
    if not utc_str:
        return None
    dt = datetime.strptime(utc_str[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    return dt.astimezone(AR_TZ)


def today_ar():
    return datetime.now(AR_TZ).date()


def fecha_corta(d):
    """date -> 'lun 19 oct'"""
    return f"{DIAS[d.weekday()]} {d.day} {MESES[d.month - 1]}"


def fecha_larga(d):
    return f"{DIAS_LARGOS[d.weekday()].capitalize()} {d.day} de {MESES_LARGOS[d.month - 1]} de {d.year}"


# ---------- Partidos ----------

STATUS_LABELS = {
    "IN_PLAY": "EN VIVO", "PAUSED": "Entretiempo", "FINISHED": "Final", "POSTPONED": "Postergado",
    "SUSPENDED": "Suspendido", "CANCELLED": "Cancelado", "AWARDED": "Adjudicado",
}


def _team(t):
    t = t or {}
    return {
        "id": t.get("id"),
        "name": t.get("name") or "Por definir",
        "short": t.get("shortName") or t.get("name") or "Por definir",
        "tla": t.get("tla") or "",
        "crest": t.get("crest"),
    }


def normalize_match(m):
    """Convierte un partido de la API en un diccionario simple."""
    status = m.get("status", "")
    local = to_local(m.get("utcDate"))
    score = m.get("score") or {}
    ft = score.get("fullTime") or {}
    ht = score.get("halfTime") or {}
    pens = score.get("penalties") or {}

    if status in ("IN_PLAY", "PAUSED"):
        state = "live"
    elif status in ("FINISHED", "AWARDED"):
        state = "finished"
    elif status in ("SCHEDULED", "TIMED"):
        state = "scheduled"
    else:
        state = "other"

    hour = local.strftime("%H:%M") if local else ""
    has_score = ft.get("home") is not None and ft.get("away") is not None
    comp = m.get("competition") or {}

    return {
        "id": m.get("id"),
        "code": comp.get("code"),
        "comp_name": comp.get("name"),
        "stage": m.get("stage"),
        "stage_label": stage_label(m.get("stage")),
        "matchday": m.get("matchday"),
        "group": m.get("group"),
        "status": status,
        "state": state,
        "status_label": STATUS_LABELS.get(status, hour),
        "date": local.date() if local else None,
        "hour": hour,
        "home": _team(m.get("homeTeam")),
        "away": _team(m.get("awayTeam")),
        "hg": ft.get("home") if has_score else None,
        "ag": ft.get("away") if has_score else None,
        "ht": f"{ht['home']}-{ht['away']}" if ht.get("home") is not None and ht.get("away") is not None else None,
        "pens": f"{pens['home']}-{pens['away']}" if pens.get("home") is not None else None,
        "winner": score.get("winner"),
    }


def build_rounds(matches):
    """Agrupa los partidos de una competición en 'rondas' (Fecha 1, Fecha 2, Octavos...)."""
    rounds, index = [], {}
    for m in sorted(matches, key=lambda x: x["utc"]):
        n = m["n"]
        if n["stage"] in LEAGUE_LIKE and n["matchday"]:
            key = ("league", n["matchday"])
            label = f"Fecha {n['matchday']}"
        else:
            key = ("stage", n["stage"])
            label = n["stage_label"] or "Partidos"
        if key not in index:
            index[key] = len(rounds)
            rounds.append({"label": label, "matches": []})
        rounds[index[key]]["matches"].append(n)
    return rounds


def default_round(rounds):
    """La primera ronda con algún partido sin terminar; si no hay, la última."""
    for i, r in enumerate(rounds):
        if any(m["state"] != "finished" for m in r["matches"]):
            return i
    return max(len(rounds) - 1, 0)


# ---------- Detalle del partido ----------

def _pos_row(position):
    p = (position or "").lower()
    if "goal" in p:
        return 0
    if "back" in p or "defen" in p:
        return 1
    if "forward" in p or "wing" in p or "offence" in p or "striker" in p:
        return 3
    return 2


def _short_name(full):
    parts = (full or "").split()
    return parts[-1] if parts else ""


def _lineup(team_raw):
    lineup = team_raw.get("lineup") or []
    bench = team_raw.get("bench") or []
    rows = [[], [], [], []]
    for p in lineup:
        rows[_pos_row(p.get("position"))].append(
            {"name": p.get("name"), "short": _short_name(p.get("name")), "number": p.get("shirtNumber")})
    coach = (team_raw.get("coach") or {}).get("name")
    return {
        "formation": team_raw.get("formation"),
        "rows": rows if lineup else None,
        "bench": [{"name": p.get("name"), "number": p.get("shirtNumber"),
                   "position": POSITIONS_ES.get(p.get("position"), p.get("position") or "")} for p in bench],
        "coach": coach,
    }


def normalize_match_detail(raw):
    base = normalize_match(raw)
    base["local_date"] = fecha_larga(base["date"]) if base["date"] else ""
    base["venue"] = raw.get("venue")
    refs = raw.get("referees") or []
    base["referee"] = next((r.get("name") for r in refs if r.get("type") == "REFEREE"), None) or (refs[0].get("name") if refs else None)

    home_id = base["home"]["id"]

    def side(team):
        return "home" if (team or {}).get("id") == home_id else "away"

    events = []
    for g in raw.get("goals") or []:
        kind = {"OWN": "own_goal", "PENALTY": "penalty"}.get(g.get("type"), "goal")
        detail = ""
        if kind == "own_goal":
            detail = "(en contra)"
        elif kind == "penalty":
            detail = "(penal)"
        elif (g.get("assist") or {}).get("name"):
            detail = f"Asist.: {g['assist']['name']}"
        score = g.get("score") or {}
        events.append({
            "minute": g.get("minute") or 0, "extra": g.get("injuryTime") or 0, "kind": kind, "side": side(g.get("team")),
            "title": (g.get("scorer") or {}).get("name", ""), "detail": detail,
            "score": f"{score['home']}-{score['away']}" if score.get("home") is not None else "",
        })
    for b in raw.get("bookings") or []:
        card = b.get("card")
        kind = "red" if card == "RED" else "yellow_red" if card == "YELLOW_RED" else "yellow"
        events.append({"minute": b.get("minute") or 0, "extra": 0, "kind": kind, "side": side(b.get("team")),
                       "title": (b.get("player") or {}).get("name", ""), "detail": "", "score": ""})
    for s in raw.get("substitutions") or []:
        events.append({"minute": s.get("minute") or 0, "extra": 0, "kind": "sub", "side": side(s.get("team")),
                       "title": (s.get("playerIn") or {}).get("name", ""),
                       "detail": "Sale: " + ((s.get("playerOut") or {}).get("name") or ""), "score": ""})
    events.sort(key=lambda e: (e["minute"], e["extra"]))
    base["events"] = events

    base["lineups"] = {"home": _lineup(raw.get("homeTeam") or {}), "away": _lineup(raw.get("awayTeam") or {})}
    base["has_lineups"] = bool(base["lineups"]["home"]["rows"] or base["lineups"]["away"]["rows"])
    return base


# ---------- Estadísticas personales ----------

def build_stats(scorers):
    """Arma los rankings con lo que informa la API en /scorers: goles, asistencias,
    penales y promedio de goles por partido (este último se calcula)."""
    def row(s, value):
        return {"name": (s.get("player") or {}).get("name", ""), "team": _team(s.get("team")), "value": value}

    goals = [s for s in scorers if s.get("goals")]
    assists = sorted([s for s in scorers if s.get("assists")], key=lambda s: (-s["assists"], -(s.get("goals") or 0)))
    pens = sorted([s for s in scorers if s.get("penalties")], key=lambda s: (-s["penalties"], -(s.get("goals") or 0)))
    avg = sorted([s for s in scorers if s.get("goals") and (s.get("playedMatches") or 0) >= 3],
                 key=lambda s: -s["goals"] / s["playedMatches"])
    played = sorted([s for s in scorers if s.get("playedMatches")], key=lambda s: -s["playedMatches"])

    cards = [
        {"title": "Goles", "rows": [row(s, s["goals"]) for s in goals]},
        {"title": "Asistencias", "rows": [row(s, s["assists"]) for s in assists]},
        {"title": "Penales convertidos", "rows": [row(s, s["penalties"]) for s in pens]},
        {"title": "Promedio de goles por partido", "rows": [row(s, f"{s['goals'] / s['playedMatches']:.2f}") for s in avg]},
        {"title": "Partidos jugados (goleadores)", "rows": [row(s, s["playedMatches"]) for s in played]},
    ]
    return [c for c in cards if c["rows"]]


def group_by_date(matches):
    """[(fecha, [partidos])] manteniendo el orden."""
    groups = []
    for m in matches:
        if not groups or groups[-1][0] != m["date"]:
            groups.append((m["date"], []))
        groups[-1][1].append(m)
    return groups
