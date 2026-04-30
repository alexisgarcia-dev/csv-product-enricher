# Audit J6 baseline - csv-product-enricher

**Date** : 2026-04-30 (J6)
**Branche** : audit/J6-baseline
**Score global** : 8/14 (code lisible et README solide, plombé par l'absence de CI, un vecteur format injection concret, et `.env.example` manquant)

---

## Resume executif

Le cœur logique est propre pour un outil CLI v0.1 : structure claire, KeyboardInterrupt géré, README de qualité client. Deux problèmes bloquent la livraison : un vecteur de format injection réel dans `prompts.py` qui skipperait silencieusement des rows en production sur toute description contenant `{` ou `}`, et un `.env.example` absent qui casse le premier `git clone`. L'axe principal d'amélioration est la robustesse : fail-fast sur API key, validation output dir, couverture de tests, et un pipeline CI minimal.

---

## Findings

### P0 - Bloquant (securite critique ou RCE)

Aucun finding P0 identifié.

---

### P1 - Haute priorite (a fixer J6)

- **`.env.example` absent** - `README.md:23`
  - Probleme : Le README instruite `cp .env.example .env` mais le fichier n'existe pas dans le repo.
  - Impact : Tout premier `git clone` échoue à l'étape setup ; onboarding client cassé.
  - Fix recommandé : Créer `.env.example` avec `ANTHROPIC_API_KEY=your_key_here`.

- **Format injection sur descriptions produit** - `prompts.py:33-36`
  - Probleme : `ENRICHMENT_PROMPT_TEMPLATE.format(sku=..., title=..., description=...)` — si `title` ou `description` contient `{` ou `}` (ex : "Sizes {S, M, L}", "Set of 3 {boards}"), `str.format()` lève `KeyError` ou `IndexError`.
  - Impact : Le row est skippé silencieusement via le `except Exception` de `enrich_row` ; l'utilisateur ne comprend pas pourquoi certains SKU sont absents du CSV de sortie.
  - Fix recommandé : Remplacer `.format()` par `string.Template` avec `safe_substitute()`, ou échapper `{`/`}` dans les champs avant le formatage.

- **Couverture de tests insuffisante** - `tests/test_enricher.py`
  - Probleme : 3 tests couvrent uniquement `load_csv` et `parse_response` (happy path + JSON invalide) ; `call_claude`, `enrich_row`, `build_prompt`, et la quasi-totalité des edge cases ne sont pas testés.
  - Impact : Le vecteur format injection ci-dessus n'est pas détecté en CI ; la logique de retry n'est jamais exercée.
  - Fix recommandé : Ajouter au minimum des tests pour `build_prompt` (titre avec accolades), `enrich_row` (mock client), et `parse_response` (score hors range, champ manquant).

- **Aucun pipeline CI** - (pas de `.github/workflows/`)
  - Probleme : `pytest` n'est pas exécuté automatiquement ; aucune vérification qualité sur PR.
  - Impact : Régression silencieuse possible à chaque commit ; le client ne peut pas valider les livraisons futures sans relancer manuellement.
  - Fix recommandé : Ajouter `.github/workflows/ci.yml` avec `pip install -r requirements.txt && pytest`.

---

### P2 - Moyenne priorite (a fixer J7-J20 dilue)

- **Fail silencieux sur API key invalide ou absente** - `enricher.py:61`
  - Probleme : `anthropic.AuthenticationError` est une sous-classe de `APIError` → capturé par `except Exception` dans `enrich_row` → tous les rows sont skippés avec des warnings jaunes sans arrêt du script.
  - Impact : L'utilisateur sans `ANTHROPIC_API_KEY` attend la fin du run pour constater 0 enrichissements, sans message d'erreur clair.
  - Fix recommandé : Valider `os.environ.get("ANTHROPIC_API_KEY")` dans `main()` avant de créer le client et lever une erreur explicite.

- **`--verbose` imprime les données produit en clair** - `enricher.py:26, 34`
  - Probleme : Prompt complet (SKU, title, description) et réponse Claude sont affichés via `console.print` en mode verbose.
  - Impact : Si les descriptions contiennent des données sensibles (noms fournisseurs, tarifs internes, notes PII), elles apparaissent dans les logs de terminal ou de CI.
  - Fix recommandé : Documenter ce comportement dans le README sous "Configuration" ; ou tronquer l'affichage à N caractères (`prompt[:200]`).

- **Répertoire de sortie non validé** - `enricher.py:106`
  - Probleme : `df.to_csv(args.output)` échoue avec `FileNotFoundError` si le dossier parent n'existe pas ; l'erreur n'est pas catchée.
  - Impact : L'utilisateur perd le run complet (résultats en mémoire) sans message user-friendly.
  - Fix recommandé : Ajouter `Path(args.output).parent.mkdir(parents=True, exist_ok=True)` dans `main()` avant le run.

- **`max_tokens=512` peut tronquer le JSON** - `enricher.py:29`
  - Probleme : Pour des descriptions longues ou un `enhanced_description` verbeux, Claude peut générer une réponse JSON tronquée avant la fermeture `}`.
  - Impact : `json.loads()` lève `JSONDecodeError` → row skippé silencieusement.
  - Fix recommandé : Monter à `max_tokens=1024` et/ou ajouter un log de troncature (`if len(raw) > 500 and not raw.strip().endswith("}")`).

- **Stratégie de retry insuffisante pour les rate limits** - `enricher.py:27-42`
  - Probleme : 2 tentatives avec 2s de wait max ; `anthropic.RateLimitError` hérite de `APIError` et est capturé, mais 2s est insuffisant pour les rate limits réels (Tier 1 : 60s cooldown possible).
  - Impact : Sur un CSV de 500 lignes, les rows en burst sont tous skippés après 2 tentatives.
  - Fix recommandé : Lire le header `Retry-After` de la réponse et attendre la durée indiquée, ou monter à 4 tentatives avec backoff exponentiel (2s, 4s, 8s, 16s).

---

### P3 - Cosmetique (optionnel)

- **`call_claude` sans annotation de retour** - `enricher.py:23`
  - Probleme : `def call_claude(...)` manque `-> str`.
  - Fix recommandé : Ajouter `-> str` à la signature.

- **`*.partial.csv` non couvert par `.gitignore`** - `.gitignore:14`
  - Probleme : Le pattern `output_*.csv` ne capture pas `result.csv.partial.csv` si l'output est nommé `result.csv`.
  - Fix recommandé : Ajouter `*.partial.csv` dans `.gitignore`.

- **`samples/output_sample.csv` référencé mais absent** - `README.md:40`
  - Probleme : Le README présente une table de sortie sous le titre "Output (samples/output_sample.csv)" mais le fichier n'existe pas dans `samples/`.
  - Fix recommandé : Créer `samples/output_sample.csv` à partir de la table du README, ou ajuster le libellé.

---

## Recommandations transverses

- **Tests en priorité** : ajouter des tests pour `build_prompt` (accolades dans données) et `enrich_row` (mock `anthropic.Anthropic`) avant toute livraison ; c'est le filet de sécurité manquant le plus critique.
- **CI minimal** : un workflow GitHub Actions `pip install + pytest` suffit à bloquer les régressions futures ; < 1h de travail, impact élevé.
- **Async pour la montée en charge** : le README le mentionne déjà — `asyncio` + `asyncio.gather` ou `anthropic.AsyncAnthropic` réduirait le temps de run de 500 lignes de 8 min à ~1-2 min.
- **Logging structuré** : remplacer les `console.print` de warning par `logging.warning(...)` pour rendre les sorties parsables en CI/log aggregator (Datadog, CloudWatch).
- **Validation d'entrée CSV** : ajouter une vérification de taille (`len(df) > 1000` → avertissement) et d'encodage (`pd.read_csv(path, encoding="utf-8-sig")`) pour robustesse sur données client réelles.

---

## Score detaille

| Critere | Score /2 | Justification |
|---|---|---|
| Lisibilite code | 2/2 | Fonctions courtes, nommage explicite, flux linéaire clair |
| Type hints / docstrings | 1/2 | Docstrings sur toutes les fonctions, mais `call_claude` manque `-> str` et `parse_response` `-> dict` explicite |
| Error handling | 1/2 | KeyboardInterrupt + partial save bien géré ; broad `except Exception` masque les bugs de programmation et l'auth error |
| Tests | 1/2 | 3 tests bien écrits, mais couverture critique absente (retry, format injection, enrich_row) |
| Documentation (README) | 2/2 | Excellent : setup, flags CLI, sample I/O, architecture, limitations — livrable client direct |
| CI / Quality automation | 0/2 | Aucun pipeline ; `pytest` dans `requirements.txt` mais jamais exécuté automatiquement |
| Securite / secrets | 1/2 | `.env` gitignored, zéro credential hardcodé ; pénalisé par format injection (P1) et verbose PII (P2) |
| **Total** | **8/14** | |

---

## Notes pour la suite

- **`.env.example`** : à créer avant tout partage du repo (hors scope du code mais bloquant pour le client).
- **Async** : l'architecture actuelle (boucle synchrone + `df.iterrows()`) supporte bien la migration async sans refactor majeur ; prévoir J10-J15.
- **`parse_response` strictness** : la validation actuelle rejette les types incorrects mais accepte des `seo_tags` avec 0 virgule (1 seul mot-clé) — à renforcer si la qualité SEO est un KPI client.
- **Modèle par défaut** : `claude-haiku-4-5-20251001` est un modèle récent/stable ; surveiller les annonces de dépréciation Anthropic pour anticiper une mise à jour du `--model` default.
