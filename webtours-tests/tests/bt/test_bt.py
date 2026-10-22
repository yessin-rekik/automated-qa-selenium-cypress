"""BT - Tests aux limites."""
import pytest
from selenium.webdriver.common.by import By

import config
from webtours.utils import future, total_from

pytestmark = pytest.mark.bt


def test_bt_01_username_is_limited_to_14_characters(app):
    app.navbar()
    field = app.driver.find_element(By.NAME, "username")
    field.send_keys("a" * 20)
    assert len(field.get_attribute("value")) == 14


def test_bt_02_credit_card_is_limited_to_20_characters(logged_app):
    logged_app.search(depart="Denver", arrive="Frankfurt", depart_date=future(2),
                      passengers=1, roundtrip=False)
    logged_app.select_flight(outbound=0)
    logged_app.info()
    field = logged_app.driver.find_element(By.NAME, "creditCard")
    field.send_keys("9" * 25)
    assert len(field.get_attribute("value")) == 20


def test_bt_03_one_passenger_is_the_lower_valid_boundary(logged_app):
    logged_app.search(depart="Denver", arrive="Frankfurt", depart_date=future(2),
                      passengers=1, roundtrip=False)
    price = logged_app.search_results()["outbound"][0][1]
    logged_app.select_flight(outbound=0)
    logged_app.pay(card=config.VALID_CARD, exp=config.VALID_EXP)
    assert total_from(logged_app.page_text()) == price


@pytest.mark.xfail(reason="BUG-02: nombre de passagers 0 accepte", strict=False)
def test_bt_04_zero_passenger_is_rejected(logged_app):
    logged_app.search(depart="Denver", arrive="Frankfurt", depart_date=future(2),
                      passengers=0, roundtrip=False)
    text = logged_app.page_text().lower()
    assert "error" in text or "invalid" in text or "passenger" in text


@pytest.mark.xfail(reason="BUG-02: nombre de passagers non numerique accepte", strict=False)
def test_bt_05_non_numeric_passenger_count_is_rejected(logged_app):
    logged_app.search(depart="Denver", arrive="Frankfurt", depart_date=future(2),
                      passengers="abc", roundtrip=False)
    text = logged_app.page_text().lower()
    assert "error" in text or "invalid" in text or "passenger" in text


def test_bt_06_eight_passengers_is_the_upper_input_boundary(logged_app):
    logged_app.search(depart="Denver", arrive="Frankfurt", depart_date=future(2),
                      passengers=8, roundtrip=False)
    price = logged_app.search_results()["outbound"][0][1]
    logged_app.select_flight(outbound=0)
    form = logged_app.payment_form()
    assert form["passengers"] == [f"pass{i}" for i in range(1, 9)]
    assert total_from(form["total_text"]) == price * 8


@pytest.mark.xfail(reason="BUG-02: 999 passagers acceptes sans limite", strict=False)
def test_bt_07_huge_passenger_count_is_rejected(logged_app):
    logged_app.search(depart="Denver", arrive="Frankfurt", depart_date=future(2),
                      passengers=999, roundtrip=False)
    text = logged_app.page_text().lower()
    assert "error" in text or "invalid" in text or "passenger" in text


@pytest.mark.xfail(reason="BUG-01: 29/02/2025 accepte sans message", strict=False)
def test_bt_08_non_existent_date_is_rejected(logged_app):
    logged_app.search(depart="Denver", arrive="Paris", depart_date="02/29/2025",
                      return_date=future(5), roundtrip=True)
    text = logged_app.page_text().lower()
    assert "error" in text or "invalid" in text

