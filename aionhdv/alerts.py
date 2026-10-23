"""Detection d'opportunites et envoi Discord (webhook). Sans webhook, les alertes vont dans logs/alerts.log."""
import json
import re
import statistics
import urllib.request
from datetime import datetime, timedelta, timezone

from .collect import paris
from .config import LOG_DIR


def fmt(n):
    return f"{n:,.0f}".replace(",", " ") if n is not None else "?"


def send(cfg, text, channel=None):
    """channel : 'unique' ou 'news' pour un salon Discord dedie (discord_webhook_<channel>_url), sinon le salon principal."""
    LOG_DIR.mkdir(exist_ok=True)
    with open(LOG_DIR / "alerts.log", "a", encoding="utf-8") as f:
        f.write(f"--- {datetime.now().isoformat(timespec='seconds')}\n{text}\n")
    url = (channel and cfg.get(f"discord_webhook_{channel}_url")) or cfg.get("discord_webhook_url")
    if not url:
        return False
    chunks, cur = [], ""
    for line in text.split("\n"):
        if len(cur) + len(line) + 1 > 1900:
            chunks.append(cur)
            cur = ""
        cur += line + "\n"
    if cur:
        chunks.append(cur)
    for c in chunks:
        req = urllib.request.Request(url, data=json.dumps({"content": c}).encode("utf-8"),
                                     headers={"Content-Type": "application/json", "User-Agent": "aion-hdv"})
        urllib.request.urlopen(req, timeout=20).read()
    return True


def safe(e):
    """Opportunite d'achat assez sure pour une alerte : feu vert de l'indice de surete."""
    return (e.get("surete") or {}).get("feu") == "vert"


def _once(con, key, message):
    if con.execute("SELECT 1 FROM alerts_sent WHERE key = ?", (key,)).fetchone():
        return False
    con.execute("INSERT INTO alerts_sent VALUES (?,?,?)",
                (key, datetime.now(timezone.utc).isoformat(timespec="seconds"), message[:500]))
    con.commit()
    return True


def freshness(con, cfg, max_hours=3, every_hours=12):
    """Donnees perimees : aucun prix recu pour mon serveur depuis `max_hours` heures (source en panne, API changee...).
    Une alerte en entrant dans la panne, puis un rappel toutes les `every_hours` heures tant qu'elle dure."""
    last = con.execute("SELECT MAX(ts) AS ts FROM quotes WHERE server = ?", (str(cfg["my_server"]),)).fetchone()["ts"]
    if not last:
        return None
    d = datetime.fromisoformat(last.replace("Z", "+00:00"))
    age = (datetime.now(timezone.utc) - (d if d.tzinfo else d.replace(tzinfo=timezone.utc))).total_seconds() / 3600
    if age < max_hours or not _once(con, f"stale|{last}|{int(age // every_hours)}", last):
        return None
    return (f"🚨 **Données périmées** : aucun prix reçu depuis **{age:.0f} h** (dernier relevé le {paris(last, '%d/%m à %H:%M')}). "
            "Les sources (a2-tracker, aion2.exchange) sont peut-être en panne : le site et les alertes se basent sur de vieux prix.")


def opportunities(cfg, result):
    """Bonnes opportunites du moment, seulement au feu vert de l'indice de surete (aucune donnee personnelle) :
    liste de (cle, ligne)."""
    a, out = cfg["alerts"], []
    for e in result.get("buy") or []:
        if (not e["flags"] and e["marge"] is not None and e["marge"] >= a["buy_craft_min_margin"]
                and e["profit_j"] >= a["buy_craft_min_profit_day"] and e["net_pess_u"] > 0 and safe(e)):
            s = e["surete"]
            out.append((f"buy{e['item_id']}", f"🟢 **{e['objet']}** (achat → craft) : ingrédients {fmt(e['achats_u'])} → vente "
                        f"~{fmt(e['prix_real'])}, **+{fmt(e['net_u'])}/u** (+{e['marge']:.0%}), max ~{fmt(s['qte_max'])} u"))
    for e in result.get("spikes") or []:
        if safe(e):
            out.append((f"spike{e['item_id']}", f"⚡ **{e['objet']}** en pic : affiché {fmt(e['prix_affiche'])} (habituellement "
                        f"{fmt(e['prix_ref'])}), +{fmt(e['net_affiche_u'])}/u en achat → craft, à vendre vite"))
    for u in result.get("uniques") or []:
        if u["ratio"] <= a["unique_ratio"] and u["releves"] >= a["unique_min_samples"] and u["mediane"] >= a["unique_min_median"]:
            out.append((f"uniq{u['item_id']}", f"💎 **{u['objet']}** ({u['categorie']}) à {fmt(u['prix'])} "
                        f"(médiane 7 j {fmt(u['mediane'])}, {u['ratio']:.0%})"))
    return out


# fenetre de vente sur laquelle une opportunite est jugee : un pic se vend vite, le reste sur 2 jours
TRACK_HOURS = {"spike": 6, "buy": 48, "flip": 48, "uniq": 48}
TRACK_KINDS = {"buy": "🟢 Achat → craft", "spike": "⚡ Pic de prix", "flip": "🔁 Flip", "uniq": "💎 Unique bradé"}


def track(con, cfg, result):
    """Precision des alertes : note chaque opportunite alertable (feu vert, flips a saisir, Unique bradés ; une fois par
    objet et par jour), puis la juge quand sa fenetre de vente est passee : prix reel = mediane des prix plancher du
    produit sur cette fenetre, net reel = prix reel apres taxe - cout au moment de l'alerte. Tenue = net reel > 0."""
    fees, now = cfg["fees"], datetime.now(timezone.utc)
    rows = []
    for key, _ in opportunities(cfg, result):                 # cles buy<id>, spike<id>, uniq<id>
        kind, iid = re.fullmatch(r"([a-z]+)(\d+)", key).groups()
        src = {"buy": result.get("buy"), "spike": result.get("spikes"), "uniq": result.get("uniques")}[kind] or []
        e = next((x for x in src if x["item_id"] == int(iid)), None)
        if not e:
            continue
        if kind == "buy":
            rows.append((key, kind, e, e["achats_u"], e["prix_real"], e["net_u"]))
        elif kind == "spike":
            rows.append((key, kind, e, e["achats_u"], e["prix_affiche"], e["net_affiche_u"]))
        else:
            rows.append((key, kind, e, e["prix"], e["mediane"], e["mediane"] * (1 - fees) - e["prix"]))
    a = cfg["alerts"]
    for f in result.get("flips") or []:
        if f["acheter"] and f["profit_j"] >= a["flip_min_profit_day"] and (f.get("surete") or {}).get("feu") != "rouge":
            rows.append((f"flip{f['item_id']}", "flip", f, f["prix"], f["revente_cible"], f["revente_cible"] * (1 - fees) - f["prix"]))
    day = (now - timedelta(hours=24)).isoformat(timespec="seconds")
    for key, kind, e, cost, price, net in rows:
        if not con.execute("SELECT 1 FROM opp_track WHERE key = ? AND ts > ?", (key, day)).fetchone():
            con.execute("INSERT INTO opp_track (key, kind, item_id, objet, ts, cout, prix_prevu, net_prevu) VALUES (?,?,?,?,?,?,?,?)",
                        (key, kind, e["item_id"], e["objet"], now.isoformat(timespec="seconds"), cost, price, net))
    # jugement des opportunites dont la fenetre de vente est passee
    for r in con.execute("SELECT rowid, * FROM opp_track WHERE checked IS NULL").fetchall():
        t = datetime.fromisoformat(r["ts"])
        end = t + timedelta(hours=TRACK_HOURS.get(r["kind"], 48))
        if end > now:
            continue
        seen = [p for (p,) in con.execute("SELECT price FROM quotes WHERE server = ? AND item_id = ? AND ts > ? AND ts <= ?",
                                          (str(cfg["my_server"]), r["item_id"], t.isoformat()[:19], end.isoformat()[:19]))]
        price = statistics.median(seen) if seen else None
        con.execute("UPDATE opp_track SET prix_reel = ?, net_reel = ?, checked = ? WHERE rowid = ?",
                    (price, price * (1 - fees) - r["cout"] if price is not None else None, now.isoformat(timespec="seconds"),
                     r["rowid"]))
    con.commit()


def precision(con, days=30):
    """Bilan des opportunites jugees sur `days` jours, par type : nombre, part tenue (net reel > 0), net reel moyen
    rapporte au net prevu."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec="seconds")
    out = {}
    for r in con.execute("SELECT kind, net_prevu, net_reel FROM opp_track WHERE checked IS NOT NULL AND net_reel IS NOT NULL "
                         "AND ts > ?", (since,)):
        k = out.setdefault(r["kind"], dict(kind=r["kind"], label=TRACK_KINDS.get(r["kind"], r["kind"]), n=0, ok=0, prevu=0, reel=0))
        k["n"] += 1
        k["ok"] += r["net_reel"] > 0
        k["prevu"] += r["net_prevu"] or 0
        k["reel"] += r["net_reel"]
    for k in out.values():
        k["taux"] = k["ok"] / k["n"]
        k["vs_prevu"] = k["reel"] / k["prevu"] if k["prevu"] > 0 else None
    pending = con.execute("SELECT COUNT(*) FROM opp_track WHERE checked IS NULL").fetchone()[0]
    return dict(kinds=[out[k] for k in TRACK_KINDS if k in out], attente=pending, jours=days)


def flips(con, cfg, result, hours=6):
    """Alerte flip : un item vient de passer sous son prix d'achat conseille (bas de sa fourchette habituelle), avec
    assez de ventes et pas au feu rouge. Une alerte par item toutes les `hours` heures au plus."""
    a, now = cfg["alerts"], datetime.now(timezone.utc)
    lines = []
    for f in result.get("flips") or []:
        s = f.get("surete") or {}
        if not f["acheter"] or f["profit_j"] < a["flip_min_profit_day"] or s.get("feu") == "rouge":
            continue
        key = f"flipnow|{f['item_id']}"
        last = con.execute("SELECT ts FROM alerts_sent WHERE key = ?", (key,)).fetchone()
        if last and datetime.fromisoformat(last["ts"]) > now - timedelta(hours=hours):
            continue
        con.execute("INSERT OR REPLACE INTO alerts_sent VALUES (?,?,?)", (key, now.isoformat(timespec="seconds"), f["objet"]))
        dot = {"vert": "🟢", "orange": "🟠"}.get(s.get("feu"), "")
        lines.append(f"🔁 **{f['objet']}** à **{fmt(f['prix'])}** ({f['annonces']} annonce(s)) : acheter ≤ {fmt(f['achat_cible'])}, "
                     f"revendre ~{fmt(f['revente_cible'])}, **+{fmt(f['net_u'])}/u** (+{f['marge']:.0%}), "
                     f"~{fmt(f['ma_part_j'])} ventes/j {dot}".rstrip())
    con.commit()
    if not lines:
        return None
    srv = con.execute("SELECT name FROM servers WHERE id = ?", (result["server"],)).fetchone()
    return "\n".join([f"🔁 **Flips à saisir {paris(None, '%Hh%M')}** · {srv['name'] if srv else result['server']}"] + lines)


def hourly(con, cfg, result, top=6):
    """Rapport horaire leger : les bonnes opportunites du moment. Rien si aucune, ou si ce sont les memes qu'au
    rapport precedent (pas de repetition d'heure en heure)."""
    ops = opportunities(cfg, result)
    if not ops:
        return None
    sig = "|".join(sorted(k for k, _ in ops[:top]))
    last = con.execute("SELECT message FROM alerts_sent WHERE key = 'hourly_last'").fetchone()
    if last and last["message"] == sig:
        return None
    con.execute("INSERT OR REPLACE INTO alerts_sent VALUES ('hourly_last', ?, ?)",
                (datetime.now(timezone.utc).isoformat(timespec="seconds"), sig))
    con.commit()
    srv = con.execute("SELECT name FROM servers WHERE id = ?", (result["server"],)).fetchone()
    lines = [f"⏰ **Opportunités {paris(None, '%Hh%M')}** · {srv['name'] if srv else result['server']}"]
    lines += [l for _, l in ops[:top]]
    if len(ops) > top:
        lines.append(f"… et {len(ops) - top} autre(s) sur le site.")
    return "\n".join(lines)


def daily_news(con, days=7):
    """Annonces officielles NCSOFT (site officiel) pas encore reprises dans un resume quotidien. Au tout premier
    passage, celles deja connues sont seulement notees (deja postees par l'ancien systeme d'alertes)."""
    first = not con.execute("SELECT 1 FROM alerts_sent WHERE key LIKE 'daily_news|%'").fetchone()
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()[:19]
    rows = [r for r in con.execute("SELECT key, label, title, url, posted FROM news WHERE key NOT LIKE 'reddit|%' "
                                   "AND posted >= ? ORDER BY posted", (since,))
            if not con.execute("SELECT 1 FROM alerts_sent WHERE key = ?", (f"daily_news|{r['key']}",)).fetchone()]
    for r in rows:
        con.execute("INSERT OR IGNORE INTO alerts_sent VALUES (?,?,?)",
                    (f"daily_news|{r['key']}", datetime.now(timezone.utc).isoformat(timespec="seconds"), r["title"][:500]))
    con.commit()
    return [] if first else rows


def weekly(con, cfg, result, top=5):
    """Resume du dimanche : plus fortes hausses et baisses de prix sur 7 j (items avec du volume), crafts entres et
    sortis du top 10."""
    m = result["market"]
    srv = con.execute("SELECT name FROM servers WHERE id = ?", (result["server"],)).fetchone()
    sname = srv["name"] if srv else result["server"]
    now = datetime.now(timezone.utc)
    cut1, cut6 = (now - timedelta(hours=24)).isoformat()[:19], (now - timedelta(days=6)).isoformat()[:19]
    moves = []
    for iid in m.price:
        it = m.items.get(iid) or {}
        if it.get("bound") or m.listings.get(iid, 0) < 2 or not m.sales(iid):    # 1 seule annonce : prix peu fiable
            continue
        rows = m.price_series(iid, 8)
        new, old = [p for t, p in rows if t >= cut1], [p for t, p in rows if t < cut6]
        if len(new) >= 3 and len(old) >= 3 and statistics.median(old) >= 1000:
            a, b = statistics.median(old), statistics.median(new)
            moves.append((b / a, it["name"], a, b))
    moves.sort()
    lines = [f"🗓️ **Tendances de la semaine : {sname}**"]
    if moves:
        lines += ["", "**Plus fortes hausses (7 j)**"]
        lines += [f"📈 {n} : {fmt(a)} → **{fmt(b)}** (×{r:.2f})" for r, n, a, b in reversed(moves[-top:]) if r > 1]
        lines += ["", "**Plus fortes baisses (7 j)**"]
        lines += [f"📉 {n} : {fmt(a)} → **{fmt(b)}** (×{r:.2f})" for r, n, a, b in moves[:top] if r < 1]
    else:
        lines.append("Pas encore assez d'historique pour comparer les prix sur 7 jours.")
    before = con.execute("SELECT MAX(run_ts) AS ts FROM analyses WHERE server=? AND kind='harvest' AND run_ts<=?",
                         (result["server"], cut6)).fetchone()["ts"]
    if before:
        old_top = {r["item_id"]: json.loads(r["data"])["objet"] for r in con.execute(
            "SELECT item_id, data FROM analyses WHERE server=? AND kind='harvest' AND run_ts=? ORDER BY score DESC LIMIT 10",
            (result["server"], before))}
        new_top = {e["item_id"]: e["objet"] for e in [e for e in result["harvest"] if not e["flags"]][:10]}
        entered = [n for i, n in new_top.items() if i not in old_top]
        left = [n for i, n in old_top.items() if i not in new_top]
        lines += ["", "**Top 10 des crafts**",
                  "Entrés : " + (", ".join(entered) or "aucun"), "Sortis : " + (", ".join(left) or "aucun")]
    prec = precision(con, 7)
    if prec["kinds"]:
        lines += ["", "**Précision des alertes (7 j)**"]
        lines += [f"{k['label']} : {k['ok']}/{k['n']} tenues ({k['taux']:.0%}), net réel moyen {fmt(k['reel'] / k['n'])}/u"
                  for k in prec["kinds"]]
    return "\n".join(lines)


def digest(con, cfg, result, top=8):
    srv = con.execute("SELECT name FROM servers WHERE id = ?", (result["server"],)).fetchone()
    sname = srv["name"] if srv else result["server"]
    lines = [f"📊 **Résumé du jour : {sname}** (prix de {paris(result['as_of'], '%H:%M')} heure de Paris, ventes mesurées sur le serveur)",
             "", f"**Récolte → craft → vente** (profit par jour à {result['market'].share:.0%} des ventes mesurées)"]
    h = result.get("hours")
    if h:
        lines.insert(1, f"🕒 Meilleur moment pour poster : **{h['best']}h – {(h['best'] + 3) % 24}h** "
                        f"(creux {h['low']}h – {(h['low'] + 3) % 24}h, heure de {h['tz']})")
    for i, e in enumerate([e for e in result["harvest"] if not e["flags"]][:top], 1):
        lines.append(f"{i}. {e['objet']} : vends à ~{fmt(e['prix_real'])}, net {fmt(e['net_u'])}/u, "
                     f"~{fmt(e['ma_part_j'])}/j → **{fmt(e['profit_j'])}/j**"
                     + (f" ({e['nb_lots_j']} annonce(s) de {fmt(e['lot_vente'])})" if e.get("nb_lots_j") else "")
                     + (f" ⚠ le brut rapporte {fmt(-e['vs_brut_u'])}/u de plus" if (e.get("vs_brut_u") or 0) < 0 else ""))
    raw = [e for e in result.get("raw") or [] if not e["flags"] and e["net_u"] > 0]
    if raw:
        lines += ["", "**Vente du brut** (ta part des ventes mesurées)"]
        for e in raw[:5]:
            lines.append(f"• {e['objet']} : vends à ~{fmt(e['prix_real'])}, net {fmt(e['net_u'])}/u, "
                         f"~{fmt(e['ma_part_j'])}/j → {fmt(e['profit_j'])}/j")
    buys = [e for e in result["buy"] if not e["flags"] and e["net_u"] > 0]
    lines += ["", "**Achat → craft → revente**"]
    if buys:
        for e in buys[:5]:
            lines.append(f"• {e['objet']} : coût {fmt(e['achats_u'])}, net {fmt(e['net_u'])}/u "
                         f"(pessimiste {fmt(e['net_pess_u'])}) → {fmt(e['profit_j'])}/j")
    else:
        lines.append("Rien de rentable en ce moment.")
    flips = result.get("flips") or []
    if flips:
        lines += ["", "**Achat → revente (flip)**"]
        for f in flips[:5]:
            lines.append(f"• {f['objet']} : acheter ≤ {fmt(f['achat_cible'])}, revendre ~{fmt(f['revente_cible'])}, "
                         f"net {fmt(f['net_u'])}/u → {fmt(f['profit_j'])}/j" + (" ✅ prix d'achat atteint" if f["acheter"] else ""))
    if result["plan"]:
        lines += ["", "**Plan de production pour ta récolte**"]
        for p in result["plan"]:
            lines.append(f"• {p['quantite_j']} × {p['objet']}{' (brut)' if p.get('brut') else ''} à "
                         f"~{fmt(p['prix_conseille'])} → {fmt(p['kinah_j'])}/j")
    ops = opportunities(cfg, result)
    if ops:
        lines += ["", "**Opportunités sûres en ce moment** (feu vert)"] + [f"• {l}" for _, l in ops[:10]]
    news = daily_news(con)
    if news:
        lines += ["", "**Annonces officielles NCSOFT**"]
        # <lien> : pas d'apercu Discord pour chaque lien du resume
        lines += [f"• {paris(n['posted'], '%d/%m')} {n['label']} : {n['title']} <{n['url']}>" for n in news]
    return "\n".join(lines)
