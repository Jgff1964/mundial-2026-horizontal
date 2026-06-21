import json
import re
from typing import Any, Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

from flags import canon_country_name

PROMIEDOS_PAGE_URL = "https://www.promiedos.com.ar/league/fifa-world-cup/fjda"
PROMIEDOS_API_URL = "https://api.promiedos.com.ar/league/tables_and_fixtures/fjda"

R32_MATCHES = [74,77,73,75,83,84,81,82,76,78,79,80,86,88,85,87]
R16_MATCHES = [89,90,93,94,91,92,95,96]
QF_MATCHES = [97,98,99,100]
SF_MATCHES = [101,102]

class PromiedosClient:
    def __init__(self, timeout=25):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
            "Accept":"application/json,text/html,*/*",
            "Origin": "https://www.promiedos.com.ar",
            "Referer": PROMIEDOS_PAGE_URL,
        })
        self.last_summary = {}

    def fetch_all(self) -> Tuple[Dict[str, List[dict]], Dict[str, dict]]:
        api_data = self.fetch_api()
        zones = self.extract_zones_from_api(api_data)
        bracket = self.fetch_bracket_page()
        return zones, bracket

    def fetch_api(self):
        r = self.session.get(PROMIEDOS_API_URL, timeout=self.timeout)
        r.raise_for_status()
        try:
            data = r.json()
        except Exception:
            data = json.loads(r.text)
        self.last_summary = {
            "api_url": PROMIEDOS_API_URL,
            "root_type": type(data).__name__,
            "root_keys": list(data.keys())[:30] if isinstance(data, dict) else None,
        }
        return data

    # ---------- TABLAS API ----------

    def extract_zones_from_api(self, data: Any) -> Dict[str, List[dict]]:
        table_candidates = []
        self._walk_for_tables(data, [], table_candidates)

        # Eliminar duplicados y listas chicas irrelevantes.
        normalized = []
        seen = set()
        for path, title, rows in table_candidates:
            clean_rows = []
            for row in rows:
                team = self._row_team(row)
                if not team:
                    continue
                clean_rows.append({
                    "team": team,
                    "pts": self._row_number(row, ["pts","points","puntos","pt","PT","Pts","Points"]),
                    "gd": self._row_number(row, ["gd","dg","diff","goalDifference","+/-"]),
                    "gf": self._row_number(row, ["gf","goalsFor","goals_for"]),
                })
            if len(clean_rows) < 2:
                continue
            key = tuple(r["team"] for r in clean_rows)
            if key in seen:
                continue
            seen.add(key)
            normalized.append((path, title, clean_rows))

        # Priorizar candidatos con títulos de grupo.
        by_group = {}
        unused = []
        for path, title, rows in normalized:
            group = self._group_from_text(" ".join([str(x) for x in path]) + " " + str(title))
            if group and group not in by_group:
                by_group[group] = rows
            else:
                unused.append((path, title, rows))

        # Si no trajo títulos claros, asignar por orden A-L.
        groups = list("ABCDEFGHIJKL")
        idx = 0
        for _, _, rows in unused:
            while idx < len(groups) and groups[idx] in by_group:
                idx += 1
            if idx >= len(groups):
                break
            by_group[groups[idx]] = rows
            idx += 1

        zones = {g: by_group[g] for g in groups if g in by_group}

        if len(zones) < 8:
            raise RuntimeError(f"Promiedos API no devolvió suficientes tablas de grupos. Leídas: {list(zones.keys())}")

        self.last_summary["tables_found"] = len(normalized)
        self.last_summary["groups_found"] = list(zones.keys())
        return zones

    def _walk_for_tables(self, obj: Any, path: List[str], out: List[tuple]):
        if isinstance(obj, dict):
            title = self._dict_title(obj)
            for k, v in obj.items():
                if isinstance(v, list) and self._looks_like_table_rows(v):
                    out.append((path + [str(k)], title or str(k), v))
                self._walk_for_tables(v, path + [str(k)], out)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                self._walk_for_tables(v, path + [str(i)], out)

    def _looks_like_table_rows(self, rows: list) -> bool:
        if not isinstance(rows, list) or len(rows) < 2:
            return False
        dicts = [r for r in rows if isinstance(r, dict)]
        if len(dicts) < 2:
            return False
        team_count = sum(1 for r in dicts if self._row_team(r))
        return team_count >= 2

    def _dict_title(self, d: dict) -> str:
        for k in ["name","nombre","title","titulo","group","grupo","phase","fase","label"]:
            if d.get(k):
                return str(d.get(k))
        return ""

    def _group_from_text(self, text: str) -> Optional[str]:
        text = str(text).upper()
        patterns = [
            r"GRUPO\s+([A-L])\b",
            r"GROUP\s+([A-L])\b",
            r"\bZONA\s+([A-L])\b",
            r"\b([A-L])\b",
        ]
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                return m.group(1)
        return None

    def _row_team(self, row: dict) -> str:
        possible = []
        for k in ["team","equipo","name","nombre","club","country","pais","selection","seleccion"]:
            if k in row:
                possible.append(row.get(k))
        for k in ["team","equipo"]:
            if isinstance(row.get(k), dict):
                possible.append(row[k].get("name") or row[k].get("nombre") or row[k].get("short_name"))
        for val in possible:
            team = canon_country_name(val)
            if team and not team.startswith("GANADOR") and not team.startswith("PERDEDOR"):
                return team

        # Fallback: buscar un string de equipo dentro del row.
        for val in row.values():
            if isinstance(val, str):
                team = canon_country_name(val)
                if team and len(team) > 2 and not team.startswith("GANADOR") and not team.startswith("PERDEDOR"):
                    return team
            if isinstance(val, dict):
                team = self._row_team(val)
                if team:
                    return team
        return ""

    def _row_number(self, row: dict, keys: list) -> int:
        for k in keys:
            if k in row:
                try:
                    return int(row[k])
                except Exception:
                    pass
        return 0

    # ---------- CUADRO HTML ----------

    def fetch_bracket_page(self):
        html = self.session.get(PROMIEDOS_PAGE_URL, timeout=self.timeout).text
        soup = BeautifulSoup(html, "html.parser")
        lines = [x.strip() for x in soup.get_text("\n").splitlines() if x.strip()]
        tokens = [x for x in lines if "Loading" not in x]

        try:
            start = tokens.index("CUADRO")
            tokens = tokens[start+1:]
        except ValueError:
            pass

        sections = self._split_sections(tokens)
        final, third = self._final(sections.get("Final", []))
        return {
            "r32": self._pairs_to_matches(sections.get("16avos de final", []), R32_MATCHES),
            "r16": self._pairs_to_matches(sections.get("Octavos de Final", []), R16_MATCHES),
            "qf": self._pairs_to_matches(sections.get("Cuartos de Final", []), QF_MATCHES),
            "sf": self._pairs_to_matches(sections.get("Semifinales", []), SF_MATCHES),
            "final": final,
            "third": third,
            "url": PROMIEDOS_PAGE_URL
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

    def _clean_bracket_token(self, t):
        t = str(t).strip()
        t = t.replace("Ganador del partido ", "Ganador M")
        t = t.replace("Perdedor del partido ", "Perdedor M")
        if t.upper().startswith("GANADOR") or t.upper().startswith("PERDEDOR"):
            return t
        return canon_country_name(t)

    def _pairs(self, tokens):
        cleaned = [self._clean_bracket_token(t) for t in tokens if self._clean_bracket_token(t) and self._clean_bracket_token(t) not in {"FINAL","3er puesto"}]
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
