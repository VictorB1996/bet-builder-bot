import os
import shutil
import traceback

from bot.website import WebsiteBot
from bot.bet_placer import BetPlacer
from bot.match_scheduler import MatchesScheduler

from utils._email import send_email
from utils.secrets import get_secret
from utils.scheduler import delete_all_schedules, delete_schedule
from utils.types import TriggerType, EmailTemplate

RETURN_BODY = {"statusCode": 200, "body": ""}


def clean_tmp():
    tmp_dir = "/tmp"
    for filename in os.listdir(tmp_dir):
        file_path = os.path.join(tmp_dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")


def lambda_handler(event, context):
    """Main function to handle the Lambda event"""
    try:
        clean_tmp()
        secrets = get_secret("bet-builder-secrets")

        bot = WebsiteBot(
            app_email=secrets["bet_app_username"],
            app_password=secrets["bet_app_password"],
            proxy_user=secrets["proxy_user"],
            proxy_password=secrets["proxy_password"],
            proxy_host=secrets["proxy_host"],
            proxy_port=secrets["proxy_port"],
        )
        logged_in = bot.login()
        if not logged_in:
            send_email(
                subject=EmailTemplate.SUBJECT_ERROR_TYPE,
                body=EmailTemplate.BODY_ERROR_TYPE.format("Bot was unable to log in."),
                from_email=secrets["from_address"],
                password=secrets["gmail_app_password"],
                to_email=secrets["to_address"],
            )
            return RETURN_BODY

        balance = bot.get_available_balance()
        print(f"Available balance: {balance}")
        if balance < 1.00:
            send_email(
                subject=EmailTemplate.SUBJECT_ERROR_TYPE,
                body=EmailTemplate.BODY_ERROR_TYPE.format(
                    f"No balance left in account. Available balance - {balance}."
                    + "All schedules have been deleted."
                ),
                from_email=secrets["from_address"],
                password=secrets["gmail_app_password"],
                to_email=secrets["to_address"],
            )
            delete_all_schedules()
            return RETURN_BODY

        if event["trigger_type"] == TriggerType.FIND_MATCHES:
            matches_scheduler = MatchesScheduler(bot=bot)
            matches = matches_scheduler.schedule_matches()
            if len(matches) < 1:
                send_email(
                    subject=EmailTemplate.SUBJECT_INFO_TYPE,
                    body=EmailTemplate.BODY_INFO_TYPE.format(
                        f"No suitable matches found for the next day."
                    ),
                    from_email=secrets["from_address"],
                    password=secrets["gmail_app_password"],
                    to_email=secrets["to_address"],
                )
            else:
                send_email(
                    subject=EmailTemplate.SUBJECT_INFO_TYPE,
                    body=EmailTemplate.BODY_INFO_TYPE.format(
                        f"Scheduled {len(matches)} matches for next day."
                    ),
                    from_email=secrets["from_address"],
                    password=secrets["gmail_app_password"],
                    to_email=secrets["to_address"],
                )
        elif event["trigger_type"] == TriggerType.PLACE_BET:
            balance = 2.5
            print(f"Placing bet with: {balance}")
            bet_placer = BetPlacer(
                bot=bot,
                match_url=event["match_url"],
                market_type_id=event["market_type_id"],
                bet_option_id=event["bet_option_id"],
                market_type_name=event["market_type_name"],
                bet_amount=balance,
                event_schedule_name=event["schedule_name"],
            )
            bet_placer.run()
            send_email(
                subject=EmailTemplate.SUBJECT_INFO_TYPE,
                body=EmailTemplate.BODY_INFO_TYPE.format(
                    f"Placed bet on {bet_placer.market_type_name} with bet amount: {bet_placer.bet_amount}.\n"
                    + f"URL: {bet_placer.match_url}"
                ),
                from_email=secrets["from_address"],
                password=secrets["gmail_app_password"],
                to_email=secrets["to_address"],
            )
    except Exception:
        traceback_path = "/tmp/traceback.txt"
        with open(traceback_path, "w") as f:
            f.write(traceback.format_exc())

        send_email(
            subject=EmailTemplate.SUBJECT_ERROR_TYPE,
            body=EmailTemplate.BODY_ERROR_TYPE.format(
                "Uncaught exception occured. See attachment."
            ),
            from_email=secrets["from_address"],
            password=secrets["gmail_app_password"],
            to_email=secrets["to_address"],
            attachment_path=traceback_path,
        )
        if event.get("schedule_name"):
            delete_schedule(event["schedule_name"])

    return RETURN_BODY
