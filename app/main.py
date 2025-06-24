import os
import shutil
import traceback

from bot.website import WebsiteBot
from bot.bet_placer import BetPlacer
from bot.match_scheduler import MatchesScheduler

from utils._email import EmailSender
from utils.secrets import get_secret
from utils.scheduler import delete_all_schedules, delete_schedule
from utils.types import TriggerType
from utils.exceptions import EventOddsChangedError

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

        email_sender = EmailSender(
            from_email=secrets["from_address"],
            password=secrets["gmail_app_password"],
        )

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
            email_sender.send_email(
                to_email=secrets["to_address"],
                subject=EmailSender.SUBJECT_ERROR_TYPE,
                body=EmailSender.BODY_NOT_LOGGED_IN,
            )
            return RETURN_BODY

        balance = bot.get_available_balance()
        print(f"Available balance: {balance}")
        if balance < 2.00:
            email_sender.send_email(
                to_email=secrets["to_address"],
                subject=EmailSender.SUBJECT_ERROR_TYPE,
                body=EmailSender.BODY_NO_BALANCE.format(balance),
            )
            # All schedules are deleted. The main one which gather matches
            # is disabled only until human intervention.
            delete_all_schedules()
            return RETURN_BODY

        if event["trigger_type"] == TriggerType.FIND_MATCHES:
            matches_scheduler = MatchesScheduler(bot=bot)
            matches_scheduler.schedule_matches()
            if len(matches_scheduler.matches) < 1:
                email_sender.send_email(
                    to_email=secrets["to_address"],
                    subject=EmailSender.SUBJECT_INFO_TYPE,
                    body=EmailSender.BODY_NO_MATCHES_FOUND,
                )
            else:
                email_sender.send_email(
                    to_email=secrets["to_address"],
                    subject=EmailSender.SUBJECT_INFO_TYPE,
                    body=EmailSender.BODY_MATCHES_SCHEDULED.format(
                        len(matches_scheduler.matches)
                    ),
                    events=matches_scheduler.matches_formatted,
                )
        elif event["trigger_type"] == TriggerType.PLACE_BET:
            try:
                print(f"Placing bet with: {balance}")
                bet_placer = BetPlacer(
                    bot=bot,
                    match_url=event["match_url"],
                    market_type_id=event["market_type_id"],
                    bet_option_id=event["bet_option_id"],
                    market_type_name=event["market_type_name"],
                    bet_amount=balance,
                )
                bet_placer.run()
                email_sender.send_email(
                    to_email=secrets["to_address"],
                    subject=EmailSender.SUBJECT_INFO_TYPE,
                    body=EmailSender.BODY_PLACED_BET.format(event["match_name"]),
                    events=[
                        {
                            "name": event["match_name"],
                            "bet_type": event["market_type_name"],
                            "odd": bet_placer.bet_odd_value,
                            "start_time": event["start_time"],
                            "match_url": event["match_url"],
                        }
                    ],
                )
            except EventOddsChangedError:
                email_sender.send_email(
                    to_email=secrets["to_address"],
                    subject=EmailSender.SUBJECT_ERROR_TYPE,
                    body=EmailSender.BODY_CHANGED_ODD.format(
                        event["match_name"],
                        event["match_url"],
                        event["odd_value"],
                        bet_placer.bet_odd_value,
                    ),
                )
    except Exception:
        traceback_path = "/tmp/traceback.txt"
        with open(traceback_path, "w") as f:
            f.write(traceback.format_exc())

        screenshot_path = bot.take_screenshot()
        if not os.path.exists(screenshot_path):
            screenshot_path = None

        email_sender.send_email(
            to_email=secrets["to_address"],
            subject=EmailSender.SUBJECT_ERROR_TYPE,
            body=EmailSender.BODY_UNCAUGHT_EXCEPTION,
            traceback_logs_path=traceback_path,
            image_path=screenshot_path,
        )
    finally:
        bot.close()
        # This should only delete TriggerType.PLACE_BET events,
        # since TriggerType.FIND_MATCHES does not send the schedule name 
        # in the event.
        if event.get("schedule_name"):
            delete_schedule(event["schedule_name"])

    return RETURN_BODY
