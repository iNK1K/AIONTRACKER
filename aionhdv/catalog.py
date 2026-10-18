"""Catalogue complet des items (noms FR/EN, images), instantane de tout le marche, points de recolte questlog."""
import json
import re
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .collect import upsert_item, num, now_iso
from .config import DATA_DIR, load_config
from .net import get_json, get_text
from .sources import a2tracker

ICON_DIR = DATA_DIR / "icons"
RAW_DIR = DATA_DIR / "raw"
A2 = "https://a2-tracker.com"
QL_MAP_JS = None  # decouvert dynamiquement depuis la page de la carte
QL_MARKERS = "https://questlog.gg/aion-2/api/trpc/map.getMarkers?input=%7B%22language%22%3A%22fr%22%7D"
QL_IMAGE = "https://cdn.questlog.gg/aion-2/map/v3/{key}.webp"
QL_TILES = "https://cdn.questlog.gg/aion-2/assets/Game/UI/Map/WorldMap/{key}/Res/{key}_{{x}}_{{y}}.webp"
QL_IMAGE_WORLDS = {"World_L_Starter", "World_L_A", "World_L_B", "World_D_Starter", "World_D_A", "World_D_B",
                   "Abyss_Reshanta_A"}


TIER_RE = re.compile(r"\s+(d'une grande pureté|pure?s?|éclatante?s?|fraîche|frais)$")


def node_name(name):
    """Les qualites superieures sortent des memes points de recolte que la ressource de base."""
    return TIER_RE.sub("", name or "")


# ---------------------------------------------------------------- catalogue

def _pages(server, locale, priced, progress=None):
    page, pages = 1, 1
    while page <= pages:
        d = a2tracker.database_page(server, page, limit=100, locale=locale) if priced == "current" else \
            get_json(f"{A2}/api.database.ashx?page={page}&limit=100&server={server}&locale={locale}"
                     f"&sort=name&dir=asc&priced=all")
        if not d:
            break
        pages = d.get("pages") or 1
        for it in d.get("items", []):
            yield it
        if progress:
            progress(page, pages)
        page += 1


def sync_catalog(con, server="2310"):
    """Tous les items du jeu (9 000+), noms francais et anglais, image, categorie."""
    n = 0
    for it in _pages(server, "fr-FR", "all"):
        loc = (it.get("localized") or {}).get("name")
        flags = []
        if it.get("namePlaceholder") or it.get("placeholder"):
            flags.append("provisoire")
        upsert_item(con, int(it["itemId"]), name=loc or it.get("name"), item_key=it.get("itemKey"),
                    grade=it.get("grade"), category=it.get("category"), sub_category=it.get("subCategory"),
                    auction_category=it.get("auctionCategory"), level=it.get("levelReq"),
                    icon_url=(A2 + it["icon"]) if it.get("icon") else None,
                    name_check=",".join(flags) or None)
        n += 1
        if n % 500 == 0:
            con.commit()
    con.commit()
    m = 0
    for it in _pages(server, "en-US", "all"):
        con.execute("UPDATE items SET name_en = ? WHERE id = ?",
                    ((it.get("localized") or {}).get("name") or it.get("name"), int(it["itemId"])))
        m += 1
    con.commit()
    return n, m


def snapshot_market(con, server):
    """Prix plancher et annonces de TOUS les items en vente sur un serveur (base de donnees a2-tracker)."""
    n = 0
    fallback_ts = now_iso()[:19]
    for it in _pages(server, "fr-FR", "current"):
        price = num(it.get("price"))
        if price is None or it.get("priceStatus") != "current":
            continue
        obs = it.get("priceObservedAt")
        ts = datetime.fromisoformat(obs).astimezone(timezone.utc).isoformat()[:19] if obs else fallback_ts
        con.execute("INSERT OR REPLACE INTO quotes VALUES (?,?,?,?,?)",
                    (str(server), int(it["itemId"]), ts, price, int(num(it.get("listings")) or 0)))
        con.execute("UPDATE items SET on_market = 1 WHERE id = ?", (int(it["itemId"]),))
        n += 1
    con.commit()
    return n


def snapshot_market_ax(con, server):
    """Complete l'instantane avec aion2.exchange (il voit plus d'items en vente qu'a2-tracker)."""
    from .sources import aion2exchange
    r = con.execute("SELECT ax_id FROM servers WHERE id = ?", (str(server),)).fetchone()
    if not r or not r["ax_id"]:
        return 0, 0
    ax = r["ax_id"]
    added = new_items = 0
    offset, total = 0, 1
    while offset < total:
        d = aion2exchange.items(ax, offset, 200)
        if not d:
            break
        total = d.get("total") or 0
        for it in d.get("items", []):
            iid = int(it["item_key"])
            if not con.execute("SELECT 1 FROM items WHERE id = ?", (iid,)).fetchone():
                upsert_item(con, iid, name=it.get("name"), name_en=it.get("name"), name_check="nom FR inconnu",
                            category=(it.get("category") or {}).get("section_name"),
                            auction_category=(it.get("category") or {}).get("name"))
                new_items += 1
            if not it.get("listed") or it.get("price") is None or not it.get("captured_at"):
                continue
            con.execute("UPDATE items SET on_market = 1 WHERE id = ?", (iid,))
            ts = it["captured_at"][:19]
            floor = (datetime.fromisoformat(ts) - timedelta(minutes=90)).isoformat()[:19]
            recent = con.execute("SELECT 1 FROM quotes WHERE server=? AND item_id=? AND ts >= ?",
                                 (str(server), iid, floor)).fetchone()
            if recent:
                continue
            con.execute("INSERT OR REPLACE INTO quotes VALUES (?,?,?,?,?)",
                        (str(server), iid, ts, float(it["price"]), int(it.get("listings") or 0)))
            added += 1
        offset += 200
    con.commit()
    return added, new_items


def check_names(con):
    """Controle des noms francais : provisoire, identique a l'anglais, absent de questlog (ressources)."""
    ql_names = {r["name"] for r in con.execute("SELECT DISTINCT name FROM gather_nodes")}
    stats = {}
    for r in con.execute("SELECT id, name, name_en, is_gather, bound, base_name, name_check FROM items").fetchall():
        flags = set(filter(None, (r["name_check"] or "").split(",")))
        flags.discard("ok")
        flags.discard("identique EN")
        flags.discard("absent questlog")
        if r["name"] and r["name_en"] and r["name"] == r["name_en"] and re.search(r"[A-Za-z]{4}", r["name"]) \
                and r["base_name"] not in ql_names:
            flags.add("identique EN")
        if r["is_gather"] and not r["bound"] and ql_names and node_name(r["base_name"]) not in ql_names:
            flags.add("absent questlog")
        val = ",".join(sorted(flags)) or "ok"
        stats[val] = stats.get(val, 0) + 1
        con.execute("UPDATE items SET name_check = ? WHERE id = ?", (val, r["id"]))
    con.commit()
    return stats


def download_icons(con, only_market=True):
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    cfg = load_config()["http"]
    q = "SELECT id, icon_url FROM items WHERE icon_url IS NOT NULL AND (icon_file IS NULL OR icon_file = '')"
    if only_market:
        q += " AND (on_market = 1 OR id IN (SELECT item_id FROM recipes) OR id IN (SELECT item_id FROM recipe_ingredients))"
    rows = con.execute(q).fetchall()
    done = 0
    cache = {}
    for r in rows:
        url = r["icon_url"]
        fname = url.rsplit("/", 1)[-1]
        path = ICON_DIR / fname
        if not path.exists() and url not in cache:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": cfg["user_agent"]})
                with urllib.request.urlopen(req, timeout=cfg["timeout_seconds"]) as resp:
                    path.write_bytes(resp.read())
                time.sleep(0.12)
            except Exception:
                cache[url] = False
                continue
        cache[url] = True
        con.execute("UPDATE items SET icon_file = ? WHERE id = ?", (f"icons/{fname}", r["id"]))
        done += 1
        if done % 200 == 0:
            con.commit()
    con.commit()
    return done, len(rows)


# ---------------------------------------------------------------- carte questlog

def _num(s):
    return float(s)


def sync_map(con):
    """Mondes de la carte + points de recolte (noms francais) depuis questlog.gg."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    page = get_text("https://questlog.gg/aion-2/fr/map")
    worlds = {}
    for js_url in sorted(set(re.findall(r"https://cdn\.questlog\.gg/_static/aion-2/_nuxt/[\w-]+\.js", page))):
        try:
            js = get_text(js_url)
        except Exception:
            continue
        if "worlds:Object.fromEntries" not in js:
            # la config peut etre dans un chunk importe : on suit les imports du point d'entree
            for sub in set(re.findall(r'"\./([\w-]+\.js)"', js)):
                try:
                    sj = get_text("https://cdn.questlog.gg/_static/aion-2/_nuxt/" + sub)
                except Exception:
                    continue
                if "worlds:Object.fromEntries" in sj:
                    js = sj
                    break
        if "worlds:Object.fromEntries" in js:
            pat = re.compile(r"([\d.e]+):\{name:`([^`]+)`,group:`([^`]+)`,key:`([^`]+)`,sectors:\[([^\]]+)\]\}")
            for wid, name, grp, key, sectors in pat.findall(js):
                x0, y0, nx, ny, size = [_num(v) for v in sectors.split(",")]
                worlds[str(int(float(wid)))] = dict(name=name, grp=grp, key=key, x0=x0, y0=y0, nx=int(nx), ny=int(ny),
                                                    size=size)
            break
    map_dir = DATA_DIR / "maps"
    map_dir.mkdir(parents=True, exist_ok=True)
    for wid, w in worlds.items():
        layer = "image" if w["key"] in QL_IMAGE_WORLDS else "tile"
        url = QL_IMAGE.format(key=w["key"]) if layer == "image" else QL_TILES.format(key=w["key"])
        dest = map_dir / f"{w['key']}.webp"
        if layer == "image" and not dest.exists():
            # copie locale du fond de carte : l'affichage direct depuis le CDN questlog ne fonctionne pas
            try:
                req = urllib.request.Request(url, headers={"User-Agent": load_config()["http"]["user_agent"],
                                                           "Referer": "https://questlog.gg/"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    dest.write_bytes(resp.read())
            except Exception:
                pass
        con.execute("INSERT OR REPLACE INTO map_worlds VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (wid, w["name"], w["grp"], w["key"], w["x0"], w["y0"], w["nx"], w["ny"], w["size"], layer, url))
    raw = get_text(QL_MARKERS)
    (RAW_DIR / "questlog_markers_fr.json").write_text(raw, encoding="utf-8")
    markers = json.loads(raw)["result"]["data"]
    by_name = {}
    for r in con.execute("SELECT id, base_name FROM items WHERE is_gather = 1 AND bound = 0"):
        by_name.setdefault(r["base_name"], r["id"])
    con.execute("DELETE FROM gather_nodes")
    n = 0
    for mk in markers:
        if mk.get("mapType") != "gatherable":
            continue
        w = worlds.get(str(mk["mapWorldId"]))
        gx, gy = mk["coordinates"][0][0], mk["coordinates"][0][1]
        px = py = None
        if w:
            k = 1024.0 / w["size"]
            px, py = (gx - w["x0"]) * k, -(gy + w["y0"]) * k
        con.execute("INSERT OR REPLACE INTO gather_nodes VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (mk["id"], mk["name"], by_name.get(mk["name"]), str(mk["mapWorldId"]), mk.get("mapCategory"),
                     gx, gy, px, py, mk.get("icon"), mk.get("dbId")))
        n += 1
    con.commit()
    return len(worlds), n
