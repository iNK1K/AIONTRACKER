"""Exporte la base locale compressee dans seed/aion.db.gz (point de depart du serveur GitHub Actions).

python -X utf8 scripts/seed_db.py
"""
import gzip
import shutil
import sqlite3
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
out = ROOT / "seed" / "aion.db.gz"
out.parent.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    tmp_db = Path(tmp) / "aion.db"
    src = sqlite3.connect(ROOT / "data" / "aion.db")
    dst = sqlite3.connect(tmp_db)
    src.backup(dst)  # copie coherente, WAL inclus
    dst.execute("PRAGMA journal_mode=DELETE")
    dst.execute("VACUUM")
    dst.close()
    src.close()
    with open(tmp_db, "rb") as f, gzip.open(out, "wb", compresslevel=9) as g:
        shutil.copyfileobj(f, g)
print(out, f"{out.stat().st_size / 1e6:.1f} Mo")
