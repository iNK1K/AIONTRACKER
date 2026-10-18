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


def safe(e):
    """Opportunite d'achat assez sure pour une alerte : feu vert de l'indice de surete."""
    return (e.get("surete") or {}).get("feu") == "vert"


def surete_txt(e):
    s = e.get("surete")
    if not s:
        return ""
    plancher = f" · ne vends pas sous {fmt(s['prix_plancher'])}" if s.get("prix_plancher") else ""
    return f"\n🛡️ Sûreté {s['score']}/100 · quantité max ~{fmt(s['qte_max'])}{plancher}"


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
        if (e["marge"] >= a["buy_craft_min_margin"] and e["profit_j"] >= a["buy_craft_min_profit_day"] and e["net_pess_u"] > 0
                and safe(e)):
            msg = (f"🟢 **Achat → craft rentable** [{sname}] {e['objet']} : coût {fmt(e['achats_u'])} → "
                   f"vente {fmt(e['prix_real'])}, net **{fmt(e['net_u'])}/u** (+{e['marge']:.0%}), "
                   f"~{fmt(e['profit_j'])}/j. Ingrédients : {'; '.join(e['ingredients'])}{surete_txt(e)}")
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
        msg = (f"💎 **Unique bradé** [{sname}] {u['objet']} ({u['categorie']}) à **{fmt(u['prix'])}** "
               f"(médiane 7 j : {fmt(u['mediane'])}, soit {u['ratio']:.0%} ; plus bas vu : {fmt(u['plus_bas'])}) "
               f"— {u['annonces']} annonce(s)")
        if _once(con, f"unique|{result['server']}|{u['item_id']}|{day}", msg):
            msgs.append(msg)
    return msgs


def detect_undercuts(con, cfg, result):
    """Quelqu'un vend moins cher qu'une de mes annonces : une alerte par nouveau prix plus bas."""
    srv = con.execute("SELECT name FROM servers WHERE id = ?", (result["server"],)).fetchone()
    sname = srv["name"] if srv else result["server"]
    msgs = []
    for l in result["listings"]:
        if not l["battu"]:
            continue
        if l["conseil"]:
            gain = f" (il te reste +{fmt(round(l['conseil'] * (1 - cfg['fees']) - l['cout']))}/u)" if l.get("cout") else ""
            advice = f"Repasse devant à **{fmt(l['conseil'])}**{gain}."
        elif l.get("seuil"):
            advice = f"Le plus bas est sous ton seuil de rentabilité ({fmt(l['seuil'])}) : baisser = vendre à perte."
        else:
            advice = "Baisse ton prix ou attends."
        msg = (f"⚔️ **Tu es battu** [{sname}] {l['nom']} : quelqu'un vend à **{fmt(l['plancher'])}** "
               f"(ton prix {fmt(l['mon_prix'])}, −{fmt(l['ecart'])}) — {l['annonces']} annonce(s). {advice}")
        if _once(con, f"undercut|{result['server']}|{l['item_id']}|{l['mon_prix']}|{l['plancher']}", msg):
            msgs.append(msg)
    return msgs


def detect_patch_moves(con, cfg, result):
    """Items cites dans une note de version depuis moins de 48 h dont le prix a bouge d'au moins 20 %."""
    m = result["market"]
    since = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()[:19]
    msgs = []
    for w in con.execute("SELECT * FROM patch_watch WHERE since >= ?", (since,)).fetchall():
        price = m.price.get(w["item_id"])
        if not price or not w["base_price"]:
            continue
        r = price / w["base_price"]
        if 0.8 < r < 1.25:
            continue
        name = m.items.get(w["item_id"], {}).get("name", w["item_id"])
        sens = "📈 en hausse" if r > 1 else "📉 en baisse"
        msg = (f"🛠️ **Effet de la note de version** {name} {sens} : **{fmt(price)}** "
               f"(avant la note {fmt(w['base_price'])}, ×{r:.2f}) — {w['title']}")
        if _once(con, f"patch|{w['news_key']}|{w['item_id']}|{'up' if r > 1 else 'down'}", msg):
            msgs.append(msg)
    return msgs


def detect_spikes(con, cfg, result):
    """Achat -> craft rentable seulement grace a un pic de prix en cours : une alerte par item et par jour."""
    srv = con.execute("SELECT name FROM servers WHERE id = ?", (result["server"],)).fetchone()
    sname = srv["name"] if srv else result["server"]
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    msgs = []
    for e in result.get("spikes") or []:
        if not safe(e):
            continue                                  # marche deja encombre ou trop risque : pas d'alerte
        depuis = f", depuis {paris(e['depuis'], '%d/%m %H:%M')}" if e["depuis"] else ""
        msg = (f"⚡ **Pic de prix** [{sname}] {e['objet']} affiché **{fmt(e['prix_affiche'])}** "
               f"(habituellement {fmt(e['prix_ref'])}, ×{e['ratio']}{depuis}) — {e['annonces']} annonce(s). "
               f"Acheter les ingrédients ({fmt(e['achats_u'])}/u) et fabriquer rapporte **+{fmt(e['net_affiche_u'])}/u** "
               f"si tu vends au prix affiché, mais **{fmt(e['net_habituel_u'])}/u** si le prix revient à la normale : "
               f"petite quantité, à vendre vite. Ingrédients : {'; '.join(e['ingredients'])}{surete_txt(e)}")
        if _once(con, f"spike_craft|{result['server']}|{e['item_id']}|{day}", msg):
            msgs.append(msg)
    return msgs


def detect_positions(con, cfg, result):
    """Mes positions : prix sous mon seuil de rentabilite, chute en cours, stock trop long a ecouler."""
    srv = con.execute("SELECT name FROM servers WHERE id = ?", (result["server"],)).fetchone()
    sname = srv["name"] if srv else result["server"]
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    msgs = []
    for l in result["listings"]:
        if not l["item_id"]:
            continue
        if l["sous_seuil"]:
            msg = (f"⛔ **Sous ton seuil de rentabilité** [{sname}] {l['nom']} : le plus bas est à **{fmt(l['plancher'])}**, "
                   f"ton seuil est {fmt(l['seuil'])} (coût {fmt(l['cout'])} + frais). Vendre maintenant = "
                   f"{fmt(l['marge_u'])}/u. Garde ton stock, ou coupe la perte si le prix continue de baisser.")
            if _once(con, f"pos_seuil|{result['server']}|{l['item_id']}|{day}", msg):
                msgs.append(msg)
        if l["chute"]:
            msg = (f"📉 **Le prix chute** [{sname}] {l['nom']} : {fmt(l['plancher'])}, soit {l['chute']:.0%} du plus haut "
                   f"des 3 dernières heures. Si tu veux vendre, c'est maintenant"
                   + (f" (seuil de rentabilité {fmt(l['seuil'])})." if l.get("seuil") else "."))
            if _once(con, f"pos_chute|{result['server']}|{l['item_id']}|{day}", msg):
                msgs.append(msg)
        if (l.get("ecoulement_h") or 0) > 24:
            msg = (f"🐢 **Stock long à écouler** [{sname}] {l['nom']} : ~{l['ecoulement_h']:.0f} h au rythme actuel des ventes "
                   f"({l['annonces']} annonces devant toi). Mets moins d'annonces à la fois, ou garde le reste en stock.")
            if _once(con, f"pos_lent|{result['server']}|{l['item_id']}|{day}", msg):
                msgs.append(msg)
    return msgs


def detect_flips(con, cfg, result):
    """Item a acheter maintenant : prix actuel sous le prix d'achat cible, et assez de kinah/j a la cle."""
    a = cfg["alerts"]
    srv = con.execute("SELECT name FROM servers WHERE id = ?", (result["server"],)).fetchone()
    sname = srv["name"] if srv else result["server"]
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    msgs = []
    for f in result["flips"]:
        if not f["acheter"] or f["profit_j"] < a["flip_min_profit_day"] or not safe(f):
            continue
        lots = f" ({f['nb_lots_j']} annonce(s) de {fmt(f['lot_vente'])})" if f.get("nb_lots_j") else ""
        msg = (f"🔁 **Flip** [{sname}] {f['objet']} à **{fmt(f['prix'])}** (achat cible {fmt(f['achat_cible'])}) → "
               f"revendre ~{fmt(f['revente_cible'])}{lots}, net **{fmt(f['net_u'])}/u** (+{f['marge']:.0%}), "
               f"~{fmt(f['ma_part_j'])}/j → {fmt(f['profit_j'])}/j — {f['annonces']} annonce(s){surete_txt(f)}")
        if _once(con, f"flip|{result['server']}|{f['item_id']}|{day}", msg):
            msgs.append(msg)
    return msgs


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
        if it.get("bound") or m.listings.get(iid, 0) < 2 or not m.ref(iid):    # 1 seule annonce : prix peu fiable
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
    return "\n".join(lines)


def digest(con, cfg, result, top=8):
    srv = con.execute("SELECT name FROM servers WHERE id = ?", (result["server"],)).fetchone()
    sname = srv["name"] if srv else result["server"]
    lines = [f"📊 **Résumé du jour : {sname}** (prix de {paris(result['as_of'], '%H:%M')} heure de Paris, ventes mesurées sur le serveur)",
             "", "**Ma récolte → craft → vente** (profit par jour à 20 % des ventes mesurées)"]
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
    flips = result.get("flips") or []
    if flips:
        lines += ["", "**Achat → revente (flip)**"]
        for f in flips[:5]:
            lines.append(f"• {f['objet']} : acheter ≤ {fmt(f['achat_cible'])}, revendre ~{fmt(f['revente_cible'])}, "
                         f"net {fmt(f['net_u'])}/u → {fmt(f['profit_j'])}/j" + (" ✅ prix d'achat atteint" if f["acheter"] else ""))
    if result["plan"]:
        lines += ["", "**Plan de production pour ta récolte**"]
        for p in result["plan"]:
            lines.append(f"• {p['quantite_j']} × {p['objet']} à ~{fmt(p['prix_conseille'])} → {fmt(p['kinah_j'])}/j")
    official = con.execute("SELECT title, url, posted FROM news WHERE key NOT LIKE 'reddit|%' "
                           "ORDER BY posted DESC LIMIT 3").fetchall()
    if official:
        lines += ["", "**Dernières annonces officielles**"]
        # <lien> : pas d'apercu Discord pour chaque lien du resume
        lines += [f"• {paris(n['posted'], '%d/%m')} {n['title']} <{n['url']}>" for n in official]
    return "\n".join(lines)
