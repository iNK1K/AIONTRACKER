# AION HDV

Outil personnel de suivi de l'hôtel des ventes d'Aion 2 (serveur Zemurru, Hadala avant le transfert du 22/10/2026) : voir README.md.

- Les tâches en attente sont dans `TODO.md`. Quand on te demande « fais la TODO », traite-les dans l'ordre, puis coche-les et déplace-les dans « Fait ».
- Réponds en français.
- Le site est publié par GitHub Actions (`.github/workflows/hdv.yml`) : ne pas republier `gh-pages` à la main. Pousser sur `main` suffit, le prochain passage horaire reprend le code.
- La page est générée par le paquet `aionhdv/report/` (un module par onglet, outils communs dans `base.py`, tableaux partagés dans `tables.py`, assemblage dans `__init__.py`) : fichiers en fins de ligne CRLF, les garder.
- Assistant (onglet 💬, chat Claude) : `aionhdv/report/assistant.py` écrit le catalogue `assist.js` ; le chat (appel API depuis le navigateur, outil `tracker_search`, Markdown) est la partie « assistant » de `site.js`. Ne jamais mettre de clé API ni de jeton d'abonnement dans le dépôt : la clé reste dans le navigateur ; le mode abonnement passe par `scripts/assistant_local.py` (Claude Code sur le PC de la personne, 127.0.0.1:8787).
- Onglet 🧙 Personnage : fiche du personnage remplie par les blocs ```perso des réponses (consigne dans `aionhdv/assistant_format.md`), partie « fiche du personnage » de `site.js` ; deux conversations (objets `AICH.chat` et `AICH.perso`, id suffixés « 2 » pour la seconde). La fusion `pMerge()` doit rester identique à `perso_merge()` du serveur AION Helper (dépôt Emikode/aion-helper, `helper.py`). Personnage officiel (armurerie NCSOFT, `PARM`, fonctions `a*`) : seulement via le serveur AION Helper (`/api/armory`, `armory.py`), l’API officielle n’envoie pas d’en-tête CORS.
- Le JavaScript de la page est dans `aionhdv/site.js` (et la lecture des captures dans `aionhdv/scan.js`) : plus de JS dans les chaînes Python.
- Tests : `python -m unittest discover tests` (petite base fabriquée en mémoire, la vraie base n'est pas touchée) ; à lancer après toute modification des calculs.
- Le code n'utilise que la bibliothèque standard de Python.
