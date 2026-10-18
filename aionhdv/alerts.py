"""Detection d'opportunites et envoi Discord (webhook). Sans webhook, les alertes vont dans logs/alerts.log."""
import json
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


def _once(con, key, message):
    if con.execute("SELECT 1 FROM alerts_sent WHERE key = ?", (key,)).fetchone():
        return False
    con.execute("INSERT INTO alerts_sent VALUES (?,?,?)",
                (key, datetime.now(timezone.utc).isoformat(timespec="seconds"), message[:500]))
    con.commit()
    return True


def detect(con, cfg, result):
    """Retourne la liste des messages d'alerte nouveaux pour ce passage."""
    m = result["market"]
    a = cfg["alerts"]
    srv = con.execute("SELECT name FROM servers WHERE id = ?", (result["server"],)).fetchone()
    sname = srv["name"] if srv else result["server"]
    hour = datetime.now(timezone.utc).strftime("%Y%m%d%H")
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    msgs = []

    # 1. annonces bradees (tout item suivi ; les Unique ont leur propre suivi, detect_uniques)
    for iid, price in m.price.items():
        if m.items.get(iid, {}).get("grade") == "Unique":
            continue
        med = m.median_price(iid, 7)
        if not med or med < a["bargain_min_median"]:
            continue
        if price <= a["bargain_ratio"] * med:
            ref = m.ref(iid)
            if ref:
                # il faut un marche reel pour revendre : volume de reference et prix de vente reel nettement plus haut
                if ref["daily"] < 3 or not ref["avg_price"] or price > 0.6 * ref["avg_price"]:
                    continue
            name = m.items.get(iid, {}).get("name", iid)
            resale = f", se vend ~{fmt(ref['avg_price'])} en moyenne sur la référence" if ref else ""
            msg = (f"💸 **Bonne affaire** [{sname}] {name} à **{fmt(price)}** "
                   f"(médiane 7 j : {fmt(med)}, soit {price / med:.0%}{resale}) — {m.listings.get(iid, '?')} annonce(s)")
            if _once(con, f"bargain|{result['server']}|{iid}|{day}", msg):
                msgs.append(msg)

    # 2. envolee / chute du prix de mes produits (top recolte -> craft)
    for e in result["harvest"][:15]:
        med = m.median_price(e["item_id"], 3)
        if not med:
            continue
        r = e["prix_affiche"] / med
        if r >= a["spike_ratio"]:
            msg = (f"📈 **Prix en hausse, c'est le moment de vendre** [{sname}] {e['objet']} : {fmt(e['prix_affiche'])} "
                   f"(médiane 3 j {fmt(med)}, x{r:.1f})")
            if _once(con, f"spike|{result['server']}|{e['item_id']}|{day}", msg):
                msgs.append(msg)
        elif r <= a["dump_ratio"]:
            msg = (f"📉 **Prix en baisse** [{sname}] {e['objet']} : {fmt(e['prix_affiche'])} "
                   f"(médiane 3 j {fmt(med)}, {r:.0%}). Mieux vaut le mettre de côté.")
            if _once(con, f"dump|{result['server']}|{e['item_id']}|{day}", msg):
                msgs.append(msg)

    # 3. achat -> craft -> revente rentable
    for e in result["buy"]:
        if e["flags"] or e["marge"] is None:
            continue
        if e["marge"] >= a["buy_craft_min_margin"] and e["profit_j"] >= a["buy_craft_min_profit_day"] and e["net_pess_u"] > 0:
            msg = (f"🟢 **Achat → craft rentable** [{sname}] {e['objet']} : coût {fmt(e['achats_u'])} → "
                   f"vente {fmt(e['prix_real'])}, net **{fmt(e['net_u'])}/u** (+{e['marge']:.0%}), "
                   f"~{fmt(e['profit_j'])}/j. Ingrédients : {'; '.join(e['ingredients'])}")
            if _once(con, f"buy|{result['server']}|{e['item_id']}|{day}", msg):
                msgs.append(msg)

    # 4. signal de levee de la restriction anti-bot : le brut revient en masse et son prix chute
    gather_ids = [i for i, it in m.items.items() if it["is_gather"] and not it["bound"] and i in m.price]
    now = datetime.now(timezone.utc)
    drops = []
    for iid in gather_ids:
        def window(h0, h1):
            rows = con.execute("SELECT price, listings FROM quotes WHERE server=? AND item_id=? AND ts>=? AND ts<?",
                               (result["server"], iid, (now - timedelta(hours=h0)).isoformat()[:19],
                                (now - timedelta(hours=h1)).isoformat()[:19])).fetchall()
            return rows
        recent, before = window(24, 0), window(96, 24)
        if len(recent) >= 6 and len(before) >= 12:
            p1 = statistics.median(r["price"] for r in recent)
            p0 = statistics.median(r["price"] for r in before)
            l1 = statistics.median(r["listings"] for r in recent)
            l0 = statistics.median(r["listings"] for r in before)
            drops.append((p1 / p0 if p0 else 1, l1 / l0 if l0 else 1))
    if len(drops) >= 10:
        share = sum(1 for p, l in drops if p <= 0.6 and l >= 1.5) / len(drops)
        if share >= 0.4:
            msg = (f"🔓 **La restriction sur le brut semble levée** [{sname}] : {share:.0%} des ressources ont un prix "
                   f"en baisse de plus de 40 % et 50 % d'annonces en plus sur 24 h. Vérifie si tu peux vendre ton brut, "
                   f"et vends tes crafts avant que leurs prix ne baissent.")
            if _once(con, f"unlock|{result['server']}|{day}", msg):
                msgs.append(msg)
    return msgs


def detect_uniques(con, cfg, result):
    """Objets Unique vendus bien en dessous de leur mediane des 7 derniers jours."""
    a = cfg["alerts"]
    srv = con.execute("SELECT name FROM servers WHERE id = ?", (result["server"],)).fetchone()
    sname = srv["name"] if srv else result["server"]
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    msgs = []
    for u in result["uniques"]:
        if u["ratio"] > a["unique_ratio"] or u["releves"] < a["unique_min_samples"] or u["mediane"] < a["unique_min_median"]:
            continue
        msg = (f"💎 **Unique bradé** [{sname}] {u['objet']} à **{fmt(u['prix'])}** "
               f"(médiane 7 j : {fmt(u['mediane'])}, soit {u['ratio']:.0%} ; plus bas vu : {fmt(u['plus_bas'])}) "
               f"— {u['annonces']} annonce(s)")
        if _once(con, f"unique|{result['server']}|{u['item_id']}|{day}", msg):
            msgs.append(msg)
    return msgs


def digest(con, cfg, result, top=8):
    srv = con.execute("SELECT name FROM servers WHERE id = ?", (result["server"],)).fetchone()
    sname = srv["name"] if srv else result["server"]
    lines = [f"📊 **Résumé du jour : {sname}** (prix de {paris(result['as_of'], '%H:%M')} heure de Paris, activité x{result['ratio']:.2f} par rapport à la référence)",
             "", "**Ma récolte → craft → vente** (profit par jour à 20 % du marché)"]
    h = result.get("hours")
    if h:
        lines.insert(1, f"🕒 Meilleur moment pour poster : **{h['best']}h – {(h['best'] + 3) % 24}h** "
                        f"(creux {h['low']}h – {(h['low'] + 3) % 24}h, heure de {h['tz']})")
    for i, e in enumerate([e for e in result["harvest"] if not e["flags"]][:top], 1):
        lines.append(f"{i}. {e['objet']} : vends à ~{fmt(e['prix_real'])}, net {fmt(e['net_u'])}/u, "
                     f"~{fmt(e['ma_part_j'])}/j → **{fmt(e['profit_j'])}/j**"
                     + (f" ({e['nb_lots_j']} annonce(s) de {fmt(e['lot_vente'])})" if e.get("nb_lots_j") else ""))
    buys = [e for e in result["buy"] if not e["flags"] and e["net_u"] > 0]
    lines += ["", "**Achat → craft → revente**"]
    if buys:
        for e in buys[:5]:
            lines.append(f"• {e['objet']} : coût {fmt(e['achats_u'])}, net {fmt(e['net_u'])}/u "
                         f"(pessimiste {fmt(e['net_pess_u'])}) → {fmt(e['profit_j'])}/j")
    else:
        lines.append("Rien de rentable en ce moment.")
    if result["plan"]:
        lines += ["", "**Plan de production pour ta récolte**"]
        for p in result["plan"]:
            lines.append(f"• {p['quantite_j']} × {p['objet']} à ~{fmt(p['prix_conseille'])} → {fmt(p['kinah_j'])}/j")
    return "\n".join(lines)
