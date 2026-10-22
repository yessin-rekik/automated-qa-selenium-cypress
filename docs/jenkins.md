# Integration continue avec Jenkins

Le pipeline est decrit dans le `Jenkinsfile` a la racine du depot :

| Stage | Action |
|---|---|
| Checkout | recupere le depot Git |
| Install dependencies | cree `.venv` et installe `webtours-tests/requirements.txt` |
| Check application is up | verifie que Web Tours repond en HTTP 200 (3 tentatives) |
| Run Selenium test suite | execute `pytest` (rapport JUnit + HTML) |
| Publish results to Xray | cree un Test Execution Xray depuis `junit.xml` |
| Generate execution report | regenere `docs/execution-report.md` |

Les artefacts publies : `junit.xml`, `report.html`, captures d'ecran des echecs.

## Option A - Jenkins dans Docker (recommandee, deja configuree)

Le dossier `deploy/jenkins/` contient une image Jenkins prete a l'emploi :

| Fichier | Role |
|---|---|
| `Dockerfile` | Jenkins LTS + Python 3 + Chromium + chromedriver + plugins |
| `casc.yaml` | *Configuration as Code* : compte `admin`, identifiants Xray, job `webtours-tests` |
| `docker-compose.yml` | lance le conteneur, monte le depot dans `/workspace` |

Le job clone le depot local (`file:///workspace`, branche `main`) : **seuls les
changements commites sont vus par Jenkins**. Les tests attaquent Web Tours sur
la machine hote via `http://host.docker.internal:1080`.

```powershell
# 1. Web Tours doit tourner sur l'hote
scripts\start_webtours.bat

# 2. Lancer Jenkins (les cles Xray sont lues depuis l'environnement)
cd deploy\jenkins
$env:XRAY_CLIENT_ID = "..." ; $env:XRAY_CLIENT_SECRET = "..."
docker compose up -d --build

# 3. Ouvrir http://localhost:8080  (admin / admin) > webtours-tests > Build Now
```

Le pipeline detecte l'agent Linux (`isUnix()`) et utilise `sh` + `.venv-ci` ;
sur un agent Windows il utilise `bat` + `.venv`.

## Option B - Jenkins installe sur Windows

Prerequis sur le noeud : Python 3.10+, Google Chrome, Git, Web Tours demarre.

1. Installer Jenkins (service Windows).
2. Creer deux identifiants *Secret text* : `xray-client-id` et `xray-client-secret`.
3. Creer un job **Pipeline** : *Pipeline script from SCM*, Git, branche `main`,
   *Script Path* `Jenkinsfile`.
4. `Build Now`, puis *Console Output*, *Test Result* et le rapport HTML.

## Resultat attendu

- Build **UNSTABLE** lorsque des tests echouent (les 14 defauts connus sont
  marques `xfail` et documentes par WT-67 a WT-71) ;
- un Test Execution Xray supplementaire a chaque build, rattache au plan **WT-65**.
