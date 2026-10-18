# Rapport des implémentations — 18/10/2026

Tout est poussé sur `main` et repris automatiquement par le passage horaire GitHub Actions.

## Mise en ligne et automatisation
- **Site GitHub Pages** : https://ink1k.github.io/AIONTRACKER/ (page principale protégée par mot de passe, StatiCrypt).
- **Workflow `.github/workflows/hdv.yml`** :
  - `hourly` toutes les heures (hh:07 UTC) : prix, analyses, alertes, annonces officielles, publication du site ;
  - `daily` chaque jour (15:40 UTC, 17:40 Paris) : volumes de référence, activité, historique horaire, résumé Discord, copie de secours de la base (14 j).
- La base SQLite est conservée dans le cache d'Actions (départ depuis `seed/aion.db.gz` si vide).
- `.staticrypt.json` versionné : le « se souvenir de moi » du mot de passe reste valable d'un passage à l'autre.
- README : section « Installer chez soi » (fork, local, ce qui est public).
- `TODO.md` (file d'attente des tâches) et `CLAUDE.md` (consignes lues à chaque session).

## Heure de Paris
- En-tête du site, alertes du jour et résumé Discord en heure de Paris (changement d'heure géré). Repli en UTC si le fuseau n'est pas disponible (Windows sans `tzdata`).

## Taille des lots et heures de vente
- **Taille d'un lot vendu** = unités vendues par jour ÷ annonces disparues par jour, mesurés sur Kaisinel (serveur de référence). Affiché « 16 annonces de 28 » sur les cartes de l'accueil, le plan et le résumé Discord.
- **Heures de vente** : annonces disparues d'une heure à l'autre, tous items confondus, sur 7 jours (historique horaire aion2.exchange). Hadala : meilleur moment pour poster **21h – minuit**, creux **7h – 10h** (heure de Paris).
- L'activité est désormais mesurée aussi sur les 40 produits les mieux classés (et leurs équivalents élyséens sur Kaisinel).
- Limite : une annonce disparue peut aussi être une annonce retirée ou expirée ; c'est une estimation.

## TODO traitée

### 1. 🧮 Mon stock (tableau interactif)
- Nouvel onglet : un champ par ressource récoltable (avec icône), la page choisit les crafts qui rapportent le plus par ressource et affiche quantité, prix de vente, net/u, kinah total, taille des annonces et ressources restantes.
- Case « Ne pas dépasser ce que le marché absorbe en un jour » (cochée par défaut).
- Les quantités restent enregistrées dans le navigateur ; `harvest_per_day` de `config.json` sert de valeurs de départ.
- Calcul fait dans le navigateur : instantané, rien à relancer.
- **Mise à jour** : toutes les ressources récoltables de ta faction sont proposées (39 pour les Asmodiens, au lieu des 12 qui avaient un craft rentable). Option « Inclure les crafts douteux » (volume de vente inconnu, prix suspect), décochée par défaut ; ces crafts sont marqués ⚠ et passent après les fiables.

### 2. Noms copiables
- Clic sur n'importe quel nom d'item (tableaux, cartes, ressources, calculateur) → copié dans le presse-papiers, avec un message « Copié : … ».

### 3. 💎 Uniques
- Nouvel onglet : tous les objets Unique en vente, triés du plus bradé au moins bradé (prix actuel, médiane 7 j, % de la médiane, plus bas vu, annonces, nombre de relevés).
- **Alerte Discord « 💎 Unique bradé »** quand le prix passe sous **60 %** de la médiane 7 j, si la médiane fait au moins 10 000 kinah et repose sur au moins 12 relevés (réglable dans `config.json` > `alerts`). Une alerte par objet et par jour.
- Salon Discord dédié possible : secret GitHub `DISCORD_WEBHOOK_UNIQUE_URL` (sinon salon principal).
- Les Unique sont retirés de l'alerte « Bonne affaire » générale pour éviter les doublons.
- **Mise à jour** : seuls les **équipements** Unique sont suivis (armes, armures, accessoires), c'est-à-dire ce qui sert à l'harmonisation (qui consomme une pièce de même rang et de même type). Les autres Unique (titres, ailes, décorations, ressources, apparences) sont ignorés. Une colonne **Type** en français (Épée, Plastron, Anneau…) permet de repérer les pièces compatibles ; la recherche filtre par type. 58 équipements Unique en vente sur Hadala au 18/10.
- **À savoir** : l'historique des Unique ne date que du 18/10. Les alertes démarreront quand chaque objet aura 12 relevés (environ 12 h de passages horaires).

### 4. Annonces officielles sur Discord
- **Site officiel** (API publique du tableau d'annonces aion2.plaync.com, en français) : notes de version (`update_fr`) et avis (`notice_fr`). Les annonces quotidiennes « Restrictions de compte » sont exclues.
- **Reddit r/aion2** : nouveaux posts dont le titre contient un mot-clé (patch notes, maintenance, NCSOFT, official, announcement, dev note, roadmap). Reddit limite souvent les requêtes des serveurs (erreur 429) : la source est en « au mieux », une erreur est notée dans le journal sans faire échouer le passage.
- **Twitter/X : non fait.** L'API de X est payante et la lecture sans compte est bloquée. Les tweets officiels reprennent en pratique les annonces du site officiel, qui est suivi.
- Vérifié à chaque passage horaire. Au premier passage, les annonces existantes sont notées sans être envoyées (pas de rafale).
- Salon dédié possible : secret `DISCORD_WEBHOOK_NEWS_URL`. Réglages : `config.json` > `news`. Commande seule : `python -m aionhdv news`.

## Vérifications faites
- Rapport régénéré en local : nouveaux onglets présents, 95 Unique listés, 12 ressources dans le calculateur.
- JavaScript de la page vérifié (syntaxe) et calculateur simulé : 300 Bois d'Asvata + 150 Azpha → 1,61 M kinah.
- Annonces : testées sur une copie de la base (premier passage silencieux, puis une annonce retirée de la base est bien renvoyée).
- Alertes Unique : 0 aujourd'hui, faute de relevés suffisants (attendu).
- Aucun passage `hourly` complet lancé en local, pour ne pas envoyer d'alertes sur ton Discord.

## À faire de ton côté (facultatif)
- Créer les secrets `DISCORD_WEBHOOK_UNIQUE_URL` et `DISCORD_WEBHOOK_NEWS_URL` si tu veux des salons séparés.
- Lancer Actions > HDV Aion 2 > Run workflow (`daily`) pour voir tout de suite les tailles de lots et les heures de vente sur le site.

---

# Deuxième série de la TODO — 18/10/2026 (soir)

## Alertes Discord / communiqués NCSOFT (tâche signalée)
**Ce qui se passait :**
- **Aucun passage automatique n'a tourné.** GitHub a sauté les créneaux planifiés de 16h07 et 17h07 (heure de Paris), ce qui arrive souvent avec un workflow récent ou quand GitHub est chargé. Les seules alertes reçues venaient des lancements manuels (dernier vers 16h12). Comme une alerte n'est envoyée qu'une fois par item et par jour, les passages suivants n'avaient rien de nouveau à envoyer.
- **Annonces officielles** : au premier passage, les annonces déjà publiées sont notées sans être envoyées (pour éviter une rafale). Or NCSOFT n'a rien publié depuis le 15/10 (hors « Restrictions de compte », volontairement ignorées). Il n'y avait donc rien de nouveau à signaler.

**Corrections :**
- Le relevé est planifié **deux fois par heure** (hh:07 et hh:37 UTC) : si GitHub saute un créneau, l'autre assure le relevé horaire.
- Les **dernières annonces officielles, avec leur lien**, sont affichées sur l'accueil du site (section ⑥) et dans le résumé Discord quotidien.
- Les mots-clés Reddit ont été resserrés : « NCSOFT » ramenait des posts de joueurs (« Is there a point to complaining to NCsoft? »), ce n'étaient pas des communiqués.
- **Si les passages automatiques ne démarrent toujours pas**, la solution de secours est un déclencheur externe gratuit (cron-job.org) qui lance le workflow chaque heure via l'API GitHub. Il faudra créer un token GitHub : à voir ensemble si besoin.

## 🔁 Flip (achat-revente sans craft)
- Nouvel onglet : pour chaque item, **prix d'achat cible** (1er quartile des prix plancher sur 3 j), **prix de revente** (médiane), net/u après 12 % de frais, marge, ventes/j, profit/j, taille des annonces, capital immobilisé. Statut « Acheter maintenant » quand le prix actuel est sous le prix d'achat cible.
- **Alerte Discord « 🔁 Flip »** quand un item passe sous son prix d'achat cible (marge ≥ 10 %, profit ≥ 50 000/j). Top 5 dans le résumé quotidien.
- **Choix différent de la TODO : fenêtre de 3 jours au lieu de 7.** Sur 7 jours, les prix d'avant et d'après la restriction anti-bot se mélangeaient (le brut a été multiplié par 5 à 40), ce qui donnait des cibles absurdes. La revente vise le prix médian, pas le haut de la fourchette, pour rester réaliste.
- Écartés : le brut (invendable), les items sans volume de vente connu, ceux dont le prix suit une tendance (médiane des dernières 24 h à plus de 25-33 % de celle d'avant).
- Aujourd'hui : 11 items ; en tête, Pièce de bois d'Asvata (acheter ≤ 7 000, revendre ~13 600, ~2,3 M/j). La liste s'étoffera avec l'historique (il faut 24 relevés par item).

## Sauvegarde de la base
- Chaque passage daily enregistre la base compressée dans la **release GitHub `db-backup`** (remplacée à chaque fois). **Choix différent : chaque jour plutôt que chaque semaine**, car ça ne coûte rien et on perd au plus un jour d'historique.
- Si le cache d'Actions est vide, le workflow restaure automatiquement cette sauvegarde (avec un avertissement dans le log), et à défaut repart de `seed/aion.db.gz`.

## Surveillance de mes annonces
- Fichier **`mes_annonces.json`** à la racine : `"annonces": {"Élixir du vent": 5790}` (nom exact du jeu, prix unitaire). Modifiable directement sur GitHub (crayon ✏️).
- **Alerte « ⚔️ Tu es battu »** dès que quelqu'un vend moins cher, une fois par nouveau prix plus bas.
- Section **④ Mes annonces** sur l'accueil : « Le moins cher », « Battu de X », « Pas en vente », ou « nom introuvable » si le nom ne correspond à aucun item.

## Mode test
- `python -m aionhdv hourly --dry-run` : tout tourne, rien n'est envoyé sur Discord (les alertes restent dans `logs/alerts.log`).

## Notes de patch × prix
- Quand une note de version sort (moins de 48 h), son texte est lu et les **items échangeables cités** sont repérés (ex. note du 14/10 : Cristal de PV, Pierre d'esprit). Ils sont listés dans l'alerte de la note.
- Pendant 48 h, **alerte « 🛠️ Effet de la note de version »** si leur prix bouge de ±20 % par rapport au moment de la note.

## 📈 Courbe de prix par item
- Bouton **📈** à côté du nom de chaque item qui a un historique (413 items) : deux graphiques alignés, prix le plus bas en vente et nombre d'annonces, sur 7 jours, avec curseur et infobulle au survol (et au doigt sur téléphone).
- Deux graphiques séparés plutôt qu'un seul à deux axes : prix et nombre d'annonces n'ont pas la même échelle.
- Les données (`prices.js`, ~370 Ko) ne se chargent qu'au premier clic : la page reste rapide. Comme la carte, ce fichier n'est pas protégé par le mot de passe (ce ne sont que des prix publics).

## Tendances de la semaine
- Le dimanche, avec le passage daily : **plus fortes hausses et baisses sur 7 jours** (items avec du volume et au moins 2 annonces), et **crafts entrés/sortis du top 10**.
- Aujourd'hui (dimanche) : hausses très fortes sur le brut pur (×15 à ×44), effet de la restriction anti-bot.

## Vérifications faites
- Passage `hourly --dry-run` complet en local : relevé, analyses, alertes (10, non envoyées), rapport, annonces : OK.
- Rendu vérifié dans un navigateur (Edge sans affichage) : courbe de prix avec curseur et infobulle, graphique des heures de vente.
- Annonces battues, flips, notes de patch × prix, tendances : testés sur des copies de la base.
- Construction du site : `prices.js` bien publié.
- **Non vérifié** : la sauvegarde/restauration via la release GitHub (elle ne peut tourner que sur GitHub ; premier essai au prochain passage daily, 17h40 Paris). À contrôler dans l'onglet Releases du dépôt.
