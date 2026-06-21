from dataclasses import dataclass
from typing import Optional


@dataclass
class Match:
    match_no: int
    stage: str
    group: Optional[str]
    home: Optional[str]
    away: Optional[str]
    home_code: Optional[str]
    away_code: Optional[str]
    home_score: Optional[int]
    away_score: Optional[int]
    status: str
    venue_code: str = ""
    kickoff: str = ""
    winner: Optional[str] = None
    loser: Optional[str] = None
