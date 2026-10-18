# AION HDV — outil personnel

Objectif : générer un maximum de kinah via l'hôtel des ventes d'Aion 2 (serveur suivi : Hadala, comparaison : Zemurru).

## Lancer
```powershell
.\run.ps1 help        # liste des commandes
.\run.ps1 hourly      # prix de tout le marché + analyses + alertes + rapport
.\run.ps1 daily       # volumes de référence, activité, historique, comparaison serveurs, résumé
```
Rapport : ouvrir `reports\index.html` dans le navigateur (onglets, filtres, tri, bouton **MAP** sur les ressources).

Python est **portable** (`.runtime\python`) : rien n'est installé sur le système. Supprimer le dossier suffit.

## Réglages : `config.json`
- `my_server` / `watch_servers` : ids a2-tracker (2310 Hadala, 2315 Zemurru, 2318 Baba…)
- `masteries` : ta maîtrise par métier (filtre les recettes)
- `harvest_per_day` : ta récolte quotidienne, ex. `{"Bois d'Asvata": 300, "Azpha": 150}` → plan de production
- `discord_webhook_url` : URL du webhook (sinon les alertes vont dans `logs\alerts.log`)
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

## Méthode
- Volume d'un craft sur ton serveur = ventes quotidiennes réelles de Kaisinel × ratio d'activité (ton serveur / Kaisinel, recalculé).
- Prix réaliste = moyenne (prix affiché, prix de vente moyen de référence) si l'affiché est plus haut.
- Profit/u = prix × (1 − 12 %) − ingrédients achetés − réactifs PNJ (400 par défaut).
- Profit/j = profit/u × ta part du marché (20 %).

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
- `DISCORD_WEBHOOK_URL` ;
- `SITE_PASSWORD`.

Pour lancer un passage à la main : onglet Actions > HDV Aion 2 > Run workflow.

En local, le webhook se range dans `config.local.json`, qui n'est jamais versionné.
