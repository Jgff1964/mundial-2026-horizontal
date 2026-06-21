import json
import re
from pathlib import Path
from flags import clean_country_name

ROUND_OF_32 = {
    73: ("2A", "2B", "LA"),
    74: ("1E", "3A/B/C/D/F", "BOS"),
    75: ("1F", "2C", "MTY"),
    76: ("1C", "2F", "HOU"),
    77: ("1I", "3C/D/F/G/H", "NYNJ"),
    78: ("2E", "2I", "DAL"),
    79: ("1A", "3C/E/F/H/I", "CDMX"),
    80: ("1L", "3E/H/I/J/K", "ATL"),
    81: ("1D", "3B/E/F/I/J", "SFBA"),
    82: ("1G", "3A/E/H/I/J", "SEA"),
    83: ("2K", "2L", "TOR"),
    84: ("1H", "2J", "LA"),
    85: ("1B", "3E/F/G/I/J", "VAN"),
    86: ("1J", "2H", "MIA"),
    87: ("1K", "3D/E/I/J/L", "KC"),
    88: ("2D", "2G", "DAL"),
}
ROUND_OF_16 = {89:(74,77,"PHI"),90:(73,75,"HOU"),91:(76,78,"NYNJ"),92:(79,80,"CDMX"),93:(83,84,"DAL"),94:(81,82,"SEA"),95:(86,88,"ATL"),96:(85,87,"VAN")}
QUARTERS = {97:(89,90,"BOS"),98:(93,94,"LA"),99:(91,92,"MIA"),100:(95,96,"KC")}
SEMIS = {101:(97,98,"DAL"),102:(99,100,"ATL")}
THIRD = {103:(101,102,"MIA")}
FINAL = {104:(101,102,"NYNJ")}

def load_zones(path="zonas_validadas.json"):
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))

def seed_like(value):
    if not value:
        return True
    v = str(value).strip().upper()
    if v in {"RIVAL A DEFINIR", "RIVAL DEFINIR"}:
        return True
    if re.fullmatch(r"[123][A-L](?:/[A-L])*", v):
        return True
    if v.startswith("GANADOR") or v.startswith("PERDEDOR"):
        return True
    return False

def resolve_seed(seed, zones, include_thirds=False):
    seed = str(seed).strip().upper()
    if re.fullmatch(r"[12][A-L]", seed):
        pos = int(seed[0]) - 1
        group = seed[1]
        rows = zones.get(group, [])
        if len(rows) > pos:
            return clean_country_name(rows[pos].get("team", seed))
        return ""

    if seed.startswith("3"):
        return ""

    return clean_country_name(seed)


def make_bracket_from_zones(zones, include_thirds=False):
    out = {"r32":{}, "r16":{}, "qf":{}, "sf":{}, "third":{}, "final":{}, "source":"zonas_validadas.json"}
    for no, (s1, s2, venue) in ROUND_OF_32.items():
        out["r32"][no] = {
            "venue": venue,
            "home": resolve_seed(s1, zones, include_thirds),
            "away": resolve_seed(s2, zones, include_thirds),
            "sub": f"{s1} vs {s2}" if not s2.startswith("3") else f"{s1} · rival pendiente",
            "winner": None
        }
    for no, (a,b,v) in ROUND_OF_16.items():
        out["r16"][no] = {"venue":v, "home":f"Ganador M{a}", "away":f"Ganador M{b}", "sub":"", "winner":None}
    for no, (a,b,v) in QUARTERS.items():
        out["qf"][no] = {"venue":v, "home":f"Ganador M{a}", "away":f"Ganador M{b}", "sub":"", "winner":None}
    for no, (a,b,v) in SEMIS.items():
        out["sf"][no] = {"venue":v, "home":f"Ganador M{a}", "away":f"Ganador M{b}", "sub":"", "winner":None}
    for no, (a,b,v) in THIRD.items():
        out["third"][no] = {"venue":v, "home":f"Perdedor M{a}", "away":f"Perdedor M{b}", "sub":"", "winner":None}
    for no, (a,b,v) in FINAL.items():
        out["final"][no] = {"venue":v, "home":f"Ganador M{a}", "away":f"Ganador M{b}", "sub":"", "winner":None}
    return out

def overlay_promiedos_bracket(base, prom):
    if not prom:
        return base
    changed = 0
    for round_key in ["r32","r16","qf","sf","third","final"]:
        for no, data in prom.get(round_key, {}).items():
            no = int(no)
            if no not in base.get(round_key, {}):
                continue
            h_clean = clean_country_name(data.get("home"))
            a_clean = clean_country_name(data.get("away"))
            if h_clean and a_clean and not seed_like(h_clean) and not seed_like(a_clean):
                base[round_key][no]["home"] = h_clean
                base[round_key][no]["away"] = a_clean
                base[round_key][no]["sub"] = ""
                changed += 1
    base["source"] = "Promiedos armado" if changed else "Zonas validadas + estructura Promiedos"
    base["promiedos_replacements"] = changed
    return base
