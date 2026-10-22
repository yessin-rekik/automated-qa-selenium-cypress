# Plan de test - Application Web Tours

## 1. Objet

Valider le site de reservation de vols **Mercury Web Tours** (http://127.0.0.1:1080/WebTours)
sur les plans fonctionnel, erreur, limites et permissions, puis automatiser la suite de tests
et l'integrer dans une chaine d'integration continue.

## 2. Perimetre

| Inclus | Exclu |
|---|---|
| Inscription, connexion, deconnexion | Paiement reel (aucune passerelle bancaire) |
| Recherche de vols aller simple et aller-retour | Administration du serveur Apache/Perl |
| Selection du siege et de la classe | Compatibilite multi-navigateurs (Chrome uniquement) |
| Reservation, facture, itineraire, annulation | Tests de charge et de performance |
| Controle d'acces aux pages CGI | Tests de securite avances (injection, XSS) |

## 3. Environnement de test

| Element | Valeur |
|---|---|
| Application | Web Tours 1.0 (Apache + Perl CGI) |
| Serveur | http://127.0.0.1:1080/WebTours/index.htm |
| Navigateur | Google Chrome 155 (headless pour l'automatisation) |
| Python | 3.12 - PyTest 9 / Selenium 4.51 |
| Gestion des tests | Jira Cloud + Xray (projet **WT**) |
| CI | Jenkins (voir `docs/jenkins.md`) |
| Versionnage | Git |

## 4. Strategie de test

Les tests sont organises **par module** (Authentification, Recherche, Reservation, Itineraire,
Securite) et **par dossier Xray** correspondant au type de test :

| Dossier | Type | Objectif |
|---|---|---|
| `/FT` | Fonctionnel | Verifier les parcours nominaux (happy path) |
| `/ET` | Error testing | Verifier la gestion des saisies invalides |
| `/BT` | Boundary testing | Verifier les bornes (0/1/8 passagers, longueurs max, dates limites) |
| `/PT` | Permission testing | Verifier le controle de session et l'isolation des donnees |

Chaque cas de test existe sous deux formes :

1. **Test manuel Xray** (45 tests) avec etapes, donnees et resultat attendu,
   rattache a une User Story par le lien *Test*.
2. **Test automatise PyTest/Selenium** portant le meme identifiant (`FT-01`, `ET-07`...),
   execute par Jenkins et publie dans Xray comme Test Execution.

## 5. Traçabilite User Stories -> Tests

| Epic | User Story | Tests |
|---|---|---|
| WT-1 Authentification | WT-6 Inscription | FT-00, FT-04, ET-04, ET-05, ET-06, BT-01 |
| | WT-7 Connexion | FT-01, FT-02, FT-05, ET-01, ET-02, ET-03 |
| | WT-8 Deconnexion | FT-03 |
| WT-2 Recherche | WT-9 Aller simple | FT-06, FT-08 |
| | WT-10 Aller-retour | FT-07 |
| | WT-11 Siege et classe | FT-09, FT-13 |
| | WT-12 Validation des criteres | ET-07 a ET-10, BT-03 a BT-08 |
| WT-3 Reservation | WT-13 Saisie du paiement | FT-10, FT-12 |
| | WT-14 Facture | FT-11 |
| | WT-15 Champs obligatoires | ET-11 a ET-14, BT-02 |
| WT-4 Itineraire | WT-16 Consultation | FT-14, FT-17 |
| | WT-17 Annulation simple | FT-15 |
| | WT-18 Annulation totale | FT-16 |
| WT-5 Securite | WT-19 Controle d'acces | PT-01 a PT-05 |

## 6. Criteres d'entree / de sortie

**Entree** : application demarree (`StartServer.bat`), compte de test cree,
navigateur et dependances Python installes.

**Sortie** : 100 % des tests FT en PASS, tous les echecs ET/BT/PT analyses et
documentes par un bug Jira (WT-67 a WT-71). La suite est consideree stable lorsque
les defauts sont marques `xfail` avec leur identifiant de bug.

## 7. Risques

- Donnees de vols statiques (`flightData`) : prix parfois a 0 $ (voir BUG-05).
- Validation cote client desactivee (`onsubmit=""`) : les controles doivent etre
  refaits cote serveur.
- Sessions stockees dans un cookie (`MTUserInfo`) : perte des donnees a la deconnexion.
