from bot.base_bot import BaseBot

from bot.selectors import (
    COOKIES_ACCEPT_BUTTON,
    LOGIN_BUTTON,
    LOGIN_INPUT_USERNAME,
    LOGIN_INPUT_PASSWORD,
    LOGIN_COFIRM_LOGIN,
)


def login_to_website(bot: BaseBot, username: str, password: str) -> None:
    """Login to the website using the provided username and password."""
    print("Logging in to the website.")
    bot.visit_url(bot.bot_config["website"]["start_url"])
    cookies_accept_button = bot.get_element(COOKIES_ACCEPT_BUTTON)
    if cookies_accept_button:
        bot.click(parent=cookies_accept_button)

    bot.click(locator=LOGIN_BUTTON)

    login_input_username = bot.get_element(LOGIN_INPUT_USERNAME)
    bot.click(parent=login_input_username)
    bot.send_keys(text=username, parent=login_input_username)

    login_input_password = bot.get_element(LOGIN_INPUT_PASSWORD)
    bot.click(parent=login_input_password)
    bot.send_keys(text=password, parent=login_input_password)

    login_confirm_button = bot.get_element(LOGIN_COFIRM_LOGIN)
    bot.click(parent=login_confirm_button)

    bot.set_session_cookies()
    print("Authentication succeeded.")
