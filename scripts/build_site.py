"""Assemble le site statique publie (site/) a partir de reports/ et des images de data/.

python -X utf8 scripts/build_site.py
Le chiffrement par mot de passe (StatiCrypt) est fait ensuite par le workflow GitHub.
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

if SITE.exists():
    shutil.rmtree(SITE)
(SITE / "data").mkdir(parents=True)
for f in ("index.html", "map.html", "map_data.js", "prices.js"):
    text = (ROOT / "reports" / f).read_text(encoding="utf-8")
    # les pages sont servies depuis la racine du site : ../data/ -> data/
    (SITE / f).write_text(text.replace("../data/", "data/"), encoding="utf-8")
for d in ("icons", "maps"):
    if (ROOT / "data" / d).exists():
        shutil.copytree(ROOT / "data" / d, SITE / "data" / d)
(SITE / ".nojekyll").write_text("", encoding="utf-8")
print("site :", sum(1 for _ in SITE.rglob("*")), "fichiers")
