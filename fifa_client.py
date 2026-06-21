import json
import re
from typing import Any, Dict, List, Optional

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
    def __init__(self, timeout: int = 25):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 Chrome/126 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml,application/json;q=0.9,*/*;q=0.8",
        })

    def fetch_matches(self) -> List[Match]:
        errors = []
        for url in FIFA_API_CANDIDATES:
            try:
                data = self._get_json(url)
                matches = self._extract_matches_from_any_json(data)
                if matches:
                    return matches
            except Exception as exc:
                errors.append(f"{url}: {exc}")

        for page_name, url in [("fixtures", OFFICIAL_FIXTURES_URL), ("standings", OFFICIAL_STANDINGS_URL)]:
            try:
                html = self._get_text(url)
                embedded = self._extract_embedded_json(html)
                matches = []
                for obj in embedded:
                    matches.extend(self._extract_matches_from_any_json(obj))
                if matches:
                    return self._dedupe_matches(matches)
            except Exception as exc:
                errors.append(f"{page_name} page: {exc}")

        raise FIFAClientError("No pude leer resultados desde FIFA.\n" + "\n".join(errors[-5:]))

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
            if "match" in txt.lower() and ("home" in txt.lower() or "away" in txt.lower()):
                for blob in self._json_blobs(txt):
                    try:
                        out.append(json.loads(blob))
                    except Exception:
                        pass
        return out

    def _json_blobs(self, text: str) -> List[str]:
        candidates = []
        for m in re.finditer(r"(\{.{200,}\}|\[.{200,}\])", text, flags=re.S):
            blob = m.group(1)
            if len(blob) < 1000000:
                candidates.append(blob)
        return candidates[:20]

    def _extract_matches_from_any_json(self, obj: Any) -> List[Match]:
        raw_matches = []
        self._walk(obj, raw_matches)
        parsed = [self._parse_match(x) for x in raw_matches]
        return self._dedupe_matches([m for m in parsed if m is not None])

    def _walk(self, obj: Any, out: List[dict]):
        if isinstance(obj, dict):
            keys = {str(k).lower() for k in obj.keys()}
            looks_like_match = (
                any(k in keys for k in ["home", "hometeam", "home_team", "homecompetitor"])
                and any(k in keys for k in ["away", "awayteam", "away_team", "awaycompetitor"])
                and any(k in keys for k in ["matchnumber", "match_no", "idmatch", "id", "matchid", "match"])
            )
            if looks_like_match:
                out.append(obj)
            for v in obj.values():
                self._walk(v, out)
        elif isinstance(obj, list):
            for v in obj:
                self._walk(v, out)

    def _parse_match(self, d: Dict[str, Any]) -> Optional[Match]:
        def pick(*names):
            for n in names:
                if n in d:
                    return d[n]
            return None

        def nested_team(raw):
            if not raw:
                return (None, None)

            if isinstance(raw, list):
                for item in raw:
                    name, code = nested_team(item)
                    if name:
                        return (name, code)
                return (None, None)

            if isinstance(raw, str):
                return (raw, None)

            if isinstance(raw, dict):
                name = (
                    raw.get("name") or raw.get("Name") or raw.get("shortName") or raw.get("ShortName")
                    or raw.get("displayName") or raw.get("teamName") or raw.get("TeamName")
                    or raw.get("Description") or raw.get("countryName") or raw.get("CountryName")
                )
                code = (
                    raw.get("abbreviation") or raw.get("Abbreviation") or raw.get("code") or raw.get("Code")
                    or raw.get("countryCode") or raw.get("CountryCode") or raw.get("triCode") or raw.get("TriCode")
                )
                return (name, code)

            return (str(raw), None)

        home_raw = pick("home", "homeTeam", "Home", "HomeTeam", "homeCompetitor")
        away_raw = pick("away", "awayTeam", "Away", "AwayTeam", "awayCompetitor")
        home, home_code = nested_team(home_raw)
        away, away_code = nested_team(away_raw)

        home_score = pick("homeScore", "HomeScore", "home_score")
        away_score = pick("awayScore", "AwayScore", "away_score")
        if home_score is None and isinstance(home_raw, dict):
            home_score = home_raw.get("score") or home_raw.get("Score")
        if away_score is None and isinstance(away_raw, dict):
            away_score = away_raw.get("score") or away_raw.get("Score")

        try:
            if home_score is not None:
                home_score = int(home_score)
            if away_score is not None:
                away_score = int(away_score)
        except Exception:
            home_score, away_score = None, None

        number = pick("matchNumber", "MatchNumber", "match_no", "matchNo", "number", "idMatch", "IdMatch", "id")
        number = self._normalize_match_number(number)
        status = str(pick("status", "Status", "matchStatus", "MatchStatus") or "").upper()
        stage = str(pick("stage", "Stage", "round", "Round", "stageName", "StageName") or "")
        group = self._extract_group(d)
        venue = self._extract_venue(d)
        kickoff = str(pick("date", "Date", "kickoff", "KickOff", "localDate", "LocalDate") or "")

        if not number or (not home and not away):
            return None

        winner = None
        loser = None
        if home_score is not None and away_score is not None and status in ("FINISHED", "FULL_TIME", "FT", "COMPLETED"):
            if home_score > away_score:
                winner, loser = home, away
            elif away_score > home_score:
                winner, loser = away, home

        return Match(number, stage, group, home, away, home_code, away_code, home_score, away_score, status, venue, kickoff, winner, loser)

    def _normalize_match_number(self, raw) -> Optional[int]:
        if raw is None:
            return None
        nums = re.findall(r"\d+", str(raw))
        if not nums:
            return None
        n = int(nums[-1])
        if 1 <= n <= 104:
            return n
        if n >= 400021443:
            last = n - 400021442
            if 1 <= last <= 104:
                return last
        return None

    def _extract_group(self, d: Dict[str, Any]) -> Optional[str]:
        text = json.dumps(d, ensure_ascii=False)
        for pat in [r"Group\s+([A-L])", r"Grupo\s+([A-L])"]:
            m = re.search(pat, text, flags=re.I)
            if m:
                return m.group(1).upper()
        return None

    def _extract_venue(self, d: Dict[str, Any]) -> str:
        text = json.dumps(d, ensure_ascii=False).lower()
        map_ = {"boston":"BOS","gillette":"BOS","new york":"NYNJ","new jersey":"NYNJ","metlife":"NYNJ","los angeles":"LA","sofi":"LA","monterrey":"MTY","toronto":"TOR","san francisco":"SFBA","bay area":"SFBA","seattle":"SEA","houston":"HOU","dallas":"DAL","ciudad de méxico":"CDMX","mexico city":"CDMX","azteca":"CDMX","atlanta":"ATL","miami":"MIA","vancouver":"VAN","kansas":"KC","philadelphia":"PHI"}
        for needle, code in map_.items():
            if needle in text:
                return code
        return ""

    def _dedupe_matches(self, matches: List[Match]) -> List[Match]:
        seen = {}
        for m in matches:
            seen[m.match_no] = m
        return [seen[k] for k in sorted(seen.keys())]
