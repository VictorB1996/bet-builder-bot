from typing import TypedDict
from datetime import datetime


class FixtureDict(TypedDict):
    """Fixture dictionary for storing fixture data."""

    id: str
    name: str
    start_time: datetime


class LeagueDict(TypedDict):
    """League dictionary for storing league data."""

    id: str
    name: str
    league_seo_name: str
    category_id: str


class MatchesToBetDict(TypedDict):
    id: str
    name: str
    start_time: datetime
    category_seo_name: str
    league_seo_name: str
    match_seo_name: str
    market_type_id: str
    market_type_name: str
    bet_option_id: str
    odd_value: float


class TriggerType:
    FIND_MATCHES: str = "FIND_MATCHES"
    PLACE_BET: str = "PLACE_BET"
