
FLAGS = {
    "ALEMANIA":"🇩🇪","NORUEGA":"🇳🇴","COREA DEL SUR":"🇰🇷","SUIZA":"🇨🇭",
    "PAÍSES BAJOS":"🇳🇱","PAISES BAJOS":"🇳🇱","MARRUECOS":"🇲🇦","RD CONGO":"🇨🇩",
    "GHANA":"🇬🇭","ARABIA SAUDITA":"🇸🇦","AUSTRIA":"🇦🇹","ESTADOS UNIDOS":"🇺🇸",
    "NUEVA ZELANDA":"🇳🇿","BRASIL":"🇧🇷","SUECIA":"🇸🇪","COSTA DE MARFIL":"🇨🇮",
    "FRANCIA":"🇫🇷","MÉXICO":"🇲🇽","MEXICO":"🇲🇽","INGLATERRA":"🏴",
    "ARGENTINA":"🇦🇷","URUGUAY":"🇺🇾","AUSTRALIA":"🇦🇺","IRÁN":"🇮🇷","IRAN":"🇮🇷",
    "CANADÁ":"🇨🇦","CANADA":"🇨🇦","BÉLGICA":"🇧🇪","BELGICA":"🇧🇪",
    "COLOMBIA":"🇨🇴","PARAGUAY":"🇵🇾","ESPAÑA":"🇪🇸","PORTUGAL":"🇵🇹",
    "JAPÓN":"🇯🇵","JAPON":"🇯🇵","BOSNIA Y HERZEGOVINA":"🇧🇦","REPÚBLICA CHECA":"🇨🇿",
    "CHEQUIA":"🇨🇿","ESCOCIA":"🏴","CATAR":"🇶🇦","QATAR":"🇶🇦","ECUADOR":"🇪🇨",
    "TÚNEZ":"🇹🇳","TUNEZ":"🇹🇳","EGIPTO":"🇪🇬","SUDÁFRICA":"🇿🇦","SUDAFRICA":"🇿🇦",
    "HAITÍ":"🇭🇹","HAITI":"🇭🇹","TURQUÍA":"🇹🇷","TURQUIA":"🇹🇷","CURAZAO":"🇨🇼",
    "CABO VERDE":"🇨🇻","SENEGAL":"🇸🇳","IRAK":"🇮🇶","IRAQ":"🇮🇶","JORDANIA":"🇯🇴",
    "ARGELIA":"🇩🇿","UZBEKISTÁN":"🇺🇿","UZBEKISTAN":"🇺🇿","PANAMÁ":"🇵🇦","PANAMA":"🇵🇦",
    "CROACIA":"🇭🇷"
}

PROMIEDOS_CODES = {
    "AR","AT","AU","BE","BI","BR","CA","CD","CH","CI","CO","CZ","DE","EC","ES","FR","GH",
    "IR","JP","KR","MA","MX","NL","NO","NZ","PY","QA","SA","SE","US","UY","ZA"
}

def clean_country_name(value):
    if value is None:
        return ""
    s = str(value).strip()
    if not s:
        return ""

    upper = s.upper().strip()

    # Los rivales no definidos quedan en blanco.
    if "RIVAL A DEFINIR" in upper or upper.startswith("RIVAL"):
        return ""
    if upper.startswith("MEJOR TERCERO"):
        return ""
    if upper.startswith("3") and "/" in upper:
        return ""

    # Mantener textos de rondas siguientes.
    if upper.startswith("GANADOR") or upper.startswith("PERDEDOR"):
        return s

    # Promiedos antepone códigos: AR ARGENTINA, BR BRASIL, DE ALEMANIA.
    parts = s.split(maxsplit=1)
    if len(parts) == 2 and parts[0].upper() in PROMIEDOS_CODES:
        s = parts[1].strip()

    # Eliminar restos colados.
    for bad in ["· rival pendiente", "rival pendiente", "pendiente"]:
        s = s.replace(bad, "").strip()

    return s

def flag_for(value):
    name = clean_country_name(value)
    if not name:
        return ""
    return FLAGS.get(name.upper().strip(), "")
