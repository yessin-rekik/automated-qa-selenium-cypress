"""Pytest fixtures: browser, page object and test accounts."""
import os
import sys
from pathlib import Path

import pytest
from selenium import webdriver

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import config as cfg  # noqa: E402
from webtours import WebTours  # noqa: E402
from webtours import api  # noqa: E402

REPORTS = ROOT / "reports"
SCREENSHOTS = REPORTS / "screenshots"


def pytest_configure(config):
    REPORTS.mkdir(exist_ok=True)
    SCREENSHOTS.mkdir(exist_ok=True)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver is not None:
            name = item.name.replace("/", "_").replace("::", "_")
            try:
                driver.save_screenshot(str(SCREENSHOTS / f"{name}.png"))
            except Exception:
                pass


def build_driver():
    if cfg.BROWSER == "edge":
        from selenium.webdriver.edge.options import Options
        options = Options()
        if cfg.HEADLESS:
            options.add_argument("--headless=new")
    else:
        from selenium.webdriver.chrome.options import Options
        options = Options()
        if cfg.HEADLESS:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")
    options.add_argument("--window-size=1400,1000")
    remote = os.getenv("SELENIUM_REMOTE_URL")
    if remote:
        driver = webdriver.Remote(command_executor=remote, options=options)
    else:
        driver = webdriver.Chrome(options=options) if cfg.BROWSER != "edge" else webdriver.Edge(options=options)
    driver.set_page_load_timeout(30)
    return driver


@pytest.fixture
def driver():
    drv = build_driver()
    yield drv
    try:
        drv.quit()
    except Exception:
        pass


@pytest.fixture
def app(driver):
    return WebTours(driver).open()


@pytest.fixture(scope="session")
def default_user():
    user = {"username": cfg.DEFAULT_USER, "password": cfg.DEFAULT_PASSWORD}
    api.register(user)
    return user


@pytest.fixture
def user():
    user = api.new_credentials()
    api.register(user)
    return user


@pytest.fixture
def logged_app(app, user):
    app.login(user["username"], user["password"])
    app.wait_for_info("welcome,")
    return app


@pytest.fixture
def existing_logged_app(app, default_user):
    app.login(default_user["username"], default_user["password"])
    app.wait_for_info("welcome,")
    return app


