
import re
import unicodedata

FLAGS = {
    "ALEMANIA":"🇩🇪",
    "NORUEGA":"🇳🇴",
    "COREA DEL SUR":"🇰🇷",
    "SUIZA":"🇨🇭",
    "PAÍSES BAJOS":"🇳🇱",
    "PAISES BAJOS":"🇳🇱",
    "MARRUECOS":"🇲🇦",
    "RD CONGO":"🇨🇩",
    "GHANA":"🇬🇭",
    "ARABIA SAUDITA":"🇸🇦",
    "AUSTRIA":"🇦🇹",
    "ESTADOS UNIDOS":"🇺🇸",
    "NUEVA ZELANDA":"🇳🇿",
    "BRASIL":"🇧🇷",
    "SUECIA":"🇸🇪",
    "COSTA DE MARFIL":"🇨🇮",
    "FRANCIA":"🇫🇷",
    "MÉXICO":"🇲🇽",
    "MEXICO":"🇲🇽",
    "INGLATERRA":"🏴",
    "ARGENTINA":"🇦🇷",
    "URUGUAY":"🇺🇾",
    "AUSTRALIA":"🇦🇺",
    "IRÁN":"🇮🇷",
    "IRAN":"🇮🇷",
    "CANADÁ":"🇨🇦",
    "CANADA":"🇨🇦",
    "BÉLGICA":"🇧🇪",
    "BELGICA":"🇧🇪",
    "COLOMBIA":"🇨🇴",
    "PARAGUAY":"🇵🇾",
    "ESPAÑA":"🇪🇸",
    "PORTUGAL":"🇵🇹",
    "JAPÓN":"🇯🇵",
    "JAPON":"🇯🇵",
    "BOSNIA Y HERZEGOVINA":"🇧🇦",
    "REPÚBLICA CHECA":"🇨🇿",
    "CHEQUIA":"🇨🇿",
    "ESCOCIA":"🏴",
    "CATAR":"🇶🇦",
    "QATAR":"🇶🇦",
    "ECUADOR":"🇪🇨",
    "TÚNEZ":"🇹🇳",
    "TUNEZ":"🇹🇳",
    "EGIPTO":"🇪🇬",
    "SUDÁFRICA":"🇿🇦",
    "SUDAFRICA":"🇿🇦",
    "HAITÍ":"🇭🇹",
    "HAITI":"🇭🇹",
    "TURQUÍA":"🇹🇷",
    "TURQUIA":"🇹🇷",
    "CURAZAO":"🇨🇼",
    "CABO VERDE":"🇨🇻",
    "SENEGAL":"🇸🇳",
    "IRAK":"🇮🇶",
    "IRAQ":"🇮🇶",
    "JORDANIA":"🇯🇴",
    "ARGELIA":"🇩🇿",
    "UZBEKISTÁN":"🇺🇿",
    "UZBEKISTAN":"🇺🇿",
    "PANAMÁ":"🇵🇦",
    "PANAMA":"🇵🇦",
    "CROACIA":"🇭🇷"
}

PROMIEDOS_CODES = {
    "AR","AT","AU","BE","BI","BR","CA","CD","CH","CI","CO","CZ","DE","EC","ES","FR","GH",
    "IR","JP","KR","MA","MX","NL","NO","NZ","PY","QA","SA","SE","US","UY","ZA"
}

def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def clean_country_name(value):
    if value is None:
        return ""

    s = str(value).replace("\xa0", " ").strip()
    s = re.sub(r"\s+", " ", s)
    if not s:
        return ""

    upper = s.upper().strip()

    # No mostrar placeholders, semillas ni terceros indefinidos.
    if "RIVAL A DEFINIR" in upper or upper.startswith("RIVAL"):
        return ""
    if upper.startswith("MEJOR TERCERO"):
        return ""
    if re.fullmatch(r"[123][A-L](?:/[A-L])+", upper):
        return ""
    if upper.startswith("3") and "/" in upper:
        return ""

    # Mantener textos de rondas futuras.
    if upper.startswith("GANADOR") or upper.startswith("PERDEDOR"):
        return s

    # Quitar bandera emoji previa si viene duplicada.
    s = re.sub(r"^[\U0001F1E6-\U0001F1FF]{2}\s*", "", s).strip()

    # Quitar prefijo Promiedos: "AR ARGENTINA", "BR BRASIL", "SA ARABIA SAUDITA".
    parts = s.split(maxsplit=1)
    if len(parts) == 2 and parts[0].upper() in PROMIEDOS_CODES:
        s = parts[1].strip()

    # Limpiar restos.
    s = re.sub(r"\b[123][A-L](?:/[A-L])+\b", "", s).strip()
    s = s.replace("· rival pendiente", "").replace("rival pendiente", "").replace("pendiente", "").strip()
    s = re.sub(r"\s+", " ", s)

    return s

def flag_for(value):
    name = clean_country_name(value)
    if not name:
        return ""
    direct = FLAGS.get(name.upper())
    if direct:
        return direct
    key = strip_accents(name.upper())
    for country, flag in FLAGS.items():
        if strip_accents(country.upper()) == key:
            return flag
    return ""
