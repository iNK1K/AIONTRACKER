"""Chaines d'amelioration (blanc -> eclatant -> expert -> maitre -> base unique -> equipement du Roi dragon) : acheter ou
crafter chaque palier. Donnees pour l'onglet ⚖️ Acheter ou crafter (calculs dans le navigateur avec mes niveaux, site.js
partie « chaines ») et historique horaire du cout de chaque option (table chain_hist), calcule ici avec les niveaux de
config.json (masteries)."""
import json
import math
from datetime import datetime, timedelta, timezone

HIST_DAYS = 7


def _combo_of(m):
    """Objet eclatant -> recette de l'objet de base dont le combo le donne."""
    out = {}
    for rs in m.recipes_by_item.values():
        for r in rs:
            if r["combo_item_id"] and not r["unresolved"]:
                out.setdefault(r["combo_item_id"], r)
    return out


def _spike(m, iid):
    """Mediane 7 j du prix plancher et dernier releve a ou sous la mediane (fin du dernier creux), pour signaler un pic."""
    rows = sorted(m.price_series(iid, 7))
    if len(rows) < 12:
        return None, None
    vals = sorted(p for _, p in rows)
    med = vals[len(vals) // 2]
    below = next((ts for ts, p in reversed(rows) if p <= med), None)
    return round(med), below


def _part(m, p):
    """Ingredient d'un palier : prix d'achat (realiste, Od transmute s'il est moins cher), et pour une ressource de
    recolte ce que coute d'utiliser la sienne = ce qu'elle rapporterait vendue brute (elle, ou l'Od a transmuter)."""
    iid = p.get("i")
    out = dict(n=p["n"], i=iid, q=p["q"], buy=round(p["p"]) if p.get("p") is not None else None, k=p["k"], via=p.get("via"),
               l=p.get("l"))
    res = p.get("via") or (m.items[iid]["base_name"] if iid and m.items.get(iid, {}).get("is_gather") else None)
    if res:
        od = m.transmute.get(res)
        cands = [(m.raw_net(res), res)] + ([(m.raw_net(m.items[od]["base_name"]), m.items[od]["base_name"])] if od else [])
        cands = [c for c in cands if c[0] is not None]
        if cands:
            v, src = min(cands)
            out.update(res=res, raw=round(v), raws=src, rawres=round(m.raw_net(res)) if m.raw_net(res) is not None else None)
    if iid and p["k"] in ("hdv", "od"):
        bp = m.buy_price(iid)
        out["med"], out["below"] = _spike(m, iid)
        out["ask"] = round(bp["ask"]) if bp else None
    return out


def _value(m, iid):
    """Valeur de revente (avant taxe) : prix realiste, sinon None."""
    sp = m.sell_price(iid)
    return round(sp["real"]) if sp else None


def build_chains(m):
    """Une entree par base unique (objet eclatant de maitre) : ses paliers depuis l'objet blanc et ses usages finaux."""
    combo_of = _combo_of(m)
    ing_all = {o["item_id"] for d in m.ingredients.values() for opts in d.values() for o in opts}
    uses = {}
    for rs in m.recipes_by_item.values():
        for r in rs:
            if m.items.get(r["item_id"], {}).get("bound"):
                continue                                    # outils lies (marteau, loupe...) : pas a vendre
            for opts in m.ingredients.get(r["id"], {}).values():
                for o in opts:
                    if o["item_id"] in combo_of:
                        uses.setdefault(o["item_id"], []).append((r, o["qty"]))

    def prev_of(r):
        """Ingredient eclatant d'une recette (palier d'avant) et sa quantite."""
        for opts in m.ingredients.get(r["id"], {}).values():
            for o in opts:
                if o["item_id"] in combo_of:
                    return o["item_id"], o["qty"]
        return None, None

    def tier(r, prev, pq):
        e = r["combo_item_id"]
        c = m.recipe_cost(r, "buy", skip={prev} if prev else ())
        bp, cfg = m.buy_price(e), m.cfg.get("combo_rate")
        st = m.price_stats(e, 7)
        return dict(i=r["item_id"], n=m.items[r["item_id"]]["name"], e=e, en=m.items[e]["name"], prof=r["profession"],
                    m=r["mastery"] or 0, cv=r.get("rate_curve"), c=cfg if cfg is not None else (r["combo_prob_raw"] or 0) / 10000,
                    pq=pq, parts=[_part(m, p) for p in c["parts"]], ok=c["ok"],
                    pn=_value(m, r["item_id"]), pl=m.listings.get(r["item_id"], 0),
                    eb=round(bp["real"]) if bp else None, ea=round(bp["ask"]) if bp else None, el=bp["listings"] if bp else 0,
                    es=_value(m, e), emd=round(st["median"]) if st else None)

    out = []
    for base, us in uses.items():
        finals = [(r, q) for r, q in us if not (r["combo_item_id"] and r["combo_item_id"] in ing_all)]
        if not finals:
            continue
        tiers, e, seen = [], base, set()
        while e in combo_of and e not in seen and len(tiers) < 6:
            seen.add(e)
            r = combo_of[e]
            prev, pq = prev_of(r)
            tiers.append(tier(r, prev, pq))
            e = prev
            if not prev:
                break
        if len(tiers) < 2 or tiers[-1]["pq"]:
            continue                                        # chaine incomplete (palier du bas introuvable)
        tiers.reverse()
        fin = []
        for r, q in finals:
            c = m.recipe_cost(r, "buy", skip={base})
            iid = r["item_id"]
            sp = m.sell_price(iid)
            fin.append(dict(i=iid, n=m.items[iid]["name"], prof=r["profession"], m=r["mastery"] or 0, cv=r.get("rate_curve"),
                            q=q, rest=round(c["cost_r"]) if c["ok"] else None, sell=round(sp["real"]) if sp else None,
                            l=m.listings.get(iid, 0), stale=bool(sp and sp["stale"]),
                            cn=m.items[r["combo_item_id"]]["name"] if r["combo_item_id"] in m.items else None))
        it = m.items[base]
        out.append(dict(i=base, n=it["name"], slot=it.get("sub_category"), s=f"../data/{it['icon_file']}" if it.get("icon_file") else None,
                        tiers=tiers, finals=fin))
    out.sort(key=lambda x: x["n"])
    return out


# ------------------------------------------------------------ cout des options (meme calcul que site.js, chOpts)
def part_cost(p, own=True):
    """Cout unitaire d'un ingredient : le moins cher entre l'acheter et utiliser sa recolte (valeur de vente brute)."""
    vals = [v for v in (p.get("buy"), p.get("raw") if own else None) if v is not None]
    return min(vals) if vals else None


def option_costs(ch, rate, fees, lose=True, own=True):
    """Cout moyen de la base unique pour chaque option j : j = nombre de paliers achetes (0 = tout crafter depuis le
    blanc ; len(tiers) = acheter la base). Palier t : K = ingredients + eclatant d'avant ; cout par craft reussi K / r
    (si les ingredients sont perdus en cas d'echec) ; 1 / c crafts reussis par combo, (1 - c) / c objets normaux
    revendus. rate(prof, niveau requis, courbe) -> taux de reussite ou None (niveau trop bas)."""
    n, out = len(ch["tiers"]), []
    for j in range(n + 1):
        x = 0 if j == 0 else ch["tiers"][j - 1]["eb"]
        for t in ch["tiers"][j:]:
            if x is None:
                break
            costs = [part_cost(p, own) for p in t["parts"]]
            r = rate(t["prof"], t["m"], t["cv"])
            if None in costs or not t["c"] or r is None:
                x = None
                break
            k = sum(c * p["q"] for c, p in zip(costs, t["parts"])) + (t["pq"] or 0) * x
            s = k / r if lose else k
            x = (s - (1 - t["c"]) * (t["pn"] or 0) * (1 - fees)) / t["c"]
        out.append(round(x) if x is not None else None)
    return out


def rate_from_config(con, cfg):
    """Taux de reussite avec les niveaux de config.json (masteries ; plafonnes au niveau maximum du jeu, 100)."""
    curves = {r["id"]: json.loads(r["rates"]) for r in con.execute("SELECT * FROM rate_curves")}
    lv = cfg.get("masteries") or {}

    def rate(prof, need, cv):
        mine = min(lv.get(prof, 100), 100)
        if mine < need:
            return None
        c = curves.get(cv)
        return c[min(mine - need, len(c) - 1)] / 1e8 if c else 1.0
    return rate


def save_history(con, cfg, server, chains, ts):
    """Cout de chaque option a ce passage (niveaux de config.json, ingredients perdus en cas d'echec)."""
    rate = rate_from_config(con, cfg)
    con.execute("CREATE TABLE IF NOT EXISTS chain_hist (ts TEXT, server TEXT, item_id INTEGER, costs TEXT, "
                "PRIMARY KEY (ts, server, item_id))")
    con.executemany("INSERT OR REPLACE INTO chain_hist VALUES (?,?,?,?)",
                    [(ts, str(server), ch["i"], json.dumps(option_costs(ch, rate, cfg["fees"]))) for ch in chains])
    cut = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()[:19]
    con.execute("DELETE FROM chain_hist WHERE ts < ?", (cut,))
    con.commit()


def load_history(con, server, days=HIST_DAYS):
    """{item_id: [[heures depuis t0, [couts]], ...]} sur les derniers jours, et t0 (epoch s)."""
    con.execute("CREATE TABLE IF NOT EXISTS chain_hist (ts TEXT, server TEXT, item_id INTEGER, costs TEXT, "
                "PRIMARY KEY (ts, server, item_id))")
    since = datetime.now(timezone.utc) - timedelta(days=days)
    t0 = math.floor(since.timestamp() / 3600) * 3600
    out = {}
    for r in con.execute("SELECT ts, item_id, costs FROM chain_hist WHERE server = ? AND ts >= ? ORDER BY ts",
                         (str(server), since.isoformat()[:19])):
        t = datetime.fromisoformat(r["ts"])
        t = t if t.tzinfo else t.replace(tzinfo=timezone.utc)
        out.setdefault(str(r["item_id"]), []).append([round((t.timestamp() - t0) / 3600, 2), json.loads(r["costs"])])
    return dict(t0=t0, s=out)
