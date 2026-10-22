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

## Option A - Jenkins sur la machine Windows (recommandee)

Prerequis sur le noeud Jenkins : Python 3.10+, Google Chrome, Git, l'application
Web Tours demarree (`WebTours\StartServer.bat`).

1. Installer Jenkins (service Windows) puis creer un noeud/agent avec le label
   `windows` (le controleur peut aussi etre le noeud).
2. Creer un identifiant *Secret text* `xray-client-id` et un autre
   `xray-client-secret` (Manage Jenkins > Credentials).
3. Creer un job **Pipeline** :
   - *Definition* : Pipeline script from SCM
   - *SCM* : Git, URL du depot, branche `main`
   - *Script Path* : `Jenkinsfile`
4. Lancer un build : `Build Now`, puis consulter *Console Output*,
   la page *Test Result* et le lien HTML du rapport.

Declenchement automatique possible avec un *GitHub hook* ou un *Poll SCM`
(`H/5 * * * *`).

## Option B - Jenkins et Selenium dans Docker

Utile si Jenkins n'est pas installe sur Windows : les tests tournent dans un
conteneur Selenium Grid et attaquent Web Tours via `host.docker.internal`.

```yaml
# docker-compose.yml
services:
  jenkins:
    image: jenkins/jenkins:lts
    ports: ["8080:8080", "50000:50000"]
    volumes:
      - jenkins_home:/var/jenkins_home
      - ./:/workspace
    environment:
      WEBTOURS_URL: http://host.docker.internal:1080/WebTours/index.htm
      WEBTOURS_CGI: http://host.docker.internal:1080/cgi-bin
      SELENIUM_REMOTE_URL: http://selenium:4444/wd/hub
  selenium:
    image: selenium/standalone-chrome:latest
    shm_size: 2gb
volumes:
  jenkins_home:
```

Dans ce cas, le `Jenkinsfile` doit etre adapte pour un agent Linux
(`sh` au lieu de `bat`, image avec Python) et le job doit s'executer sur
l'agent Docker ; la variable `SELENIUM_REMOTE_URL` est deja prise en charge
par `conftest.py`.

## Resultat attendu

- Build **UNSTABLE** lorsque des tests echouent (les 14 defauts connus sont
  marques `xfail` et documentes par WT-67 a WT-71) ;
- un Test Execution Xray supplementaire a chaque build, rattache au plan **WT-65**.
