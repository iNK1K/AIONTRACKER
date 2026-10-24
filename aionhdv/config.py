import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"
REPORT_DIR = ROOT / "reports"
DB_PATH = DATA_DIR / "aion.db"
LISTING_FEE = 0.02      # frais d'enregistrement par defaut (config.json : listing_fee)


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
    # cout d'une vente pour les calculs de profit : taxe retenue a la vente + frais d'enregistrement (perdus)
    if "sale_tax" in cfg:
        cfg["fees"] = round(cfg["sale_tax"] + cfg.get("listing_fee", LISTING_FEE), 6)
    journal = ROOT / "journal.json"
    if journal.exists():
        # journal des ventes (rempli depuis le site, onglet Mes ventes, branche journal)
        with open(journal, encoding="utf-8-sig") as f:      # -sig : copie faite par PowerShell (run.ps1)
            cfg["journal"] = json.load(f)
        cfg["my_listings"], cfg["my_sales"] = from_journal(cfg["journal"], cfg.get("listing_fee", LISTING_FEE))
    # depot GitHub ou le site enregistre le journal (connu dans GitHub Actions)
    cfg["_github_repo"] = os.environ.get("GITHUB_REPOSITORY") or cfg.get("github_repo")
    for key in ("discord_webhook_url", "discord_webhook_unique_url", "discord_webhook_news_url"):
        if os.environ.get(key.upper()):
            cfg[key] = os.environ[key.upper()]
    return cfg


def lot_state(lot, fee=LISTING_FEE):
    """Etat d'une annonce du journal d'apres ses evenements (poste, reliste, corrige, vendu, retire) : meme calcul que le site
    (site.js, jState). frais = frais d'enregistrement de chaque mise en vente (poste, reliste) : fee x prix total, arrondi a
    l'inferieur, perdus meme si l'annonce se vend (la taxe de vente est retenue sur le reglement : champ recu) ; retirer
    ne coute rien de plus."""
    ev = sorted((e for e in lot.get("ev") or [] if not e.get("x")), key=lambda e: e.get("t") or "")   # x = annule
    prix, cout, src, sold, retired, frais, recu, relistes = lot.get("prix"), lot.get("cout"), lot.get("src"), 0, 0, 0, 0, 0
    qte, mise_q, mise_f = lot["qte"], 0, 0                  # quantite et frais de la derniere mise en vente
    for e in ev:
        if e["type"] in ("poste", "reliste"):
            prix, mise_q = e.get("prix", prix), e.get("qte", 0)
            mise_f = math.floor(fee * prix * mise_q)
            frais += mise_f
            relistes += e["type"] == "reliste"
        elif e["type"] == "corrige":                        # erreur de saisie : les frais suivent la mise en vente corrigee
            mise_q += (e.get("qte") or qte) - qte
            prix, qte = e["prix"], e.get("qte") or qte
            f = math.floor(fee * prix * max(0, mise_q))
            frais, mise_f = frais + f - mise_f, f
        elif e["type"] == "vendu":
            sold += e["qte"]
            recu += e.get("recu") or 0
        elif e["type"] == "retire":
            retired += e["qte"]
        elif e["type"] == "cout":
            cout = e["cout"]
        elif e["type"] == "src":                            # origine : recolte, achat (-> craft) ou flip
            src = e["src"]
    return dict(prix=prix, cout=cout, src=src, vendus=sold, retires=retired, reste=max(0, qte - sold - retired), frais=frais,
                recu=recu, relistes=relistes)


def from_journal(journal, fee=LISTING_FEE):
    """Journal -> (mes annonces en cours par objet, mes ventes) : le format qu'utilisent l'analyse et les alertes."""
    listings, sales = {}, []
    for lot in journal.get("lots") or []:
        if lot.get("del"):
            continue
        st = lot_state(lot, fee)
        if st["reste"] > 0:
            a = listings.setdefault(lot["objet"], {"prix": st["prix"], "quantite": 0, "_c": 0, "_q": 0})
            a["prix"] = min(a["prix"], st["prix"])           # mon annonce la moins chere face au marche
            a["quantite"] += st["reste"]
            if st["cout"] is not None:
                a["_c"] += st["cout"] * st["reste"]
                a["_q"] += st["reste"]
        for e in lot.get("ev") or []:
            if e["type"] == "vendu" and e.get("t") and not e.get("x"):
                sales.append(dict(date=e["t"], objet=lot["objet"], quantite=e["qte"], prix=e["prix"] * e["qte"],
                                  recu=e.get("recu"), cout=st["cout"], origine=st["src"]))
    for a in listings.values():
        if a["_q"]:
            a["cout"] = round(a["_c"] / a["_q"])
        del a["_c"], a["_q"]
    sales.sort(key=lambda v: v["date"], reverse=True)
    return listings, sales
