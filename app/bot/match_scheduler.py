from bot.website import WebsiteBot
from utils.scheduler import create_schedule
from utils.types import TriggerType


class MatchesScheduler:
    def __init__(self, bot: WebsiteBot):
        self.bot = bot

    def schedule_matches(self):
        matches = self.bot.get_matches_to_bet()
        for match in matches:
            schedule_name = f"match-schedule-{match['id']}".replace(":", "-")
            create_schedule(
                schedule_name=schedule_name,
                start_date=match["start_time"],
                payload={
                    "trigger_type": TriggerType.PLACE_BET,
                    "market_type_name": match["market_type_name"],
                    "market_type_id": match["market_type_id"],
                    "bet_option_id": match["bet_option_id"],
                    "match_url": self.bot.bot_config["website"][
                        "match_base_url"
                    ].format(
                        match["category_seo_name"],
                        match["league_seo_name"],
                        match["match_seo_name"],
                    ),
                    # We need this so that we have a reference to the
                    # Amazon EventBridge event that triggered the Lambda
                    "schedule_name": schedule_name,
                },
            )
        return matches
