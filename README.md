# AION HDV — outil personnel

Objectif : générer un maximum de kinah via l'hôtel des ventes d'Aion 2 (serveur suivi : Zemurru, seul serveur relevé).

## Lancer
```powershell
.\run.ps1 help        # liste des commandes
.\run.ps1 hourly      # prix de tout le marché + analyses + alertes + annonces officielles + rapport
.\run.ps1 daily       # prix, activité, purge de la base, résumé
```
Rapport : ouvrir `reports\index.html` dans le navigateur (onglets : 💬 Assistant, Aujourd’hui, Opportunités, Mes ventes, Ravitaillement, le reste dans 🧰 Outils ; filtres, tri, bouton **MAP** sur les ressources, bouton **📈** pour la courbe de prix, clic sur un nom pour le copier).

Onglet **💬 Assistant** (ouvert par défaut) : un chat façon ChatGPT pour toutes les questions sur Aion 2 (loot, donjons, crafts, builds, récolte, prix). Claude (Opus 5.5) cherche sur le web et lit les pages utiles, et consulte le catalogue du tracker (`assist.js` : objets, prix du serveur, recettes, zones de récolte ; données du jeu et prix publics, rien de personnel, hors de la page chiffrée, chargé à l’ouverture du chat). L’appel à l’API Anthropic part du navigateur : il faut une **clé API** (`sk-ant-api…`, console.anthropic.com, avec une limite de dépense mensuelle et la recherche web activée), gardée dans le navigateur comme le jeton GitHub du journal. Un jeton d’abonnement Claude Pro/Max (`sk-ant-oat…`) ne marche pas ici. Compter environ 0,10 à 0,40 $ par question avec recherche web ; le pied du chat affiche le total dépensé depuis ce navigateur. Code : `aionhdv/report/assistant.py` (onglet et catalogue), partie « assistant » de `aionhdv/site.js`.

**Assistant avec son abonnement Claude (sans clé API)** : lancer `py scriptsssistant_local.py` sur son PC (Claude Code installé et connecté) et laisser la fenêtre ouverte, puis cliquer « 💻 Mon abonnement Claude » en bas du chat. Le chat passe alors par Claude Code de ce PC (abonnement de la personne connectée, rien à payer en plus). Le pont n'écoute que 127.0.0.1, ne répond qu'aux pages du site, fait tourner Claude Code en lecture seule (recherche web, lecture de pages, catalogue) dans `.runtime/assistant/`, et relit le catalogue publié (`assist.js`) toutes les 30 min. Chrome peut demander une fois l'autorisation d'accéder aux appareils du réseau local : accepter.

Onglet **Mon stock** : coller une capture de la réserve (Ctrl + V) remplit le stock automatiquement (reconnaissance des icônes et des quantités dans le navigateur, `aionhdv/scan.js`).

Onglet **Mes métiers** : niveaux de métier enregistrés dans le navigateur ; les crafts impossibles sont grisés partout et le profit tient compte du taux de réussite du jeu (tables extraites du client, mises à jour par le passage daily).

Onglet **Mes ventes** : journal des annonces (`journal.json`) — un clic quand tu postes, vends (tout ou partie), relistes ou retires, ou une capture (fenêtre des annonces ou historique des ventes). Chaque annonce en cours a un conseil : ✅ garder, 🔁 relister à X (taxe perdue et gain restant comptés), ⏳ attendre (le plus bas est anormalement bas ou sous ton seuil), ↩ retirer (le prix habituel est passé sous ton seuil : libère l’annonce). Bilan réel : kinah reçus, taxe perdue en relistes et retraits, bénéfice ; comparaison avec les estimations de l’outil. Le site enregistre le journal sur GitHub, sur la branche `journal` (jamais sur `main`), avec un jeton à droits limités (gardé dans le navigateur) ; le workflow et `run.ps1` en prennent une copie avant chaque passage.

Onglet **🎯 Opportunités** : récolte (ressources blanches), achat → craft et flip dans une seule liste ; une opportunité occupe une annonce (relistée à chaque vente). La page garde les meilleures selon les annonces libres (`max_listings` moins mes annonces en cours du journal), les kinah disponibles et le temps de récolte saisis.

Onglet **🌲 Récolte** : une section par grade. Seules les ressources blanches se récoltent sur les points (récolte/heure, kinah/heure) ; vertes, bleues et éclatantes sont des procs, non planifiés : la page dit seulement quoi en faire. Crafts triés par profit, avec le prix de chaque ressource. « Mes procs de récolte » : je note mes sessions (blancs récoltés, procs obtenus) pour mesurer mes taux de proc et ce qu’ils rapportent en plus.

**Précision des alertes** (bas de l'onglet Opportunités, et résumé du dimanche) : chaque opportunité alertable (feu vert, pic, Unique bradé, flip à saisir) est notée puis jugée une fois sa fenêtre de vente passée (48 h, 6 h pour un pic) : prix réel = médiane du prix plancher sur la fenêtre, tenue = net réel > 0 après taxe.

Alerte Discord **données périmées** : aucun prix reçu depuis 3 h (source en panne), puis rappel toutes les 12 h. Le site affiche aussi un bandeau rouge si les prix ont plus de 3 h ou si la page n'a pas été régénérée depuis 2 h.

Alerte Discord **flip** : dès qu’un item passe sous son prix d’achat conseillé (pas au feu rouge), une fois par item toutes les 6 h.

Onglet **Ravitaillement** : coller une capture de la fenêtre de ravitaillement → objets reconnus ; un tableau des objets demandés du jour trié par gain à les crafter pour les revendre ; la lecture distingue l’objet normal de sa version éclatante par la couleur de qualité du fond de la case (même icône) : l’objet normal s’obtient sans combo (combo montré à part), l’éclatant seulement par combo de l’objet de base (coût = crafts pour un combo − objets normaux revendus) (prix de vente modifiable, prérempli avec la moins chère des annonces − 1 ; échecs et combo comptés ; ingrédient éclatant crafté par sa chaîne ou acheté), détail repliable, bouton 📦 Poster vers Mes ventes.

Tests des calculs : `python -m unittest discover tests`.

Mode test : ajouter `--dry-run` (ex. `python -m aionhdv hourly --dry-run`) pour ne rien envoyer sur Discord.

Python est **portable** (`.runtime\python`) : rien n'est installé sur le système. Supprimer le dossier suffit.

## Réglages : `config.json`
- `my_server` / `watch_servers` : ids a2-tracker (2315 Zemurru, 2310 Hadala, 2318 Baba…)
- `masteries` : ta maîtrise par métier (filtre les recettes)
- `journal.json` : mes annonces et mes ventes (rempli depuis l’onglet Mes ventes, branche `journal`, ne pas modifier à la main) → alertes « Tu es battu », sous le seuil, etc.
- `github_repo` : dépôt où le site enregistre le journal
- `alerts.hourly` / `alerts.daily` : rapport Discord horaire (bonnes opportunités au feu vert, seulement s'il y en a de nouvelles) et résumé quotidien détaillé (+ annonces NCSOFT pas encore postées). Jamais d'alerte sur tes annonces (salon partagé)
- `alerts.flip_min_margin`, `flip_min_samples`, `flip_min_profit_day` : seuils de l'onglet et de l'alerte Flip
- `harvest_per_day` : ta récolte quotidienne, ex. `{"Bois d'Asvata": 300, "Azpha": 150}` → plan de production
- `discord_webhook_url` : URL du webhook (sinon les alertes vont dans `logs\alerts.log`)
- `discord_webhook_unique_url`, `discord_webhook_news_url` : salons dédiés (facultatifs) aux Unique bradés et aux annonces officielles
- `news` : tableaux du site officiel suivis (`update_fr` notes de version, `notice_fr` avis), mots exclus, Reddit et ses mots-clés
- `alerts.unique_ratio`, `unique_min_median`, `unique_min_samples` : seuils de l'alerte « Unique bradé »
- `market_share`, `fees`, `npc_reagent_price`, seuils `alerts`
- `brut_vendable_depuis` : date de la levée de la restriction sur le brut (prix et ventes du brut d'avant ignorés)

## Tâches planifiées (à activer quand tu veux)
```powershell
.\scripts\install_tasks.ps1     # crée AION-HDV-hourly et AION-HDV-daily
```

## Sources
| Source | Utilisation |
|---|---|
| a2-tracker.com | catalogue complet FR/EN + images, recettes, prix plancher de tout le marché, mouvements d'annonces 24 h |
| aion2.exchange | complément des prix (items qu'a2-tracker ne voit pas), historique de prix horaire |
| questlog.gg | points de récolte (noms FR) et fonds de carte |
| aion2.plaync.com | notes de version et avis officiels (API publique du tableau d'annonces) |
| reddit.com/r/aion2 | posts dont le titre contient un mot-clé (au mieux : Reddit limite souvent les serveurs) |

## Méthode
- Ventes d'un item sur ton serveur = annonces disparues sur 24 h × taille estimée des annonces (le jeu ne publie pas les quantités pour Zemurru) : mesure de Kaisinel figée le 22/10 pour 65 objets (`aionhdv/lots_kaisinel.json`, objets élyséens et mesures trop maigres écartés), sinon 1 pour un objet non empilable (pile max 0 ou 1) ou un équipement, sinon `lots` dans config.json (récolte 200 / 50 / 10 / 3 selon le grade blanc, vert, bleu, éclatant ; matériau 20 ; consommable 20). Modifiable par objet dans l'onglet Opportunités (gardé dans le navigateur). Pour contrôler ces tailles sur Zemurru : l'onglet Mes ventes met côte à côte l'achat moyen de tes vraies ventes et la taille estimée (colonne « Annonce estimée »).
- Délai de vente (Opportunités) : devant = 1 ÷ annonces vendues par heure (tu postes au prix le plus bas) ; à la file = annonces en vente ÷ annonces vendues par heure.
- Prix réaliste = moyenne (prix affiché, prix habituel des ventes observées sur ton serveur) si l'affiché est plus haut.
- Profit/u = prix × (1 − 10 %) − ingrédients achetés − réactifs PNJ (400 par défaut).
- Brut vendable depuis la MaJ du 21/10/2026 : une ressource récoltée vaut au moins sa vente brute (prix réaliste − 10 %). La vente du brut est un usage comme un craft (Quoi récolter, Planning, Mon stock) ; « vs brut/u » = gain d'un craft face à la vente brute des mêmes ressources, un craft qui fait moins bien n'est plus conseillé. Prix et ventes du brut d'avant `brut_vendable_depuis` sont ignorés (autre régime de marché).
- Profit/j = profit/u × ta part du marché : 20 % supposés (`market_share`), remplacés automatiquement par ta part réelle (journal : médiane des objets vendus au moins 3 fois, bornée 2-50 %) dès que 3 objets la mesurent.
- Heures de vente = annonces disparues d'une heure à l'autre, tous items confondus (heure de Paris).
- Unique bradé = prix actuel ≤ 60 % de la médiane des 7 derniers jours (au moins 12 relevés).
- Flip = acheter au 1er quartile des prix plancher sur 3 j, revendre au prix médian, marge ≥ 10 % après frais ; items sans volume, prix en tendance et prix aberrants écartés (prix actuel hors de 50 % à 200 % de la médiane : erreur de saisie d'un vendeur ou relevé faux ; ou 1er quartile sous 50 % de la médiane : prix erratique ; `alerts.flip_max_ecart`) (brut compris, sur son historique depuis le 21/10).
- Notes de version : items cités surveillés 48 h, alerte si le prix bouge de ±20 %.

## Structure
```
aionhdv/        code (collect, catalog, analysis, alerts ; report/ : la page, un module par onglet)
data/aion.db    base SQLite        data/icons/   images des items
data/raw/       données brutes      reports/      rapport HTML + carte
logs/           run.log, alerts.log
```

## Serveur gratuit (GitHub Actions)

Le workflow `.github/workflows/hdv.yml` tourne sur GitHub. Il est déclenché par **cron-job.org** (les créneaux planifiés de GitHub prenaient des heures de retard) :
- tâche « HDV hourly », toutes les heures : relevé des prix, analyses, alertes Discord, annonces officielles, mise à jour du site ;
- tâche « HDV daily », chaque jour à 17h40 : recettes, prix, activité, purge de la base, résumé Discord (+ tendances le dimanche), sauvegarde de la base.

Chaque tâche appelle `POST https://api.github.com/repos/<pseudo>/<depot>/actions/workflows/hdv.yml/dispatches` avec les en-têtes `Accept: application/vnd.github+json`, `Authorization: Bearer <token>` (token fine-grained, permission Actions : lecture et écriture) et `X-GitHub-Api-Version: 2022-11-28`, et le corps `{"ref":"main","inputs":{"job":"hourly"}}` (ou `daily`).

La base est conservée dans le cache d'Actions. Un passage horaire fait le daily si celui-ci n'a pas tourné depuis 26 h. Chaque passage daily la sauvegarde aussi dans la release GitHub `db-backup` : si le cache est vidé, elle est restaurée depuis cette sauvegarde, et à défaut depuis `seed/aion.db.gz` (à régénérer avec `scripts/seed_db.py`).

Le site est publié sur GitHub Pages (branche `gh-pages`). La page principale est chiffrée par mot de passe avec StatiCrypt.

Secrets à créer dans Settings > Secrets and variables > Actions :
- `SITE_PASSWORD` (obligatoire) ;
- `DISCORD_WEBHOOK_URL` ;
- `DISCORD_WEBHOOK_UNIQUE_URL`, `DISCORD_WEBHOOK_NEWS_URL` (facultatifs : sinon tout va dans le salon principal).

Pour lancer un passage à la main : onglet Actions > HDV Aion 2 > Run workflow (ou « Tester l'exécution » sur cron-job.org).

En local, le webhook se range dans `config.local.json`, qui n'est jamais versionné.

## Installer chez soi

Les secrets (mot de passe du site, webhook Discord) ne sont pas dans le dépôt : chacun met les siens.

### Son propre site automatique (GitHub, rien à installer)
1. Bouton **Fork** en haut du dépôt.
2. Dans le fork, onglet **Actions** > *I understand my workflows, go ahead and enable them* (GitHub désactive les tâches planifiées des forks).
3. Settings > Secrets and variables > Actions : créer `SITE_PASSWORD` (obligatoire) et `DISCORD_WEBHOOK_URL` (facultatif).
4. Dans `config.json`, choisir son serveur : `my_server` et `watch_servers` (ids a2-tracker : 2315 Zemurru, 2310 Hadala, 2318 Baba…).
5. Remplacer le sel de `.staticrypt.json` par une valeur à soi (`openssl rand -hex 16`), puis commit.
6. Actions > HDV Aion 2 > **Run workflow** une première fois, puis Settings > Pages : *Deploy from a branch*, `gh-pages`, `/ (root)`.
7. Créer les deux tâches cron-job.org (voir « Serveur gratuit » ci-dessus) avec son propre token.

Le site est publié sur `https://<pseudo>.github.io/<nom-du-depot>/` et se met à jour tout seul ensuite.

### En local (sans site)
Python 3.10+ suffit : le code n'utilise que la bibliothèque standard.
```bash
git clone https://github.com/iNK1K/AIONTRACKER.git && cd AIONTRACKER
gunzip -c seed/aion.db.gz > data/aion.db
git fetch origin journal && git show FETCH_HEAD:journal.json > journal.json   # journal des ventes (facultatif)
python3 -X utf8 -m aionhdv hourly
```
Rapport : `reports/index.html`. Sous Windows, `run.ps1` attend un Python portable dans `.runtime\python` (absent du dépôt) : avec un Python installé, lancer directement `python -X utf8 -m aionhdv hourly`.

### Ce qui est public
- Le dépôt : code, `config.json`, base de départ (prix déjà publics).
- Le site : seule `index.html` est protégée par mot de passe ; `map.html`, les images et les données de prix (`prices.js`, `data.js` : rien de personnel) restent accessibles par leur adresse. Le journal des ventes est sur la branche `journal` du dépôt public.
