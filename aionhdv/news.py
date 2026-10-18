"""Annonces officielles AION 2 (notes de version, avis du site officiel) et Reddit : chaque nouvelle annonce
part une seule fois sur Discord. Au premier passage reussi d'une source, ses annonces existantes sont notees
sans etre envoyees."""
import html
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from .alerts import _once
from .net import get_json, get_text

COMMUNITY = "https://api-global-community.plaync.com/aion2_global/board/{board}/article"
ATOM = "{http://www.w3.org/2005/Atom}"
LABELS = {"update": "🛠️ **Notes de version**", "notice": "📢 **Annonce officielle**"}


def official(board, lang):
    """Articles d'un tableau du site officiel (ex. update_fr, notice_fr), les plus recents d'abord."""
    data = get_json(COMMUNITY.format(board=board)) or {}
    label = LABELS.get(board.split("_")[0], "📢 **AION 2**")
    for a in data.get("contentList", []):
        pattern = (a.get("categoryBoard") or {}).get("boardUrlPattern") or ""
        url = pattern.replace("{lang}-{country}", lang).replace("{articleId}", a["id"])
        yield dict(key=f"{board}|{a['id']}", label=label, title=a["title"].strip(), url=url, board=board,
                   article=a["id"], posted=((a.get("timestamps") or {}).get("postedAt") or "")[:19])


def article_text(board, article_id):
    """Texte brut d'un article du site officiel."""
    d = get_json(f"{COMMUNITY.format(board=board)}/{article_id}") or {}
    body = (((d.get("article") or {}).get("content") or {}).get("content")) or ""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body)))


def watch_items(con, cfg, it):
    """Notes de version : items echangeables cites dans le texte, a surveiller 48 h (prix de depart = prix actuel)."""
    text = article_text(it["board"], it["article"]).lower()
    server = str(cfg["my_server"])
    found = []
    for r in con.execute("SELECT id, base_name FROM items WHERE bound = 0 AND on_market = 1 AND length(base_name) >= 5"):
        if not re.search(r"(?<!\w)" + re.escape(r["base_name"].lower()) + r"(?!\w)", text):
            continue
        q = con.execute("SELECT price FROM quotes WHERE server=? AND item_id=? ORDER BY ts DESC LIMIT 1",
                        (server, r["id"])).fetchone()
        if not q:
            continue
        con.execute("INSERT OR IGNORE INTO patch_watch VALUES (?,?,?,?,?,?)",
                    (r["id"], it["key"], it["title"], it["url"], datetime.now(timezone.utc).isoformat()[:19], q["price"]))
        found.append(r["base_name"])
    return found


def reddit(sub, keywords):
    """Nouveaux posts Reddit dont le titre contient un des mots-cles (Reddit bloque parfois les serveurs : best effort)."""
    pat = re.compile("|".join(map(re.escape, keywords)), re.I)
    root = ET.fromstring(get_text(f"https://www.reddit.com/r/{sub}/new.rss"))
    for e in root.iter(ATOM + "entry"):
        title = (e.findtext(ATOM + "title") or "").strip()
        link = e.find(ATOM + "link")
        if title and pat.search(title):
            yield dict(key=f"reddit|{e.findtext(ATOM + 'id')}", label=f"💬 **r/{sub}**", title=title,
                       url=link.get("href") if link is not None else "", posted=(e.findtext(ATOM + "updated") or "")[:19])


def check(con, cfg):
    """Retourne (messages a envoyer, erreurs par source)."""
    ncfg = cfg.get("news") or {}
    items, errors = [], []
    for board in ncfg.get("boards", []):
        try:
            items += list(official(board, ncfg.get("lang", "fr-fr")))
        except Exception as e:
            errors.append(f"{board} : {e}")
    if ncfg.get("reddit"):
        try:
            items += list(reddit(ncfg["reddit"], ncfg.get("reddit_keywords") or ["patch"]))
        except Exception as e:
            errors.append(f"reddit : {e}")
    exclude = re.compile("|".join(map(re.escape, ncfg.get("exclude", []))), re.I) if ncfg.get("exclude") else None
    first = {}                       # par source : premier passage reussi = on note sans envoyer
    msgs = []
    for it in items:
        if exclude and exclude.search(it["title"]):
            continue
        src = it["key"].split("|")[0]
        if src not in first:
            first[src] = not con.execute("SELECT 1 FROM alerts_sent WHERE key LIKE ?", (f"news|{src}|%",)).fetchone()
        con.execute("INSERT OR IGNORE INTO news VALUES (?,?,?,?,?)",
                    (it["key"], it["label"], it["title"], it["url"], it["posted"]))
        msg = f"{it['label']} : {it['title']}\n{it['url']}"
        if con.execute("SELECT 1 FROM alerts_sent WHERE key = ?", (f"news|{it['key']}",)).fetchone():
            continue
        recent = it["posted"] and it["posted"] >= (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()[:19]
        if it.get("board", "").startswith("update") and recent:
            try:
                found = watch_items(con, cfg, it)
            except Exception as e:
                errors.append(f"note {it['key']} : {e}")
                found = []
            if found:
                msg += f"\nItems cités, prix surveillés 48 h : {', '.join(sorted(found)[:15])}"
        if _once(con, f"news|{it['key']}", msg) and not first[src]:
            msgs.append(msg)
    con.commit()
    return msgs, errors


def latest(con, limit=6):
    """Dernieres annonces vues, les plus recentes d'abord."""
    return [dict(r) for r in con.execute("SELECT * FROM news ORDER BY posted DESC LIMIT ?", (limit,))]
