# Mission 001 — Coverage pytest enricher.py

**Mission ID** : 001
**Slug** : pytest-coverage
**Date création** : 2026-05-01

═══ AUTONOMOUS MISSION ═══

## OBJECTIF UNIQUE MESURABLE

Créer ou compléter `tests/test_enricher.py` avec au minimum 3 tests 
pytest couvrant les cas critiques de `src/enricher.py` (ou 
fichier équivalent contenant la logique d'enrichissement). 
La commande `pytest tests/ -v` doit retourner tous tests verts 
à la fin.

## CONTEXTE

- Projet : csv-product-enricher (vertical Python automation Upwork P1)
- État actuel : enricher.py existe (audit J6 fait, 5 PR mergés sur main).
  Issue GitHub #5 ouverte : "Pytest coverage". Tests partiels ou absents.
- Pourquoi : combler issue #5, score audit 11/14 → 12/14.

## SCOPE DUR

Tu peux modifier UNIQUEMENT :
- `tests/test_enricher.py` (créer ou compléter)
- `tests/__init__.py` (créer si absent, vide ou avec docstring)
- `tests/conftest.py` (créer si fixtures pytest nécessaires)
- `tasks/done.md` (log obligatoire)
- `tasks/blocked.md` (si applicable)
- `tasks/lessons.md` (si applicable)

Tu NE PEUX PAS modifier :
- `src/enricher.py` (sauf bug évident bloquant les tests : alors STOP + blocked.md)
- `requirements.txt` (si pytest absent : STOP + blocked.md, ne pip install pas)
- Tout autre fichier

## WHITELIST

- Toutes commandes git (status, diff, log, add, commit, checkout -b)
- python, pytest, pytest -v, pytest --collect-only
- Get-ChildItem, Test-Path, Get-Content, Set-Content, New-Item
- Lectures de tous fichiers du repo (pour comprendre enricher.py)

## DENY

- pip install, npm install, winget install
- Modifications hors scope listé ci-dessus
- Push origin, merge main
- Remove-Item, rm

## CRITÈRES D'ARRÊT

1. SUCCÈS : `pytest tests/ -v` retourne 3+ tests PASSED, 0 FAILED
2. BLOCAGE : pytest non installé OU enricher.py inutilisable sans 
   modification → STOP + blocked.md
3. SCOPE : tu détectes que enricher.py a un bug à corriger → STOP + blocked.md
4. TEMPS : 60 min max (mission test bornée, pas 90)

## CAS PYTEST À COUVRIR (suggestions, à adapter selon code réel)

Adapte selon ce que fait réellement enricher.py. Idées :
1. Cas nominal : entrée valide → sortie attendue
2. Cas vide : CSV ou input vide → comportement gracieux
3. Cas malformé : ligne avec champ manquant → erreur claire ou skip
4. Cas API mockée : si enricher appelle Anthropic, mock la réponse 
   (utilise unittest.mock ou pytest-mock SI déjà disponible, sinon 
   skip ce cas)

Si tu trouves >3 cas légitimes : ajoute jusqu'à 5 max. Pas plus 
(scope creep).

## RÈGLES D'IMPRÉVU

- pytest non installé : STOP, append blocked.md "pytest absent, 
  mission requiert install hors scope"
- Tests existants déjà présents : LIS-LES d'abord, complète plutôt 
  que dupliquer. Mission = atteindre 3 tests verts, pas tout réécrire.
- enricher.py utilise une API externe (Anthropic, OpenAI...) : 
  mock obligatoire dans tests, ne pas appeler API réelle (coût + 
  fragilité)
- Imports cassés : log dans blocked.md, STOP

## LIVRAISON FINALE (MISSION REPORT dans done.md)

À la fin, append à done.md une section :
- Mission : 001-pytest-coverage
- Statut : SUCCESS / PARTIAL / BLOCKED
- Branche : feature/auto-20260501-pytest-coverage
- Commits : [hashes courts]
- Tests : N passent / M total
- Fichiers créés/modifiés : [liste]
- Recommandations humain : [3 lignes max, ex : "merge si OK", 
  "ajouter cas X plus tard"]

## DÉMARRAGE

1. Crée `feature/auto-20260501-pytest-coverage`
2. Append done.md : `[timestamp] MISSION 001 START | pytest-coverage`
3. Lis enricher.py et fichiers tests existants pour comprendre
4. Plan ton approche en 3-5 étapes (peut être interne, pas obligé 
   de logger le plan)
5. Exécute, log chaque étape

═══ FIN AUTONOMOUS MISSION ═══
