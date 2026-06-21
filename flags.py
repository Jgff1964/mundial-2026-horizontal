
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

# Códigos ISO/Promiedos que NO deben mostrarse.
PROMIEDOS_PREFIXES = {
    "AR", "AT", "AU", "BE", "BI", "BR", "CA", "CD", "CH", "CI", "CO", "CZ",
    "DE", "EC", "ES", "FR", "GH", "IR", "JP", "KR", "MA", "MX", "NL", "NO",
    "NZ", "PY", "QA", "SA", "SE", "US", "UY", "ZA"
}

# Alias y nombres con tilde.
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
}

def strip_accents(text):
    text = str(text)
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")

def canon_country_name(value):
    """
    Devuelve SOLO el país limpio.
    Ejemplos:
    'AR ARGENTINA' -> 'ARGENTINA'
    'SA ARABIA SAUDITA' -> 'ARABIA SAUDITA'
    'BR BRASIL' -> 'BRASIL'
    'RIVAL A DEFINIR' -> ''
    """
    if value is None:
        return ""

    s = str(value).replace("\xa0", " ").strip()
    s = re.sub(r"\s+", " ", s)
    if not s:
        return ""

    # Quitar banderas emoji si vinieran duplicadas desde otra fuente.
    s = re.sub(r"^[\U0001F1E6-\U0001F1FF]{2}\s*", "", s).strip()

    upper = s.upper().strip()

    # No mostrar semillas/placeholders.
    if "RIVAL A DEFINIR" in upper or upper.startswith("RIVAL"):
        return ""
    if upper.startswith("MEJOR TERCERO"):
        return ""
    if re.fullmatch(r"[123][A-L](?:/[A-L])+", upper):
        return ""
    if upper.startswith("3") and "/" in upper:
        return ""

    # Mantener rondas posteriores.
    if upper.startswith("GANADOR") or upper.startswith("PERDEDOR"):
        return s

    # Quitar prefijo Promiedos al inicio.
    # La clave: quitar SIEMPRE los dos primeros caracteres si son un código conocido y luego hay país.
    m = re.match(r"^([A-Za-z]{2})\s+(.+)$", s)
    if m and m.group(1).upper() in PROMIEDOS_PREFIXES:
        s = m.group(2).strip()

    # Quitar cualquier semilla colada.
    s = re.sub(r"\b[123][A-L](?:/[A-L])+\b", "", s).strip()
    s = s.replace("· rival pendiente", "").replace("rival pendiente", "").replace("pendiente", "").strip()
    s = re.sub(r"\s+", " ", s)

    upper = s.upper().strip()
    if upper in ALIASES:
        return ALIASES[upper]

    no_accents = strip_accents(upper)
    if no_accents in FLAGS:
        return no_accents

    return upper

# Compatibilidad con versiones previas
clean_country_name = canon_country_name

def flag_for(value):
    country = canon_country_name(value)
    if not country:
        return ""
    return FLAGS.get(country, "")

def display_country(value):
    """
    Devuelve el texto final para SVG:
    bandera + país, sin abreviatura.
    """
    country = canon_country_name(value)
    if not country:
        return ""
    if country.startswith("GANADOR") or country.startswith("PERDEDOR"):
        return country
    flag = FLAGS.get(country, "")
    return f"{flag} {country}".strip()
