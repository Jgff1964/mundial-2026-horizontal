from __future__ import annotations
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from models import Match

GROUPS = list("ABCDEFGHIJKL")
ROUND_OF_32 = {73:("2A","2B","LA"),74:("1E","3?","BOS"),75:("1F","2C","MTY"),76:("1C","2F","HOU"),77:("1I","3?","NYNJ"),78:("2E","2I","DAL"),79:("1A","3?","CDMX"),80:("1L","3?","ATL"),81:("1D","3?","SFBA"),82:("1G","3?","SEA"),83:("2K","2L","TOR"),84:("1H","2J","LA"),85:("1B","3?","VAN"),86:("1J","2H","MIA"),87:("1K","3?","KC"),88:("2D","2G","DAL")}
ROUND_OF_16 = {89:(74,77,"PHI"),90:(73,75,"HOU"),91:(76,78,"NYNJ"),92:(79,80,"CDMX"),93:(83,84,"DAL"),94:(81,82,"SEA"),95:(86,88,"ATL"),96:(85,87,"VAN")}
QUARTERS = {97:(89,90,"BOS"),98:(93,94,"LA"),99:(91,92,"MIA"),100:(95,96,"KC")}
SEMIS = {101:(97,98,"DAL"),102:(99,100,"ATL")}
THIRD_PLACE = {103:(101,102,"MIA")}
FINAL = {104:(101,102,"NYNJ")}


def normalize_team(name) -> str:
    """
    FIFA a veces devuelve el equipo como string, dict o list.
    Esta función lo normaliza a texto para evitar:
    TypeError: cannot use 'list' as a dict key
    """
    if name is None:
        return ""

    if isinstance(name, list):
        # Tomar el primer elemento útil de la lista.
        for item in name:
            value = normalize_team(item)
            if value:
                return value
        return ""

    if isinstance(name, dict):
        # Formatos posibles que FIFA puede devolver.
        for key in [
            "name", "Name", "shortName", "ShortName", "displayName",
            "teamName", "TeamName", "Description", "countryName",
            "CountryName", "Abbreviation", "abbreviation", "code", "Code"
        ]:
            value = name.get(key)
            if value:
                return normalize_team(value)
        return ""

    if not isinstance(name, str):
        name = str(name)

    name = name.strip()
    if not name:
        return ""

    aliases = {
        "Korea Republic": "Corea del Sur",
        "Czechia": "República Checa",
        "Congo DR": "RD Congo",
        "DR Congo": "RD Congo",
        "USA": "Estados Unidos",
        "IR Iran": "Irán",
        "Türkiye": "Turquía",
        "Saudi Arabia": "Arabia Saudita",
        "Netherlands": "Países Bajos",
        "Côte d'Ivoire": "Costa de Marfil",
        "Ivory Coast": "Costa de Marfil",
        "New Zealand": "Nueva Zelanda",
        "Bosnia and Herzegovina": "Bosnia y Herzegovina",
        "England": "Inglaterra",
        "Spain": "España",
        "Switzerland": "Suiza",
        "Morocco": "Marruecos",
        "Germany": "Alemania",
        "Brazil": "Brasil",
        "France": "Francia",
        "Mexico": "México",
        "Argentina": "Argentina",
        "Uruguay": "Uruguay",
        "Belgium": "Bélgica",
        "Colombia": "Colombia",
        "Paraguay": "Paraguay",
        "Austria": "Austria",
        "Norway": "Noruega",
        "Japan": "Japón",
        "Sweden": "Suecia",
        "Australia": "Australia",
        "Ghana": "Ghana",
        "Canada": "Canadá",
        "Portugal": "Portugal",
    }
    return aliases.get(name, name)

def is_finished(m: Match) -> bool:
    return m.home_score is not None and m.away_score is not None and (m.status or "").upper() in {"FINISHED","FULL_TIME","FT","COMPLETED","AFTER_EXTRA_TIME","PENALTIES"}

def build_group_tables(matches: List[Match]) -> Dict[str, List[dict]]:
    tables = {g: defaultdict(lambda: {"team":"","code":"","group":g,"played":0,"won":0,"drawn":0,"lost":0,"gf":0,"ga":0,"gd":0,"pts":0,"fair_play":0}) for g in GROUPS}
    for m in matches:
        if not m.group or m.group not in tables or m.match_no > 72: continue
        home, away = normalize_team(m.home), normalize_team(m.away)
        if not home or not away:
            continue
        ht, at = tables[m.group][home], tables[m.group][away]
        ht["team"], ht["code"] = home, m.home_code or ""
        at["team"], at["code"] = away, m.away_code or ""
        if not is_finished(m): continue
        hs, aw = m.home_score, m.away_score
        ht["played"] += 1; at["played"] += 1
        ht["gf"] += hs; ht["ga"] += aw; at["gf"] += aw; at["ga"] += hs
        if hs > aw: ht["won"] += 1; at["lost"] += 1; ht["pts"] += 3
        elif aw > hs: at["won"] += 1; ht["lost"] += 1; at["pts"] += 3
        else: ht["drawn"] += 1; at["drawn"] += 1; ht["pts"] += 1; at["pts"] += 1
    final = {}
    for g, rows in tables.items():
        arr = []
        for row in rows.values():
            row["gd"] = row["gf"] - row["ga"]; arr.append(row)
        arr.sort(key=lambda r:(r["pts"],r["gd"],r["gf"],-r.get("fair_play",0),r["team"]), reverse=True)
        final[g] = arr
    return final

def qualifiers_from_tables(tables):
    q, third_rows = {}, []
    for g in GROUPS:
        rows = tables.get(g, [])
        if len(rows) >= 1: q[f"1{g}"] = rows[0]
        if len(rows) >= 2: q[f"2{g}"] = rows[1]
        if len(rows) >= 3:
            rows[2]["third_group"] = g; third_rows.append(rows[2])
    third_rows.sort(key=lambda r:(r["pts"],r["gd"],r["gf"],-r.get("fair_play",0),r["team"]), reverse=True)
    for row in third_rows[:8]: q[f"3{row['third_group']}"] = row
    return q

def team_label(q, seed, include_thirds):
    if seed == "3?": return ("Rival a definir","rival pendiente")
    if seed.startswith("3") and not include_thirds: return ("Rival a definir","rival pendiente")
    row = q.get(seed)
    if not row: return ("Rival a definir",f"{seed} · pendiente")
    return (row["team"], seed)

def make_bracket(matches, include_thirds=False):
    tables = build_group_tables(matches); q = qualifiers_from_tables(tables)
    bracket = {"r32":{},"r16":{},"qf":{},"sf":{},"third":{},"final":{},"tables":tables}
    for no,(s1,s2,venue) in ROUND_OF_32.items():
        t1,_ = team_label(q,s1,include_thirds)
        t2 = "Rival a definir" if s2 == "3?" else team_label(q,s2,include_thirds)[0]
        actual = next((m for m in matches if m.match_no == no), None)
        if actual and (actual.home or actual.away):
            t1 = normalize_team(actual.home) or t1; t2 = normalize_team(actual.away) or t2
        bracket["r32"][no] = {"venue":venue,"home":t1,"away":t2,"sub":f"{s1} vs {s2}" if s2!="3?" else f"{s1} · rival pendiente","winner":_winner(matches,no)}
    for no,(a,b,v) in ROUND_OF_16.items(): bracket["r16"][no] = _future(matches,no,a,b,v)
    for no,(a,b,v) in QUARTERS.items(): bracket["qf"][no] = _future(matches,no,a,b,v)
    for no,(a,b,v) in SEMIS.items(): bracket["sf"][no] = _future(matches,no,a,b,v)
    for no,(a,b,v) in THIRD_PLACE.items(): bracket["third"][no] = _future(matches,no,a,b,v,loser=True)
    for no,(a,b,v) in FINAL.items(): bracket["final"][no] = _future(matches,no,a,b,v)
    return bracket

def _winner(matches,no):
    m = next((x for x in matches if x.match_no == no), None)
    if not m or not is_finished(m): return None
    if m.winner: return normalize_team(m.winner)
    if m.home_score > m.away_score: return normalize_team(m.home)
    if m.away_score > m.home_score: return normalize_team(m.away)
    return None

def _future(matches,no,a,b,venue,loser=False):
    actual = next((m for m in matches if m.match_no == no), None)
    if actual and (actual.home or actual.away): home, away = normalize_team(actual.home), normalize_team(actual.away)
    else: home, away = f"{'Perdedor' if loser else 'Ganador'} M{a}", f"{'Perdedor' if loser else 'Ganador'} M{b}"
    return {"venue":venue,"home":home,"away":away,"sub":"","winner":_winner(matches,no)}
