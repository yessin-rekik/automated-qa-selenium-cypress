"""HTTP helpers used to create accounts and to probe unauthenticated access."""
import uuid

import requests

import config


def new_credentials(prefix="wt"):
    username = f"{prefix}{uuid.uuid4().hex[:8]}"[:14]
    return {"username": username, "password": config.PASSWORD,
            "firstName": "Web", "lastName": "Tours",
            "address1": "1 Rue de la Paix", "address2": "Tunis"}


def register(user, session=None):
    """Registers a user through the application's own sign-up endpoint."""
    s = session or requests.Session()
    payload = {
        "register.x": "1",
        "username": user["username"],
        "password": user["password"],
        "passwordConfirm": user.get("passwordConfirm", user["password"]),
        "firstName": user.get("firstName", "Web"),
        "lastName": user.get("lastName", "Tours"),
        "address1": user.get("address1", "1 Rue de la Paix"),
        "address2": user.get("address2", "Tunis"),
    }
    r = s.post(f"{config.CGI_URL}/login.pl", data=payload, timeout=30)
    r.raise_for_status()
    return r.text


def get_direct(path, session=None):
    """GET a cgi path with a clean session (no authentication cookies)."""
    s = session or requests.Session()
    r = s.get(f"{config.CGI_URL}/{path.lstrip('/')}", timeout=30)
    return r


def ensure_user(user=None):
    user = user or {"username": config.DEFAULT_USER, "password": config.DEFAULT_PASSWORD}
    body = register(user)
    if "Thank you" not in body and "username is taken" not in body:
        # already existing accounts answer with the profile form
        pass
    return user
