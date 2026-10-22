"""Create Xray tests, link them to user stories and build the test plan."""
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
from xray_catalog import CATALOG  # noqa: E402

BASE = os.environ["URL"].rstrip("/")
AUTH = (os.environ["EMAIL"], os.environ["JIRA_API"])
PROJECT = os.environ.get("JIRA_PROJECT", "WT")
H = {"Accept": "application/json", "Content-Type": "application/json"}
MAP_FILE = ROOT / "scripts" / "xray_map.json"

CREATE_TEST = """
mutation CreateTest($jira: JSON!, $steps: [CreateStepInput], $folder: String) {
  createTest(testType: {name: "Manual"}, steps: $steps, folderPath: $folder, jira: $jira) {
    test { issueId }
  }
}
"""

CREATE_PLAN = """
mutation CreatePlan($jira: JSON!, $tests: [String]) {
  createTestPlan(jira: $jira, testIssueIds: $tests) { testPlan { issueId } }
}
"""


def jira_get(path, **params):
    r = requests.get(f"{BASE}{path}", auth=AUTH, headers=H, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def existing_tests():
    r = jira_get("/rest/api/3/search/jql", jql=f"project={PROJECT} AND issuetype=Test ORDER BY created ASC",
                 maxResults=100, fields="summary,parent,labels")
    return {i["fields"]["summary"]: {"key": i["key"], "id": i["id"]} for i in r["issues"]}


def link_test_to_story(test_key, story_key):
    issue = jira_get(f"/rest/api/3/issue/{test_key}", fields="issuelinks")
    for link in issue["fields"].get("issuelinks", []):
        if link["type"]["name"] == "Test":
            other = link.get("outwardIssue") or link.get("inwardIssue") or {}
            if other.get("key") == story_key:
                return False
    payload = {"type": {"name": "Test"},
               "inwardIssue": {"key": test_key},
               "outwardIssue": {"key": story_key}}
    r = requests.post(f"{BASE}/rest/api/3/issueLink", auth=AUTH, headers=H, json=payload, timeout=60)
    if r.status_code >= 300:
        print("  link ERR", test_key, story_key, r.status_code, r.text[:200])
        return False
    return True


def fix_smoke_issue():
    """WT-20 was created while probing the API; turn it into the smoke test."""
    tests_now = existing_tests()
    found = (tests_now.get('[TEMP] probe xray')
             or tests_now.get("FT-00 - Smoke: l'application Web Tours est accessible"))
    if not found:
        return None
    key, issue_id = found["key"], found["id"]
    requests.put(f"{BASE}/rest/api/3/issue/{key}", auth=AUTH, headers=H, timeout=60,
                 json={"fields": {"summary": "FT-00 - Smoke: l'application Web Tours est accessible",
                                  "labels": ["ft", "smoke"]}}).raise_for_status()
    x = Xray()
    x.authenticate()
    folder = "/FT/Authentification"
    try:
        x.gql('mutation($id: String!, $p: String!) { updateTestFolder(issueId: $id, folderPath: $p) }',
              {"id": issue_id, "p": folder})
    except RuntimeError as exc:
        print("  folder update skipped:", exc)
    x.gql("""
      mutation($id: String!) {
        addTestStep(issueId: $id, step: {action: "Verifier la reponse HTTP de l'application",
                                         data: "GET /WebTours/index.htm",
                                         result: "Code 200 et titre 'Web Tours' affiche"}) { id }
      }""", {"id": issue_id})
    print(f"reused {key} as smoke test")
    return {"key": key, "id": issue_id}


def main():
    x = Xray()
    x.authenticate()

    existing = existing_tests()

    mapping = {"tests": {}, "automated": {}, "folders": {}}
    if MAP_FILE.exists():
        mapping = json.loads(MAP_FILE.read_text(encoding="utf-8"))
    mapping.setdefault("tests", {})

    created = 0
    for tid, item in CATALOG.items():
        summary = item["summary"]
        if summary in existing:
            key, issue_id = existing[summary]["key"], existing[summary]["id"]
        else:
            data = x.gql(CREATE_TEST, {
                "jira": {"fields": {
                    "summary": summary,
                    "project": {"key": PROJECT},
                    "labels": [tid.split("-")[0].lower()],
                    "description": (f"Test manuel {tid}. Automatisation: "
                                    f"{item['automated']} (Selenium/PyTest)."),
                }},
                "steps": item["steps"],
                "folder": item["folder"],
            })
            issue_id = data["createTest"]["test"]["issueId"]
            key = requests.get(f"{BASE}/rest/api/3/issue/{issue_id}", auth=AUTH,
                               headers=H, timeout=60).json()["key"]
            existing[summary] = {"key": key, "id": issue_id}
            created += 1
            print(f"created {key} {summary}")

        mapping["tests"][tid] = {"key": key, "id": issue_id,
                                 "summary": summary, "folder": item["folder"],
                                 "story": item["story"]}
        mapping["automated"][item["automated"]] = key
        mapping["folders"].setdefault(item["folder"], []).append(key)

        if link_test_to_story(key, item["story"]):
            print(f"  linked {key} -> {item['story']}")

    smoke = fix_smoke_issue()
    if smoke:
        mapping['automated']["test_ft_00_application_is_available"] = smoke["key"]
        mapping["tests"]["FT-00"] = {"key": smoke["key"], "id": smoke["id"],
                                     "summary": "FT-00 - Smoke: l'application Web Tours est accessible",
                                     "folder": "/FT", "story": None}
        mapping["folders"].setdefault("/FT", []).append(smoke["key"])
        if link_test_to_story(smoke["key"], "WT-7"):
            print(f"  linked {smoke['key']} -> WT-7")

    all_ids = [t["id"] for t in mapping["tests"].values()]
    plan_summary = "Plan de test - Web Tours (FT/ET/BT/PT)"
    plans = jira_get("/rest/api/3/search/jql",
                     jql=f'project={PROJECT} AND issuetype="Test Plan" AND summary ~ "Web Tours"',
                     maxResults=10, fields="summary")
    if plans["issues"]:
        plan_key = plans["issues"][0]["key"]
        plan_id = plans["issues"][0]["id"]
        x.gql("""
            mutation($id: String!, $tests: [String]!) {
              addTestsToTestPlan(issueId: $id, testIssueIds: $tests) { __typename }
            }""", {"id": plan_id, "tests": all_ids})
        print(f"updated test plan {plan_key} with {len(all_ids)} tests")
    else:
        data = x.gql(CREATE_PLAN, {
            "jira": {"fields": {
                "summary": plan_summary,
                "project": {"key": PROJECT},
                "description": "Plan de test du site de reservation de vols Web Tours: "
                               "tests fonctionnels (FT), d'erreur (ET), aux limites (BT) "
                               "et de permissions (PT).",
            }},
            "tests": all_ids,
        })
        plan_id = data["createTestPlan"]["testPlan"]["issueId"]
        plan_key = requests.get(f"{BASE}/rest/api/3/issue/{plan_id}", auth=AUTH,
                                headers=H, timeout=60).json()["key"]
        print(f"created test plan {plan_key} with {len(all_ids)} tests")

    mapping["plan"] = {"key": plan_key, "id": plan_id}
    MAP_FILE.write_text(json.dumps(mapping, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n{created} tests created, {len(mapping['tests'])} total, plan {plan_key}")
    print(f"mapping saved to {MAP_FILE}")


if __name__ == "__main__":
    main()





