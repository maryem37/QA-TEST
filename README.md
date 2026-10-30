# QA-TEST — Pipeline QA assisté par IA

Pipeline de test logiciel de bout en bout, appliqué à
[restful-booker-platform](https://github.com/mwinteringham/restful-booker-platform)
(application de réservation de chambres, composée de plusieurs services).

Un LLM génère les **cas de test** à partir d'exigences écrites à la main, puis le
**code des tests automatisés**. Les résultats sont exportés vers Jira/Xray, exécutés
en CI avec GitHub Actions et résumés dans un rapport. **Un humain valide chaque
contenu généré par l'IA** (Pull Request) avant son exécution.

> **État du projet** : phase 0 (préparation) en cours. Les phases suivantes sont
> décrites dans la [feuille de route](#feuille-de-route).

---

## Sommaire

1. [Principe](#principe)
2. [Architecture](#architecture)
3. [Prérequis](#prérequis)
4. [Démarrage rapide](#démarrage-rapide)
5. [Configuration](#configuration)
6. [Commandes Make](#commandes-make)
7. [Structure du dépôt](#structure-du-dépôt)
8. [Application sous test](#application-sous-test)
9. [Conventions](#conventions)
10. [Feuille de route](#feuille-de-route)
11. [Limites et risques](#limites-et-risques)

---

## Principe

```
requirements/REQ-xxx.md ──► LLM ──► cases/*.json ──► revue humaine (PR)
                                          │
                                          ├──► export Jira / Xray (ou FileBackend)
                                          │
                                          └──► LLM ──► tests/ (API, Playwright, Selenium)
                                                          │
                                                   GitHub Actions
                                                          │
                                       JUnit XML ──► report.md / report.html
```

Règles de conception :

- Les **exigences** sont écrites à la main, d'après le comportement attendu.
- Le LLM est utilisé de façon **reproductible** : `temperature=0`, modèle épinglé,
  cache par hash, retry avec backoff, log JSONL (tokens, coût, durée, version du prompt).
- Toute sortie du LLM est **validée par Pydantic** (boucle de réparation limitée à 3 essais).
- Le LLM **ne calcule jamais de chiffres** : les métriques du rapport sont calculées par le code.
- Aucun secret dans Git (`.env` ignoré, GitHub Secrets en CI).

## Architecture

| Domaine | Outils |
|---|---|
| Environnement | Git/GitHub, Python 3.11, uv, Docker, Docker Compose, Make, VS Code |
| IA | API LLM (Anthropic), Pydantic, `llm_client.py` |
| Application sous test | restful-booker-platform (sous-module Git) |
| Gestion de tests | Jira Cloud, Xray (avec `FileBackend` de secours) |
| Tests | pytest, requests, Playwright, Selenium, ruff |
| CI | GitHub Actions, GitHub Secrets, actions/cache, artefacts |
| Rapport | JUnit XML, `report.py`, `$GITHUB_STEP_SUMMARY`, HTML |
| Bonus | OpenTelemetry + Jaeger, LLM-as-judge |

## Prérequis

- [Git](https://git-scm.com/) (Git for Windows inclut le Credential Manager)
- [Python 3.11](https://www.python.org/) et [uv](https://docs.astral.sh/uv/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (démarré, avec au moins 8 Go de RAM conseillés)
- [Make](https://www.gnu.org/software/make/) (GnuWin32 3.81 suffit sous Windows)
- Une clé API LLM (Anthropic)
- Optionnel (phase 3) : un compte Jira Cloud avec Xray

Pas besoin d'installer Java, Maven ni Node : l'application est compilée dans Docker.

## Démarrage rapide

```powershell
# 1. Cloner, avec le sous-module de l'application
git clone --recurse-submodules https://github.com/maryem37/QA-TEST.git
cd QA-TEST

# 2. Installer les dépendances Python et les navigateurs Playwright
uv sync
uv run playwright install chromium firefox

# 3. Configurer l'environnement
copy .env.example .env      # puis renseigner ANTHROPIC_API_KEY, etc.

# 4. Démarrer l'application sous test
make up
```

Si le sous-module est vide après un clone simple :
`git submodule update --init --recursive`.

L'application est ensuite disponible sur <http://localhost:8080>
(identifiants : `admin` / `password`).

Pour limiter la consommation mémoire pendant le premier build :

```powershell
$env:COMPOSE_PARALLEL_LIMIT = 2
```

## Configuration

Copier `.env.example` vers `.env`. Ce fichier n'est jamais commité.

| Variable | Rôle |
|---|---|
| `ANTHROPIC_API_KEY` | Clé de l'API LLM |
| `LLM_MODEL` | Modèle utilisé (à épingler) |
| `PROMPT_VERSION` | Version des prompts (`v1`) |
| `BASE_URL` | URL de l'application sous test (`http://localhost:8080`) |
| `BACKEND` | `file` (par défaut) ou `xray` |
| `JIRA_URL`, `JIRA_USER`, `JIRA_API_TOKEN`, `JIRA_PROJECT_KEY` | Accès Jira Cloud |
| `XRAY_CLIENT_ID`, `XRAY_CLIENT_SECRET` | Accès API Xray |

En CI, les secrets (clé LLM, identifiants Xray) sont fournis via **GitHub Secrets**.

## Commandes Make

| Commande | Action |
|---|---|
| `make up` | Construit et démarre l'application, puis attend qu'elle réponde |
| `make down` | Arrête l'application et supprime les volumes |
| `make lint` | Vérifie le code avec ruff |
| `make cases` | Génère et contrôle les cas de test (phase 2) |
| `make sync` | Exporte les cas vers le backend choisi (`BACKEND=file` ou `xray`) |
| `make tests` | Génère et contrôle les tests automatisés (phase 4) |
| `make run` | Exécute les tests (API, Playwright, Selenium) et produit `reports/junit.xml` |
| `make push` | Envoie les résultats vers le backend |
| `make report` | Génère `report.md` et `report.html` |
| `make all` | Enchaîne tout : `up cases sync tests run push report` |

> Certaines commandes dépendent de modules des phases suivantes, pas encore écrits.

## Structure du dépôt

```
QA-TEST/
├── app/restful-booker-platform/   # application sous test (sous-module Git)
├── backends/                      # export vers Jira/Xray ou fichiers JSON
├── cases/                         # cas de test générés (revus par PR)
├── docker/                        # Dockerfile des services Java, settings Maven
├── pipeline/                      # LLM client, génération, contrôles, rapport
├── prompts/v1/                    # prompts versionnés
├── reports/                       # JUnit, rapports (ignoré par Git)
├── requirements/                  # exigences REQ-xxx.md
├── schemas/                       # modèles Pydantic
├── scripts/                       # utilitaires (attente de l'application...)
├── spec/                          # notes d'API fournies au LLM
├── tests/
│   ├── gold/                      # tests de référence écrits à la main
│   ├── api/                       # tests API générés
│   ├── ui_playwright/             # tests UI Playwright générés
│   └── ui_selenium/               # tests smoke Selenium générés
├── .github/workflows/             # CI GitHub Actions
├── docker-compose.yml
├── Makefile
└── pyproject.toml
```

## Application sous test

restful-booker-platform est une application de réservation de chambres composée de
sept services. Le dépôt officiel ne fournit pas de Dockerfile qui compile le code
des services Java (il attend des `.jar` déjà construits). Ce projet ajoute donc :

- `docker/java-service.Dockerfile` : build multi-étapes (Maven JDK 26, puis JRE 26),
  paramétré par le nom du module ;
- `docker/maven-settings.xml` : dépôt Maven *milestone* de Spring (le projet utilise
  Spring Boot `4.1.0-M4`) ;
- `docker-compose.yml` : les sept services, avec le site exposé sur le port 8080.

| Service | Port hôte |
|---|---|
| `rbp-assets` (site web) | 8080 |
| `rbp-booking` | 3000 |
| `rbp-room` | 3001 |
| `rbp-branding` | 3002 |
| `rbp-auth` | 3004 |
| `rbp-report` | 3005 |
| `rbp-message` | 3006 |

La version de l'application est **épinglée** par le commit du sous-module.
Pour la mettre à jour, modifier explicitement le sous-module puis commiter.

## Conventions

- Chaque test porte un marqueur de traçabilité : `@pytest.mark.tc("TC-...")`.
- `BASE_URL` provient de l'environnement, jamais codé en dur.
- Attentes explicites, **pas de `sleep`**, données de test nettoyées.
- Selenium : 4 à 6 scénarios smoke seulement.
- Les cas et tests générés par l'IA passent par une **Pull Request** avec revue humaine.
- Corriger les **prompts**, pas le code généré à la main, puis régénérer.

## Feuille de route

| Phase | Contenu | Livrable |
|---|---|---|
| 0 | Préparation : dépôt, uv, Docker, Makefile, CI de lint, Jira/Xray, clé LLM | `make up` démarre l'application |
| 1 | 10 à 12 exigences `REQ-xxx.md`, `spec/api_notes.md` | Exigences commitées |
| 2 | Génération de cas de test par IA, contrôle, revue par PR | 30 à 40 cas valides |
| 3 | Export Jira/Xray idempotent, `mapping.json` | Tests visibles dans Xray |
| 4 | Génération des tests API, Playwright, Selenium | Suites exécutables |
| 5 | CI GitHub Actions complète, exécution nocturne | Run vert de bout en bout |
| 6 | Rapport de synthèse (`report.md`, `report.html`) | Rapport généré par la CI |
| 7 | Évaluation : métriques, injection de bug, reproductibilité | Preuves chiffrées |
| 8 | Bonus : OpenTelemetry + Jaeger, LLM-as-judge | — |
| 9 | Livraison et soutenance | README, schémas, captures |

**Avancement de la phase 0** : structure du dépôt, dépendances uv, Makefile, CI de lint
et sous-module de l'application en place. Reste : Docker Compose de l'application
(vérification), Jira Cloud + Xray, clé LLM et secrets GitHub.

Ordre de priorité si le temps manque : exigences → cas → tests API → CI → rapport
(avec `FileBackend`), puis Xray réel, Playwright et reproductibilité, puis le bonus.

## Limites et risques

- **Hallucinations** : le LLM peut produire des cas ou des tests faux ; d'où la validation
  Pydantic, les contrôles automatiques et la revue humaine.
- **Coût et quotas** de l'API LLM : cache par hash et suivi dans les logs JSONL.
- **Données envoyées au LLM** : seules les exigences et les notes d'API sont transmises ;
  aucun secret ni donnée personnelle.
- **Instabilité des tests UI** : Playwright et Selenium sont comparés (durée, instabilité,
  effort de correction).
- **Dépendance à Xray** : essai limité dans le temps, d'où le `FileBackend` de secours.
- **Application en version milestone** : Spring Boot `4.1.0-M4` peut changer ou disparaître
  des dépôts ; le commit du sous-module est épinglé pour cette raison.

## Perspectives

`ZephyrBackend`, Jenkins (`Jenkinsfile.example`), BDD, OpenTelemetry.

## Licence

À définir. L'application restful-booker-platform reste soumise à sa propre licence.
