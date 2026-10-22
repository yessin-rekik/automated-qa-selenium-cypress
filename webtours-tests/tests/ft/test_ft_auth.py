"""FT - Authentication: inscription, connexion, deconnexion."""
import pytest
from selenium.webdriver.common.by import By

from webtours import api
from webtours.utils import future

pytestmark = pytest.mark.ft


def test_ft_01_login_with_valid_credentials(logged_app, user):
    assert logged_app.is_logged_in(user["username"])


def test_ft_02_logged_in_user_sees_main_menu(logged_app):
    logged_app.navbar()
    alts = [img.get_attribute("alt") for img in logged_app.driver.find_elements(By.TAG_NAME, "img")]
    assert "Search Flights Button" in alts
    assert "Itinerary Button" in alts
    assert "SignOff Button" in alts


def test_ft_03_sign_off_returns_to_login(logged_app):
    logged_app.sign_off()
    assert logged_app.driver.find_element(By.NAME, "username").get_attribute("value") == ""
    assert not logged_app.is_logged_in()


def test_ft_04_register_then_login(app):
    new_user = api.new_credentials("ft")
    app.submit_registration(new_user["username"], new_user["password"])
    assert "Thank you" in app.registration_text()
    assert new_user["username"] in app.registration_text()

    app.open().login(new_user["username"], new_user["password"])
    app.wait_for_info("welcome,")
    assert app.is_logged_in(new_user["username"])


def test_ft_05_home_page_welcomes_the_user(logged_app, user):
    logged_app.goto_home()
    text = logged_app.page_text().lower()
    assert f"welcome, {user['username']}".lower() in text
