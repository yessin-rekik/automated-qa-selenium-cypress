# Comparaison Selenium / Cypress - Web Tours

L'enonce demande des tests automatiques avec **Selenium et Cypress, avec comparaison**.
La suite principale (45 tests) est ecrite avec **Selenium + PyTest** (`webtours-tests/`).
Une suite **Cypress** (`cypress-tests/`) reprend 6 cas representatifs, avec les memes
identifiants, pour comparer les deux outils sur la meme application.

## 1. Cas compares

| ID | Cas | Selenium (PyTest) | Cypress |
|---|---|---|---|
| FT-00 | Application disponible (index + page CGI) | PASS | PASS |
| FT-01 | Connexion valide | PASS | PASS |
| FT-06 | Recherche aller simple (4 vols) | PASS | PASS |
| FT-10 | Reservation complete + facture | PASS | PASS |
| ET-01 | Mot de passe incorrect | PASS | PASS |
| PT-01 | Page protegee sans session (BUG-04) | XFAIL (defaut confirme) | PASS (constate le defaut) |

Les deux outils donnent **les memes verdicts** et detectent le meme defaut BUG-04 (WT-70).

## 2. Mesures (meme machine, 6 tests, Web Tours local)

| Mesure | Selenium + PyTest | Cypress 13 (Electron) |
|---|---|---|
| Duree totale (lancement compris) | ~16 s | ~16 s |
| Duree des tests seuls | ~3,9 s d'actions + ~2 s de demarrage Chrome par test | ~8 s (navigateur deja lance) |
| Test le plus long (FT-10) | 1,5 - 1,8 s | ~3 s |
| Lignes de code (outillage + tests) | 385 (page object + fixtures) pour 45 tests | 145 pour 6 tests |
| Stabilite sur 3 executions | 3/3 identiques | 3/3 identiques |

Sur cette application, aucun outil n'est nettement plus rapide : Selenium relance un
navigateur pour chaque test (isolation totale), Cypress paie un cout de demarrage
unique plus eleve puis enchaine les tests.

## 3. Comparaison qualitative

| Critere | Selenium + PyTest | Cypress |
|---|---|---|
| Langage | Python (au choix : Java, C#, JS...) | JavaScript / TypeScript uniquement |
| Architecture | Pilote le navigateur de l'exterieur (WebDriver) | S'execute dans le navigateur |
| **Frames** (Web Tours = framesets imbriques) | Natif : `driver.switch_to.frame("body")` | Pas d'API : passage par `contentDocument` (commande `cy.frame` ecrite a la main) |
| Attentes | Explicites (`WebDriverWait`) a ecrire soi-meme | Automatiques (retry des assertions) |
| Navigateurs | Chrome, Edge, Firefox, Safari, Selenium Grid | Chrome, Edge, Firefox, Electron (pas de Safari) |
| Plusieurs onglets / fenetres | Supporte | Non supporte (genant pour l'inscription qui ouvre une fenetre) |
| Appels HTTP directs | Via `requests` | Integre : `cy.request` |
| Tests attendus en echec | `xfail` natif (le defaut est documente sans casser la suite) | Pas d'equivalent : on teste le comportement actuel |
| Debogage | Captures d'ecran (ajoutees dans `conftest.py`) | Captures automatiques, mode interactif `cypress open` avec "time travel" |
| Rapports | JUnit + HTML (`pytest-html`) | JUnit (reporter integre) |
| Integration Jenkins / Xray | JUnit importe dans Xray par `results_to_xray.py` | Meme format JUnit, importable de la meme facon |
| Installation | `pip install` + navigateur | `npm install` (~500 Mo avec le binaire Cypress) |

## 4. Conclusion

- **Selenium** est le meilleur choix pour **Web Tours** : application ancienne a base de
  framesets et de fenetres multiples, que Selenium gere nativement ; il permet aussi le
  `xfail` pour documenter les defauts et s'integre simplement avec Python (scripts Jira/Xray).
- **Cypress** est plus agreable a ecrire (attentes automatiques, `cy.request`, debogage
  visuel) et serait preferable pour une application web moderne (SPA, une seule fenetre,
  sans frames).
- Les deux outils produisent les memes resultats sur les cas compares, ce qui confirme
  la fiabilite des verdicts de la suite principale.

## 5. Reproduire

```powershell
# Selenium : les 6 memes cas
cd webtours-tests
..\.venv\Scripts\python -m pytest -k "ft_00 or ft_01 or ft_06 or ft_10 or et_01 or pt_01"

# Cypress
cd ..\cypress-tests
npm install
npx cypress run          # ou : npx cypress open (mode interactif)
```
