"""Publish the pytest results as an Xray Test Execution.

Usage: python scripts/results_to_xray.py [--junit PATH] [--plan KEY] [--summary TEXT]

Les tests sont retrouves par nom PyTest (xray_map.json) ou, pour Cypress, par
l'identifiant present dans le titre ("FT-01 ..."). Un titre contenant "[BUG-"
constate un defaut connu : il est publie FAILED comme les xfail PyTest.
"""
import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
load_dotenv(ROOT / ".env")

from xray_client import Xray  # noqa: E402


def parse_junit(path):
    tree = ET.parse(path)
    results = []
    for case in tree.iter("testcase"):
        name = case.get("name")
        failure = case.find("failure")
        error = case.find("error")
        skipped = case.find("skipped")
        if failure is not None or error is not None:
            node = failure if failure is not None else error
            message = (node.get("message") or node.text or "").strip().splitlines()
            results.append((name, "FAILED", message[0][:400] if message else "assertion failed"))
        elif skipped is not None:
            kind = skipped.get("type", "")
            message = (skipped.get("message") or "").strip().splitlines()
            comment = message[0][:400] if message else "skipped"
            if "xfail" in kind.lower():
                results.append((name, "FAILED", f"Defaut confirme (xfail): {comment}"))
            else:
                results.append((name, "TODO", comment))
        elif "[BUG-" in name:
            results.append((name, "FAILED", f"Defaut confirme: {name}"))
        else:
            results.append((name, "PASSED", ""))
    return results


def xray_key(name, mapping):
    if name in mapping["automated"]:
        return mapping["automated"][name]
    match = re.search(r"(?<![A-Z])([FEBP]T-[0-9]{2})(?![0-9])", name)
    if match and match.group(1) in mapping["tests"]:
        return mapping["tests"][match.group(1)]["key"]
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--junit", default=str(ROOT / "webtours-tests" / "reports" / "junit.xml"))
    parser.add_argument("--plan", default=os.environ.get("XRAY_TEST_PLAN", "WT-65"))
    parser.add_argument("--summary", default="Execution automatisee Selenium - Web Tours")
    parser.add_argument("--environments", default="Chrome headless / http://127.0.0.1:1080")
    args = parser.parse_args()

    mapping = json.loads((ROOT / "scripts" / "xray_map.json").read_text(encoding="utf-8"))

    raw = parse_junit(args.junit)
    tests, unknown = [], []
    passed = failed = 0
    for name, status, comment in raw:
        key = xray_key(name, mapping)
        if not key:
            unknown.append(name)
            continue
        entry = {"testKey": key, "status": status}
        if comment:
            entry["comment"] = comment
        tests.append(entry)
        passed += status == "PASSED"
        failed += status == "FAILED"

    now = datetime.now(timezone(timedelta(hours=1)))
    payload = {
        "info": {
            "summary": f"{args.summary} - {now:%d/%m/%Y %H:%M}",
            "description": (f"{args.summary}. "
                            f"{passed} tests PASSED, {failed} tests FAILED. "
                            f"Environnement: {args.environments}."),
            "project": os.environ.get("JIRA_PROJECT", "WT"),
            "testPlanKey": args.plan,
            "startDate": now.strftime("%Y-%m-%dT%H:%M:%S+01:00"),
            "finishDate": now.strftime("%Y-%m-%dT%H:%M:%S+01:00"),
        },
        "tests": tests,
    }

    out = ROOT / "webtours-tests" / "reports" / "xray_import.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    x = Xray()
    x.authenticate()
    response = x.rest("import/execution", method="POST", json=payload)
    data = response.json()
    print(f"Test Execution: {data.get('key')} (statuses: {passed} PASSED / {failed} FAILED)")
    if unknown:
        print("tests without Xray mapping:", unknown)
    return data.get("key")


if __name__ == "__main__":
    main()

