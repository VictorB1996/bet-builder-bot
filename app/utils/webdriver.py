import os
import uuid
import tempfile

from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def get_new_driver(
    proxy_user: str,
    proxy_password: str,
    proxy_host: str,
    proxy_port: int,
    headless: bool = True,
) -> webdriver.Chrome:
    """Initializes a new browser based on specific options
    and returns its handle"""
    chrome_options = Options()
    chrome_options.binary_location = "/opt/chrome/chrome-linux64/chrome"

    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-tools")
    chrome_options.add_argument("--no-zygote")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--single-process")

    temporary_data_dir = f"/tmp/selenium_profile_{uuid.uuid4().hex}"
    os.makedirs(temporary_data_dir, exist_ok=True)
    chrome_options.add_argument(f"--user-data-dir={temporary_data_dir}")
    chrome_options.add_argument(f"--data-path={temporary_data_dir}")
    chrome_options.add_argument(f"--disk-cache-dir={temporary_data_dir}")

    chrome_options.add_argument("--remote-debugging-pipe")
    chrome_options.add_argument("--verbose")
    chrome_options.add_argument("--log-path=/tmp")

    service = Service(
        executable_path="/opt/chrome-driver/chromedriver-linux64/chromedriver",
        service_log_path="/tmp/chromedriver.log",
    )

    seleniumwire_options = {
        "proxy": {
            "http": "http://{}:{}@{}:{}".format(
                proxy_user, proxy_password, proxy_host, proxy_port
            )
        },
        "disable-encoding": True,
    }

    driver = webdriver.Chrome(
        service=service,
        options=chrome_options,
        seleniumwire_options=seleniumwire_options,
    )
    driver.maximize_window()
    return driver
