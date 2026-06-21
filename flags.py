
import re, unicodedata
FLAGS={"ALEMANIA":"🇩🇪","NORUEGA":"🇳🇴","COREA DEL SUR":"🇰🇷","SUIZA":"🇨🇭","PAISES BAJOS":"🇳🇱","MARRUECOS":"🇲🇦","RD CONGO":"🇨🇩","GHANA":"🇬🇭","ARABIA SAUDITA":"🇸🇦","AUSTRIA":"🇦🇹","ESTADOS UNIDOS":"🇺🇸","NUEVA ZELANDA":"🇳🇿","BRASIL":"🇧🇷","SUECIA":"🇸🇪","COSTA DE MARFIL":"🇨🇮","FRANCIA":"🇫🇷","MEXICO":"🇲🇽","INGLATERRA":"🏴","ARGENTINA":"🇦🇷","URUGUAY":"🇺🇾","AUSTRALIA":"🇦🇺","IRAN":"🇮🇷","CANADA":"🇨🇦","BELGICA":"🇧🇪","COLOMBIA":"🇨🇴","PARAGUAY":"🇵🇾","ESPANA":"🇪🇸","PORTUGAL":"🇵🇹","JAPON":"🇯🇵","BOSNIA Y HERZEGOVINA":"🇧🇦","REPUBLICA CHECA":"🇨🇿","CHEQUIA":"🇨🇿","ESCOCIA":"🏴","CATAR":"🇶🇦","QATAR":"🇶🇦","ECUADOR":"🇪🇨","TUNEZ":"🇹🇳","EGIPTO":"🇪🇬","SUDAFRICA":"🇿🇦","HAITI":"🇭🇹","TURQUIA":"🇹🇷","CURAZAO":"🇨🇼","CABO VERDE":"🇨🇻","SENEGAL":"🇸🇳","IRAK":"🇮🇶","IRAQ":"🇮🇶","JORDANIA":"🇯🇴","ARGELIA":"🇩🇿","UZBEKISTAN":"🇺🇿","PANAMA":"🇵🇦","CROACIA":"🇭🇷"}
PREFIXES={"AR","AT","AU","BE","BI","BR","CA","CD","CH","CI","CO","CZ","DE","EC","ES","FR","GH","IR","JP","KR","MA","MX","NL","NO","NZ","PY","QA","SA","SE","US","UY","ZA"}
ALIASES={"PAÍSES BAJOS":"PAISES BAJOS","MÉXICO":"MEXICO","IRÁN":"IRAN","CANADÁ":"CANADA","BÉLGICA":"BELGICA","ESPAÑA":"ESPANA","JAPÓN":"JAPON","REPÚBLICA CHECA":"REPUBLICA CHECA","TÚNEZ":"TUNEZ","SUDÁFRICA":"SUDAFRICA","HAITÍ":"HAITI","TURQUÍA":"TURQUIA","UZBEKISTÁN":"UZBEKISTAN","PANAMÁ":"PANAMA"}
def strip_accents(s): return ''.join(c for c in unicodedata.normalize('NFD',str(s)) if unicodedata.category(c)!='Mn')
def canon_country_name(v):
    if v is None: return ''
    s=re.sub(r'\s+',' ',str(v).replace('\xa0',' ').strip())
    if not s: return ''
    s=re.sub(r'^[\U0001F1E6-\U0001F1FF]{2}\s*','',s).strip()
    u=s.upper()
    if 'RIVAL A DEFINIR' in u or u.startswith('RIVAL') or u.startswith('MEJOR TERCERO'): return ''
    if re.fullmatch(r'[123][A-L](?:/[A-L])+',u) or (u.startswith('3') and '/' in u): return ''
    if u.startswith('GANADOR') or u.startswith('PERDEDOR'): return u
    m=re.match(r'^([A-Za-z]{2})\s+(.+)$',s)
    if m and m.group(1).upper() in PREFIXES: s=m.group(2).strip()
    s=re.sub(r'\b[123][A-L](?:/[A-L])+\b','',s).strip()
    s=s.replace('· rival pendiente','').replace('rival pendiente','').replace('pendiente','').strip()
    u=s.upper()
    if u in ALIASES: return ALIASES[u]
    return strip_accents(u)
clean_country_name=canon_country_name
def flag_for(v): return FLAGS.get(canon_country_name(v),'')
def display_country(v):
    c=canon_country_name(v)
    if not c: return ''
    if c.startswith('GANADOR') or c.startswith('PERDEDOR'): return c
    return (FLAGS.get(c,'')+' '+c).strip()
