"""Create the Bug issues found by the automated suite and link them to tests."""
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

BASE = os.environ["URL"].rstrip("/")
AUTH = (os.environ["EMAIL"], os.environ["JIRA_API"])
PROJECT = os.environ.get("JIRA_PROJECT", "WT")
H = {"Accept": "application/json", "Content-Type": "application/json"}
MAP_FILE = ROOT / "scripts" / "xray_map.json"


def p(text):
    return {"type": "paragraph", "content": [{"type": "text", "text": text}]}


def heading(text, level=3):
    return {"type": "heading", "attrs": {"level": level},
            "content": [{"type": "text", "text": text}]}


def bullets(items):
    return {"type": "bulletList", "content": [
        {"type": "listItem", "content": [p(i)]} for i in items]}


BUGS = [
    {
        "summary": "BUG-01 - Les criteres de recherche de vol ne sont pas valides",
        "priority": "High",
        "labels": ["bug", "et", "bt", "recherche"],
        "tests": ["ET-07", "ET-08", "ET-09", "ET-10", "BT-08"],
        "story": "WT-12",
        "steps": [
            "Se connecter a Web Tours.",
            "Cliquer sur Search Flights.",
            "Saisir une date invalide (31/45/2026), une date passee, deux villes identiques "
            "ou une date de retour anterieure au depart.",
            "Cliquer sur la fleche de recherche.",
        ],
        "expected": "La recherche est refusee avec un message explicite pour chaque cas.",
        "actual": "La recherche est executee: la page 'Find Flight' s'affiche sans aucun message "
                  "d'erreur (aucun vol pour les dates invalides, vols a 0 $ pour Denver-Denver). "
                  "Les tests ET-07 a ET-10 et BT-08 echouent.",
    },
    {
        "summary": "BUG-02 - Le nombre de passagers n'est pas valide",
        "priority": "High",
        "labels": ["bug", "bt", "recherche"],
        "tests": ["BT-04", "BT-05", "BT-07"],
        "story": "WT-12",
        "steps": [
            "Se connecter et ouvrir Search Flights.",
            "Saisir 0, 'abc' ou 999 dans le champ No. of Passengers.",
            "Lancer la recherche puis poursuivre jusqu'au paiement.",
        ],
        "expected": "Seuls les entiers positifs dans une plage raisonnable (1-8) sont acceptes.",
        "actual": "Toutes les valeurs sont acceptees: la recherche aboutit et le formulaire de "
                  "paiement genere autant de champs passager que demande (999 champs). "
                  "Tests BT-04, BT-05 et BT-07 en echec.",
    },
    {
        "summary": "BUG-03 - Les donnees de paiement ne sont pas validees",
        "priority": "Highest",
        "labels": ["bug", "et", "paiement"],
        "tests": ["ET-11", "ET-12", "ET-13", "ET-14"],
        "story": "WT-15",
        "steps": [
            "Reserver un vol jusqu'au formulaire Payment Details.",
            "Vider le champ Credit Card (ou saisir 'abcdefgh'), saisir 13/30 comme date "
            "d'expiration ou vider First Name.",
            "Cliquer sur Buy Flights.",
        ],
        "expected": "Le paiement est refuse et un message indique les champs invalides.",
        "actual": "La facture est generee et le message 'Thank you for booking' s'affiche, avec un "
                  "numero de carte vide ou non numerique. Tests ET-11 a ET-14 en echec.",
    },
    {
        "summary": "BUG-04 - Les pages protegees sont accessibles sans authentification",
        "priority": "Highest",
        "labels": ["bug", "pt", "securite"],
        "tests": ["PT-01", "PT-02"],
        "story": "WT-19",
        "steps": [
            "Ouvrir un navigateur sans cookie de session.",
            "Acceder directement a /cgi-bin/itinerary.pl.",
            "Acceder directement a /cgi-bin/reservations.pl?page=welcome.",
        ],
        "expected": "Redirection vers la page de connexion ou erreur 401/403.",
        "actual": "Les deux pages repondent en HTTP 200: l'itineraire ('No flights have been "
                  "reserved') et le formulaire de recherche sont affiches sans session. "
                  "Tests PT-01 et PT-02 en echec.",
    },
    {
        "summary": "BUG-05 - Les vols Denver-Denver sont proposes au prix de 0 $",
        "priority": "Medium",
        "labels": ["bug", "donnees"],
        "tests": ["ET-09"],
        "story": "WT-12",
        "steps": [
            "Se connecter, ouvrir Search Flights.",
            "Choisir Denver comme ville de depart et d'arrivee.",
            "Lancer la recherche.",
        ],
        "expected": "La recherche est refusee (villes identiques) ou aucun vol n'est propose.",
        "actual": "Quatre vols 'Blue Sky Air' sont proposes au prix de 0 $, ce qui permet une "
                  "reservation gratuite. Observe pendant ET-09.",
    },
]


def adf(bug):
    return {"type": "doc", "version": 1, "content": [
        heading("Etapes de reproduction"),
        {"type": "orderedList", "content": [
            {"type": "listItem", "content": [p(s)]} for s in bug["steps"]]},
        heading("Resultat attendu"),
        p(bug["expected"]),
        heading("Resultat obtenu"),
        p(bug["actual"]),
        heading("Tests automatises en echec"),
        bullets([f"{tid} - voir le Test Execution WT-66" for tid in bug["tests"]]),
    ]}


def existing(summary):
    r = requests.get(f"{BASE}/rest/api/3/search/jql", auth=AUTH, headers=H, timeout=60,
                     params={"jql": f'project={PROJECT} AND summary ~ "{summary.split(" - ")[0]}"',
                             "maxResults": 10, "fields": "summary"})
    r.raise_for_status()
    for issue in r.json()["issues"]:
        if issue["fields"]["summary"] == summary:
            return issue["key"]
    return None


def link(source, target):
    payload = {"type": {"name": "Relates"}, "inwardIssue": {"key": source},
               "outwardIssue": {"key": target}}
    requests.post(f"{BASE}/rest/api/3/issueLink", auth=AUTH, headers=H, json=payload, timeout=60)


def main():
    mapping = json.loads(MAP_FILE.read_text(encoding="utf-8"))["tests"]
    for bug in BUGS:
        key = existing(bug["summary"])
        if not key:
            body = {"fields": {
                "project": {"key": PROJECT},
                "issuetype": {"name": "Bug"},
                "summary": bug["summary"],
                "description": adf(bug),
                "priority": {"name": bug["priority"]},
                "labels": bug["labels"],
            }}
            r = requests.post(f"{BASE}/rest/api/3/issue", auth=AUTH, headers=H, json=body, timeout=60)
            if r.status_code >= 300:
                print("ERR", bug["summary"], r.status_code, r.text[:300])
                continue
            key = r.json()["key"]
            print("created", key, bug["summary"])
        else:
            print("exists ", key, bug["summary"])
        link(key, bug["story"])
        for tid in bug["tests"]:
            if tid in mapping:
                link(key, mapping[tid]["key"])
    return 0


if __name__ == "__main__":
    sys.exit(main())

