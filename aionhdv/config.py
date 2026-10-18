import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"
REPORT_DIR = ROOT / "reports"
DB_PATH = DATA_DIR / "aion.db"


def load_config():
    """config.json (partage, versionne) + config.local.json (secrets locaux, jamais versionne)
    + variables d'environnement (secrets GitHub Actions)."""
    path = ROOT / "config.json"
    if not path.exists():
        path = ROOT / "config.example.json"
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    local = ROOT / "config.local.json"
    if local.exists():
        with open(local, encoding="utf-8") as f:
            cfg.update(json.load(f))
    listings = ROOT / "mes_annonces.json"
    if listings.exists():
        with open(listings, encoding="utf-8") as f:
            data = json.load(f)
        cfg["my_listings"] = data.get("annonces") or {}
        cfg["_my_listings_help"] = data.get("_", "")
    # lien vers l'editeur GitHub du fichier (le depot est connu dans GitHub Actions)
    repo = os.environ.get("GITHUB_REPOSITORY") or cfg.get("github_repo")
    if repo:
        cfg["_github_edit_url"] = f"https://github.com/{repo}/edit/main/mes_annonces.json"
    for key in ("discord_webhook_url", "discord_webhook_unique_url", "discord_webhook_news_url"):
        if os.environ.get(key.upper()):
            cfg[key] = os.environ[key.upper()]
    return cfg
