# AION HDV — outil personnel

Objectif : générer un maximum de kinah via l'hôtel des ventes d'Aion 2 (serveur suivi : Hadala, comparaison : Zemurru).

## Lancer
```powershell
.\run.ps1 help        # liste des commandes
.\run.ps1 hourly      # prix de tout le marché + analyses + alertes + annonces officielles + rapport
.\run.ps1 daily       # volumes de référence, activité, historique, comparaison serveurs, résumé
```
Rapport : ouvrir `reports\index.html` dans le navigateur (onglets, filtres, tri, bouton **MAP** sur les ressources).

Python est **portable** (`.runtime\python`) : rien n'est installé sur le système. Supprimer le dossier suffit.

## Réglages : `config.json`
- `my_server` / `watch_servers` : ids a2-tracker (2310 Hadala, 2315 Zemurru, 2318 Baba…)
- `masteries` : ta maîtrise par métier (filtre les recettes)
- `harvest_per_day` : ta récolte quotidienne, ex. `{"Bois d'Asvata": 300, "Azpha": 150}` → plan de production
- `discord_webhook_url` : URL du webhook (sinon les alertes vont dans `logs\alerts.log`)
- `discord_webhook_unique_url`, `discord_webhook_news_url` : salons dédiés (facultatifs) aux Unique bradés et aux annonces officielles
- `news` : tableaux du site officiel suivis (`update_fr` notes de version, `notice_fr` avis), mots exclus, Reddit et ses mots-clés
- `alerts.unique_ratio`, `unique_min_median`, `unique_min_samples` : seuils de l'alerte « Unique bradé »
- `market_share`, `fees`, `npc_reagent_price`, seuils `alerts`

## Tâches planifiées (à activer quand tu veux)
```powershell
.\scripts\install_tasks.ps1     # crée AION-HDV-hourly et AION-HDV-daily
```

## Sources
| Source | Utilisation |
|---|---|
| a2-tracker.com | catalogue complet FR/EN + images, recettes, prix plancher de tout le marché, mouvements d'annonces 24 h |
| aion2.exchange | unités vendues publiées par le jeu (Kaisinel, serveur de référence), historique de prix horaire |
| questlog.gg | points de récolte (noms FR) et fonds de carte |
| aion2.plaync.com | notes de version et avis officiels (API publique du tableau d'annonces) |
| reddit.com/r/aion2 | posts dont le titre contient un mot-clé (au mieux : Reddit limite souvent les serveurs) |

## Méthode
- Volume d'un craft sur ton serveur = ventes quotidiennes réelles de Kaisinel × ratio d'activité (ton serveur / Kaisinel, recalculé).
- Prix réaliste = moyenne (prix affiché, prix de vente moyen de référence) si l'affiché est plus haut.
- Profit/u = prix × (1 − 12 %) − ingrédients achetés − réactifs PNJ (400 par défaut).
- Profit/j = profit/u × ta part du marché (20 %).
- Taille des lots = unités vendues par jour ÷ annonces disparues par jour (Kaisinel). Heures de vente = annonces disparues d'une heure à l'autre, tous items confondus (heure de Paris).
- Unique bradé = prix actuel ≤ 60 % de la médiane des 7 derniers jours (au moins 12 relevés).

## Structure
```
aionhdv/        code (collect, catalog, analysis, alerts, report)
data/aion.db    base SQLite        data/icons/   images des items
data/raw/       données brutes      reports/      rapport HTML + carte
logs/           run.log, alerts.log
```

## Serveur gratuit (GitHub Actions)

Le workflow `.github/workflows/hdv.yml` tourne sur GitHub :
- toutes les heures à hh:07 UTC : relevé des prix, analyses, alertes Discord, mise à jour du site ;
- chaque jour à 15:40 UTC : volumes de référence, activité, résumé Discord.

La base est conservée dans le cache d'Actions. Au premier passage, elle part de `seed/aion.db.gz` (à régénérer avec `scripts/seed_db.py`). Une copie de secours est faite chaque jour.

Le site est publié sur GitHub Pages (branche `gh-pages`). La page principale est chiffrée par mot de passe avec StatiCrypt.

Secrets à créer dans Settings > Secrets and variables > Actions :
- `SITE_PASSWORD` (obligatoire) ;
- `DISCORD_WEBHOOK_URL` ;
- `DISCORD_WEBHOOK_UNIQUE_URL`, `DISCORD_WEBHOOK_NEWS_URL` (facultatifs : sinon tout va dans le salon principal).

Pour lancer un passage à la main : onglet Actions > HDV Aion 2 > Run workflow.

En local, le webhook se range dans `config.local.json`, qui n'est jamais versionné.

## Installer chez soi

Les secrets (mot de passe du site, webhook Discord) ne sont pas dans le dépôt : chacun met les siens.

### Son propre site automatique (GitHub, rien à installer)
1. Bouton **Fork** en haut du dépôt.
2. Dans le fork, onglet **Actions** > *I understand my workflows, go ahead and enable them* (GitHub désactive les tâches planifiées des forks).
3. Settings > Secrets and variables > Actions : créer `SITE_PASSWORD` (obligatoire) et `DISCORD_WEBHOOK_URL` (facultatif).
4. Dans `config.json`, choisir son serveur : `my_server` et `watch_servers` (ids a2-tracker : 2310 Hadala, 2315 Zemurru, 2318 Baba…).
5. Remplacer le sel de `.staticrypt.json` par une valeur à soi (`openssl rand -hex 16`), puis commit.
6. Actions > HDV Aion 2 > **Run workflow** une première fois, puis Settings > Pages : *Deploy from a branch*, `gh-pages`, `/ (root)`.

Le site est publié sur `https://<pseudo>.github.io/<nom-du-depot>/` et se met à jour tout seul ensuite.

### En local (sans site)
Python 3.10+ suffit : le code n'utilise que la bibliothèque standard.
```bash
git clone https://github.com/iNK1K/AIONTRACKER.git && cd AIONTRACKER
gunzip -c seed/aion.db.gz > data/aion.db
python3 -X utf8 -m aionhdv hourly
```
Rapport : `reports/index.html`. Sous Windows, `run.ps1` attend un Python portable dans `.runtime\python` (absent du dépôt) : avec un Python installé, lancer directement `python -X utf8 -m aionhdv hourly`.

### Ce qui est public
- Le dépôt : code, `config.json`, base de départ (prix déjà publics).
- Le site : seule `index.html` est protégée par mot de passe ; `map.html` et les images restent accessibles par leur adresse.
