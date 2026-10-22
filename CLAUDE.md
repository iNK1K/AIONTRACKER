# AION HDV

Outil personnel de suivi de l'hôtel des ventes d'Aion 2 (serveur Zemurru, Hadala avant le transfert du 22/10/2026) : voir README.md.

- Les tâches en attente sont dans `TODO.md`. Quand on te demande « fais la TODO », traite-les dans l'ordre, puis coche-les et déplace-les dans « Fait ».
- Réponds en français.
- Le site est publié par GitHub Actions (`.github/workflows/hdv.yml`) : ne pas republier `gh-pages` à la main. Pousser sur `main` suffit, le prochain passage horaire reprend le code.
- `aionhdv/report.py` est en fins de ligne CRLF : les garder.
- Le JavaScript de la page est dans `aionhdv/site.js` (et la lecture des captures dans `aionhdv/scan.js`) : plus de JS dans les chaînes Python.
- Tests : `python -m unittest discover tests` (petite base fabriquée en mémoire, la vraie base n'est pas touchée) ; à lancer après toute modification des calculs.
- Le code n'utilise que la bibliothèque standard de Python.
