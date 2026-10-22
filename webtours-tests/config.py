"""Configuration for the Web Tours test suite (env-overridable)."""
import os

BASE_URL = os.getenv("WEBTOURS_URL", "http://127.0.0.1:1080/WebTours/index.htm")
CGI_URL = os.getenv("WEBTOURS_CGI", "http://127.0.0.1:1080/cgi-bin")
HOST_URL = os.getenv("WEBTOURS_HOST", "http://127.0.0.1:1080")

HEADLESS = os.getenv("HEADLESS", "1").lower() not in ("0", "false", "no")
BROWSER = os.getenv("BROWSER", "chrome").lower()
TIMEOUT = int(os.getenv("WEBTOURS_TIMEOUT", "10"))

PASSWORD = "Passw0rd"
DEFAULT_USER = os.getenv("WEBTOURS_USER", "wttester")
DEFAULT_PASSWORD = os.getenv("WEBTOURS_PASSWORD", PASSWORD)

CITIES = ["Denver", "Frankfurt", "London", "Los Angeles", "Paris",
          "Portland", "San Francisco", "Seattle", "Sydney", "Zurich"]
SEAT_PREFS = ["Aisle", "Window", "None"]
SEAT_TYPES = ["First", "Business", "Coach"]

VALID_CARD = "12345678"
VALID_EXP = "12/30"
