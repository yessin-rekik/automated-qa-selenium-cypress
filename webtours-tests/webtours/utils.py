"""Small helpers shared by the tests."""
from datetime import date, timedelta


def _fmt(d):
    return d.strftime("%m/%d/%Y")


def future(days=1):
    return _fmt(date.today() + timedelta(days=days))


def past(days=1):
    return _fmt(date.today() - timedelta(days=days))


def total_from(text):
    """Extracts the amount following 'Total Cost' or 'Total for N ticket(s) is = $'."""
    import re

    for pattern in (r"Total Cost\s*\$?\s*([\d.]+)",
                    r"Total for \d+ ticket\(s\) is\s*=\s*\$\s*([\d.]+)",
                    r"Total Charge:\s*\$\s*([\d.]+)"):
        match = re.search(pattern, text)
        if match:
            return float(match.group(1))
    return None
