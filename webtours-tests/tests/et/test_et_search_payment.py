"""ET - Recherche et paiement: entrees invalides.

Les tests marques xfail documentent des defauts constates de l'application
(voir docs/bugs.md); ils passent automatiquement si le defaut est corrige.
"""
import pytest

import config
from webtours.utils import future, past

pytestmark = pytest.mark.et

ERROR_WORDS = ("error", "invalid", "please", "must", "refus", "incorrect")


def _rejected(app):
    text = app.page_text().lower()
    return any(word in text for word in ERROR_WORDS)


@pytest.mark.xfail(reason="BUG-01: date invalide acceptee sans message d'erreur", strict=False)
def test_et_07_invalid_date_format_is_rejected(logged_app):
    logged_app.search(depart="Denver", arrive="Paris", depart_date="31/45/2026",
                      return_date=future(3), roundtrip=True)
    assert _rejected(logged_app)


@pytest.mark.xfail(reason="BUG-01: date de depart passee acceptee", strict=False)
def test_et_08_past_departure_date_is_rejected(logged_app):
    logged_app.search(depart="Denver", arrive="Paris", depart_date=past(60),
                      return_date=past(30), roundtrip=True)
    assert _rejected(logged_app)


@pytest.mark.xfail(reason="BUG-01: ville de depart = ville d'arrivee acceptee", strict=False)
def test_et_09_same_departure_and_arrival_city_is_rejected(logged_app):
    logged_app.search(depart="Denver", arrive="Denver", depart_date=future(2),
                      return_date=future(3), roundtrip=True)
    assert _rejected(logged_app)


@pytest.mark.xfail(reason="BUG-01: date de retour anterieure au depart acceptee", strict=False)
def test_et_10_return_before_departure_is_rejected(logged_app):
    logged_app.search(depart="Denver", arrive="Paris", depart_date=future(10),
                      return_date=future(2), roundtrip=True)
    assert _rejected(logged_app)


def _reach_payment(app):
    app.search(depart="Denver", arrive="Frankfurt", depart_date=future(2),
               passengers=1, roundtrip=False)
    app.select_flight(outbound=0)


@pytest.mark.xfail(reason="BUG-03: paiement accepte sans numero de carte", strict=False)
def test_et_11_payment_without_credit_card_is_rejected(logged_app):
    _reach_payment(logged_app)
    logged_app.pay(card="", exp=config.VALID_EXP)
    assert "please" in logged_app.page_text().lower() or "invalid" in logged_app.page_text().lower()


@pytest.mark.xfail(reason="BUG-03: carte non numerique acceptee", strict=False)
def test_et_12_payment_with_non_numeric_card_is_rejected(logged_app):
    _reach_payment(logged_app)
    logged_app.pay(card="abcdefgh", exp=config.VALID_EXP)
    assert "invalid" in logged_app.page_text().lower()


@pytest.mark.xfail(reason="BUG-03: mois d'expiration 13 accepte", strict=False)
def test_et_13_payment_with_invalid_expiration_month_is_rejected(logged_app):
    _reach_payment(logged_app)
    logged_app.pay(card=config.VALID_CARD, exp="13/30")
    assert "invalid" in logged_app.page_text().lower()


@pytest.mark.xfail(reason="BUG-03: nom vide accepte au paiement", strict=False)
def test_et_14_payment_with_empty_first_name_is_rejected(logged_app):
    _reach_payment(logged_app)
    logged_app.pay(card=config.VALID_CARD, exp=config.VALID_EXP, first_name="")
    assert "please" in logged_app.page_text().lower() or "invalid" in logged_app.page_text().lower()
