from selenium.webdriver.common.by import By

COOKIES_ACCEPT_BUTTON = (By.ID, "cookie-consent-button-accept")
LOGIN_BUTTON = (By.ID, "login-mounted")
LOGIN_INPUT_USERNAME = (By.XPATH, "//input[@id='login-dialog-input-name']")
LOGIN_INPUT_PASSWORD = (By.XPATH, "//input[@id='login-dialog-input-password']")
LOGIN_COFIRM_LOGIN = (By.ID, "login-dialog-sign-in")

BET_CONTAINER = (
    By.XPATH,
    "//div[@data-testing-selector='MatchDetailCard' and @market-type-id='{}']",
)
BET_OPTION_BUTTON = (By.XPATH, "//button[@data-id='{}']")
# BETSLIP_CONTAINER = (By.ID, "betslip-container-root")
BETSLIP_PAY_INPUT = (By.XPATH, "//input[@data-test='betslip-payin-input']")
# BETSLIP_ALL_IN_BUTTON = (By.XPATH, "//button[@data-test='betslip-quick-stakes-all-in']")
BETSPLIT_PLACEMENT_BUTTON = (
    By.XPATH,
    "//button[@data-test='betslip-placement-button']",
)
