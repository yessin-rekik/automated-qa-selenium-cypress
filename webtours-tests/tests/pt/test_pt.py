"""PT - Controle d'acces et isolation des donnees."""
import pytest

import config
from webtours import api
from webtours.utils import future

pytestmark = pytest.mark.pt


@pytest.mark.xfail(reason="BUG-04: itinerary.pl accessible sans session", strict=False)
def test_pt_01_itinerary_requires_authentication():
    response = api.get_direct("itinerary.pl")
    body = response.text.lower()
    assert response.status_code in (302, 401, 403) or "sign" in body or "login" in body


@pytest.mark.xfail(reason="BUG-04: reservations.pl accessible sans session", strict=False)
def test_pt_02_flight_search_requires_authentication():
    response = api.get_direct("reservations.pl?page=welcome")
    body = response.text.lower()
    assert response.status_code in (302, 401, 403) or "sign in" in body or "login" in body


def test_pt_03_anonymous_profile_page_does_not_leak_session():
    response = api.get_direct("login.pl?intro=true")
    body = response.text
    assert "Welcome, ," not in body


def test_pt_04_users_cannot_see_each_others_reservations(app):
    owner = api.new_credentials("pt")
    api.register(owner)
    stranger = api.new_credentials("pt")
    api.register(stranger)

    app.login(owner["username"], owner["password"])
    app.wait_for_info("welcome,")
    app.search(depart="Denver", arrive="Frankfurt", depart_date=future(2),
               passengers=1, roundtrip=False)
    app.select_flight(outbound=0)
    app.pay(card=config.VALID_CARD, exp=config.VALID_EXP)
    assert "Thank you for booking" in app.page_text()

    app.sign_off()
    app.login(stranger["username"], stranger["password"])
    app.wait_for_info("welcome,")
    assert "No flights have been reserved" in app.itinerary_text()


def test_pt_05_reservations_are_not_available_after_sign_off(app):
    user = api.new_credentials("pt")
    api.register(user)
    app.login(user["username"], user["password"])
    app.wait_for_info("welcome,")
    app.search(depart="Denver", arrive="Frankfurt", depart_date=future(2),
               passengers=1, roundtrip=False)
    app.select_flight(outbound=0)
    app.pay(card=config.VALID_CARD, exp=config.VALID_EXP)

    app.sign_off()
    app.driver.get(f"{config.CGI_URL}/itinerary.pl")
    assert "No flights have been reserved" in app.driver.find_element("tag name", "body").text

