set -e

CHROME_URL="https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/124.0.6367.91/linux64/chrome-linux64.zip"
CHROMEDRIVER_URL="https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/124.0.6367.91/linux64/chromedriver-linux64.zip"

mkdir -p /opt/chrome /opt/chrome-driver

curl -Lo /opt/chrome.zip "$CHROME_URL"
unzip -q /opt/chrome.zip -d /opt/chrome
rm -f /opt/chrome.zip

curl -Lo /opt/chromedriver.zip "$CHROMEDRIVER_URL"
unzip -q /opt/chromedriver.zip -d /opt/chrome-driver
rm -f /opt/chromedriver.zip
