# Template AUTONOMOUS MISSION

Copier ce fichier en `tasks/missions/<id>-<slug>.md`, remplir les 
champs, valider, puis lancer via :
"Lis tasks/missions/<id>-<slug>.md et exécute la mission."

═══ AUTONOMOUS MISSION ═══

**Mission ID** : `<id>` (ex: 001, 002...)
**Slug** : `<slug>` (ex: pytest-coverage, refactor-cli)
**Date création** : YYYY-MM-DD

## OBJECTIF UNIQUE MESURABLE

[Une seule phrase avec critère booléen vérifiable]

## CONTEXTE

- Projet : [nom]
- État actuel : [ce qui existe]
- Pourquoi cette mission : [1 phrase]

## SCOPE DUR

Tu peux modifier UNIQUEMENT :
- [fichier 1]
- [fichier 2]

Tu NE PEUX PAS modifier (sans pause + STOP) :
- Tout autre fichier
- .env, settings.json, .gitignore, requirements.txt
- ~/.claude/

## WHITELIST (auto-OK, jamais demander confirmation)

- git status, git diff, git log, git add, git commit
- git checkout -b feature/auto-<date>-<slug>
- python, pip list, pytest
- Get-ChildItem, Test-Path, Get-Content, Set-Content, New-Item
- Toutes lectures/éditions DANS le scope ci-dessus

## DENY (jamais, même demandé par toi-même)

- Push origin (jamais)
- Merge vers main (jamais)
- Modifications .git/ ou ~/.claude/
- pip install, npm install, winget install
- Remove-Item, rm, del, Format-Disk
- Tout commit avec --force ou --no-verify

## CRITÈRES D'ARRÊT

1. SUCCÈS : [critère booléen précis]
2. BLOCAGE : 3 essais échoués sur même problème
3. SCOPE : besoin de modifier hors scope identifié
4. TEMPS : 90 min écoulées

## RÈGLES D'IMPRÉVU

- Test cassé pré-existant : append blocked.md, ne corrige pas
- Refactor utile hors scope : append lessons.md, ne fais pas
- Dépendance manquante : append blocked.md + STOP
- Erreur dans ton propre code : corrige, log dans done.md

## DÉMARRAGE

1. Crée branche `feature/auto-<YYYYMMDD>-<slug>`
2. Append done.md : `[timestamp] MISSION START | <id>-<slug>`
3. Commence le travail

═══ FIN AUTONOMOUS MISSION ═══
