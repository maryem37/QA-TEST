# QA-TEST : pipeline QA assisté par IA

[![ci](https://github.com/maryem37/QA-TEST/actions/workflows/ci.yml/badge.svg)](https://github.com/maryem37/QA-TEST/actions/workflows/ci.yml)

Pipeline de test logiciel de bout en bout, appliqué à
[restful-booker-platform](https://github.com/mwinteringham/restful-booker-platform)
(application de réservation de chambres composée de plusieurs services).

Un LLM génère les **cas de test** à partir d'exigences écrites à la main, puis le
**code des tests automatisés** (API et UI Playwright). Les cas sont exportés vers
Jira/Xray, les tests sont exécutés en CI avec GitHub Actions, et un rapport de synthèse
est produit. **Un humain relit les contenus générés** (cas, tests, tickets) et trace
ses corrections dans `spec/human_review.md`.

> **État du projet** : les phases 0 à 7 sont réalisées (exigences, cas, export Jira/Xray,
> tests API et Playwright, CI, rapport, évaluation). Selenium et les bonus
> (OpenTelemetry, LLM-as-judge) ne sont **pas** réalisés. Voir la
> [feuille de route](#feuille-de-route) et les [limites](#limites-et-risques).

---

## Sommaire

1. [Principe](#principe)
2. [Résultats](#résultats)
3. [Outils](#outils)
4. [Prérequis](#prérequis)
5. [Démarrage rapide](#démarrage-rapide)
6. [Configuration](#configuration)
7. [Commandes](#commandes)
8. [Intégration continue](#intégration-continue)
9. [Jira et Xray](#jira-et-xray)
10. [Structure du dépôt](#structure-du-dépôt)
11. [Application sous test](#application-sous-test)
12. [Défauts détectés](#défauts-détectés)
13. [Conventions et revue humaine](#conventions-et-revue-humaine)
14. [Feuille de route](#feuille-de-route)
15. [Exigences non couvertes](#exigences-non-couvertes-par-un-test-automatisé)
16. [Limites et risques](#limites-et-risques)
17. [Perspectives](#perspectives)

---

## Principe

```
requirements/REQ-xxx.md ──► LLM ──► cases/*.json ──► revue humaine (PR)
                                          │
                                          ├──► export Jira / Xray (ou FileBackend)
                                          │
                                          └──► LLM ──► tests/api, tests/ui_playwright
                                                          │
                                                   GitHub Actions
                                                          │
                              JUnit XML (API + UI) ──► report.md ──► résumé du job
                                                          └──► résultats dans Xray
```

Règles de conception :

- Les **exigences** sont écrites à la main, d'après le comportement **attendu**, pas
  d'après ce que fait l'application.
- Le LLM est utilisé de façon **reproductible** : `temperature=0`, modèle épinglé
  (`LLM_MODEL`), cache par hash, retry avec backoff, journal JSONL
  (`reports/llm_log.jsonl` : tokens, durée, version du prompt).
- Toute sortie du LLM est **validée** : Pydantic pour les cas, `ast.parse` et
  `check_tests.py` pour le code, boucle de réparation limitée à 3 essais.
- Le LLM **ne calcule jamais de chiffres** : les métriques du rapport sont calculées par le code.
- Un test vérifie le comportement **attendu** par l'exigence, jamais un comportement
  défectueux observé : un défaut connu est marqué `xfail` (avec `xfail_strict`).
- Aucun secret dans Git (`.env` ignoré, GitHub Secrets en CI).

## Résultats

Dernier run de référence sur `main` (CI verte, 5 jobs) :

| Indicateur | Valeur |
|---|---|
| Exigences | 12 (`requirements/`) |
| Cas de test générés et relus | 34 (API : 15, UI : 19) |
| Cas avec test automatisé | 19 / 34 (API : 15 sur 15, UI : 4 sur 19) |
| Tests exécutés | 34 (tests gold inclus) |
| Réussis / en défaut connu / échoués | 27 / 7 / 0 |
| Défauts réels documentés | 2 (DEF-001, DEF-002) |
| Jira/Xray | 34 tests et 12 Stories, sans doublon après deux exports |
| Exécution Xray | 19 tests rattachés à un cas : 15 PASSED, 4 FAILED (défaut connu DEF-002) |

Les chiffres du rapport sont recalculés à chaque run (`reports/report.md`, résumé du job).

## Outils

| Domaine | Outils | État |
|---|---|---|
| Environnement | Git/GitHub, Python 3.11, uv, Docker, Docker Compose, Make, VS Code | en place |
| IA | API Groq (modèle `openai/gpt-oss-120b`), Pydantic, `llm_client.py` | en place |
| Application sous test | restful-booker-platform (sous-module Git) | en place |
| Gestion de tests | Jira Cloud, Xray Cloud (API REST et GraphQL), `FileBackend` de secours | en place |
| Tests | pytest, requests, Playwright, ruff | en place |
| CI | GitHub Actions, GitHub Secrets, artefacts | en place |
| Rapport | JUnit XML, `report.py`, `$GITHUB_STEP_SUMMARY` | en place (Markdown) |
| Tests Selenium | Selenium | non réalisé |
| Bonus | OpenTelemetry + Jaeger, LLM-as-judge | non réalisés |

## Prérequis

- [Git](https://git-scm.com/) (Git for Windows inclut le Credential Manager)
- [Python 3.11](https://www.python.org/) et [uv](https://docs.astral.sh/uv/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) démarré, avec
  au moins 8 Go de RAM conseillés
- [Make](https://www.gnu.org/software/make/) (GnuWin32 3.81 suffit sous Windows)
- Une clé API Groq (`GROQ_API_KEY`). Le plan gratuit est limité (environ 200 000 tokens par jour).
- Optionnel : un compte Jira Cloud avec Xray, pour `BACKEND=xray`

Pas besoin d'installer Java, Maven ni Node : l'application est compilée dans Docker.

## Démarrage rapide

```powershell
# 1. Cloner, avec le sous-module de l'application
git clone --recurse-submodules https://github.com/maryem37/QA-TEST.git
cd QA-TEST

# 2. Installer les dépendances Python et le navigateur Playwright
uv sync
uv run playwright install chromium

# 3. Configurer l'environnement
copy .env.example .env      # puis renseigner GROQ_API_KEY et LLM_MODEL

# 4. Démarrer l'application sous test (1 à 3 minutes la première fois)
make up
```

Si le sous-module est vide après un clone simple :
`git submodule update --init --recursive`.

L'application est ensuite disponible sur <http://localhost:8080>
(identifiants : `admin` / `password`).

Pour limiter la mémoire pendant le premier build :

```powershell
$env:COMPOSE_PARALLEL_LIMIT = 2
```

Arrêt en fin de session : `make down`.

## Configuration

Copier `.env.example` vers `.env`. Ce fichier n'est **jamais** commité.

| Variable | Rôle |
|---|---|
| `GROQ_API_KEY` | Clé de l'API Groq |
| `LLM_MODEL` | Modèle utilisé (`openai/gpt-oss-120b`) |
| `BASE_URL` | URL de l'application sous test (`http://localhost:8080`) |
| `BACKEND` | `file` (par défaut) ou `xray` |
| `JIRA_BASE_URL` | Adresse du site Jira Cloud (`https://votresite.atlassian.net`) |
| `JIRA_EMAIL`, `JIRA_API_TOKEN` | Compte et jeton API Jira |
| `JIRA_PROJECT_KEY` | Clé du projet Jira |
| `XRAY_CLIENT_ID`, `XRAY_CLIENT_SECRET` | Clé API Xray Cloud |

Les variables `JIRA_*` et `XRAY_*` ne servent que pour `BACKEND=xray`.
En CI, seule `GROQ_API_KEY` est fournie (GitHub Secrets) : la CI n'expose aucun secret Jira.

## Commandes

### Make

| Commande | Action |
|---|---|
| `make up` | Construit et démarre l'application, puis attend qu'elle réponde |
| `make down` | Arrête l'application et supprime les volumes |
| `make lint` | Vérifie le code avec ruff |
| `make cases` | Génère les cas de test depuis `requirements/` et les contrôle |
| `make sync BACKEND=file` | Exporte les cas dans `reports/xray_mock/` (aucun compte requis) |
| `make sync BACKEND=xray` | Crée ou met à jour les Stories et les tests dans Jira/Xray |
| `make run` | Exécute les tests API et gold |

### Génération et contrôle des tests

```powershell
# Tests API ou UI, un cas à la fois (le quota Groq est limité)
uv run python -m pipeline.gen_tests REQ-004 --layer=API
uv run python -m pipeline.gen_tests REQ-003 --layer=UI

uv run ruff check --fix tests/api tests/ui_playwright
uv run python -m pipeline.check_tests
```

Par défaut, un test déjà généré est ignoré. `--force` régénère **tous** les cas du
filtre : pour corriger un seul cas, supprimer son fichier puis relancer sans `--force`,
et relire `git diff` avant de commiter.

### Exécution et résultats

PowerShell ne développe pas les jokers (`*`), d'où l'étape intermédiaire pour l'UI.

```powershell
uv run pytest tests/gold tests/api --ignore-glob="tests/gold/test_ui_*" --junitxml=reports/junit.xml -q

$ui = (Get-ChildItem tests\gold\test_ui_pw_*.py).FullName
uv run pytest $ui tests/ui_playwright --junitxml=reports/junit-ui.xml -q

uv run python -m pipeline.merge_junit          # fusionne les deux JUnit
uv run python -m pipeline.report --no-llm      # rapport (sans commentaire IA)
uv run python -m pipeline.push_results --backend file    # ou xray
```

`push_results` refuse d'importer un lot contenant des échecs (site arrêté ?) sans `--force`.

### Nettoyage des données de test

Les tests créent des chambres éphémères et les suppriment. Après une session
interrompue, restaurer l'état initial (chambres 1, 2 et 3) :

```powershell
uv run python scratch/cleanup_rooms.py     # script local, non versionné
docker compose restart rbp-room            # la base est en mémoire (H2)
```

## Intégration continue

Fichier : `.github/workflows/ci.yml`, déclenché sur `push`, `pull_request` et `workflow_dispatch`.

| Job | Rôle |
|---|---|
| `lint` | ruff, `check_cases`, `check_tests` |
| `test-api` | Démarre l'application (3 essais), exécute les tests API et gold, publie `api-results` |
| `test-ui` | Démarre l'application, exécute les tests Playwright avec traces, publie `ui-results` |
| `export` | Exporte les cas en mode fichier **deux fois** : aucun doublon, empreintes identiques |
| `report` | Fusionne les JUnit, génère `report.md` et la matrice de traçabilité, publie le résumé du job |

Choix de conception :

- `report` échoue si les résultats API manquent (pas de rapport partiel qui paraîtrait valide).
- `docker compose up` est retenté 3 fois : un téléchargement d'image interrompu ne rend
  pas toute la CI rouge.
- `concurrency` annule les runs obsolètes d'une même branche (un run « Cancelled » n'est pas un échec).
- Permissions minimales (`contents: read`).

## Jira et Xray

Deux backends implémentent la même interface (`backends/base.py`) :

- `file` : écrit des JSON dans `reports/xray_mock/` et `mapping.json`.
- `xray` : Jira Cloud (API REST) pour les Stories et les liens, Xray Cloud (GraphQL)
  pour les tests et leurs étapes, API REST d'import pour les résultats.

Correspondance : chaque exigence devient une **Story** `REQ-xxx`, chaque cas un **Test**
Xray (type Manual, avec étapes) lié à sa Story (« is tested by »). Les résultats sont
importés dans une Test Execution.

**Idempotence** : un test est retrouvé par son identifiant externe (label = ID du cas,
recherche JQL) avant toute création. Le mapping cas ↔ clé Jira est sauvegardé dans
`mapping.xray.json`. Preuve : deux exports consécutifs, puis un export après
suppression du fichier de correspondance, donnent `0 créés, 34 mis à jour`, sans doublon dans Jira.

| Fichier | Contenu |
|---|---|
| `mapping.json` | correspondance cas ↔ identifiant du mode fichier |
| `mapping.xray.json` | correspondance cas et exigences ↔ clés Jira (`QA-n`) |

## Structure du dépôt

```
QA-TEST/
├── app/restful-booker-platform/   # application sous test (sous-module Git)
├── backends/                      # base.py, file_backend.py, xray_backend.py
├── cases/                         # cas de test générés puis relus (REQ-xxx.json)
├── docker/                        # Dockerfile des services Java, settings Maven
├── docs/                          # métriques et limites
├── pipeline/                      # LLM client, génération, contrôles, export, rapport
├── prompts/v1/                    # prompts versionnés
├── reports/                       # JUnit, rapports, journal LLM (ignoré par Git)
├── requirements/                  # exigences REQ-xxx.md
├── schemas/                       # modèles Pydantic
├── scripts/                       # attente de l'application, comparaison d'exécutions
├── spec/                          # notes API et UI, défauts, revue humaine
├── tests/
│   ├── gold/                      # tests de référence écrits à la main
│   ├── api/                       # tests API générés
│   └── ui_playwright/             # tests UI générés
├── .github/workflows/ci.yml
├── docker-compose.yml
├── Makefile
└── pyproject.toml
```

Fichiers de `spec/` :

| Fichier | Rôle |
|---|---|
| `api_notes.md` | endpoints observés, fournis au LLM (comportement attendu et observé) |
| `ui_notes.md` | sélecteurs et messages **observés** dans l'interface, fournis au LLM |
| `defects.md` | défauts documentés (DEF-xxx) |
| `human_review.md` | corrections humaines des contenus générés |

## Application sous test

restful-booker-platform est composée de sept services. Le dépôt officiel ne fournit pas
de Dockerfile qui compile les services Java (il attend des `.jar` déjà construits).
Ce projet ajoute donc :

- `docker/java-service.Dockerfile` : build multi-étapes (Maven JDK 26, puis JRE 26),
  paramétré par le nom du module ;
- `docker/maven-settings.xml` : dépôt Maven *milestone* de Spring (le projet utilise
  Spring Boot `4.1.0-M4`) ;
- `docker-compose.yml` : les sept services, avec le site exposé sur le port 8080.

| Service | Port hôte |
|---|---|
| `rbp-assets` (site web et passerelle) | 8080 |
| `rbp-booking` | 3000 |
| `rbp-room` | 3001 |
| `rbp-branding` | 3002 |
| `rbp-auth` | 3004 |
| `rbp-report` | 3005 |
| `rbp-message` | 3006 |

Les tests passent **uniquement** par `BASE_URL` (port 8080), jamais par les ports des services.
La version de l'application est épinglée par le commit du sous-module.

## Défauts détectés

| ID | Description | Tests | Statut |
|---|---|---|---|
| DEF-001 | `POST /api/auth/login` avec un JSON invalide renvoie 500 au lieu de 400 | `test_login_invalid_json_returns_400` | ouvert |
| DEF-002 | `GET /api/message` répond 200 sans jeton ou avec un jeton invalide (attendu : 401 ou 403) | TC-010-02, TC-010-03, TC-012-02, TC-012-03 et tests gold associés | ouvert |
| DEF-003 | Suppression d'une chambre en erreur 500 via la passerelle | — | **retiré** (faux positif, voir ci-dessous) |

DEF-002 est établi par rapport à l'exigence REQ-012 ; il peut correspondre à un choix de
conception des auteurs de l'application.

DEF-003 a été déclaré trop tôt, à partir d'appels de test directs. Après vérification du
parcours réel dans l'interface (suppression en 202, ligne disparue), il a été retiré.
Les défauts ouverts sont marqués `xfail` (avec `xfail_strict`) : la CI distingue un défaut
connu, une régression et un défaut corrigé.

## Conventions et revue humaine

- Chaque test porte un marqueur de traçabilité : `@pytest.mark.tc("TC-...")`.
- `BASE_URL` provient de l'environnement, jamais codé en dur.
- Attentes explicites, **pas de `sleep`** ni de `wait_for_timeout` ; pour une action UI,
  attendre la réponse réseau (`expect_response`) puis vérifier l'effet par l'API.
- Données de test uniques (uuid) et supprimées dans un `finally`.
- Aucun libellé, message ou sélecteur inventé : seuls ceux de `spec/ui_notes.md` sont autorisés.
- Corriger les **prompts** ou les **notes**, puis régénérer, plutôt que modifier le code généré.
- Chaque correction humaine d'un cas ou d'un test est tracée dans `spec/human_review.md`.

## Feuille de route

| Phase | Contenu | État |
|---|---|---|
| 0 | Préparation : dépôt, uv, Docker, Makefile, CI de lint, Jira/Xray, clé LLM | fait |
| 1 | 12 exigences `REQ-xxx.md`, notes d'API | fait |
| 2 | Génération de cas par IA, contrôle, revue | fait (34 cas) |
| 3 | Export Jira/Xray idempotent, mapping | fait |
| 4 | Génération des tests API et Playwright | fait (19 cas automatisés) ; Selenium non réalisé |
| 5 | CI GitHub Actions | fait ; exécution nocturne non réalisée |
| 6 | Rapport de synthèse | fait (Markdown, résumé du job) |
| 7 | Évaluation : métriques, preuves | voir `docs/metrics.md` |
| 8 | Bonus : OpenTelemetry + Jaeger, LLM-as-judge | non réalisé |
| 9 | Livraison : README, schémas, captures | en cours |

## Exigences non couvertes par un test automatisé

| Exigence | Raison |
|---|---|
| REQ-007 (réservation refusée) | Libellés de l'interface non relevés ; quota LLM limité |
| REQ-008 (contact valide) | Idem |
| REQ-009 (contact refusé) | Idem |
| REQ-011 (déconnexion) | Idem |

Les cas existent dans `cases/` et sont exportés dans Jira ; seule l'automatisation manque.
Règle appliquée : aucun test n'est généré tant que les libellés et messages de
l'interface n'ont pas été observés (`spec/ui_notes.md`).

## Limites et risques

**Qualité de l'IA**

- **Hallucinations** : le LLM peut produire des cas ou des tests faux. Exemples rencontrés :
  messages et champs inventés dans les cas UI, fixture inexistante, URL externe et
  `except: pass` dans un test généré. Garde-fous : Pydantic, `check_tests.py`, ruff, revue humaine.
- **Les contrôles automatiques vérifient la forme, pas la pertinence.** Un cas hors sujet
  (TC-002-03, un test de connexion rattaché à l'exigence sur la liste des chambres) a passé tous
  les contrôles et la CI ; il n'a été repéré qu'en relisant Jira.
- **Tests générés fragiles** : une course (lecture de l'API avant la fin de l'action UI) a fait
  échouer un test ; corrigée en attendant la réponse réseau dans l'exemple de référence et dans le prompt.
- **Format de sortie** : demander du code Python dans un objet JSON provoque des erreurs
  d'échappement ; le prompt demande un bloc de code, extrait puis validé.
- **Régénération** : `--force` régénère tous les cas du filtre, pas seulement celui visé.
- **Commentaire du rapport** : parfois générique (« impact à évaluer ») ou imprécis
  (confusion entre défauts et tests en défaut connu). Les chiffres, eux, sont calculés par le code.

**Exploitation**

- **Coût et quotas** : plan gratuit Groq limité en tokens par jour ; cache par hash et journal JSONL.
- **Données envoyées au LLM** (service tiers) : exigences, cas, notes API et UI, tests de
  référence, et pour le rapport les chiffres agrégés et les descriptions de défauts.
  Aucun secret ni donnée personnelle.
- **Dépendance à Xray** : essai limité dans le temps, d'où le `FileBackend` de secours. L'export
  est séquentiel (quelques minutes pour 34 tests). Les tests gold sans identifiant de cas ne sont
  pas importés, et les tests en défaut connu sont envoyés en `FAILED`.
- **Réseau du runner** : un téléchargement d'image Docker interrompu a fait échouer un run ;
  `docker compose up` est maintenant retenté 3 fois.
- **Couverture partielle** : 19 cas sur 34 sont automatisés, surtout côté API. Les tests UI
  dépendent de sélecteurs observés à la main.
- **Application en version milestone** : Spring Boot `4.1.0-M4` peut changer ou disparaître des
  dépôts ; le commit du sous-module est épinglé.
- **Faux positif de défaut** : DEF-003 déclaré puis retiré. Un défaut se confirme par le
  parcours réel avant d'être marqué `xfail`.

## Perspectives

`ZephyrBackend`, Jenkins (`Jenkinsfile.example`), tests Selenium (comparaison avec Playwright),
exécution nocturne pour repérer les tests instables, LLM-as-judge pour évaluer la
pertinence des cas, couverture des exigences REQ-007, 008, 009 et 011, OpenTelemetry.

## Licence

À définir pour le code du projet. L'application restful-booker-platform reste soumise à sa propre licence.