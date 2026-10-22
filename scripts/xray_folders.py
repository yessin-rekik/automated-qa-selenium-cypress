"""Create the Xray Test Repository folders (FT/ET/BT/PT) and file every test."""
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
load_dotenv(ROOT / ".env")

from xray_client import Xray  # noqa: E402

BASE = os.environ["URL"].rstrip("/")
AUTH = (os.environ["EMAIL"], os.environ["JIRA_API"])
MAP_FILE = ROOT / "scripts" / "xray_map.json"
PROJECT_ID = os.environ.get("JIRA_PROJECT_ID", "10035")


def main():
    mapping = json.loads(MAP_FILE.read_text(encoding="utf-8"))
    x = Xray()
    x.authenticate()

    paths = sorted({t["folder"] for t in mapping["tests"].values()},
                   key=lambda p: p.count("/"))
    created = set()
    for path in paths:
        parts = [p for p in path.split("/") if p]
        for depth in range(1, len(parts) + 1):
            current = "/" + "/".join(parts[:depth])
            if current in created:
                continue
            try:
                x.gql('mutation($p: String!) { createFolder(projectId: "%s", path: $p) { warnings } }' % PROJECT_ID,
                      {"p": current})
                created.add(current)
            except Exception as exc:
                print("folder", current, "->", exc)

    moved = 0
    for tid, item in mapping["tests"].items():
        try:
            x.gql('mutation($id: String!, $p: String!){ updateTestFolder(issueId: $id, folderPath: $p) }',
                  {"id": item["id"], "p": item["folder"]})
            moved += 1
        except Exception as exc:
            print("move", tid, item["key"], "->", exc)
    print(f"{len(created)} folders created, {moved} tests filed")

    for path in sorted(paths):
        keys = [i["key"] for i in mapping["tests"].values() if i["folder"] == path]
        print(f"  {path}: {len(keys)} tests ({', '.join(sorted(keys)[:6])}...)")


if __name__ == "__main__":
    main()
