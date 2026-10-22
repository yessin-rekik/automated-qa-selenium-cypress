"""Vérifie que l'application Web Tours répond (utilisé par Jenkins)."""
import os
import sys
import time

import requests

url = os.getenv("WEBTOURS_URL", "http://127.0.0.1:1080/WebTours/index.htm")
# index.htm est statique : on verifie aussi une page Perl CGI (500 si perl absent)
cgi_url = os.getenv("WEBTOURS_CGI", "http://127.0.0.1:1080/cgi-bin") + "/welcome.pl?signOff=true"
last_error = None
for attempt in range(1, 6):
    try:
        response = requests.get(url, timeout=10)
        print(f"[{attempt}] GET {url} -> HTTP {response.status_code}")
        if response.status_code == 200 and "Web Tours" in response.text:
            cgi = requests.get(cgi_url, timeout=10)
            print(f"[{attempt}] GET {cgi_url} -> HTTP {cgi.status_code}")
            if cgi.status_code == 200:
                sys.exit(0)
            response = cgi
        last_error = f"unexpected content (HTTP {response.status_code})"
    except Exception as exc:  # noqa: BLE001
        last_error = str(exc)
        print(f"[{attempt}] {last_error}")
    time.sleep(3)
print(f"Web Tours is not reachable at {url}: {last_error}")
sys.exit(1)
