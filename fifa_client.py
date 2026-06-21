
import json
import re
from typing import Any, Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

from models import Match


OFFICIAL_FIXTURES_URL = "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/scores-fixtures"
OFFICIAL_STANDINGS_URL = "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/standings"

FIFA_API_CANDIDATES = [
    "https://api.fifa.com/api/v3/calendar/matches?language=en&count=500&idCompetition=17&idSeason=285023",
    "https://api.fifa.com/api/v3/calendar/matches?language=es&count=500&idCompetition=17&idSeason=285023",
    "https://api.fifa.com/api/v3/calendar/matches?count=500&idCompetition=17&idSeason=285023",
]


class FIFAClientError(RuntimeError):
    pass


class FifaOfficialClient:
    """
    Cliente FIFA en modo estricto.

    La versión anterior era demasiado permisiva: recorría todo el JSON/HTML de FIFA y
    aceptaba estructuras internas que parecían partidos, pero no lo eran. Eso generaba
    cuadros visualmente correctos con datos deportivos incorrectos.

    Esta versión acepta solamente objetos con:
    - número de partido explícito entre 1 y 104;
    - equipo local y visitante normalizables a texto;
    - grupo o ronda identificable;
    - estructura compatible con partido real.

    Si FIFA cambia la estructura y no devuelve datos limpios, la app muestra error
    en lugar de inventar cruces.
    """

    def __init__(self, timeout: int = 25):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0 Safari/537.36"
            ),
            "Accept": "application/json,text/html,application/xhtml+xml,*/*;q=0.8",
        })

    def fetch_matches(self) -> List[Match]:
        errors = []

        # 1) Primero, endpoints API oficiales conocidos.
        for url in FIFA_API_CANDIDATES:
            try:
                data = self._get_json(url)
                matches = self._extract_matches_from_any_json(data)
                matches = self._validate_match_set(matches)
                if matches:
                    return matches
            except Exception as exc:
                errors.append(f"API {url}: {exc}")

        # 2) Fallback HTML oficial: solo si hay JSON embebido limpio.
        for page_name, url in [("fixtures", OFFICIAL_FIXTURES_URL), ("standings", OFFICIAL_STANDINGS_URL)]:
            try:
                html = self._get_text(url)
                embedded = self._extract_embedded_json(html)
                matches = []
                for obj in embedded:
                    matches.extend(self._extract_matches_from_any_json(obj))
                matches = self._validate_match_set(matches)
                if matches:
                    return matches
            except Exception as exc:
                errors.append(f"{page_name}: {exc}")

        raise FIFAClientError(
            "No pude obtener datos oficiales limpios desde FIFA. "
            "Para evitar cruces incorrectos, no se generó el cuadro.\n"
            + "\n".join(errors[-6:])
        )

    def _get_json(self, url: str) -> Any:
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def _get_text(self, url: str) -> str:
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.text

    def _extract_embedded_json(self, html: str) -> List[Any]:
        soup = BeautifulSoup(html, "html.parser")
        out = []

        for script in soup.find_all("script"):
            txt = script.string or script.get_text() or ""
            txt = txt.strip()
            if not txt:
                continue

            if script.get("id") == "__NEXT_DATA__":
                try:
                    out.append(json.loads(txt))
                except Exception:
                    pass

            if script.get("type") in ("application/json", "application/ld+json"):
                try:
                    out.append(json.loads(txt))
                except Exception:
                    pass

        return out

    def _extract_matches_from_any_json(self, obj: Any) -> List[Match]:
        raw_matches = []
        self._walk_for_strict_matches(obj, raw_matches)
        parsed = [self._parse_match(x) for x in raw_matches]
        return self._dedupe_matches([m for m in parsed if m is not None])

    def _walk_for_strict_matches(self, obj: Any, out: List[dict]):
        if isinstance(obj, dict):
            if self._looks_like_real_match(obj):
                out.append(obj)
                return
            for v in obj.values():
                self._walk_for_strict_matches(v, out)
        elif isinstance(obj, list):
            for v in obj:
                self._walk_for_strict_matches(v, out)

    def _looks_like_real_match(self, d: Dict[str, Any]) -> bool:
        keys = {str(k).lower() for k in d.keys()}

        has_match_number = any(k in keys for k in [
            "matchnumber", "matchno", "match_no", "matchnum", "number"
        ])

        # Acepta idMatch solo si también hay un campo de número explícito en otro nivel.
        if not has_match_number:
            return False

        has_home = any(k in keys for k in ["home", "hometeam", "home_team", "homecompetitor"])
        has_away = any(k in keys for k in ["away", "awayteam", "away_team", "awaycompetitor"])
        if not (has_home and has_away):
            return False

        home_raw = self._pick(d, "home", "homeTeam", "Home", "HomeTeam", "homeCompetitor")
        away_raw = self._pick(d, "away", "awayTeam", "Away", "AwayTeam", "awayCompetitor")
        home, _ = self._nested_team(home_raw)
        away, _ = self._nested_team(away_raw)

        return bool(home and away)

    def _pick(self, d: Dict[str, Any], *names):
        for n in names:
            if n in d:
                return d[n]
        return None

    def _nested_team(self, raw) -> Tuple[Optional[str], Optional[str]]:
        if not raw:
            return (None, None)

        if isinstance(raw, list):
            # Evita tomar listas de candidatos/metadata como equipo real.
            # Solo acepta lista si tiene un único objeto inequívoco.
            if len(raw) != 1:
                return (None, None)
            return self._nested_team(raw[0])

        if isinstance(raw, str):
            return (raw.strip() or None, None)

        if isinstance(raw, dict):
            name = (
                raw.get("name") or raw.get("Name")
                or raw.get("shortName") or raw.get("ShortName")
                or raw.get("displayName") or raw.get("DisplayName")
                or raw.get("teamName") or raw.get("TeamName")
                or raw.get("Description") or raw.get("countryName")
                or raw.get("CountryName")
            )
            code = (
                raw.get("abbreviation") or raw.get("Abbreviation")
                or raw.get("code") or raw.get("Code")
                or raw.get("countryCode") or raw.get("CountryCode")
                or raw.get("triCode") or raw.get("TriCode")
            )

            if isinstance(name, list) or isinstance(name, dict):
                nested_name, nested_code = self._nested_team(name)
                return (nested_name, code or nested_code)

            if name:
                return (str(name).strip(), str(code).strip() if code else None)

            return (None, str(code).strip() if code else None)

        return (None, None)

    def _parse_match(self, d: Dict[str, Any]) -> Optional[Match]:
        home_raw = self._pick(d, "home", "homeTeam", "Home", "HomeTeam", "homeCompetitor")
        away_raw = self._pick(d, "away", "awayTeam", "Away", "AwayTeam", "awayCompetitor")
        home, home_code = self._nested_team(home_raw)
        away, away_code = self._nested_team(away_raw)

        number = self._pick(
            d,
            "matchNumber", "MatchNumber", "matchNo", "MatchNo",
            "match_no", "number", "Number"
        )
        number = self._normalize_match_number(number)

        if not number or not home or not away:
            return None

        home_score = self._pick(d, "homeScore", "HomeScore", "home_score")
        away_score = self._pick(d, "awayScore", "AwayScore", "away_score")

        if home_score is None and isinstance(home_raw, dict):
            home_score = home_raw.get("score") or home_raw.get("Score")
        if away_score is None and isinstance(away_raw, dict):
            away_score = away_raw.get("score") or away_raw.get("Score")

        home_score = self._to_int_or_none(home_score)
        away_score = self._to_int_or_none(away_score)

        status = str(self._pick(d, "status", "Status", "matchStatus", "MatchStatus") or "").upper()
        stage = str(self._pick(d, "stage", "Stage", "round", "Round", "stageName", "StageName") or "")
        group = self._extract_group(d)
        venue = self._extract_venue(d)
        kickoff = str(self._pick(d, "date", "Date", "kickoff", "KickOff", "localDate", "LocalDate") or "")

        winner = None
        loser = None
        if home_score is not None and away_score is not None and status in (
            "FINISHED", "FULL_TIME", "FT", "COMPLETED", "AFTER_EXTRA_TIME", "PENALTIES"
        ):
            if home_score > away_score:
                winner, loser = home, away
            elif away_score > home_score:
                winner, loser = away, home

        return Match(
            match_no=number,
            stage=stage,
            group=group,
            home=home,
            away=away,
            home_code=home_code,
            away_code=away_code,
            home_score=home_score,
            away_score=away_score,
            status=status,
            venue_code=venue,
            kickoff=kickoff,
            winner=winner,
            loser=loser,
        )

    def _to_int_or_none(self, value):
        if value is None or value == "":
            return None
        try:
            return int(value)
        except Exception:
            return None

    def _normalize_match_number(self, raw) -> Optional[int]:
        if raw is None:
            return None
        nums = re.findall(r"\d+", str(raw))
        if not nums:
            return None
        n = int(nums[-1])

        # Punto clave: no convertir IDs enormes de FIFA en match numbers.
        # La versión anterior hacía n - 400021442 y eso produjo cruces falsos.
        if 1 <= n <= 104:
            return n

        return None

    def _extract_group(self, d: Dict[str, Any]) -> Optional[str]:
        for key in ["group", "Group", "groupName", "GroupName", "stageName", "StageName", "round", "Round"]:
            value = d.get(key)
            if isinstance(value, str):
                m = re.search(r"(?:Group|Grupo)\s+([A-L])\b", value, flags=re.I)
                if m:
                    return m.group(1).upper()

        text = json.dumps(d, ensure_ascii=False)
        for pat in [r"Group\s+([A-L])\b", r"Grupo\s+([A-L])\b"]:
            m = re.search(pat, text, flags=re.I)
            if m:
                return m.group(1).upper()

        return None

    def _extract_venue(self, d: Dict[str, Any]) -> str:
        text = json.dumps(d, ensure_ascii=False).lower()
        map_ = {
            "boston": "BOS", "gillette": "BOS",
            "new york": "NYNJ", "new jersey": "NYNJ", "metlife": "NYNJ",
            "los angeles": "LA", "sofi": "LA",
            "monterrey": "MTY",
            "toronto": "TOR",
            "san francisco": "SFBA", "bay area": "SFBA",
            "seattle": "SEA",
            "houston": "HOU",
            "dallas": "DAL",
            "ciudad de méxico": "CDMX", "mexico city": "CDMX", "azteca": "CDMX",
            "atlanta": "ATL",
            "miami": "MIA",
            "vancouver": "VAN",
            "kansas": "KC",
            "philadelphia": "PHI",
        }
        for needle, code in map_.items():
            if needle in text:
                return code
        return ""

    def _dedupe_matches(self, matches: List[Match]) -> List[Match]:
        seen = {}
        for m in matches:
            if 1 <= m.match_no <= 104:
                seen[m.match_no] = m
        return [seen[k] for k in sorted(seen.keys())]

    def _validate_match_set(self, matches: List[Match]) -> List[Match]:
        clean = []
        for m in matches:
            if not (1 <= m.match_no <= 104):
                continue
            if not m.home or not m.away:
                continue
            # Para fase de grupos, exigir grupo. Sin grupo no se puede calcular tabla.
            if m.match_no <= 72 and not m.group:
                continue
            clean.append(m)
        return self._dedupe_matches(clean)
