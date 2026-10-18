"""Annonces officielles AION 2 (notes de version, avis du site officiel) et Reddit : chaque nouvelle annonce
part une seule fois sur Discord. Au premier passage reussi d'une source, ses annonces existantes sont notees
sans etre envoyees."""
import re
import xml.etree.ElementTree as ET

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
        yield dict(key=f"{board}|{a['id']}", label=label, title=a["title"].strip(), url=url)


def reddit(sub, keywords):
    """Nouveaux posts Reddit dont le titre contient un des mots-cles (Reddit bloque parfois les serveurs : best effort)."""
    pat = re.compile("|".join(map(re.escape, keywords)), re.I)
    root = ET.fromstring(get_text(f"https://www.reddit.com/r/{sub}/new.rss"))
    for e in root.iter(ATOM + "entry"):
        title = (e.findtext(ATOM + "title") or "").strip()
        link = e.find(ATOM + "link")
        if title and pat.search(title):
            yield dict(key=f"reddit|{e.findtext(ATOM + 'id')}", label=f"💬 **r/{sub}**", title=title,
                       url=link.get("href") if link is not None else "")


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
        msg = f"{it['label']} : {it['title']}\n{it['url']}"
        if _once(con, f"news|{it['key']}", msg) and not first[src]:
            msgs.append(msg)
    return msgs, errors
