"""FT - Itineraire et annulation."""
import pytest

import config
from webtours.utils import future

pytestmark = pytest.mark.ft


def _book_one_way(app):
    app.search(depart="Denver", arrive="Frankfurt", depart_date=future(2),
               passengers=1, roundtrip=False)
    app.select_flight(outbound=0)
    app.pay(card=config.VALID_CARD, exp=config.VALID_EXP)
    return app.page_text()


def test_ft_14_booking_appears_in_itinerary(logged_app):
    invoice = _book_one_way(logged_app)
    flight = invoice.split("Flight ")[1][:3]
    itinerary = logged_app.itinerary_text()
    assert "Flight Details" in itinerary
    assert flight in itinerary
    assert "Total Charge" in itinerary


def test_ft_15_cancel_a_single_reservation(logged_app):
    _book_one_way(logged_app)
    _book_one_way(logged_app)
    logged_app.itinerary_text()
    assert len(logged_app.itinerary_rows()) == 2

    logged_app.cancel_first_reservation()
    itinerary = logged_app.itinerary_text()
    assert "No flights have been reserved" not in itinerary
    assert len(logged_app.itinerary_rows()) == 1


def test_ft_16_cancel_all_reservations(logged_app):
    _book_one_way(logged_app)
    _book_one_way(logged_app)
    logged_app.itinerary_text()
    assert len(logged_app.itinerary_rows()) == 2

    logged_app.cancel_all_reservations()
    itinerary = logged_app.itinerary_text()
    assert "No flights have been reserved" in itinerary


def test_ft_17_empty_itinerary_message(logged_app):
    itinerary = logged_app.itinerary_text()
    assert "No flights have been reserved" in itinerary
