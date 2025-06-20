import time
import random

from bot.website import WebsiteBot
from utils.scheduler import delete_schedule
from utils.exceptions import EventOddsChangedError

from bot.selectors import (
    BET_CONTAINER,
    BET_OPTION_BUTTON,
    BETSLIP_PAY_INPUT,
    BETSPLIT_PLACEMENT_BUTTON,
)


class BetPlacer:
    def __init__(
        self,
        bot: WebsiteBot,
        match_url: str,
        market_type_id: str,
        bet_option_id: str,
        market_type_name: str,
        event_schedule_name: str = "",
        bet_amount: float = 0.0,
    ):
        self.bot = bot
        self.match_url = match_url
        self.market_type_id = market_type_id
        self.bet_option_id = bet_option_id
        self.market_type_name = market_type_name
        self.bet_amount = bet_amount or self.bot.get_available_balance()
        self.event_schedule_name = event_schedule_name
        self.bet_odd_value = ""

    def place_bet(self) -> str:
        self.bot.visit_url(self.match_url)
        # wait some comfortable amount of time here.
        time.sleep(random.uniform(15, 30))

        bet_container_locator = (
            BET_CONTAINER[0],
            BET_CONTAINER[1].format(self.market_type_id),
        )
        bet_option_locator = (
            BET_OPTION_BUTTON[0],
            BET_OPTION_BUTTON[1].format(self.bet_option_id),
        )
        bet_option_element = self.bot.get_element(
            locator=bet_option_locator, parent=None
        )
        try:
            self.bet_odd_value = bet_option_element.text.split("\n")[1]
        except Exception:
            self.bet_odd_value = ""

        if (
            float(self.bet_odd_value)
            > self.bot.bot_config["website"]["maximum_bet_odd"]
        ):
            raise EventOddsChangedError()

        bet_container = self.bot.get_element(locator=bet_container_locator)
        # Means the section is collapsed
        if "\n" not in bet_container.text:
            print("Expanding bet container.")
            self.bot.click(parent=bet_container)
        else:
            print("Bet container already expanded.")

        self.bot.click(locator=bet_option_locator, parent=None)

        bet_pay_input = self.bot.get_element(locator=BETSLIP_PAY_INPUT)
        self.bot.driver.execute_script(
            """
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """,
            bet_pay_input,
            self.bet_amount,
        )

        self.bot.click(locator=BETSPLIT_PLACEMENT_BUTTON, parent=None)

    def run(self):
        self.place_bet()
        if self.event_schedule_name:
            delete_schedule(schedule_name=self.event_schedule_name)
