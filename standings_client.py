
import re, requests, unicodedata
from bs4 import BeautifulSoup
from flags import canon_country_name
PROMIEDOS_URL='https://www.promiedos.com.ar/league/fifa-world-cup/fjda'
CANCHALLENA_URL='https://canchallena.lanacion.com.ar/futbol/mundial/'
GROUP_TEAMS={'A':['México','Corea del Sur','República Checa','Sudáfrica'],'B':['Canadá','Suiza','Bosnia y Herzegovina','Catar'],'C':['Brasil','Marruecos','Escocia','Haití'],'D':['Estados Unidos','Australia','Paraguay','Turquía'],'E':['Alemania','Costa de Marfil','Ecuador','Curazao'],'F':['Países Bajos','Suecia','Japón','Túnez'],'G':['Nueva Zelanda','Irán','Bélgica','Egipto'],'H':['Uruguay','Arabia Saudita','España','Cabo Verde'],'I':['Noruega','Francia','Senegal','Irak'],'J':['Argentina','Austria','Jordania','Argelia'],'K':['Colombia','RD Congo','Portugal','Uzbekistán'],'L':['Inglaterra','Ghana','Panamá','Croacia']}
class StandingsClient:
    def __init__(self,timeout=25):
        self.timeout=timeout; self.s=requests.Session(); self.s.headers.update({'User-Agent':'Mozilla/5.0 Chrome/126 Safari/537.36'})
    def fetch_zones(self):
        errs=[]
        for name,url in [('Promiedos',PROMIEDOS_URL),('CanchaLaNacion',CANCHALLENA_URL)]:
            try:
                zones=self._parse(self._text(url))
                if len(zones)>=8: return zones,name
            except Exception as e: errs.append(f'{name}: {e}')
        raise RuntimeError('No pude leer posiciones actuales. '+' | '.join(errs))
    def _text(self,url):
        r=self.s.get(url,timeout=self.timeout); r.raise_for_status(); return BeautifulSoup(r.text,'html.parser').get_text('\n')
    def _norm(self,s): return ''.join(c for c in unicodedata.normalize('NFD',str(s)) if unicodedata.category(c)!='Mn').upper()
    def _parse(self,text):
        text=re.sub(r'[ \t]+',' ',text.replace('\xa0',' ')); zones={}
        for g,teams in GROUP_TEAMS.items():
            block=self._block(text,g); bnorm=self._norm(block); rows=[]
            for team in teams:
                canon=canon_country_name(team); idx=bnorm.find(self._norm(canon))
                for a in {'ESTADOS UNIDOS':['USA','EEUU','EE.UU.'],'PAISES BAJOS':['HOLANDA','NETHERLANDS'],'REPUBLICA CHECA':['CHEQUIA','CZECHIA'],'COREA DEL SUR':['KOREA REPUBLIC'],'RD CONGO':['CONGO DR','DR CONGO']}.get(canon,[]):
                    if idx<0: idx=bnorm.find(self._norm(a))
                if idx<0: continue
                nums=re.findall(r'\b-?\d+\b',block[idx:idx+160]); pts=int(nums[0]) if nums else 0
                rows.append({'team':canon,'pts':pts,'gd':0,'gf':0,'_idx':idx})
            rows.sort(key=lambda r:r['_idx'])
            for r in rows: r.pop('_idx',None)
            if len(rows)>=2: zones[g]=rows
        return zones
    def _block(self,text,g):
        m=re.search(rf'(Grupo\s+{g}\b.*?)(?=Grupo\s+[A-L]\b|CUADRO|16avos|Octavos|$)',text,re.I|re.S)
        if m: return m.group(1)
        m=re.search(rf'Grupo\s+{g}\b',text,re.I)
        return text[m.start():m.start()+4000] if m else text
