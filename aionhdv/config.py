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
    if os.environ.get("DISCORD_WEBHOOK_URL"):
        cfg["discord_webhook_url"] = os.environ["DISCORD_WEBHOOK_URL"]
    return cfg
