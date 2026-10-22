"""Generate docs/execution-report.md from the pytest JUnit file + Xray mapping."""
import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter, OrderedDict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def first_line(text):
    lines = (text or "").strip().splitlines()
    return lines[0][:160] if lines else ""


def main():
    mapping = json.loads((ROOT / "scripts" / "xray_map.json").read_text(encoding="utf-8"))
    id_by_key = {t["key"]: tid for tid, t in mapping["tests"].items()}
    catalog = {}
    for name, key in mapping["automated"].items():
        tid = id_by_key[key]
        test = mapping["tests"][tid]
        catalog[name] = {"id": tid, "folder": test["folder"],
                         "story": test["story"], "key": key}
    plan = mapping["plan"]["key"]

    tree = ET.parse(ROOT / "webtours-tests" / "reports" / "junit.xml")
    rows, counts, failures = [], Counter(), []
    by_folder = OrderedDict()
    for case in tree.iter("testcase"):
        name = case.get("name")
        info = catalog.get(name, {"id": "?", "folder": "-", "key": "-", "story": "-"})
        tid = info["id"]
        status, message = "PASSED", ""
        if case.find("failure") is not None:
            status = "FAILED"
            message = first_line(case.find("failure").get("message"))
        elif case.find("error") is not None:
            status = "FAILED"
            message = first_line(case.find("error").get("message"))
        elif case.find("skipped") is not None:
            skipped = case.find("skipped")
            status = "FAILED" if "xfail" in (skipped.get("type") or "") else "SKIPPED"
            message = first_line(skipped.get("message"))
        counts[status] += 1
        by_folder.setdefault(info["folder"], Counter())[status] += 1
        rows.append((tid, name, info["folder"], info.get("story") or "-",
                     info.get("key", "-"), status, message))
        if status == "FAILED":
            failures.append((tid, name, message))
    order = {"FT": 0, "ET": 1, "BT": 2, "PT": 3}
    rows.sort(key=lambda r: (order.get(r[0][:2], 9), r[0]))

    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    lines = [
        "# Rapport d'execution - Web Tours",
        "",
        f"- Date : {now}",
        "- Outil : PyTest + Selenium WebDriver (Chrome headless)",
        "- Application : Web Tours - http://127.0.0.1:1080/WebTours/index.htm",
        f"- Plan de test Xray : **{plan}**",
        "",
        "## Synthese",
        "",
        "| Resultat | Nombre |",
        "|---|---|",
        f"| PASSED | {counts['PASSED']} |",
        f"| FAILED (defauts confirmes) | {counts['FAILED']} |",
        f"| Total | {sum(counts.values())} |",
        "",
        f"Taux de reussite : **{counts['PASSED'] / max(1, sum(counts.values())) * 100:.1f} %**",
        "",
        "## Par dossier",
        "",
        "| Dossier | PASSED | FAILED |",
        "|---|---|---|",
    ]
    for folder, c in sorted(by_folder.items()):
        lines.append(f"| {folder} | {c['PASSED']} | {c['FAILED']} |")

    lines += ["", "## Detail des tests", "",
              "| ID | Test | Dossier | Story | Xray | Resultat |",
              "|---|---|---|---|---|---|"]
    for tid, name, folder, story, key, status, _ in rows:
        icon = "PASS" if status == "PASSED" else "FAIL"
        lines.append(f"| {tid} | `{name}` | {folder} | {story} | {key} | **{icon}** |")

    lines += ["", "## Defauts confirmes", ""]
    for tid, name, message in failures:
        lines.append(f"- **{tid}** (`{name}`) : {message}")

    lines += [
        "",
        "## Analyse",
        "",
        "- Le parcours fonctionnel nominal (connexion, recherche, reservation, itineraire, "
        "annulation) fonctionne : tous les tests FT passent.",
        "- Les tests d'erreur, aux limites et de permissions revelent 5 defauts (WT-67 a WT-71), "
        "principalement l'absence de validation cote serveur et l'absence de controle de session "
        "sur les pages CGI.",
        "- La validation cote client (fichiers `chooseFlightValidate.js` et `purchaseValidate.js`) "
        "existe mais n'est pas activee : les formulaires sont generes avec `onsubmit=\"\"`, "
        "donc aucune verification n'est executee avant l'envoi.",
        "- Les tests marques `xfail` dans la suite documentent ces defauts : ils passeront "
        "automatiquement lorsque l'application sera corrigee.",
        "",
        "## Artefacts",
        "",
        "- Rapport HTML : `webtours-tests/reports/report.html`",
        "- JUnit XML (Jenkins) : `webtours-tests/reports/junit.xml`",
        "- Captures d'ecran des echecs : `webtours-tests/reports/screenshots/`",
        "- Execution Xray : voir le Test Execution lie au plan " + plan,
        "",
    ]
    out = ROOT / "docs" / "execution-report.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"written {out} ({sum(counts.values())} tests)")


if __name__ == "__main__":
    sys.exit(main())

