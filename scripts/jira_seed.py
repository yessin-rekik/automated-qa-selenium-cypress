"""Seed the Jira project WT with epics and user stories (French)."""
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


def adf_paragraph(text):
    return {"type": "paragraph", "content": [{"type": "text", "text": text}]}


def adf_bullets(items):
    return {
        "type": "bulletList",
        "content": [
            {"type": "listItem", "content": [adf_paragraph(i)]} for i in items
        ],
    }


def adf(*blocks):
    return {"type": "doc", "version": 1, "content": list(blocks)}


def create_issue(fields):
    r = requests.post(f"{BASE}/rest/api/3/issue", auth=AUTH, headers=H, json={"fields": fields}, timeout=60)
    if r.status_code >= 300:
        print("ERR", fields["summary"], r.status_code, r.text[:500])
        return None
    key = r.json()["key"]
    print("created", key, fields["issuetype"]["name"], "-", fields["summary"])
    return key


def existing_issues():
    jql = f"project={PROJECT} ORDER BY created ASC"
    r = requests.get(f"{BASE}/rest/api/3/search/jql", auth=AUTH, headers=H,
                     params={"jql": jql, "maxResults": 100, "fields": "summary,issuetype,parent"}, timeout=60)
    r.raise_for_status()
    out = {}
    for i in r.json().get("issues", []):
        out[i["fields"]["summary"]] = {"key": i["key"], "type": i["fields"]["issuetype"]["name"],
                                       "parent": (i["fields"].get("parent") or {}).get("key")}
    return out


EPICS = {
    "Authentification et compte": (
        "Gestion de l'inscription, de la connexion et de la déconnexion des clients.",
        ["Création de compte", "Connexion sécurisée", "Déconnexion"],
    ),
    "Recherche de vols": (
        "Recherche de vols aller simple et aller-retour avec critères de siège.",
        ["Critères de recherche", "Résultats de vols", "Validation des critères"],
    ),
    "Réservation et paiement": (
        "Sélection du vol, saisie des informations de paiement et facturation.",
        ["Sélection du vol", "Paiement", "Facture"],
    ),
    "Itinéraire et annulation": (
        "Consultation, modification et annulation des réservations du client.",
        ["Consultation de l'itinéraire", "Annulation"],
    ),
    "Sécurité des accès": (
        "Contrôle d'accès aux pages protégées de l'application.",
        ["Contrôle de session", "Isolation des données entre clients"],
    ),
}

STORIES = [
    ("Authentification et compte", "En tant que visiteur, je veux créer un compte avec un nom d'utilisateur et un mot de passe, afin de pouvoir réserver des vols.",
     ["Le formulaire d'inscription accepte un nom d'utilisateur alphanumérique et un mot de passe confirmé.",
      "Un compte existant affiche le message \"username is taken\".",
      "Une confirmation de mot de passe différente est refusée.",
      "Après inscription, l'utilisateur peut se connecter avec ses identifiants."]),
    ("Authentification et compte", "En tant que client enregistré, je veux me connecter avec mon nom d'utilisateur et mon mot de passe, afin d'accéder à mes réservations.",
     ["Des identifiants valides ouvrent la page d'accueil personnalisée (\"Welcome, <user>\").",
      "Le menu de navigation affiche Rechercher, Itinéraire et Déconnexion.",
      "Un mot de passe erroné affiche \"Error - Incorrect Password\".",
      "Un utilisateur inconnu est refusé avec le même message d'erreur."]),
    ("Authentification et compte", "En tant que client connecté, je veux me déconnecter, afin de protéger mes données personnelles.",
     ["Le clic sur Sign Off termine la session.",
      "La page de connexion est réaffichée.",
      "Les pages protégées ne sont plus accessibles avec les données du client."]),
    ("Recherche de vols", "En tant que client, je veux rechercher un vol aller simple en choisissant une ville de départ, une ville d'arrivée et une date, afin de trouver un vol disponible.",
     ["La liste des 10 villes est proposée pour le départ et l'arrivée.",
      "La recherche affiche la liste des vols avec compagnie, numéro, heure et prix.",
      "Chaque vol peut être sélectionné pour la réservation."]),
    ("Recherche de vols", "En tant que client, je veux rechercher un vol aller-retour avec une date de retour, afin d'organiser un voyage complet.",
     ["La case \"Roundtrip ticket\" active la date de retour.",
      "La recherche retourne un vol aller puis un vol retour.",
      "La date de retour doit être postérieure à la date de départ."]),
    ("Recherche de vols", "En tant que client, je veux choisir ma classe et ma préférence de siège, afin de personnaliser ma réservation.",
     ["Les options de siège (Aisle, Window, None) sont sélectionnables.",
      "Les classes (First, Business, Coach) sont sélectionnables.",
      "Le choix est repris sur la facture."]),
    ("Recherche de vols", "En tant que client, je veux que mes critères de recherche soient validés, afin d'éviter des recherches incohérentes.",
     ["Une date au format invalide est refusée avec un message.",
      "Une date de départ passée est refusée.",
      "Un nombre de passagers nul, négatif ou non numérique est refusé.",
      "Une ville de départ identique à la ville d'arrivée est refusée."]),
    ("Réservation et paiement", "En tant que client, je veux saisir mes informations de paiement et confirmer ma réservation, afin de finaliser l'achat du billet.",
     ["Le formulaire de paiement reprend les informations du profil.",
      "Le nombre de champs passager correspond au nombre de passagers.",
      "Le total à payer est affiché.",
      "La confirmation génère une réservation dans l'itinéraire."]),
    ("Réservation et paiement", "En tant que client, je veux recevoir une facture récapitulative après le paiement, afin de conserver une preuve d'achat.",
     ["La page Invoice affiche le récapitulatif des vols.",
      "Le montant total et les 4 derniers chiffres de la carte sont affichés.",
      "Le message \"Thank you for booking through Web Tours\" est présent."]),
    ("Réservation et paiement", "En tant que client, je veux que les champs obligatoires du paiement soient validés, afin de ne pas envoyer de données incomplètes.",
     ["Un champ nom, adresse, carte ou date vide est refusé avec un message.",
      "Un numéro de carte non numérique est refusé.",
      "Une date d'expiration au format invalide ou un mois hors 1-12 est refusé."]),
    ("Itinéraire et annulation", "En tant que client, je veux consulter la liste de mes réservations, afin de vérifier mes vols.",
     ["L'itinéraire liste chaque vol réservé avec date, heure et compagnie.",
      "Le total facturé et la carte utilisée sont affichés.",
      "Un message s'affiche lorsqu'aucune réservation n'existe."]),
    ("Itinéraire et annulation", "En tant que client, je veux annuler une réservation précise, afin de ne plus payer un vol non désiré.",
     ["La case du vol peut être cochée puis \"Cancel Reservation\" appliqué.",
      "Le vol annulé disparaît de l'itinéraire.",
      "Les autres réservations restent intactes."]),
    ("Itinéraire et annulation", "En tant que client, je veux annuler toutes mes réservations en une action, afin de repartir de zéro.",
     ["\"Cancel All Reservations\" vide l'itinéraire.",
      "Le message \"No flights have been reserved\" est affiché ensuite."]),
    ("Sécurité des accès", "En tant qu'administrateur du site, je veux que les pages de réservation et d'itinéraire exigent une session authentifiée, afin de protéger les données des clients.",
     ["L'accès direct à itinerary.pl sans session est refusé ou redirigé vers la connexion.",
      "L'accès direct à reservations.pl sans session est refusé ou redirigé.",
      "Un client ne peut pas consulter l'itinéraire d'un autre client."]),
]


def main():
    cur = existing_issues()
    epic_keys = {}
    for name, (desc, _) in EPICS.items():
        if name in cur:
            epic_keys[name] = cur[name]["key"]
            continue
        k = create_issue({
            "project": {"key": PROJECT},
            "issuetype": {"name": "Epic"},
            "summary": name,
            "description": adf(adf_paragraph(desc)),
        })
        if k:
            epic_keys[name] = k

    for epic, summary, ac in STORIES:
        if summary in cur:
            continue
        create_issue({
            "project": {"key": PROJECT},
            "issuetype": {"name": "Story"},
            "summary": summary,
            "description": adf(
                adf_paragraph("Contexte: application Web Tours (réservation de vols)."),
                adf_paragraph("Critères d'acceptation :"),
                adf_bullets(ac),
            ),
            "parent": {"key": epic_keys[epic]},
        })

    total = existing_issues()
    print(f"\n{len(total)} issues in {PROJECT}")
    for s, v in total.items():
        print(f"  {v['key']:8} {v['type']:10} {s[:90]}")


if __name__ == "__main__":
    sys.exit(main())
