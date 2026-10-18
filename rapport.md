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
