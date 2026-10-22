"""FT - Reservation et paiement."""
import pytest

import config
from webtours.utils import future, total_from

pytestmark = pytest.mark.ft


def _open_payment(app, passengers=1, roundtrip=False, seat_type=None):
    app.search(depart="Denver", arrive="Frankfurt",
               depart_date=future(2), return_date=future(4) if roundtrip else None,
               passengers=passengers, roundtrip=roundtrip, seat_type=seat_type)
    results = app.search_results()
    price = results["outbound"][0][1]
    inbound = 0 if roundtrip else None
    if roundtrip:
        price += results["return"][0][1]
    app.select_flight(outbound=0, inbound=inbound)
    return price


def test_ft_10_complete_booking_shows_invoice(logged_app):
    price = _open_payment(logged_app)
    logged_app.pay(card=config.VALID_CARD, exp=config.VALID_EXP)
    text = logged_app.page_text()
    assert "Thank you for booking through Web Tours" in text
    assert total_from(text) == price


def test_ft_11_invoice_contains_payment_information(logged_app):
    _open_payment(logged_app)
    logged_app.pay(card="12345678", exp="12/30")
    text = logged_app.page_text()
    assert "Credit Card # 12345678" in text
    assert "Total Charged" in text
    itinerary = logged_app.itinerary_text()
    assert "x-5678" in itinerary


def test_ft_12_total_depends_on_passenger_count(logged_app):
    price = _open_payment(logged_app, passengers=3)
    form = logged_app.payment_form()
    assert form["passengers"] == ["pass1", "pass2", "pass3"]
    assert total_from(form["total_text"]) == price * 3

    logged_app.pay(card=config.VALID_CARD, exp=config.VALID_EXP)
    assert total_from(logged_app.page_text()) == price * 3


def test_ft_13_seat_class_is_used_in_invoice(logged_app):
    _open_payment(logged_app, seat_type="Business")
    logged_app.pay(card=config.VALID_CARD, exp=config.VALID_EXP)
    assert "business class" in logged_app.page_text().lower()
