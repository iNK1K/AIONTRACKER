# À faire

Une tâche par ligne. Claude les traite dans l'ordre et coche `[x]` quand c'est fait.


## Fait
- [x] Journal des ventes (onglet 💰 Mes ventes) : annonces postées / vendues / relistées / retirées en un clic ou par capture, enregistré sur GitHub depuis le site, bilan réel (taxe, frais de mise en vente, relistes, bénéfice) ; remplace mes_annonces.json et mes_ventes.json
- [x] Accueil fiable : taxe 10 %, prix habituel = prix des ventes observées (48 h), potentiel du jour = Planning safe (compter seulement les « vrais achats » écarté : sous-compte 7 à 14 fois, voir rapport.md)
- [x] Accueil orienté action : liste « ✅ À faire maintenant » (annonces à ajuster, achats sûrs, plan du jour, quand poster, notes de version)
- [x] Suivi des vrais gains : onglet 💰 Mes gains (capture de l'historique des ventes → mes_ventes.json, réel vs estimé, part de marché réelle, ventes à perte)
- [x] Alertes plus calmes : alerts.types (par défaut annonces, achat-craft au vert, notes, restriction) + option alerts.resume_seul
- [x] Code consolidé : JavaScript dans aionhdv/site.js + tests automatiques (python -m unittest discover tests)
- [x] Transmutation intégrée (Od → ressource de même rareté, gratuite, sans échec, non liée) : Quoi récolter, Achat → craft (Od si moins cher), Mon stock, Planning safe (marchés partagés)
- [x] Onglet 📅 Planning : plan safe (temps de jeu → quoi récolter, quoi crafter, combien d'annonces, gain) et plan gamble (chaînes blanc → vert → bleu → unique : réussite selon les niveaux, combo 24 %, perte si échec, gain du proc, vendre ou continuer, jackpot)
- [x] Volumes de vente mesurés sur le serveur (annonces disparues × taille des annonces) au lieu de l'extrapolation Kaisinel
- [x] Quoi récolter : kinah par heure de récolte (100/h par défaut) et heures avant saturation
- [x] Capture de la fenêtre des ventes → mes_annonces.json
- [x] Capture de la fenêtre des ventes → remplissage de mes_annonces.json (accueil, section ④ : coller la capture, copier le fichier, lien vers l'éditeur GitHub)
- [x] Indice de sûreté (0-100, feu vert/orange/rouge) pour chaque opportunité d'achat : pression de l'offre (nouvelles annonces/h ÷ ventes/h), temps d'écoulement, marge si le prix revient à la normale, âge du pic ; alertes seulement au vert
- [x] Suivi de mes positions : coût de revient dans mes_annonces.json, alertes « baisse à X (encore rentable) », « sous ton seuil de rentabilité », « le prix chute : vends », temps d'écoulement de mon stock
- [x] Garde-fous chiffrés : quantité maximale conseillée (~2 h de ventes du marché) et prix plancher (« ne vends pas sous X ») sur chaque opportunité
- [x] Afficher l'heure de Paris sur le site et dans le résumé Discord
- [x] Taille des lots à mettre en vente et meilleures heures pour vendre
- [x] Tableau interactif des ressources ou peut rentrer le nombre de ressources que l'on possede et ca nous indique quels craft faire et combien ca va rapporter → onglet 🧮 Mon stock
- [x] Faire en sorte que les noms d'items soit copiable dans le presse papiers pour des recherches rapides dans le jeu → clic sur un nom
- [x] Nouvelle categorie tracking pour les items UNIQUE ou on recoit une alerte quand le prix est vraiment bas (setup bot discord) → onglet 💎 Uniques + alerte Discord
- [x] Mon stock : toutes les ressources récoltables de la faction + option crafts douteux
- [x] Onglet 🛠️ Mes métiers : niveaux par métier (enregistrés dans le navigateur, bouton +1), crafts impossibles grisés partout, profit ajusté au taux de réussite du jeu, « bientôt débloqué »
- [x] Prix de référence = prix habituel du serveur (médiane 3 j) + ⚡ pics de prix (achat → craft)
- [x] Mon stock : lecture d'une capture de la réserve (Ctrl+V) → liste des ressources et quantités, dans le navigateur
- [x] Mon stock : bouton « Coller une liste » (remplissage depuis une liste ; Claude peut la produire à partir d'une capture de la réserve)
- [x] Onglet Uniques : seulement les équipements Unique (armes, armures, accessoires) utilisables pour l'harmonisation, avec leur type
- [x] Setup les alertes discord pour rajouter une alerte quand un note de patch officielle est sortie + communique officiel de NCSOFT via le site officiel/twitter/reddit → site officiel + Reddit ; Twitter impossible (voir rapport.md)
- [x] Achat-revente pur (flip) → onglet 🔁 Flip + alerte Discord « Flip » (fenêtre 3 j plutôt que 7, voir rapport.md)
- [x] Sauvegarde solide de la base → release GitHub « db-backup » mise à jour chaque jour (plutôt que chaque semaine), restaurée automatiquement
- [x] Surveillance de mes annonces → fichier `mes_annonces.json` + alerte « Tu es battu » + section sur l'accueil
- [x] Mode test `--dry-run`
- [x] Notes de patch × prix → items cités surveillés 48 h, alerte si le prix bouge de ±20 %
- [x] Courbe de prix par item → bouton 📈 à côté du nom
- [x] Tendances de la semaine → résumé Discord le dimanche, avec le passage daily
- [x] Alertes Discord / communiqués NCSOFT : passages automatiques sautés par GitHub (2 créneaux par heure désormais) ; annonces officielles avec lien sur l'accueil et dans le résumé quotidien (voir rapport.md)
