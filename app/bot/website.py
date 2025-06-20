import pytz
from datetime import datetime, timedelta

from utils.types import FixtureDict, LeagueDict, MatchesToBetDict

from typing import Any

from bot.base_bot import BaseBot
from bot.login_helper import login_to_website


class WebsiteBot(BaseBot):
    def login(self) -> bool:
        """Login to the website using the provided username and password."""
        try:
            login_to_website(self, self.app_email, self.app_password)
            return True
        except Exception:
            return False

    def get_available_balance(self) -> float:
        """Get the available balance using session"""
        response = self.session_send_request(
            "GET", self.bot_config["website"]["balance_endpoint"]
        )
        return response.json()["userInfo"]["account"]["balance"]

    def get_leagues_data(self) -> list[LeagueDict]:
        """Get the leagues data using session."""
        response = self.session_send_request(
            "GET", self.bot_config["website"]["leagues_ids_endpoint"]
        )

        leagues = []

        for league in response.json()["tournaments"]:
            if (
                isinstance(league["features"], list) and "MATCHES" in league["features"]
            ) and (
                isinstance(league["filters"], list) and "tomorrow" in league["filters"]
            ):
                leagues.append(
                    {
                        "id": league["id"],
                        "name": league["name"],
                        "league_seo_name": league["seoName"],
                        "category_id": league["categoryId"],
                    }
                )
        return leagues

    def get_fixtures_data_from_league(
        self, league: LeagueDict, category_seo_name: str
    ) -> list[FixtureDict]:
        """
        Get the fixtures from a league using session.
        We also filter out the fixtures which start before `bet_events_minimum_start_hour`.
        """
        league_id = league["id"]
        response = self.session_send_request(
            "GET",
            self.bot_config["website"]["fixtures_from_league_endpoint"].format(
                league_id
            ),
        )

        timezone = pytz.timezone("Europe/Bucharest")
        tomorrow = datetime.now(timezone) + timedelta(days=1)

        fixtures = []

        for fixture in response.json()["fixtures"]:
            timestamp = fixture["startDatetime"] / 1000
            utc_date = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
            match_local_date = utc_date.astimezone(timezone)

            # For some reason, even we hit the /tomorrow endpoint, some matches from
            # the day after tomorrow appear, especially from leagues from South America
            # so make sure to filter those out as well.
            if (
                match_local_date.hour
                < self.bot_config["website"]["bet_events_minimum_start_hour"]
                or match_local_date.day - tomorrow.day != 0
            ):
                continue

            fixtures.append(
                {
                    "id": fixture["id"],
                    "name": fixture["name"],
                    "start_time": match_local_date,
                    "category_seo_name": category_seo_name,
                    "league_seo_name": league["league_seo_name"],
                    "match_seo_name": fixture["seoName"],
                }
            )
        return fixtures

    def get_markets_from_fixture(self, fixture: FixtureDict) -> list[dict[str, Any]]:
        """Get the markets from a fixture using session."""
        fixture_id = fixture["id"]
        response = self.session_send_request(
            "GET",
            self.bot_config["website"]["markets_from_fixture_endpoint"].format(
                fixture_id
            ),
        )
        return response.json()

    def get_bet_type_from_fixture_markets(
        self, fixture_markets: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Return the predefined `bet_type` across all markets from a given fixture if it exists.
        """
        try:
            return [
                market
                for market in fixture_markets
                if market["name"] == self.bot_config["website"]["bet_type"]
            ][0]
        except Exception:
            pass
        return None

    def get_matches_to_bet(self, maximum_bet_odd: int = 0) -> list[MatchesToBetDict]:
        """
        Get the matches to bet on.
        Check all leagues and fixtures for the bet type we are interested in.
        We also need to make sure that the fixtures are at least `minimum_hours_between_matches`
        apart from each other and their markets contain the predefined `bet_type` and that
        the `bet_type` has odds within `maximum_bet_odd` range.
        """
        all_fixtures = []

        categories = self.session_send_request(
            "GET", self.bot_config["website"]["categories_endpoint"]
        ).json()

        leagues = self.get_leagues_data()
        for league in leagues:
            # Find league category based on the league's category_id
            try:
                found_category_id = [
                    c for c in categories if c["id"] == league["category_id"]
                ][0]
                category_seo_name = found_category_id["seoName"]
            except Exception:
                continue

            league_fixtures = self.get_fixtures_data_from_league(
                league, category_seo_name
            )
            if league_fixtures:
                all_fixtures.extend(league_fixtures)

        all_fixtures.sort(key=lambda x: x["start_time"])

        _maximum_bet_odd = (
            maximum_bet_odd or self.bot_config["website"]["maximum_bet_odd"]
        )

        hours_between_matches = self.bot_config["website"][
            "minimum_hours_between_matches"
        ]

        matches_to_bet = []

        for fixture in all_fixtures:
            if (
                len(matches_to_bet)
                >= self.bot_config["website"]["max_number_of_bets_per_day"]
            ):
                break

            if len(matches_to_bet) > 0:
                last_bet_match = matches_to_bet[-1]
                if (
                    not (
                        fixture["start_time"] - last_bet_match["start_time"]
                    ).total_seconds()
                    / 3600
                    >= hours_between_matches
                ):
                    continue

            fixture_markets = self.get_markets_from_fixture(fixture)
            target_bet_market = self.get_bet_type_from_fixture_markets(fixture_markets)
            if not target_bet_market:
                continue

            suitable_bet = None
            for outcome in target_bet_market["outcomes"]:
                if outcome["odds"] <= _maximum_bet_odd:
                    suitable_bet = outcome

            if suitable_bet:
                matches_to_bet.append(
                    {
                        "id": fixture["id"],
                        "name": fixture["name"],
                        "start_time": fixture["start_time"],
                        "category_seo_name": fixture["category_seo_name"],
                        "league_seo_name": fixture["league_seo_name"],
                        "match_seo_name": fixture["match_seo_name"],
                        "market_type_id": target_bet_market[
                            "marketTypeId"
                        ],  # The id of the container in which the bet is found
                        "market_type_name": target_bet_market["marketTypeName"],
                        "bet_option_id": suitable_bet[
                            "id"
                        ],  # The id of the bet option (example 1 / X / 2)
                        "odd_value": suitable_bet["odds"],
                    }
                )

        return matches_to_bet
