import time
import random
import requests


from typing import Optional

from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
)

from utils.webdriver import get_new_driver
from utils.headers import get_headers
from config.config import load_yaml


class BaseBot:
    def __init__(
        self,
        app_email: str,
        app_password: str,
        proxy_user: str,
        proxy_password: str,
        proxy_host: str,
        proxy_port: int,
    ):
        self.bot_config = load_yaml()

        self.driver = get_new_driver(proxy_user, proxy_password, proxy_host, proxy_port)
        self.app_email = app_email
        self.app_password = app_password
        self.proxy_user = proxy_user
        self.proxy_password = proxy_password
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port

        self.wait = WebDriverWait(self.driver, self.bot_config["driver"]["wait_time"])

        self.session = requests.Session()
        self.session.proxies = {
            "http": f"http://{proxy_user}:{proxy_password}@{proxy_host}:{proxy_port}",
            "https": f"https://{proxy_user}:{proxy_password}@{proxy_host}:{proxy_port}",
        }
        self.session.headers.update(get_headers())

    def visit_url(self, url: str) -> None:
        """Visit a given URL"""
        self.driver.get(url)

    def click(self, locator: tuple[By, str] = None, parent: WebElement = None) -> None:
        """Click on an element either using driver or element itself"""
        try:
            if parent:
                self.wait.until(lambda _: parent.is_enabled() and parent.is_displayed())
                parent.click()
            else:
                self.wait.until(EC.element_to_be_clickable(locator)).click()
        except ElementClickInterceptedException:
            # Reload page and try again
            self.driver.refresh()
            self.click(locator=locator, parent=parent)
        time.sleep(random.uniform(0, 1))

    def send_keys(
        self, text: str, locator: tuple[By, str] = None, parent: WebElement = None
    ) -> None:
        """Send keys to an element located by the given locator or from parent."""
        if parent:
            input_element = parent
        else:
            input_element = self.wait.until(EC.presence_of_element_located(locator))

        input_element.clear()
        for char in text:
            input_element.send_keys(char)
            time.sleep(random.uniform(0, 2))

    def get_element(
        self, locator: tuple[By, str] = None, parent: WebElement = None
    ) -> Optional[WebElement]:
        """Get an element located by the given locator either globally
        or from a parent element."""
        try:
            if parent:
                return WebDriverWait(parent, 10).until(
                    lambda x: x.find_element(*locator)
                )
            else:
                return self.wait.until(EC.presence_of_element_located(locator))
        except (TimeoutException, NoSuchElementException):
            print(f"Element not found: {locator}")
            return None

    def get_elements(
        self, locator: tuple[By, str] = None, parent: WebElement = None
    ) -> Optional[list[WebElement]]:
        """Get elements located by the given locator either globally
        or from a parent element."""
        try:
            if parent:
                return WebDriverWait(parent, 10).until(
                    lambda x: x.find_elements(*locator)
                )
            else:
                return self.wait.until(EC.presence_of_all_elements_located(locator))
        except (TimeoutException, NoSuchElementException):
            print(f"Elements not found: {locator}")
            return None

    def refresh_page(self) -> None:
        """Refresh the current page"""
        self.driver.refresh()

    def get_browser_cookies(self, max_attempts: int = 5) -> dict[str, str]:
        """
        Get cookies from the browser after authentication.
        Ensure that some cookies exist before sending them out.
        Retry up to `max_attempts` times.
        """
        cookies = {}
        mandatory_cookies = self.bot_config["driver"]["mandatory_cookies"].split(",")

        for _ in range(max_attempts):
            cookies = {
                cookie["name"]: cookie["value"] for cookie in self.driver.get_cookies()
            }
            if all(c in cookies.keys() for c in mandatory_cookies):
                break
            time.sleep(5)

        if not cookies or not all(c in cookies for c in mandatory_cookies):
            raise ValueError("Authentication cookies could not be obtained.")
        return cookies

    def session_send_request(
        self, method: str, url: str, **kwargs
    ) -> requests.models.Response:
        """Send a request using the session with the given method and URL."""
        try:
            mandatory_cookies = self.bot_config["driver"]["mandatory_cookies"].split(
                ","
            )
            if not all(c in self.session.cookies.keys() for c in mandatory_cookies):
                self.session.cookies.update(self.get_browser_cookies())
            if method.upper() not in ["GET", "POST"]:
                raise ValueError("Invalid HTTP method specified.")
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise ValueError("Error sending requests using session.")

    def close(self):
        """Close the driver"""
        try:
            self.driver.quit()
        except Exception:
            pass
