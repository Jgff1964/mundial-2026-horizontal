FLAGS = {
    "GER": "🇩🇪", "ALEMANIA": "🇩🇪",
    "NOR": "🇳🇴", "NORUEGA": "🇳🇴",
    "KOR": "🇰🇷", "COREA DEL SUR": "🇰🇷",
    "SUI": "🇨🇭", "SUIZA": "🇨🇭",
    "NED": "🇳🇱", "PAÍSES BAJOS": "🇳🇱", "PAISES BAJOS": "🇳🇱",
    "MAR": "🇲🇦", "MARRUECOS": "🇲🇦",
    "COD": "🇨🇩", "RD CONGO": "🇨🇩", "DR CONGO": "🇨🇩",
    "GHA": "🇬🇭", "GHANA": "🇬🇭",
    "KSA": "🇸🇦", "SAU": "🇸🇦", "ARABIA SAUDITA": "🇸🇦",
    "AUT": "🇦🇹", "AUSTRIA": "🇦🇹",
    "USA": "🇺🇸", "ESTADOS UNIDOS": "🇺🇸",
    "NZL": "🇳🇿", "NUEVA ZELANDA": "🇳🇿",
    "BRA": "🇧🇷", "BRASIL": "🇧🇷",
    "SWE": "🇸🇪", "SUECIA": "🇸🇪",
    "CIV": "🇨🇮", "COSTA DE MARFIL": "🇨🇮",
    "FRA": "🇫🇷", "FRANCIA": "🇫🇷",
    "MEX": "🇲🇽", "MÉXICO": "🇲🇽", "MEXICO": "🇲🇽",
    "ENG": "🏴", "INGLATERRA": "🏴",
    "ARG": "🇦🇷", "ARGENTINA": "🇦🇷",
    "URU": "🇺🇾", "URUGUAY": "🇺🇾",
    "AUS": "🇦🇺", "AUSTRALIA": "🇦🇺",
    "IRN": "🇮🇷", "IRÁN": "🇮🇷", "IRAN": "🇮🇷",
    "CAN": "🇨🇦", "CANADÁ": "🇨🇦", "CANADA": "🇨🇦",
    "BEL": "🇧🇪", "BÉLGICA": "🇧🇪", "BELGICA": "🇧🇪",
    "COL": "🇨🇴", "COLOMBIA": "🇨🇴",
    "PAR": "🇵🇾", "PARAGUAY": "🇵🇾",
    "ESP": "🇪🇸", "ESPAÑA": "🇪🇸",
    "POR": "🇵🇹", "PORTUGAL": "🇵🇹",
    "JPN": "🇯🇵", "JAPÓN": "🇯🇵", "JAPON": "🇯🇵",
    "BIH": "🇧🇦", "BOSNIA Y HERZEGOVINA": "🇧🇦",
    "CZE": "🇨🇿", "CZECHIA": "🇨🇿", "REPÚBLICA CHECA": "🇨🇿", "CHEQUIA": "🇨🇿",
    "SCO": "🏴", "ESCOCIA": "🏴",
    "QAT": "🇶🇦", "CATAR": "🇶🇦", "QATAR": "🇶🇦",
    "ECU": "🇪🇨", "ECUADOR": "🇪🇨",
    "TUN": "🇹🇳", "TÚNEZ": "🇹🇳", "TUNEZ": "🇹🇳",
    "EGY": "🇪🇬", "EGIPTO": "🇪🇬",
}


def flag_for(value: str | None) -> str:
    if not value:
        return ""
    return FLAGS.get(value.upper().strip(), "")
