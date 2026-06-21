import requests
from flags import canon_country_name
from bs4 import BeautifulSoup

PROMIEDOS_URL = "https://www.promiedos.com.ar/league/fifa-world-cup/fjda"

R32_MATCHES = [74,77,73,75,83,84,81,82,76,78,79,80,86,88,85,87]
R16_MATCHES = [89,90,93,94,91,92,95,96]
QF_MATCHES = [97,98,99,100]
SF_MATCHES = [101,102]

class PromiedosClient:
    def __init__(self, timeout=25):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent":"Mozilla/5.0 Chrome/126 Safari/537.36"})

    def fetch_bracket(self):
        html = self.session.get(PROMIEDOS_URL, timeout=self.timeout).text
        soup = BeautifulSoup(html, "html.parser")
        lines = [x.strip() for x in soup.get_text("\\n").splitlines() if x.strip()]
        tokens = [x for x in lines if "Loading" not in x]

        try:
            start = tokens.index("CUADRO")
            tokens = tokens[start+1:]
        except ValueError:
            pass

        sections = self._split_sections(tokens)
        return {
            "r32": self._pairs_to_matches(sections.get("16avos de final", []), R32_MATCHES),
            "r16": self._pairs_to_matches(sections.get("Octavos de Final", []), R16_MATCHES),
            "qf": self._pairs_to_matches(sections.get("Cuartos de Final", []), QF_MATCHES),
            "sf": self._pairs_to_matches(sections.get("Semifinales", []), SF_MATCHES),
            "final": self._final(sections.get("Final", []))[0],
            "third": self._final(sections.get("Final", []))[1],
            "url": PROMIEDOS_URL
        }

    def _split_sections(self, tokens):
        names = ["16avos de final","Octavos de Final","Cuartos de Final","Semifinales","Final"]
        sections = {}
        current = None
        for t in tokens:
            if t in names:
                current = t
                sections[current] = []
                continue
            if current:
                if t in {"FINAL","3er puesto"}:
                    continue
                sections[current].append(t)
        return sections

    def _clean(self, t):
        t = str(t).strip()
        t = t.replace("Ganador del partido ", "Ganador M")
        t = t.replace("Perdedor del partido ", "Perdedor M")
        if t.upper().startswith("GANADOR") or t.upper().startswith("PERDEDOR"):
            return t
        return canon_country_name(t)


    def _pairs(self, tokens):
        cleaned = [self._clean(t) for t in tokens if self._clean(t) and self._clean(t) not in {"FINAL","3er puesto"}]
        return [(cleaned[i], cleaned[i+1]) for i in range(0, len(cleaned)-1, 2)]

    def _pairs_to_matches(self, tokens, match_numbers):
        pairs = self._pairs(tokens)
        out = {}
        for no, pair in zip(match_numbers, pairs):
            out[no] = {"venue":"", "home":pair[0], "away":pair[1], "sub":""}
        return out

    def _final(self, tokens):
        pairs = self._pairs(tokens)
        final = {}
        third = {}
        if len(pairs) >= 1:
            final[104] = {"venue":"NYNJ", "home":pairs[0][0], "away":pairs[0][1], "sub":""}
        if len(pairs) >= 2:
            third[103] = {"venue":"MIA", "home":pairs[1][0], "away":pairs[1][1], "sub":""}
        return final, third
