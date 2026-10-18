"""Collecte des donnees vers SQLite."""
import json
import re
from datetime import datetime, timedelta, timezone

from .sources import a2tracker, aion2exchange

BOUND_RE = re.compile(r"\s*\((li[ée]+s?)\)$")


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


try:
    from zoneinfo import ZoneInfo
    PARIS = ZoneInfo("Europe/Paris")
except Exception:          # Windows sans le paquet tzdata : on reste en UTC
    PARIS = None


def paris(ts=None, fmt="%d/%m/%Y à %H:%M"):
    """Horodatage UTC (texte ISO, ou maintenant) affiche a l'heure de Paris."""
    d = datetime.now(timezone.utc) if ts is None else datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    if PARIS is None:
        return d.astimezone(timezone.utc).strftime(fmt) + " UTC"
    return d.astimezone(PARIS).strftime(fmt)


def log_run(con, job, status, detail=""):
    con.execute("INSERT INTO runs VALUES (?,?,?,?)", (now_iso(), job, status, str(detail)[:1000]))
    con.commit()


def num(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- referentiels

ITEM_COLS = ("name", "item_key", "grade", "category", "sub_category", "name_en", "auction_category", "level",
             "icon_url", "icon_file", "on_market", "name_check")


def upsert_item(con, item_id, **fields):
    fields = {k: v for k, v in fields.items() if k in ITEM_COLS and v is not None}
    if "name" in fields:
        fields["bound"] = 1 if BOUND_RE.search(fields["name"]) else 0
        fields["base_name"] = BOUND_RE.sub("", fields["name"])
    if "sub_category" in fields:
        fields["is_gather"] = 1 if fields["sub_category"] == "GatherResource" else 0
    if not fields:
        return
    cols = ", ".join(fields)
    marks = ", ".join("?" for _ in fields)
    upd = ", ".join(f"{k}=excluded.{k}" for k in fields)
    con.execute(f"INSERT INTO items (id, {cols}) VALUES (?, {marks}) ON CONFLICT(id) DO UPDATE SET {upd}",
                (item_id, *fields.values()))


def sync_servers(con):
    rows = a2tracker.servers()
    ax = {}
    for s in aion2exchange.servers():
        ax[(str(s.get("game_server_key")), (s.get("region") or "").lower())] = s.get("server_id")
    for s in rows:
        ax_id = ax.get((s["id"], s["region"]))
        con.execute("INSERT OR REPLACE INTO servers VALUES (?,?,?,?,?,?)",
                    (s["id"], s["name"], s["region"], s["faction"], s["env"], ax_id))
    con.commit()
    return len(rows)


def sync_recipes(con, locale="fr-FR"):
    data = a2tracker.crafting(locale)
    items = data["items"]
    for key, it in items.items():
        upsert_item(con, int(key), name=it.get("name") or "", item_key=it.get("itemKey"), grade=it.get("grade"),
                    category=it.get("category"), sub_category=it.get("subCategory"))
    con.execute("DELETE FROM recipes")
    curves = {}
    con.execute("DELETE FROM recipe_ingredients")
    for r in data["recipes"]:
        combo = r.get("combo") or {}
        # table de reussite du jeu, indexee par l'ecart (mon niveau - niveau requis) ; les recettes partagent quelques
        # courbes, tronquees a 100 - niveau requis : on garde la plus longue, identifiee par sa premiere valeur
        rates = (r.get("successRates") or {}).get("rates") or []
        if rates and len(rates) > len(curves.get(rates[0], [])):
            curves[rates[0]] = rates
        con.execute("INSERT OR REPLACE INTO recipes (id, item_id, method, profession, mastery, faction, output_qty, visible, "
                    "combo_result, unresolved, combo_item_id, combo_prob_raw, rate_curve, fail_gauge) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (r["id"], r["itemId"], r.get("method"), r.get("profession"), r.get("requiredMastery"),
                     r.get("faction"), num(r.get("outputQuantity")) or 1, 1 if r.get("visibleInClientUi") else 0,
                     1 if r.get("isComboResult") else 0, 1 if r.get("hasUnresolvedAdditionalInputs") else 0,
                     combo.get("itemId"), combo.get("probabilityRaw"), rates[0] if rates else None,
                     (r.get("client") or {}).get("failGaugeRaw")))
        for slot, ing in enumerate(r.get("ingredients") or []):
            con.execute("INSERT INTO recipe_ingredients VALUES (?,?,?,?,0)",
                        (r["id"], slot, ing["itemId"], num(ing.get("quantity")) or 0))
            for alt in ing.get("alternatives") or []:
                con.execute("INSERT INTO recipe_ingredients VALUES (?,?,?,?,1)",
                            (r["id"], slot, alt["itemId"], num(alt.get("quantity")) or 0))
    con.execute("DELETE FROM rate_curves")
    for k, rates in curves.items():
        con.execute("INSERT INTO rate_curves VALUES (?,?)", (k, json.dumps(rates)))
    con.commit()
    return len(items), len(data["recipes"])


# ---------------------------------------------------------------- prix horaires

def collect_quotes(con, server):
    q = a2tracker.quotes(server)
    if not q:
        return 0
    ts = (q.get("asOf") or now_iso())[:19]
    n = 0
    for x in q.get("quotes", []):
        if x.get("status") == "current" and x.get("price"):
            con.execute("INSERT OR REPLACE INTO quotes VALUES (?,?,?,?,?)",
                        (str(server), x["itemId"], ts, num(x["price"]), int(num(x.get("listings")) or 0)))
            n += 1
    con.commit()
    return n


# ---------------------------------------------------------------- activite 24 h

def activity_from_history(h):
    obs = [o for o in (h or {}).get("observations", []) if o.get("listings") not in (None, "")]
    if len(obs) < 2:
        return None
    drops = adds = floor_up = 0
    for a, b in zip(obs, obs[1:]):
        dl = int(num(b["listings"])) - int(num(a["listings"]))
        dp = (num(b["price"]) or 0) - (num(a["price"]) or 0)
        if dl < 0:
            drops += -dl
            if dp > 0:
                floor_up += 1
        elif dl > 0:
            adds += dl
    t0 = datetime.fromisoformat(obs[0]["fetchedAt"].replace("Z", "+00:00"))
    t1 = datetime.fromisoformat(obs[-1]["fetchedAt"].replace("Z", "+00:00"))
    hours = max((t1 - t0).total_seconds() / 3600, 1.0)
    recorded = ((h.get("period") or {}).get("recordedObservations")) or 0
    return dict(hours=hours, drops_h=drops / hours, adds_h=adds / hours, floor_up_drops_h=floor_up / hours,
                points=len(obs), recorded=recorded)


def collect_activity(con, server, item_ids):
    ts = now_iso()
    n = 0
    for iid in item_ids:
        a = activity_from_history(a2tracker.history(iid, server, 1))
        if a:
            con.execute("INSERT OR REPLACE INTO activity VALUES (?,?,?,?,?,?,?,?,?)",
                        (str(server), iid, ts, a["hours"], a["drops_h"], a["adds_h"], a["floor_up_drops_h"],
                         a["points"], a["recorded"]))
            n += 1
    con.commit()
    return n


# ---------------------------------------------------------------- aion2.exchange

def collect_ref_volume(con, ax_server, item_ids):
    n = 0
    for iid in item_ids:
        v = aion2exchange.volume(iid, ax_server)
        for d in (v or {}).get("days", []):
            con.execute("INSERT OR REPLACE INTO ref_volume VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (ax_server, iid, d["registered"], num(d.get("units_sold")), num(d.get("units_delta")),
                         num(d.get("days_since_previous")), num(d.get("avg_price")), num(d.get("min_price")),
                         num(d.get("max_price")), d.get("window_from")))
            n += 1
    con.commit()
    return n


def collect_ax_prices(con, ax_server, item_ids, since_iso):
    n = 0
    for iid in item_ids:
        p = aion2exchange.prices(iid, ax_server, since_iso)
        if not p:
            continue
        bucket = p.get("bucket")
        for pt in p.get("points", []):
            con.execute("INSERT OR REPLACE INTO ax_prices VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        (ax_server, iid, pt["ts"], bucket, num(pt.get("low")), num(pt.get("high")), num(pt.get("avg")),
                         num(pt.get("close")), num(pt.get("listings")), num(pt.get("listings_min")),
                         num(pt.get("listings_max"))))
            n += 1
    con.commit()
    return n


# ---------------------------------------------------------------- selection des items suivis

def tracked_items(con):
    """Produits des recettes qui utilisent une ressource de recolte + tous leurs ingredients + ressources."""
    rows = con.execute("""
        SELECT DISTINCT r.id, r.item_id FROM recipes r
        JOIN recipe_ingredients ri ON ri.recipe_id = r.id
        JOIN items i ON i.id = ri.item_id
        WHERE r.method = 'craft' AND r.visible = 1 AND r.combo_result = 0 AND i.is_gather = 1
    """).fetchall()
    ids = set()
    for r in rows:
        ids.add(r["item_id"])
        for ing in con.execute("SELECT item_id FROM recipe_ingredients WHERE recipe_id = ?", (r["id"],)):
            ids.add(ing["item_id"])
    ids |= {r["id"] for r in con.execute("SELECT id FROM items WHERE is_gather = 1 AND bound = 0")}
    # on ne garde que les versions echangeables (les versions liees n'ont pas de marche)
    tradeable = set()
    for iid in ids:
        it = con.execute("SELECT bound, base_name FROM items WHERE id = ?", (iid,)).fetchone()
        if not it:
            continue
        if it["bound"]:
            t = con.execute("SELECT id FROM items WHERE base_name = ? AND bound = 0", (it["base_name"],)).fetchone()
            if t:
                tradeable.add(t["id"])
        else:
            tradeable.add(iid)
    return sorted(tradeable)


def core_items(con, limit=60):
    """Sous-ensemble pour l'activite 24 h : items deja cotes, les plus actifs en annonces."""
    ids = tracked_items(con)
    srv = con.execute("SELECT MAX(ts) AS ts FROM quotes").fetchone()["ts"]
    if not srv:
        return ids[:limit]
    q = {r["item_id"]: r["listings"] for r in con.execute(
        "SELECT item_id, MAX(listings) AS listings FROM quotes GROUP BY item_id")}
    ids = [i for i in ids if i in q]
    ids.sort(key=lambda i: -q[i])
    return ids[:limit]


def top_products(con, server, limit=40):
    """Produits les mieux classes de la derniere analyse (recolte et achat) : on mesure aussi leur activite,
    pour connaitre la taille des lots qui se vendent."""
    run = con.execute("SELECT MAX(run_ts) AS ts FROM analyses WHERE server=?", (str(server),)).fetchone()["ts"]
    if not run:
        return []
    rows = con.execute("SELECT item_id, MAX(score) AS s FROM analyses WHERE run_ts=? AND server=? "
                       "AND kind IN ('harvest', 'buy') GROUP BY item_id ORDER BY s DESC LIMIT ?",
                       (run, str(server), limit))
    return [r["item_id"] for r in rows]


def ref_item_ids(con):
    """Items suivis + equivalents elyseens (pour le volume de reference de Kaisinel)."""
    from .analysis import elyos_equivalent
    ids = set(tracked_items(con))
    for iid in list(ids):
        e = elyos_equivalent(con, iid)
        if e:
            ids.add(e)
    return sorted(ids)
