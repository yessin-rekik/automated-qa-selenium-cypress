# Web Tours - Projet de test (Jira / Xray / Selenium / Jenkins)

Projet de test complet du site de reservation de vols **Mercury Web Tours** :

- **Jira Cloud** : projet `WT` avec epics et user stories ;
- **Xray** : 45 tests manuels classes en dossiers `FT`, `ET`, `BT`, `PT`,
  plan de test `WT-65` et executions ;
- **Selenium + PyTest** : 45 tests automatises (Page Object Model) ;
- **Cypress** : 6 tests equivalents pour la comparaison des deux outils
  (`docs/comparison-selenium-cypress.md`) ;
- **Jenkins** : `Jenkinsfile` + Jenkins Docker pre-configure (`deploy/jenkins/`) ;
- **Git** : depot versionne.

## Structure

```
hw_jira/
├── Jenkinsfile                  # pipeline CI
├── .env                         # URL Jira + token API + cles Xray (non versionne)
├── work.txt                     # enonce du projet
├── PRESENTATION.md              # presentation du projet + guide pas a pas
├── deploy/jenkins/              # Jenkins Docker (Dockerfile, casc.yaml, compose)
├── cypress-tests/               # suite Cypress de comparaison
├── docs/
│   ├── test-plan.md             # plan de test et tracabilite
│   ├── bugs.md                  # defauts detectes
│   ├── execution-report.md      # rapport genere depuis junit.xml
│   ├── comparison-selenium-cypress.md  # comparaison des deux outils
│   └── jenkins.md               # mise en place de la CI
├── scripts/                     # outillage Jira / Xray / rapports
│   ├── start_webtours.bat       # demarre Web Tours avec Perl dans le PATH
│   ├── check_app.py             # verifie que Web Tours repond (Jenkins)
│   ├── jira_seed.py             # epics + user stories
│   ├── jira_bugs.py             # bugs detectes
│   ├── xray_catalog.py          # catalogue des 45 tests
│   ├── xray_seed.py             # creation des tests, liens, plan
│   ├── xray_folders.py          # dossiers du Test Repository
│   ├── results_to_xray.py       # publication de l'execution
│   ├── make_report.py           # docs/execution-report.md
│   └── xray_map.json            # correspondance test <-> issue Jira
└── webtours-tests/
    ├── conftest.py              # fixtures Selenium
    ├── pytest.ini
    ├── requirements.txt
    ├── webtours/                # page object + helpers
    │   ├── app.py
    │   ├── api.py
    │   └── utils.py
    └── tests/
        ├── ft/                  # fonctionnel
        ├── et/                  # erreurs
        ├── bt/                  # limites
        └── pt/                  # permissions
```

## Demarrage rapide

```powershell
# 1. Application (ajoute C:\strawberry\perl\bin au PATH puis lance Apache)
.\scripts\start_webtours.bat  # http://127.0.0.1:1080/WebTours/index.htm

# 2. Environnement Python
python -m venv .venv
.\.venv\Scripts\python -m pip install -r webtours-tests\requirements.txt

# 3. Suite de tests
cd webtours-tests
..\.venv\Scripts\python -m pytest              # 45 tests
..\.venv\Scripts\python -m pytest -m ft        # seulement le fonctionnel
$env:HEADLESS="0"; ..\.venv\Scripts\python -m pytest   # navigateur visible

# 4. Rapports
#    reports/report.html, reports/junit.xml, reports/screenshots/

# 5. Suite Cypress (comparaison)
cd ..\cypress-tests
npm install
npx cypress run
```

> Erreur **500 Internal Server Error** sur les pages `cgi-bin` : Apache ne trouve pas
> `perl` (les scripts commencent par `#!perl`). Utiliser `scripts\start_webtours.bat`
> ou ouvrir un nouveau terminal apres l'installation de Strawberry Perl.

Options par variables d'environnement : `WEBTOURS_URL`, `WEBTOURS_CGI`,
`HEADLESS=0`, `BROWSER=edge`, `SELENIUM_REMOTE_URL` (Selenium Grid).

## Resultats

Execution de reference : **31 PASSED / 14 FAILED** (les echecs correspondent aux
5 defauts documentes dans `docs/bugs.md` et sont marques `xfail` pour garder
une suite stable).

| Element | Lien |
|---|---|
| Projet Jira | https://yessinrekik666.atlassian.net/browse/WT |
| Plan de test | https://yessinrekik666.atlassian.net/browse/WT-65 |
| Execution de reference | https://yessinrekik666.atlassian.net/browse/WT-66 |
| Derniere execution Selenium | https://yessinrekik666.atlassian.net/browse/WT-72 |
| Execution Cypress (comparaison) | https://yessinrekik666.atlassian.net/browse/WT-73 |
| Bugs | WT-67 a WT-71 |
| Rapport detaille | `docs/execution-report.md` |
| Comparaison Selenium / Cypress | `docs/comparison-selenium-cypress.md` |

## Recreer la configuration Jira/Xray

Les scripts sont idempotents (ils reutilisent les issues existantes) :

```powershell
.\.venv\Scripts\python scripts\jira_seed.py       # epics + stories
.\.venv\Scripts\python scripts\xray_seed.py       # tests + liens + plan
.\.venv\Scripts\python scripts\xray_folders.py    # dossiers FT/ET/BT/PT
.\.venv\Scripts\python scripts\jira_bugs.py       # bugs
.\.venv\Scripts\python scripts\results_to_xray.py # execution depuis junit.xml
.\.venv\Scripts\python scripts\make_report.py     # rapport markdown
```

Variables attendues dans `.env` : `URL`, `EMAIL`, `JIRA_API`, `XRAY_CLIENT_ID`,
`XRAY_CLIENT_SECRET` (optionnel : `JIRA_PROJECT`, `JIRA_PROJECT_ID`).
