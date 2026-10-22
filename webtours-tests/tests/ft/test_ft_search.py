"""FT - Recherche de vols."""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import config
from webtours.utils import future

pytestmark = pytest.mark.ft


def test_ft_06_search_flights_one_way(logged_app):
    logged_app.search(depart="Denver", arrive="Frankfurt",
                      depart_date=future(2), passengers=1, roundtrip=False)
    results = logged_app.search_results()
    assert len(results["outbound"]) == 4
    assert results["return"] == []
    assert all(price > 0 for _, price, _ in results["outbound"])


def test_ft_07_search_flights_roundtrip(logged_app):
    logged_app.search(depart="Denver", arrive="Frankfurt", depart_date=future(2),
                      return_date=future(4), passengers=1, roundtrip=True)
    results = logged_app.search_results()
    assert len(results["outbound"]) == 4
    assert len(results["return"]) == 4
    assert all(price > 0 for _, price, _ in results["outbound"] + results["return"])


def test_ft_08_city_lists_are_complete(logged_app):
    logged_app.goto_search()
    logged_app.info()
    for field in ("depart", "arrive"):
        options = Select(logged_app.driver.find_element(By.NAME, field)).options
        labels = [o.text for o in options]
        assert labels == config.CITIES


def test_ft_09_seat_and_class_options_are_available(logged_app):
    logged_app.goto_search()
    logged_app.info()
    seat_prefs = [e.get_attribute("value") for e in
                  logged_app.driver.find_elements(By.NAME, "seatPref")]
    seat_types = [e.get_attribute("value") for e in
                  logged_app.driver.find_elements(By.NAME, "seatType")]
    assert seat_prefs == config.SEAT_PREFS
    assert seat_types == config.SEAT_TYPES
