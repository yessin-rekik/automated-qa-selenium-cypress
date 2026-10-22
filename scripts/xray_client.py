"""Minimal Xray Cloud client (GraphQL + REST)."""
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

REGIONS = [
    "https://xray.cloud.getxray.app",
    "https://eu.xray.cloud.getxray.app",
    "https://us.xray.cloud.getxray.app",
]


class Xray:
    def __init__(self):
        self.client_id = os.environ["XRAY_CLIENT_ID"]
        self.client_secret = os.environ["XRAY_CLIENT_SECRET"]
        self.base = os.environ.get("XRAY_URL", "").rstrip("/")
        self.token = None

    def authenticate(self):
        errors = []
        for base in ([self.base] if self.base else REGIONS):
            r = requests.post(f"{base}/api/v2/authenticate",
                              json={"client_id": self.client_id,
                                    "client_secret": self.client_secret}, timeout=60)
            if r.status_code == 200:
                self.base = base
                self.token = r.json() if isinstance(r.json(), str) else r.text.strip('"')
                return self.token
            errors.append(f"{base} -> {r.status_code} {r.text[:120]}")
        raise RuntimeError("Xray authentication failed:\n" + "\n".join(errors))

    def gql(self, query, variables=None):
        if not self.token:
            self.authenticate()
        r = requests.post(f"{self.base}/api/v2/graphql", timeout=120,
                          headers={"Authorization": f"Bearer {self.token}",
                                   "Content-Type": "application/json"},
                          json={"query": query, "variables": variables or {}})
        payload = r.json()
        if payload.get("errors"):
            raise RuntimeError(payload["errors"])
        return payload["data"]

    def rest(self, path, method="GET", **kwargs):
        if not self.token:
            self.authenticate()
        r = requests.request(method, f"{self.base}/api/v2/{path.lstrip('/')}", timeout=120,
                             headers={"Authorization": f"Bearer {self.token}"}, **kwargs)
        r.raise_for_status()
        return r
