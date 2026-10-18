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

---

# Lecture d'une capture de la réserve — 18/10/2026 (soir)

## Ce que ça fait
Dans l'onglet **🧮 Mon stock**, cadre **📷 Lire une capture de ta réserve** : coller une capture (Ctrl + V), la glisser sur le cadre ou choisir le fichier. Le navigateur repère la grille, reconnaît chaque ressource de récolte et lit sa quantité, puis remplit « Coller une liste » : il ne reste qu'à vérifier et cliquer sur **Remplir**. Les autres objets (potions, viandes, planches…) et les cases vides sont ignorés. Rien n'est envoyé nulle part.

## Comment
- **Grille** : repérage des fines lignes sombres entre les cases, au 1/20 de pixel, axe par axe (les cases ne sont pas carrées : ~57,0 × 59,2 px sur tes captures). Les cases coupées sur les bords (jusqu'à 25 %) sont gardées.
- **Icônes** : comparaison avec les 33 icônes officielles des ressources de ta faction (aucune icône en double une fois les ressources élyséennes écartées). Une case n'est retenue que si elle ressemble nettement plus à une ressource qu'à toute ressource d'une autre famille, et si elle n'est pas vide.
- **Quantités** : pas d'outil externe. Les chiffres du jeu ont toujours la même police : j'ai appris leur forme sur tes deux captures (148 chiffres), le site compare chaque chiffre à ces modèles.
- Fichier `aionhdv/scan.js`, chargé seulement au premier collage.

## Fiabilité mesurée (tes 2 captures)
- Ressources : **66 sur 66** reconnues, **0** objet pris à tort pour une ressource.
- Quantités : **65 sur 66** justes ; la fausse (69 au lieu de 169, case coupée à droite) est signalée « à vérifier » avec sa vignette.
- Limites : mesuré sur 2 captures à la même résolution. Une autre taille d'écran ou d'interface peut dégrader la lecture des chiffres ; envoie-moi alors une capture et je réentraîne les modèles. Les cases coupées à droite ou en bas sont toujours signalées « à vérifier ».
- La lecture ne marche que sur le site en ligne (un navigateur interdit de lire les pixels des icônes depuis un fichier local).

## Corrigé au passage
- **Ressources élyséennes** : Mon stock filtre maintenant les ressources d'après les zones de récolte de la carte (Targena, Coriolus, Méla, Aria… écartées pour un Asmodien). 33 ressources sur Hadala.
- Mes lectures à l'œil de tes captures contenaient des erreurs que l'outil corrige : les « 9 » sont du **Bois d'Asvata pur**, les « 8 » de l'**Od pur**, les « 89 » de l'**Od d'une grande pureté**.

## Mise à jour : version générale (3 captures, 2 tailles d'interface)
Ta 3e capture (avec le titre « Matériaux de fabrication », une marge, et des cases 8 % plus petites) faisait échouer la détection : elle prenait des cases deux fois trop grandes. Corrigé de façon générale, sans réglage propre à une capture :
- **Grille** : quand un multiple du pas (2 ou 3 cases) ressemble presque autant au vrai pas, on garde le plus petit ; pas mesuré sur chaque axe. Les zones hors grille (titre, onglets, marges) donnent des cases ignorées.
- **Icônes** : seuils recalculés sur les 3 captures ensemble.
- **Chiffres** : modèles réappris sur les 3 captures (216 chiffres, dont 2 tailles d'affichage). Validation croisée (apprendre sur 2 captures, tester sur la 3e jamais vue) : 90 % des quantités justes.
- L'aperçu montre maintenant **toutes** les cases reconnues avec leur vignette et la quantité lue (⚠ sur les douteuses), pour vérifier d'un coup d'œil avant de remplir.

Résultat sur les 3 captures : **85 ressources reconnues sur 88, aucune inventée ni confondue** (manquées : 2 Bois d'Asvata, 1 Morfa) ; **82 quantités justes sur 85** (2 erreurs signalées ⚠, 1 non signalée : 9 au lieu de 19).

---

# Prix de référence et pics de prix — 18/10/2026 (soir)

## Pourquoi le Lingot d'orichalque n'apparaissait pas en achat → craft
Vérifié sur les sites HDV (Hadala) : le lingot vaut habituellement **1 500 à 1 800** (médiane 3 j : 1 497 sur a2-tracker, 1 800 sur aion2.exchange ; ventes réelles sur Kaisinel : 1 767 en moyenne), soit 3 fois moins que ses 2 minerais (~5 450 pièce). Il est monté à 10 000 ce matin (retombé en 6 h), puis à **20 000 à 15h45** et 15 000 ensuite. Coût du craft : 2 minerais + Solvant d'orichalque (400, prix PNJ vérifié) ≈ 10 200. Vendu à 15 000 : **+3 000/u** ; revendu au prix habituel : **−8 600/u**. L'outil le jugeait donc (à raison) non rentable en temps normal, mais masquait l'opportunité.

## Point 1 : prix de référence = prix habituel sur ton serveur
- Avant : le « prix réaliste » était ramené vers le prix de vente moyen de **Kaisinel** (autre serveur, autre niveau de prix : minerai 2 200 là-bas contre 5 450 sur Hadala).
- Maintenant : référence = **médiane des prix plancher de Hadala sur 3 jours** (au moins 12 relevés) ; Kaisinel ne sert plus qu'à défaut, et pour les volumes de vente.
- Effet immédiat : 2 crafts achat → craft rentables apparaissent (Poudre de Pierre d'esprit, Potion de soin supérieure), masqués jusque-là. Colonne « Prix réf. » renommée « Prix habituel ».

## Point 2 : ⚡ Pics de prix
- Nouveau tableau en tête de l'onglet **Achat → craft** : crafts rentables **au prix affiché** (marge ≥ 15 %) alors que le prix affiché est au moins 1,5× le prix habituel. Colonnes : prix affiché, prix habituel, ×pic, depuis quand, coût, net/u si vendu au prix affiché, net/u si le prix redescend, ingrédients à acheter.
- Rappel sur l'accueil (section ③) quand il y a des pics en cours.
- **Alerte Discord « ⚡ Pic de prix »** (une par item et par jour) avec le gain si tu vends vite et la perte si le prix redescend.
- Seuil réglable : `alerts.spike_craft_min_margin` (0.15).
- Aujourd'hui : Lingot d'orichalque (×11), Cuir résistant (×2,9), Papier d'Asvata (×6,1).

---

# Onglet 🛠️ Mes métiers — 18/10/2026 (soir)

## Tables de réussite
- Source : tables du client du jeu, extraites par a2-tracker (`CraftRecipeRate`), indexées par l'**écart de niveau** (ton niveau − niveau requis). **Vérifiées contre ta capture « Chances de fabrication »** du lingot : identiques au millionième (95,200927 %, 95,587774 %, 95,724539 %…), et 98,761433 % à l'écart 40 (ton niveau 41).
- 6 courbes utilisées par les recettes visibles (la 7e ne sert à aucune) :

| Recettes concernées | Écart 0 | 5 | 10 | 20 | 30 | 50+ |
|---|---|---|---|---|---|---|
| Équipements « Roi dragon » (Spécialiste 5–10) | 67,5 | 74,1 | 79,0 | 86,2 | 90,5 | 94,6 |
| Potions, élixirs, plats, pierres, parchemins (Alchimie, Cuisine, Débutant 1 à Spécialiste 45) | 72,9 | 75,5 | 79,6 | 83,8 | 87,3 | 90,9 |
| Équipements d'orichalque (Débutant 3–10) | 74,0 | 78,2 | 81,4 | 87,4 | 90,3 | 93,1 |
| Équipements d'orichalque d'expert (Débutant 15–25) | 76,8 | 81,6 | 85,1 | 89,6 | 92,4 | 94,6 |
| Équipements d'orichalque de maître (Débutant 30–40) | 79,6 | 83,6 | 87,2 | 91,4 | 94,1 | 96,8 |
| Matériaux : lingots, pièces, poudres, cornes raffinées (Débutant 1 à Spécialiste 30) | 95,2 | 95,9 | 97,0 | 98,0 | 98,6 | 99,2 |

- Les recettes de niveau 0 sans table (et sans jauge d'échec) sont comptées à 100 %.
- Recettes et tables rechargées à chaque passage daily (suivent les patchs).

## L'onglet
- Un cadre par métier (Alchimie, Artisanat, Forge d'armures, Forge d'armes, Cuisine) : grade **Débutant / Spécialiste** et niveau 1–50 comme en jeu, bouton **+1** (Débutant 50 → Spécialiste 1), nombre de crafts rentables débloqués. Partout sur le site, les niveaux requis s'affichent ainsi (« 🔒 Alchimie Spécialiste 5 »).
- Niveaux enregistrés **dans le navigateur** (chaque joueur a les siens) ; bouton **🔗 Copier le lien de mes niveaux** pour les transférer sur un autre appareil.
- Options : **En cas d'échec, les ingrédients sont perdus** (cochée par défaut, à confirmer en jeu) ; **Masquer les crafts que je ne peux pas faire** (sinon grisés).
- **Bientôt débloqué** : crafts rentables accessibles dans les 10 prochains niveaux, triés par profit/jour.
- Tableau des chances de réussite (ci-dessus).

## Effets sur le reste du site
- Aujourd'hui, Mes crafts, Achat → craft, pics de prix : crafts impossibles grisés (« 🔒 Alchimie niv. 55 ») ou masqués ; nouvelle colonne **Réussite** ; Net/u et Profit/j recalculés (coût ÷ taux de réussite si les ingrédients sont perdus).
- Mon stock : seuls les crafts faisables sont proposés, et la consommation de ressources tient compte des échecs (ex. 300 Bois d'Asvata → 145 Pièces au lieu de 150 à 97 %).
- Pour un item fabricable par plusieurs métiers (ex. Lingot : Forge d'armes ou d'armures), le site prend la façon la plus favorable selon tes niveaux.
- Sans niveau renseigné pour un métier, rien ne change pour ses crafts.

---

# Sûreté des achats et suivi des positions — 18/10/2026 (soir)

## Ce qui s'est passé sur tes lingots et ton papier
- **Lingot d'orichalque** : pic à 20 000 à 15h41, puis le nombre d'annonces passe de 11 à 50 en 4 h (tout le monde a crafté, aidé par l'alerte de pic) et le prix retombe à 10 000. 4,8 nouvelles annonces/h pour 3,7 vendues : le stock s'accumule. Seuil de rentabilité ~11 600 (coût ~10 200 + 12 % de frais).
- **Papier d'Asvata** : prix en baisse continue (7 400 → 6 000), annonces 13 → 44, 1,7 nouvelle annonce/h pour 0,3 vendue : ~5 jours pour écouler une nouvelle annonce.

## 1. Indice de sûreté (0-100, 🟢 / 🟠 / 🔴)
Calculé pour chaque opportunité d'achat (pics de prix, achat → craft, flips), sur l'item que tu revends :
- **pression de l'offre** = nouvelles annonces/h ÷ annonces vendues/h, mesurée **sur les 3 dernières heures** à chaque passage horaire pour les items surveillés (repli sur 24 h) ; > 0,8 : −12, > 1,2 : −30, > 2 : −45 ;
- **temps d'écoulement** = annonces devant toi ÷ ventes/h ; > 4 h : −10, > 12 h : −22, > 24 h : −35 ;
- **perte si le prix revient à la normale** : −25 ;
- **pic vieux de plus de 6 h** (d'autres vendeurs ont eu le temps d'arriver) : −10 ;
- activité inconnue : −25.
🟢 ≥ 70, 🟠 40–69, 🔴 < 40. Le détail des raisons s'affiche au survol du badge.
**Les alertes « ⚡ Pic de prix », « Achat → craft » et « Flip » ne partent plus qu'au 🟢.**

## 2. Suivi de mes positions
`mes_annonces.json` accepte maintenant le coût de revient et la quantité :
```json
"annonces": {
  "Lingot d'orichalque": {"prix": 15000, "cout": 10200, "quantite": 20},
  "Papier d'Asvata": 6500
}
```
Alertes (une fois par jour et par item, sauf « battu » : une par nouveau prix plus bas) :
- **⚔️ Tu es battu** : avec le prix pour repasser devant et ce qu'il te reste par unité, ou « le plus bas est sous ton seuil : baisser = vendre à perte » ;
- **⛔ Sous ton seuil de rentabilité** : le plus bas est passé sous coût + frais ;
- **📉 Le prix chute** : prix actuel ≤ 75 % du plus haut des 3 dernières heures ;
- **🐢 Stock long à écouler** : plus de 24 h au rythme actuel des ventes pour ta quantité.
Accueil, section ④ : seuil de rentabilité, gain/u au plus bas, et conseil (repasser devant à X, ne pas baisser, vendre maintenant, temps d'écoulement).
Testé sur les données réelles de 20h29 avec une position fictive de 20 lingots à 12 000 (coût 10 200) : les 4 alertes attendues sont sorties (battu → ne baisse pas, sous ton seuil −1 400/u, chute de 50 % en 3 h, papier : repasse devant à 5 999).

## 3. Garde-fous chiffrés
Sous chaque badge : **quantité max conseillée** (~2 h de ventes du marché, plafonnée à ta part de marché sur 2 h, divisée par 3 pendant un pic) et **« ne vends pas sous X »** (prix plancher = coût ÷ 0,88). Repris dans les alertes Discord.

---

# Plus d'items comparés — 18/10/2026 (soir)

**Pourquoi si peu d'items** (constat sur les données) :
- **Mes crafts** : 192 crafts utilisent des ressources de récolte, mais 130 n'ont aucune annonce sur Hadala (surtout les équipements Roi dragon) : sans prix, pas de comparaison possible. Parmi ceux qui ont un prix, 33 ont un volume de vente inconnu (jamais vendus sur Kaisinel, seul serveur dont le jeu publie les ventes).
- **Aujourd'hui** : n'affichait que les 6 meilleurs crafts rentables (sur 16).
- **Flip** : 265 items sur 434 écartés faute d'historique (24 relevés horaires demandés, relevés commencés le 18/10).

**Changements :**
- Aujourd'hui : **12 crafts** (au lieu de 6), avec le nombre total et un lien vers la liste complète.
- Mes crafts / Achat → craft : les items **pas en vente en ce moment mais vus dans les 3 derniers jours** sont comparés avec leur dernier prix connu, marqués « pas en vente en ce moment ». Mes crafts : 62 → 82 crafts comparés ; Achat → craft : 86 → 106.
- Flip : **12 relevés** suffisent (au lieu de 24), avec un badge « historique court » sous 48 relevés. L'onglet se remplit tout seul : chaque passage horaire ajoute un relevé par item.

---

# Capture de mes ventes → mes_annonces.json — 18/10/2026 (soir)

## Utilisation
Accueil, section **④ Mes annonces**, cadre **📷 Remplir depuis une capture de mes ventes** : coller une capture de la fenêtre des ventes (Ctrl + V sur l'onglet Aujourd'hui), la glisser ou choisir le fichier. Plusieurs captures s'ajoutent (si tes ventes tiennent sur plusieurs écrans). Le site affiche chaque annonce lue (vignette, objet, quantité, prix unitaire ; ⚠ si douteuse), puis le **contenu complet de `mes_annonces.json`** :
- annonces du même objet regroupées (quantités additionnées, prix le plus bas) ;
- **coût de revient prérempli** avec l'estimation du site (achat des ingrédients au prix actuel) — à corriger si tu as récolté ou acheté moins cher ;
- choix « Remplacer mes annonces » ou « Ajouter à mes annonces actuelles » (garde aussi tes coûts déjà saisis) ;
- bouton **📋 Copier le fichier** et lien **✏️ Ouvrir mes_annonces.json sur GitHub** : coller, « Commit changes », et le passage horaire suivant suit tes annonces.
Choix retenu : copier-coller (pas de token d'écriture dans le navigateur).

## Comment ça lit la capture
- **Annonces** : une pièce dorée devant chaque prix total ; l'icône est à une position fixe par rapport à elle (mesurée sur tes captures, à l'échelle de l'interface ; remontée quand une ligne « par unité » est présente).
- **Objet** : par son icône, comparée aux icônes des ~770 objets vus en vente, avec une comparaison tolérante aux badges (ex. le badge rouge des équipements fabriqués).
- **Prix** : chiffres appris sur ta capture (total en blanc, unitaire en gris). **Quantité** = total ÷ unitaire quand les deux sont lus (plus sûr que le petit chiffre sur l'icône), sinon chiffre de l'icône.
- **Vérifications** : total = unitaire × quantité, objet nettement reconnu ; sinon ⚠ « à vérifier ».

## Fiabilité
- Tes 2 captures : **9 annonces sur 9** justes (objet, quantité, prix unitaire, total).
- **Limite : ta capture ne contient aucun chiffre 8**, la forme du 8 n'est donc pas apprise. Un prix avec un 8 sera mal lu ou illisible, mais la vérification total = unitaire × quantité le signalera (⚠). Envoie-moi une capture avec un 8 dans un prix et j'ajoute le modèle.
- Mesuré sur une seule taille d'interface (capture plein écran 1507 px de large).

---

# Volumes de vente mesurés sur ton serveur — 18/10/2026 (soir)

**Constat** : tu n'as vendu aucune potion alors que l'outil annonçait ~430 ventes/jour. Vérifié sur Hadala : seulement 12 à 16 annonces disparues en 24 h pour les potions/élixirs de PV. L'outil extrapolait les ventes de **Kaisinel** (seul serveur dont le jeu publie les ventes) × un coefficient d'activité global de Hadala (×0,37) : faux pour beaucoup de produits.

**Correction** :
- **Ventes/jour = annonces disparues sur 24 h sur Hadala × taille habituelle des annonces.** La taille des annonces (unités par annonce vendue) est mesurée sur Kaisinel : c'est une habitude de vendeurs (taille des piles), pas une demande.
- L'activité (annonces disparues) est désormais relevée **chaque jour pour tous les produits comparés** (≈ 110 par serveur), plus seulement ~100 items.
- À défaut de mesure sur ton serveur : extrapolation depuis Kaisinel, **signalée** (le craft passe en « à vérifier »). Sans aucune mesure : « volume inconnu ».
- Si la taille des annonces est inconnue : comptée 1 unité par annonce (minimum certain), signalée.
- Flip : seulement sur des ventes mesurées sur ton serveur.
- Nouvelle colonne détaillée « Annonces vendues/j » ; accueil : « Ventes mesurées X / Y crafts ».

**Effet (Hadala, 18/10 22h36)** :

| Craft | Annonces vendues/j | Ta part/j avant → après | Profit/j avant → après |
|---|---|---|---|
| Pièce de bois d'Asvata | 60 | 461 → 346 | 6,1 M → 4,6 M |
| Décoration en saphir | 24 | 269 → 311 | 1,1 M → 1,3 M |
| Papier d'Asvata | 10 | 366 → 309 | 1,3 M → 1,1 M |
| Élixir du vent | 38 | 309 → 199 | 1,1 M → 0,7 M |
| Potion de PV supérieure | 18 | 278 → 140 | 0,9 M → 0,45 M |
| Élixir de PV supérieur | 11 | 431 → 54 | 2,4 M → 0,3 M |

Limites restantes : une annonce retirée par son vendeur compte comme une vente (surestimation possible, surtout pendant les pics où beaucoup de vendeurs remettent en vente) ; « ta part » reste une hypothèse de 20 % des ventes, que tu n'atteins que si tu es parmi les moins chers.

Sur GitHub, ces mesures se rempliront au prochain passage **daily** (17h40), ou tout de suite avec un Run workflow `daily`.

---

# Onglet 📅 Planning — 18/10/2026 (soir)

## 🛡️ Planning safe
- Tu indiques ton **temps de jeu** (3 h par défaut, enregistré). Le site répartit tes heures de récolte sur les débouchés qui rapportent le plus **par heure** (récolte/h de « Quoi récolter », 100 par défaut × net par ressource, ajusté à ta réussite selon tes niveaux), sans dépasser ce que chaque marché absorbe par jour (ventes mesurées).
- Résultat : « Récolter X pendant Y h (≈ Z ressources) → fabriquer N × objet, en A annonces de L », gain par craft, gain total, et l'heure de mise en vente (fenêtre de 3 h la plus active).
- Exemple (3 h, 100/h, Artisanat/Alchimie de test) : Bois d'Asvata 3 h → 305 Papiers d'Asvata (1,06 M) + 95 Pièces de bois (1,26 M) = **2,3 M**.

## 🎲 Planning gamble (blanc → vert → bleu → unique)
- **Mécanique (données du jeu)** : chaque étape d'une chaîne (ex. Masse d'orichalque → d'expert → de maître) donne, si la fabrication réussit, soit l'objet normal, soit, avec le **combo**, la version **éclatante** (grade supérieur), **seule utilisable à l'étape suivante**. Un échec fait perdre les matières **et** l'objet éclatant mis dedans.
- **Combo : 25 %**, valeur des données du jeu, confirmée en jeu. Réglable dans l'onglet et dans `config.json` (`combo_rate`, `null` = données du jeu).
- Par étape : réussite selon ton niveau (🔒 si insuffisant), coût de l'essai (matières achetées + **ressources récoltées comptées à ce qu'elles rapporteraient en safe**, option), **si échec** (probabilité, perte), **si réussite sans combo** (probabilité, valeur), **si le combo procque** (probabilité, valeur, **gain du proc** = éclatant − normal), et **conseil** : vendre l'éclatant ou tenter l'étape suivante (comparaison d'espérances, calculée du haut de la chaîne vers le bas).
- Par chaîne : **espérance par essai** de l'étape 1, **jackpot** (chance de tout réussir avec combo et gain si ça arrive), nombre d'essais permis par ton stock (Mon stock). Chaînes triées par espérance ; « ⚠ prix douteux » si un objet normal est plus cher que sa version éclatante (annonce aberrante).
- Exemple (Alchimie Débutant 41) : Orbe de vérité → éclatant (370 k) → éclatant d'expert (4,4 M) → éclatant de maître (22,5 M) ; réussite 92 % / 91 % / 88 % ; échec à l'étape 3 = −6 M ; espérance par essai +299 k ; jackpot ~1 %.
- **Limites** : les objets éclatants hauts (bleu, unique) ont des ventes **non mesurées** (peu d'échanges) : leur prix habituel est fiable, mais **le temps pour les vendre est inconnu**. Les chaînes s'arrêtent au dernier palier ayant un prix sur Hadala (pas de prix pour les « Roi dragon »).

---

# Transmutation (étude) — 18/10/2026 (soir)

## Ce que disent les données du jeu
Onglet « Transmutation » du jeu = recettes de **conversion** (278 dans les données, dont 58 de « matériaux récoltables »). Pour les matériaux, c'est toujours le même schéma : **1 Od → 1 ressource de même rareté**, **100 % de réussite**, **sans coût** indiqué, résultat **lié** (invendable).

| Od utilisé | Ressources obtenues (Asmodiens) | Maîtrise demandée (données) |
|---|---|---|
| Od (commun) | Bois d'Asvata, Saphir/Diamant/Rubis bruts | « Jewelcrafting » 1 |
| | Minerai d'orichalque | Forge (Blacksmithing) 1 |
| | Azpha (1), Calendula (10), Morfa/Ohkra/Raydam (10), Conide/Pujery (20) | Alchimie |
| Od d'une grande pureté | mêmes ressources « d'une grande pureté », Azpha/Calendula fraîches | Jewelcrafting / Forge / Alchimie 30 |
| Od pur | mêmes ressources « pures » | 30 |
| Od éclatant | mêmes ressources « éclatantes » | 30 |

À vérifier en jeu :
1. **Les crafts acceptent-ils la ressource liée ?** Les recettes demandent « Bois d'Asvata » (non lié) ; la transmutation donne « Bois d'Asvata (lié) ». Les données ne permettent pas de trancher.
2. Quel métier correspond à « Jewelcrafting » (aucun craft de ce nom ; sans doute l'Artisanat) ?
3. Aucun coût ni échec : à confirmer.

## Rentabilité (Hadala, prix du 18/10 22h50, si la ressource liée est acceptée)
Valeur d'une ressource = gain moyen par ressource dans ses crafts fiables, après frais (onglet Quoi récolter), dans la limite de ce que les marchés absorbent.

**Od commun (prix habituel 5 268, actuel 4 500)** :

| Transmuté en | Gain par ressource (crafts) | Absorbé/j | Acheter un Od pour ça |
|---|---|---|---|
| **Bois d'Asvata** (→ Papier, Pièces de bois) | **7 132** | ~795 | **+1 864 par Od (+35 %)** au prix habituel, +2 632 (+58 %) au prix actuel |
| Ohkra (→ Bœuf Wellington) | 4 679 | ~57 | −588 |
| Pujery, Azpha, Saphir brut… | 2 100–2 500 | | −2 700 à −3 200 |

- **Ta propre récolte d'Od** : aujourd'hui son meilleur usage direct est le Bœuf Wellington (3 249 par Od, ~32 par jour). **Transmuté en Bois, chaque Od vaut ~7 100**, comme le Bois lui-même : récolter de l'Od devient aussi rentable que récolter du Bois (mais les deux remplissent les mêmes marchés : Papier et Pièces de bois).
- **Acheter de l'Od pour le transmuter en Bois** puis crafter est rentable (+35 % au prix habituel) — oui, ton intuition est juste : l'Od coûte moins cher que le Bois (Bois brut affiché 7 500) pour le même usage.
- **Od d'une grande pureté** (habituel 4 594) → Azpha/Calendula fraîches : à perte (−44 à −49 %). Les autres conversions « grande pureté », « pur », « éclatant » n'ont aucun craft rentable en ce moment.

Limites : les gains dépendent de la capacité des marchés (Papier d'Asvata saturé en ce moment, Pièces de bois ~350/j pour ta part) ; acheter beaucoup d'Od fera monter son prix.

## Fonctionnalité proposée
1. **Transmutation dans l'analyse** : pour chaque ressource, le site considère aussi « Od de même rareté → ressource » quand c'est plus avantageux.
   - Quoi récolter : la ligne Od affiche son meilleur usage via transmutation (ex. « Od → Bois d'Asvata → Pièce de bois : 7 100/Od ») et son vrai kinah/heure ; capacité partagée avec le Bois.
   - Achat → craft : coût d'un ingrédient = le moins cher entre la ressource et l'Od de même rareté (marqué « via Od transmuté »), avec indice de sûreté.
   - Mon stock et Planning safe : l'Od en stock est utilisé comme Bois/gemmes/minerai quand c'est plus rentable ; le plan indique « transmuter N Od en Bois ».
   - Niveau de maîtrise requis vérifié avec Mes métiers (🔒 sinon).
2. **Alerte « Od bon marché »** : quand Od × (prix) est nettement sous la valeur du Bois en Pièces de bois (marge ≥ 25 % et marché des Pièces non saturé), avec la quantité max conseillée.

## Mise à jour : transmutation intégrée
Vérifié en jeu par toi : la transmutation donne des ressources **non liées**, **gratuite**, **sans échec**. Intégrée partout :
- **Achat → craft** : pour chaque ingrédient récoltable, coût = le moins cher entre la ressource et l'Od de même rareté (ligne « Od x2 @4 898 → transmuté en Bois d'Asvata »). Résultat : **Pièce de bois d'Asvata via Od : coût 10 196, +3 483/pièce (+34 %), sûreté 🟢** — l'alerte « Achat → craft » partira. Papier via Od : +113 % mais marché saturé (🔴).
- **Quoi récolter** : l'Od est valorisé avec les usages des ressources en lesquelles il se transmute (« Papier d'Asvata (Od → Bois d'Asvata) ») : **~6 900 par Od au lieu de 3 249**.
- **Mon stock** : l'Od en stock remplace la ressource qui manque (Bois, gemmes, minerai, herbes de même rareté) ; la ligne indique « dont N Od transmuté ».
- **Planning safe** : Od et Bois alimentent les mêmes crafts : la capacité des marchés est partagée (pas de double comptage).
- Les chaînes du Planning gamble profitent aussi de l'Od à la place du minerai quand il est moins cher.
- Limite : le niveau de maîtrise des transmutations (Débutant 1 pour le commun, 30 pour les raretés supérieures selon les données) n'est pas vérifié par le site : le métier « Jewelcrafting » des données ne correspond à aucun de tes 5 métiers.

---

# Passage daily : plus rapide et plus robuste — 18/10/2026 (nuit)

**Constats** :
- Le `daily` était passé à ~35 min. Cause : **aion2.exchange met 5 à 11 s par requête** (et répond « 503 surchargé » par moments), pour ~450 requêtes (historique horaire + volumes de Kaisinel). a2-tracker répond en 0,3 s.
- Un `daily` (23h13) a **échoué** au bout de 20 min, très probablement sur une erreur réseau de cette source : une seule erreur faisait échouer tout le passage, et le site n'était pas republié.

**Changements** :
- **Étapes isolées** (hourly et daily) : une étape en erreur est notée dans le journal, les suivantes continuent, et le site est publié quand même (seule une erreur d'analyse bloque).
- **Historique horaire d'aion2.exchange : plus téléchargé** — nos relevés horaires du marché le remplacent (graphique des heures de vente calculé dessus, résultat identique : meilleur moment 21h–0h).
- **Volumes de Kaisinel** (taille des annonces vendues, évolue lentement) : rechargés seulement s'ils ont plus de 3 jours.
- **Téléchargements en parallèle** : 3 à la fois (a2-tracker), 2 pour aion2.exchange (source fragile), toujours au moins 0,35 s entre deux départs de requête. Aucun effet sur la justesse des données (mêmes réponses, écritures en base faites une par une).

**Résultat** : `daily` complet en **~6 min** (recettes 1 s, activité 5 min, serveurs 29 s, images 6 s, analyse 9 s), contre ~35 min.
