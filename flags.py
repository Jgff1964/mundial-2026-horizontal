import re
import unicodedata

FLAGS = {
    "ALEMANIA": "🇩🇪",
    "NORUEGA": "🇳🇴",
    "COREA DEL SUR": "🇰🇷",
    "SUIZA": "🇨🇭",
    "PAISES BAJOS": "🇳🇱",
    "MARRUECOS": "🇲🇦",
    "RD CONGO": "🇨🇩",
    "GHANA": "🇬🇭",
    "ARABIA SAUDITA": "🇸🇦",
    "AUSTRIA": "🇦🇹",
    "ESTADOS UNIDOS": "🇺🇸",
    "NUEVA ZELANDA": "🇳🇿",
    "BRASIL": "🇧🇷",
    "SUECIA": "🇸🇪",
    "COSTA DE MARFIL": "🇨🇮",
    "FRANCIA": "🇫🇷",
    "MEXICO": "🇲🇽",
    "INGLATERRA": "🏴",
    "ARGENTINA": "🇦🇷",
    "URUGUAY": "🇺🇾",
    "AUSTRALIA": "🇦🇺",
    "IRAN": "🇮🇷",
    "CANADA": "🇨🇦",
    "BELGICA": "🇧🇪",
    "COLOMBIA": "🇨🇴",
    "PARAGUAY": "🇵🇾",
    "ESPANA": "🇪🇸",
    "PORTUGAL": "🇵🇹",
    "JAPON": "🇯🇵",
    "BOSNIA Y HERZEGOVINA": "🇧🇦",
    "REPUBLICA CHECA": "🇨🇿",
    "CHEQUIA": "🇨🇿",
    "ESCOCIA": "🏴",
    "CATAR": "🇶🇦",
    "QATAR": "🇶🇦",
    "ECUADOR": "🇪🇨",
    "TUNEZ": "🇹🇳",
    "EGIPTO": "🇪🇬",
    "SUDAFRICA": "🇿🇦",
    "HAITI": "🇭🇹",
    "TURQUIA": "🇹🇷",
    "CURAZAO": "🇨🇼",
    "CABO VERDE": "🇨🇻",
    "SENEGAL": "🇸🇳",
    "IRAK": "🇮🇶",
    "IRAQ": "🇮🇶",
    "JORDANIA": "🇯🇴",
    "ARGELIA": "🇩🇿",
    "UZBEKISTAN": "🇺🇿",
    "PANAMA": "🇵🇦",
    "CROACIA": "🇭🇷",
}

PREFIXES = {
    "AR","AT","AU","BE","BI","BR","CA","CD","CH","CI","CO","CZ","DE","EC","ES","FR","GH",
    "IR","JP","KR","MA","MX","NL","NO","NZ","PY","QA","SA","SE","US","UY","ZA"
}

ALIASES = {
    "PAÍSES BAJOS": "PAISES BAJOS",
    "MÉXICO": "MEXICO",
    "IRÁN": "IRAN",
    "CANADÁ": "CANADA",
    "BÉLGICA": "BELGICA",
    "ESPAÑA": "ESPANA",
    "JAPÓN": "JAPON",
    "REPÚBLICA CHECA": "REPUBLICA CHECA",
    "TÚNEZ": "TUNEZ",
    "SUDÁFRICA": "SUDAFRICA",
    "HAITÍ": "HAITI",
    "TURQUÍA": "TURQUIA",
    "UZBEKISTÁN": "UZBEKISTAN",
    "PANAMÁ": "PANAMA",
    "UNITED STATES": "ESTADOS UNIDOS",
    "SOUTH KOREA": "COREA DEL SUR",
    "KOREA REPUBLIC": "COREA DEL SUR",
    "NETHERLANDS": "PAISES BAJOS",
    "IVORY COAST": "COSTA DE MARFIL",
    "COTE D IVOIRE": "COSTA DE MARFIL",
    "CÔTE D'IVOIRE": "COSTA DE MARFIL",
    "CZECHIA": "REPUBLICA CHECA",
    "DR CONGO": "RD CONGO",
    "CONGO DR": "RD CONGO",
    "SAUDI ARABIA": "ARABIA SAUDITA",
    "NEW ZEALAND": "NUEVA ZELANDA",
    "BOSNIA AND HERZEGOVINA": "BOSNIA Y HERZEGOVINA",
    "CAPE VERDE": "CABO VERDE",
}

def strip_accents(text):
    return "".join(c for c in unicodedata.normalize("NFD", str(text)) if unicodedata.category(c) != "Mn")

def canon_country_name(value):
    if value is None:
        return ""

    if isinstance(value, dict):
        for k in ("name", "nombre", "team", "equipo", "short_name", "shortName", "displayName", "title"):
            if value.get(k):
                return canon_country_name(value.get(k))
        return ""

    s = str(value).replace("\xa0", " ").strip()
    s = re.sub(r"\s+", " ", s)
    if not s:
        return ""

    s = re.sub(r"^[\U0001F1E6-\U0001F1FF]{2}\s*", "", s).strip()
    upper = s.upper().strip()

    if "RIVAL A DEFINIR" in upper or upper.startswith("RIVAL"):
        return ""
    if upper.startswith("MEJOR TERCERO"):
        return ""
    if re.fullmatch(r"[123][A-L](?:/[A-L])+", upper):
        return ""
    if upper.startswith("3") and "/" in upper:
        return ""
    if upper.startswith("GANADOR") or upper.startswith("PERDEDOR"):
        return upper

    m = re.match(r"^([A-Za-z]{2})\s+(.+)$", s)
    if m and m.group(1).upper() in PREFIXES:
        s = m.group(2).strip()

    s = re.sub(r"\b[123][A-L](?:/[A-L])+\b", "", s).strip()
    s = s.replace("· rival pendiente", "").replace("rival pendiente", "").replace("pendiente", "").strip()
    s = re.sub(r"\s+", " ", s)

    upper = s.upper().strip()
    if upper in ALIASES:
        return ALIASES[upper]

    no_accents = strip_accents(upper)
    if no_accents in ALIASES:
        return ALIASES[no_accents]
    return no_accents

clean_country_name = canon_country_name

def flag_for(value):
    return FLAGS.get(canon_country_name(value), "")

def display_country(value):
    c = canon_country_name(value)
    if not c:
        return ""
    if c.startswith("GANADOR") or c.startswith("PERDEDOR"):
        return c
    flag = FLAGS.get(c, "")
    return f"{flag} {c}".strip()
