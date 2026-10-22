"""Smoke test - verifie que l'application repond avant la suite."""
import pytest
import requests

import config

pytestmark = pytest.mark.ft


def test_ft_00_application_is_available():
    response = requests.get(config.BASE_URL, timeout=15)
    assert response.status_code == 200
    assert "Web Tours" in response.text
