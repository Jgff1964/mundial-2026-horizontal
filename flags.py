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

def flag_for(value):
    if not value:
        return ""
    return FLAGS.get(str(value).strip().upper(), "")
