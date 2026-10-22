# Defauts detectes - Web Tours

Execution de reference : **WT-66** (31 PASSED / 14 FAILED) sur le plan **WT-65**.

| Bug Jira | Severite | Titre | Tests |
|---|---|---|---|
| WT-67 | High | Les criteres de recherche de vol ne sont pas valides | ET-07, ET-08, ET-09, ET-10, BT-08 |
| WT-68 | High | Le nombre de passagers n'est pas valide | BT-04, BT-05, BT-07 |
| WT-69 | Highest | Les donnees de paiement ne sont pas validees | ET-11, ET-12, ET-13, ET-14 |
| WT-70 | Highest | Les pages protegees sont accessibles sans authentification | PT-01, PT-02 |
| WT-71 | Medium | Les vols Denver-Denver sont proposes au prix de 0 $ | ET-09 |

## BUG-01 (WT-67) - Criteres de recherche non valides

**Etapes** : connexion > Search Flights > saisir `31/45/2026`, une date passee,
deux villes identiques, ou un retour anterieur au depart > rechercher.

**Attendu** : refus avec message explicite.

**Obtenu** : la recherche s'execute. Pour une date invalide, la page *Find Flight* est
affichee sans aucun vol ni message. Pour Denver-Denver, quatre vols a 0 $ sont proposes.

**Cause probable** : `chooseFlightValidate.js` contient les regles (`isDate`,
`isPosNumber`, ville differente) mais le formulaire est genere avec `onsubmit=""`
dans `reservations.pl` (option `MSO_JSFormSubmit2` desactivee) et le serveur ne
refait aucune verification.

## BUG-02 (WT-68) - Nombre de passagers non valide

**Etapes** : saisir `0`, `abc` ou `999` dans *No. of Passengers* puis rechercher.

**Attendu** : seuls les entiers 1-8 sont acceptes.

**Obtenu** : toutes les valeurs passent. Avec 999, le formulaire de paiement genere
999 champs passager (`pass1` ... `pass999`).

**Cause probable** : `param('numPassengers')` est utilise directement dans
`reservations.pl` sans controle de type ni de plage.

## BUG-03 (WT-69) - Paiement non valide

**Etapes** : reserver un vol > laisser *Credit Card* vide (ou `abcdefgh`),
saisir `13/30` en expiration, ou vider *First Name* > Buy Flights.

**Attendu** : paiement refuse.

**Obtenu** : facture generee avec le message *Thank you for booking through Web Tours*
et un numero de carte vide ou non numerique (`Total Charged to Credit Card # $386`).

**Cause probable** : `purchaseValidate.js` n'est pas attache au formulaire
(`onSubmit="void(0);"`) et aucune validation serveur n'existe avant l'ecriture
de la reservation dans `MTData/users`.

## BUG-04 (WT-70) - Pages protegees accessibles sans session

**Etapes** : sans cookie, ouvrir `/cgi-bin/itinerary.pl` puis
`/cgi-bin/reservations.pl?page=welcome`.

**Attendu** : redirection vers la page de connexion (302) ou 401/403.

**Obtenu** : HTTP 200, l'itineraire vide et le formulaire de recherche sont servis.
`login.pl?intro=true` affiche egalement *Welcome, ,* (nom vide).

**Cause probable** : les scripts CGI ne verifient jamais la presence du cookie
`MTUserInfo`; l'authentification n'est controlee que par l'interface.

## BUG-05 (WT-71) - Vols Denver-Denver a 0 $

**Etapes** : rechercher Denver -> Denver.

**Attendu** : recherche refusee (meme ville) ou aucun vol.

**Obtenu** : 4 vols *Blue Sky Air* a 0 $, reservation gratuite possible.

**Cause probable** : donnees de `flightData` incompletes (distance 0 -> prix 0)
et absence de controle sur les villes identiques.
