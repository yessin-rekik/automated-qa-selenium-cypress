"""ET - Authentification: erreurs d'identification et d'inscription."""
import pytest

from webtours import api
from webtours.utils import future

pytestmark = pytest.mark.et


def test_et_01_wrong_password(app, default_user):
    app.login(default_user["username"], "definitely-wrong")
    app.wait_for_info("error")
    text = app.error_message()
    assert "Incorrect Password" in text
    assert not app.is_logged_in()


def test_et_02_unknown_user(app):
    app.login("unknownuser99", "whatever")
    app.wait_for_info("error")
    text = app.error_message()
    assert "Incorrect Password" in text
    assert not app.is_logged_in()


def test_et_03_empty_credentials_are_rejected(app):
    app.login("", "")
    app.wait_for_info("error")
    assert "error" in app.error_message().lower()
    assert not app.is_logged_in()


def test_et_04_registration_password_mismatch(app):
    user = api.new_credentials("et")
    app.submit_registration(user["username"], user["password"],
                            confirm="AnotherPass1")
    text = app.registration_text()
    assert "password is invalid" in text.lower()


def test_et_05_registration_duplicate_username(app, default_user):
    app.submit_registration(default_user["username"], "SomePass1")
    text = app.registration_text()
    assert "username is taken" in text.lower()


def test_et_06_registration_non_alphanumeric_username(app):
    app.submit_registration("bad user!", "SomePass1")
    text = app.registration_text()
    assert "username is invalid" in text.lower()
