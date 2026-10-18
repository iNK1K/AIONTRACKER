"""Moteur d'analyse : rentabilite x volume, recolte -> craft, achat -> craft -> revente, cibles de recolte."""
import json
import math
import statistics
from datetime import datetime, timedelta, timezone

from .catalog import node_name
from .collect import PARIS, paris

# types d'equipement (harmonisation : meme rang et meme type)
EQUIP_TYPES = {"Sword": "Épée", "Greatsword": "Espadon", "Dagger": "Dague", "Bow": "Arc", "Mace": "Masse", "Staff": "Bâton",
               "Orb": "Orbe", "Magicbook": "Grimoire", "Guarder": "Bouclier", "Helmet": "Casque", "Shoulder": "Épaulières",
               "Torso": "Plastron", "Pants": "Jambières", "Gloves": "Gants", "Boots": "Bottes", "Cape": "Cape",
               "Necklace": "Collier", "Earring": "Boucle d'oreille", "Ring": "Anneau", "Bracelet": "Bracelet",
               "Belt": "Ceinture", "Amulet": "Amulette"}

# equivalences Asmodiens -> Elyseens (Kaisinel, serveur de reference, est elyseen)
ELYOS_EQ = [("Asvata", "Yggdrasil"), ("conide", "l'inina"), ("pujery", "cypri"), ("d'ohkra", "de kukuru"),
            ("dragon noir", "dragon blanc")]


def _dt(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def elyos_equivalent(con, item_id):
    it = con.execute("SELECT base_name FROM items WHERE id = ?", (item_id,)).fetchone()
    if not it:
        return None
    name = it["base_name"]
    for a, b in ELYOS_EQ:
        name = name.replace(a, b)
    name = name.replace("Pâtes de l'inina", "Pâtes à l'inina")
    if name == it["base_name"]:
        return None
    r = con.execute("SELECT id FROM items WHERE name = ? AND bound = 0", (name,)).fetchone()
    return r["id"] if r else None


class Market:
    def __init__(self, con, cfg, server):
        self.con, self.cfg, self.server = con, cfg, str(server)
        ref = con.execute("SELECT ax_id FROM servers WHERE id = ?", (cfg["reference_server"],)).fetchone()
        self.ref_ax = ref["ax_id"] if ref else 11304
        self.items = {r["id"]: dict(r) for r in con.execute("SELECT * FROM items")}
        # nom -> item echangeable ; plusieurs objets peuvent porter le meme nom : on prefere celui vu en vente
        self.by_base = {}
        for it in sorted(self.items.values(), key=lambda i: not i.get("on_market")):
            if not it["bound"]:
                self.by_base.setdefault(it["base_name"], it["id"])
        self._load_prices()
        self._ref = {}
        self._usual = {}
        self._sales = {}
        self.ratio = self._activity_ratio()
        srow = con.execute("SELECT faction FROM servers WHERE id = ?", (self.server,)).fetchone()
        self.faction = (srow["faction"] if srow else "").lower()      # 'asmodian' / 'elyos'
        self.recipes_by_item = {}
        for r in con.execute("SELECT * FROM recipes WHERE method='craft' AND visible=1 AND combo_result=0"):
            if r["faction"] and self.faction and r["faction"].lower() != self.faction:
                continue                                              # recette de l'autre faction
            self.recipes_by_item.setdefault(r["item_id"], []).append(dict(r))
        self.ingredients = {}
        for ri in con.execute("SELECT * FROM recipe_ingredients ORDER BY recipe_id, slot, is_alternative"):
            self.ingredients.setdefault(ri["recipe_id"], {}).setdefault(ri["slot"], []).append(dict(ri))
        # transmutation : 1 Od -> 1 ressource de meme rarete, gratuite, sans echec, non liee (verifie en jeu)
        self.transmute = {}                                   # ressource (nom de base) -> id de l'Od source
        for r in con.execute("SELECT r.faction, i.base_name AS target, j.id AS src FROM recipes r "
                             "JOIN items i ON i.id = r.item_id JOIN recipe_ingredients ri ON ri.recipe_id = r.id "
                             "JOIN items j ON j.id = ri.item_id WHERE r.method = 'convert' AND j.is_gather = 1 AND j.bound = 0"):
            if not r["faction"] or not self.faction or r["faction"].lower() == self.faction:
                self.transmute[r["target"]] = r["src"]

    # ------------------------------------------------------------ donnees de marche
    def _load_prices(self):
        last = self.con.execute("SELECT MAX(ts) AS ts FROM quotes WHERE server = ?", (self.server,)).fetchone()["ts"]
        self.as_of = last
        self.price, self.listings = {}, {}
        if not last:
            return
        since = (_dt(last) - timedelta(hours=3)).isoformat()[:19]
        for r in self.con.execute("""SELECT item_id, price, listings FROM quotes q
                                     WHERE server = ? AND ts = (SELECT MAX(ts) FROM quotes q2
                                       WHERE q2.server = q.server AND q2.item_id = q.item_id AND q2.ts >= ?)""",
                                  (self.server, since)):
            self.price[r["item_id"]] = r["price"]
            self.listings[r["item_id"]] = r["listings"]

    def price_series(self, item_id, days=7):
        """Prix plancher recents [(ts, prix)] : releves horaires (quotes) + historique aion2.exchange."""
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()[:19]
        rows = [(r["ts"], r["price"]) for r in self.con.execute(
            "SELECT ts, price FROM quotes WHERE server=? AND item_id=? AND ts>=?", (self.server, item_id, since))]
        srv = self.con.execute("SELECT ax_id FROM servers WHERE id=?", (self.server,)).fetchone()
        if srv and srv["ax_id"]:
            rows += [(r["ts"][:19], r["avg"]) for r in self.con.execute(
                "SELECT ts, avg FROM ax_prices WHERE ax_server=? AND item_id=? AND ts>=? AND avg IS NOT NULL",
                (srv["ax_id"], item_id, since))]
        return rows

    def price_stats(self, item_id, days=7):
        """Mediane, plus bas et nombre de releves des prix plancher recents."""
        vals = [p for _, p in self.price_series(item_id, days)]
        return dict(median=statistics.median(vals), low=min(vals), n=len(vals)) if vals else None

    def my_listings(self):
        """Mes annonces (mes_annonces.json) face au prix le plus bas actuel. Une annonce peut etre un simple prix,
        ou {"prix": .., "cout": .., "quantite": ..} : avec le cout de revient, on calcule le seuil de rentabilite."""
        fees, out = self.cfg["fees"], []
        for name, v in (self.cfg.get("my_listings") or {}).items():
            v = v if isinstance(v, dict) else {"prix": v}
            mine, cost, qty = v.get("prix"), v.get("cout"), v.get("quantite")
            iid = self.by_base.get(name.strip())
            floor = self.price.get(iid) if iid else None
            seuil = math.ceil(cost / (1 - fees)) if cost else None
            # prix conseille pour repasser devant : 1 sous le plus bas, s'il reste au-dessus du seuil
            conseil = floor - 1 if floor is not None and mine and floor < mine and (not seuil or floor - 1 >= seuil) else None
            out.append(dict(nom=name, item_id=iid, mon_prix=mine, cout=cost, quantite=qty, plancher=floor,
                            annonces=self.listings.get(iid, 0), seuil=seuil, conseil=conseil,
                            battu=floor is not None and mine is not None and floor < mine,
                            ecart=(mine - floor) if floor is not None and mine else None,
                            sous_seuil=bool(seuil and floor is not None and floor < seuil),
                            marge_u=round(floor * (1 - fees) - cost) if cost and floor is not None else None,
                            chute=self.price_drop(iid) if iid else None))
        return out

    def real_gains(self):
        """Mes vraies ventes (mes_ventes.json, lues sur les captures de l'historique en jeu) face aux estimations de
        l'outil : ventes par jour, part de marche, prix obtenu, taille des achats. Une ligne de l'historique = un achat
        (un acheteur peut prendre une partie d'une annonce). Les rythmes ne sont calcules qu'a partir de 3 ventes d'un
        meme objet, sur sa propre periode : (n - 1) achats entre le premier et le dernier."""
        sales = []
        for v in self.cfg.get("my_sales") or []:
            try:
                t = datetime.strptime(v["date"], "%Y-%m-%d %H:%M").replace(tzinfo=PARIS or timezone.utc).astimezone(timezone.utc)
            except (KeyError, ValueError):
                continue
            if v.get("objet") and v.get("prix"):
                sales.append(dict(v, t=t))
        if not sales:
            return None
        start, end = min(s["t"] for s in sales), max(s["t"] for s in sales)
        days = max(1.0, (end - start).total_seconds() / 86400)
        share, fees = self.cfg["market_share"], self.cfg["fees"]
        costs = {n: v.get("cout") for n, v in (self.cfg.get("my_listings") or {}).items() if isinstance(v, dict)}
        items = {}
        for s in sales:
            it = items.setdefault(s["objet"], dict(objet=s["objet"], item_id=self.by_base.get(s["objet"]), lots=0,
                                                   unites=0, brut=0, recu=0, ts=[]))
            q = s.get("quantite") or 1
            it["lots"] += 1; it["unites"] += q; it["brut"] += s["prix"]; it["ts"].append(s["t"])
            it["recu"] += s.get("recu") or math.floor(s["prix"] * (1 - fees))
        out = []
        for it in items.values():
            iid, ts = it["item_id"], sorted(it.pop("ts"))
            a, b = ts[0], ts[-1]
            span = (b - a).total_seconds() / 86400
            it.update(prix_u=it["brut"] / it["unites"], recu_u=it["recu"] / it["unites"], achat_moyen=it["unites"] / it["lots"],
                      debut=a, fin=b, unites_j=None, achats_j=None, recu_j=None)
            if it["lots"] >= 3 and span >= 0.5:
                k = (it["lots"] - 1) / it["lots"] / span        # rythme sans biais : n - 1 intervalles sur la periode
                it.update(unites_j=it["unites"] * k, achats_j=it["lots"] * k, recu_j=it["recu"] * k)
            # estimations de l'outil sur la meme periode (marche mesure : annonces disparues x taille des annonces)
            mk = lot = None
            if iid:
                r = self.con.execute("SELECT AVG(drops_h) AS d, COUNT(*) AS n FROM activity WHERE server=? AND item_id=? "
                                     "AND ts>=? AND ts<=?", (self.server, iid, a.isoformat()[:19],
                                                             (b + timedelta(hours=24)).isoformat()[:19])).fetchone()
                mk = r["d"] * 24 if r and r["n"] and r["d"] else None
                lot = self.lot_size(iid)
            it["lot_outil"] = lot
            it["marche_unites_j"] = mk * lot if mk and lot else None
            it["estime_unites_j"] = it["marche_unites_j"] * share if it["marche_unites_j"] else None
            it["part"] = it["unites_j"] / it["marche_unites_j"] if it["unites_j"] and it["marche_unites_j"] else None
            # prix : ce que le marche payait pendant la periode (ventes observees sur les releves horaires)
            seen = self.sale_prices(iid, (b - a).total_seconds() / 3600 + 24, until=b + timedelta(hours=1)) if iid else []
            it["prix_marche"] = statistics.median(seen) if len(seen) >= 3 else None
            cost = costs.get(it["objet"])
            it["cout"] = cost
            it["marge_u"] = it["recu_u"] - cost if cost else None
            out.append(it)
        out.sort(key=lambda x: -x["recu"])
        # calibrage, sur les objets vendus au moins 3 fois
        cal = [x for x in out if x["unites_j"]]
        ratio = [x["unites_j"] / x["estime_unites_j"] for x in cal if x["estime_unites_j"]]
        parts = [x["part"] for x in cal if x["part"]]
        prix = [x["prix_u"] / x["prix_marche"] for x in cal if x["prix_marche"]]
        achat = [(x["achat_moyen"], x["lot_outil"]) for x in cal if x["lot_outil"]]
        return dict(items=out, debut=start, fin=end, jours=days, ventes=len(sales), recu=sum(x["recu"] for x in out),
                    recu_j=sum(x["recu"] for x in out) / days, part_supposee=share,
                    part=statistics.median(parts) if parts else None,
                    ratio=statistics.median(ratio) if ratio else None,
                    prix_ratio=statistics.median(prix) if prix else None,
                    achat=statistics.median(a / l for a, l in achat) if achat else None, n_cal=len(cal))

    def price_drop(self, item_id, hours=3):
        """Chute en cours : prix actuel compare au plus haut des dernieres heures (None si pas de chute nette)."""
        now = self.price.get(item_id)
        since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()[:19]
        recent = [p for t, p in self.price_series(item_id, 1) if t >= since]
        if not now or not recent:
            return None
        top = max(recent)
        return round(now / top, 2) if now <= 0.75 * top else None

    def flips(self, days=3):
        """Achat-revente sans craft : acheter au bas de la fourchette habituelle (1er quartile des prix plancher sur
        3 j), revendre au prix median, apres frais. Ecarte le brut (invendable), les items sans volume de reference et
        ceux dont le prix suit une tendance (mediane des dernieres 24 h a plus de 25-33 % de celle d'avant)."""
        a, fees = self.cfg["alerts"], self.cfg["fees"]
        cut = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()[:19]
        out = []
        for iid, price in self.price.items():
            it = self.items.get(iid) or {}
            if it.get("bound") or it.get("is_gather"):
                continue
            rows = self.price_series(iid, days)
            if len(rows) < a["flip_min_samples"]:
                continue                              # historique trop court pour une fourchette de prix
            old, new = [p for t, p in rows if t < cut], [p for t, p in rows if t >= cut]
            if old and new and not 0.75 <= statistics.median(new) / statistics.median(old) <= 1.33:
                continue
            q1, med, _ = statistics.quantiles([p for _, p in rows], n=4)
            sl = self.sales(iid)
            net_u = med * (1 - fees) - q1
            if not sl or sl["source"] != "serveur" or q1 <= 0 or net_u / q1 < a["flip_min_margin"]:
                continue                              # flip seulement sur des ventes mesurees sur mon serveur
            mine = sl["units"] * self.cfg["market_share"]
            out.append(dict(item_id=iid, objet=it["name"], prix=price, achat_cible=round(q1), revente_cible=round(med),
                            net_u=round(net_u), marge=round(net_u / q1, 3), ma_part_j=round(mine),
                            profit_j=round(mine * net_u), capital_j=round(mine * q1), annonces=self.listings.get(iid, 0),
                            acheter=price <= q1, releves=len(rows), **self.sizing(iid, mine)))
        out.sort(key=lambda f: -f["profit_j"])
        return out

    def median_price(self, item_id, days=7):
        st = self.price_stats(item_id, days)
        return st["median"] if st else None

    def uniques(self, days=7):
        """Equipements Unique en vente (armes, armures, accessoires : ce qui sert a l'harmonisation, qui consomme une piece
        de meme rang et de meme type) : prix actuel compare a la mediane des 7 derniers jours, les moins chers d'abord."""
        out = []
        for iid, price in self.price.items():
            it = self.items.get(iid) or {}
            if it.get("grade") != "Unique" or it.get("bound") or it.get("category") != "Equip":
                continue
            st = self.price_stats(iid, days)
            if not st or not st["median"]:
                continue
            out.append(dict(item_id=iid, objet=it["name"], categorie=EQUIP_TYPES.get(it.get("sub_category"), it.get("sub_category")),
                            prix=price, annonces=self.listings.get(iid, 0), mediane=round(st["median"]),
                            plus_bas=st["low"], releves=st["n"], ratio=round(price / st["median"], 3)))
        out.sort(key=lambda u: u["ratio"])
        return out

    def ref(self, item_id):
        """Volume quotidien et prix moyen de vente sur le serveur de reference."""
        if item_id in self._ref:
            return self._ref[item_id]
        res = None
        for iid in (item_id, elyos_equivalent(self.con, item_id)):
            if not iid:
                continue
            rows = [dict(r) for r in self.con.execute(
                "SELECT * FROM ref_volume WHERE ax_server=? AND item_id=? ORDER BY registered", (self.ref_ax, iid))]
            rows = [r for r in rows if r["units_sold"] is not None]
            if not rows or not rows[-1]["units_sold"]:
                continue
            last = rows[-1]
            first = next(r for r in rows if r["units_sold"])
            eff_days = min(28.0, (_dt(last["registered"]) - _dt(first["registered"])).days + 1.0)
            recent = [r for r in rows if _dt(r["registered"]) > _dt(last["registered"]) - timedelta(days=7)
                      and r["units_delta"] is not None and r["days_since_previous"]]
            if eff_days < 28 and len(recent) >= 3:
                daily = sum(r["units_delta"] for r in recent) / sum(r["days_since_previous"] for r in recent)
            else:
                daily = last["units_sold"] / eff_days
            # prix moyen sur ~7 jours, deduit des moyennes glissantes
            avg = last["avg_price"]
            old = [r for r in rows if _dt(r["registered"]) <= _dt(last["registered"]) - timedelta(days=7)]
            if old and old[-1]["units_sold"] and last["units_sold"] > old[-1]["units_sold"] and old[-1]["avg_price"]:
                o = old[-1]
                w = (last["avg_price"] * last["units_sold"] - o["avg_price"] * o["units_sold"]) / (last["units_sold"] - o["units_sold"])
                if w > 0:
                    avg = w
            res = dict(daily=max(daily, 0.0), avg_price=avg, ref_item=iid, as_of=last["registered"])
            break
        self._ref[item_id] = res
        return res

    def _drops_per_day(self, server, item_id, days=7):
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()[:19]
        r = self.con.execute("SELECT AVG(drops_h) AS d, COUNT(*) AS n FROM activity WHERE server=? AND item_id=? AND ts>=?",
                             (str(server), item_id, since)).fetchone()
        return r["d"] * 24 if r and r["n"] and r["d"] is not None else None

    def lot_size(self, item_id):
        """Taille moyenne d'une annonce vendue = unites vendues par jour / annonces disparues par jour, les deux mesures
        sur le serveur de reference (seul serveur dont le jeu publie les unites vendues). C'est une habitude des
        vendeurs (taille des piles mises en vente), pas une demande : elle se transpose d'un serveur a l'autre."""
        ref = self.ref(item_id)
        if not ref or not ref["daily"]:
            return None
        drops = self._drops_per_day(self.cfg["reference_server"], ref["ref_item"])
        return max(1, round(ref["daily"] / drops)) if drops and drops >= 3 else None

    def sales(self, item_id):
        """Ventes par jour sur MON serveur, mesurees : annonces disparues sur 24 h x taille des annonces.
        A defaut de mesure sur mon serveur : ventes de Kaisinel x activite relative (extrapolation, signalee)."""
        if item_id in self._sales:
            return self._sales[item_id]
        res = None
        drops = self._drops_per_day(self.server, item_id, days=1.25)
        if drops is not None:
            lot = self.lot_size(item_id)
            res = dict(units=drops * (lot or 1), listings=drops, lot=lot, source="serveur")
        else:
            ref = self.ref(item_id)
            if ref and ref["daily"]:
                res = dict(units=ref["daily"] * self.ratio, listings=None, lot=None, source="Kaisinel")
        self._sales[item_id] = res
        return res

    def hourly_profile(self, days=7):
        """Part des ventes par heure (heure de Paris) : annonces disparues d'une heure a l'autre, tous items confondus
        (historique horaire aion2.exchange). None tant qu'il n'y a pas assez de donnees."""
        srv = self.con.execute("SELECT ax_id FROM servers WHERE id=?", (self.server,)).fetchone()
        if not srv or not srv["ax_id"]:
            return None
        since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        tz = PARIS or timezone.utc
        sold = [0.0] * 24
        # nombre d'annonces heure par heure : historique horaire d'aion2.exchange + nos releves horaires du marche
        hourly = {}
        for r in self.con.execute("SELECT item_id, ts, listings FROM ax_prices WHERE ax_server=? AND bucket='1h' "
                                  "AND ts>=? AND listings IS NOT NULL", (srv["ax_id"], since)):
            hourly[(r["item_id"], _dt(r["ts"]).replace(minute=0, second=0))] = r["listings"]
        for r in self.con.execute("SELECT item_id, ts, listings FROM quotes WHERE server=? AND ts>=?",
                                  (self.server, since[:19])):
            hourly[(r["item_id"], _dt(r["ts"] + ("Z" if len(r["ts"]) == 19 else "")).replace(minute=0, second=0))] = r["listings"]
        prev = {}
        for (iid, t), n in sorted(hourly.items()):
            p = prev.get(iid)
            if p and t - p[0] == timedelta(hours=1) and n < p[1]:
                sold[t.astimezone(tz).hour] += p[1] - n
            prev[iid] = (t, n)
        total = sum(sold)
        if total < 200:
            return None
        share = [s / total for s in sold]

        def window(best):
            sums = [(sum(share[(h + k) % 24] for k in range(3)), h) for h in range(24)]
            return (max if best else min)(sums)[1]
        return dict(share=share, best=window(True), low=window(False), sold=round(total), days=days,
                    tz="Paris" if PARIS else "UTC")

    def _activity_ratio(self):
        ref_server = str(self.cfg["reference_server"])
        since = (datetime.now(timezone.utc) - timedelta(hours=30)).isoformat()[:19]

        def latest(server):
            out = {}
            for r in self.con.execute("SELECT item_id, drops_h, ts FROM activity WHERE server=? AND ts>=? ORDER BY ts",
                                      (server, since)):
                out[r["item_id"]] = r["drops_h"]
            return out
        a, b = latest(self.server), latest(ref_server)
        ratios = [a[i] / b[i] for i in a if i in b and b[i] >= 0.5]
        if len(ratios) >= 8:
            return max(0.05, min(3.0, statistics.median(ratios)))
        return 0.40

    # ------------------------------------------------------------ prix d'achat / de vente
    def sale_prices(self, item_id, hours, until=None):
        """Prix des ventes observees : quand le nombre d'annonces baisse d'une heure a l'autre, les annonces parties
        l'ont ete au prix le plus bas de l'heure precedente (une valeur par annonce disparue). Fenetre : les `hours`
        heures avant `until` (maintenant par defaut)."""
        end = until or datetime.now(timezone.utc)
        since = (end - timedelta(hours=hours)).isoformat()[:19]
        stop = end.isoformat()[:19]
        hourly = {}
        srv = self.con.execute("SELECT ax_id FROM servers WHERE id=?", (self.server,)).fetchone()
        if srv and srv["ax_id"]:
            for r in self.con.execute("SELECT ts, close, listings FROM ax_prices WHERE ax_server=? AND bucket='1h' "
                                      "AND item_id=? AND ts>=? AND ts<=?", (srv["ax_id"], item_id, since, stop)):
                hourly[r["ts"][:13]] = (r["close"], r["listings"])
        for r in self.con.execute("SELECT ts, price, listings FROM quotes WHERE server=? AND item_id=? AND ts>=? AND ts<=?",
                                  (self.server, item_id, since, stop)):
            hourly[r["ts"][:13]] = (r["price"], r["listings"])
        pts, out = sorted(hourly.items()), []
        for (_, (p0, l0)), (_, (p1, l1)) in zip(pts, pts[1:]):
            if p0 and l0 is not None and l1 is not None and l1 < l0:
                out += [p0] * int(l0 - l1)
        return out

    def usual_price(self, item_id):
        """Prix habituel sur MON serveur = prix auquel l'item se vend vraiment : mediane des prix des ventes observees
        sur 48 h (au moins 5), sinon 7 jours. Un pic ou l'on n'achete pas compte peu ; un vrai changement de niveau est
        suivi. A defaut : mediane des prix plancher sur 7 jours hors jours en pic, puis prix moyen de Kaisinel."""
        if item_id not in self._usual:
            res = None
            for hours in (48, 168):
                sold = self.sale_prices(item_id, hours)
                if len(sold) >= 5:
                    res = dict(price=statistics.median(sold), source="ventes", sales=len(sold), hours=hours)
                    break
            if not res:
                rows = self.price_series(item_id, 7)
                if len(rows) >= 12:
                    days = {}
                    for ts, p in rows:
                        days.setdefault(ts[:10], []).append(p)
                    dmed = {d: statistics.median(v) for d, v in days.items()}
                    m = statistics.median(dmed.values())
                    kept = [p for d, v in days.items() if dmed[d] <= 1.6 * m for p in v]
                    res = dict(price=statistics.median(kept or [p for _, p in rows]), source="serveur")
                else:
                    ref = self.ref(item_id)
                    if ref and ref["avg_price"]:
                        res = dict(price=ref["avg_price"], source="Kaisinel")
            self._usual[item_id] = res
        return self._usual[item_id]

    def spike_since(self, item_id, usual):
        """Depuis quand le prix affiche est au moins 1,5x le prix habituel (debut du pic en cours)."""
        since = None
        for ts, p in sorted(self.price_series(item_id, 3), reverse=True):
            if p < 1.5 * usual:
                break
            since = ts
        return since

    def buy_price(self, item_id):
        iid = item_id
        if iid not in self.price:
            it = self.items.get(iid)
            iid = self.by_base.get(it["base_name"]) if it else None
            if iid not in self.price:
                return None
        ask = self.price[iid]
        u = self.usual_price(iid)
        k = u["price"] if u else None
        real, pess = ask, ask * 1.5
        if k:
            if ask < k:
                real = (ask + k) / 2
            pess = max(ask, k)
        return dict(item_id=iid, ask=ask, real=real, pess=pess, listings=self.listings.get(iid, 0))

    def last_seen(self, item_id, days=3):
        """Dernier prix plancher connu d'un item qui n'est plus en vente : (ts, prix), ou None."""
        rows = sorted(self.price_series(item_id, days))
        return rows[-1] if rows else None

    def sell_price(self, item_id):
        ask, stale = self.price.get(item_id), None
        if ask is None:
            # plus en vente en ce moment : dernier prix connu (3 j), pour pouvoir comparer quand meme
            seen = self.last_seen(item_id)
            if not seen:
                return None
            stale, ask = seen
        u = self.usual_price(item_id)
        k = u["price"] if u else None
        real = (ask + k) / 2 if (k and ask > k) else ask
        pess = min(real, k) if k else real * 0.7
        return dict(ask=ask, real=real, pess=pess, ref=k, ref_source=u and u["source"],
                    listings=self.listings.get(item_id, 0), stale=stale)

    # ------------------------------------------------------------ cout d'une recette
    def recipe_cost(self, recipe, mode, depth=0, skip=(), trans="auto"):
        """mode 'harvest' : ressources de recolte gratuites ; mode 'buy' : tout s'achete a l'HDV.
        skip : ingredients deja en main (ex. l'objet eclatant de l'etape precedente d'une chaine), non comptes.
        trans : 'auto' = le moins cher entre la ressource et l'Od a transmuter ; 'off' = achat direct seulement ;
        'force' = l'Od transmute des qu'il est achetable (pour comparer les deux facons d'acheter)."""
        npc = self.cfg["npc_reagent_price"]
        cost_r = cost_p = 0.0
        lines, gather, buys, thin_list = [], {}, {}, []
        ok = True
        for slot, opts in sorted(self.ingredients.get(recipe["id"], {}).items()):
            if any(o["item_id"] in skip for o in opts):
                continue
            gopt = next((o for o in opts if self.items.get(o["item_id"], {}).get("is_gather")), None)
            if gopt and mode == "harvest":
                base = self.items[gopt["item_id"]]["base_name"]
                gather[base] = gather.get(base, 0) + gopt["qty"]
                lines.append(f"{base} x{gopt['qty']:g} (récolte)")
                continue
            best = None
            for thin_ok in (False, True):          # d'abord les ingredients achetables en volume (>= 2 annonces)
                for o in opts:
                    # la ressource elle-meme, ou l'Od de meme rarete a transmuter (1 pour 1)
                    target = self.items.get(o["item_id"], {}).get("base_name")
                    od = self.transmute.get(target) if trans != "off" else None
                    cands = ((od, target),) if trans == "force" and od and self.buy_price(od) else \
                        ((o["item_id"], None), (od, target))
                    for src, via in cands:
                        bp = self.buy_price(src) if src else None
                        if bp and (thin_ok or bp["listings"] >= 2):
                            c = bp["real"] * o["qty"]
                            if best is None or c < best[0]:
                                best = (c, bp["pess"] * o["qty"], o, bp, via)
                if best:
                    break
            if best:
                cost_r += best[0]
                cost_p += best[1]
                name = self.items[best[3]["item_id"]]["name"]
                buys[best[3]["item_id"]] = buys.get(best[3]["item_id"], 0) + best[2]["qty"]
                thin = best[3]["listings"] <= 1
                if thin:
                    thin_list.append(name)
                lines.append(f"{name} x{best[2]['qty']:g} @{best[3]['real']:,.0f}".replace(",", " ")
                             + (f" → transmuté en {best[4]}" if best[4] else "") + (" (1 annonce)" if thin else ""))
                continue
            o = opts[0]
            it = self.items.get(o["item_id"], {})
            if it.get("is_gather") and mode == "buy":
                ok = False
                lines.append(f"{it.get('base_name')} x{o['qty']:g} INTROUVABLE")
                continue
            sub = self.recipes_by_item.get(self.by_base.get(it.get("base_name")) or o["item_id"]) or \
                self.recipes_by_item.get(o["item_id"])
            if depth == 0 and not sub:
                # version liee : chercher la recette de l'objet de meme nom
                for rid_item, rs in self.recipes_by_item.items():
                    if self.items.get(rid_item, {}).get("base_name") == it.get("base_name"):
                        sub = rs
                        break
            if depth == 0 and sub:
                sc = self.recipe_cost(sub[0], mode, depth + 1, trans=trans)
                per = o["qty"] / (sub[0]["output_qty"] or 1)
                cost_r += sc["cost_r"] * per
                cost_p += sc["cost_p"] * per
                for g, q in sc["gather"].items():
                    gather[g] = gather.get(g, 0) + q * per
                for b, q in sc["buys"].items():
                    buys[b] = buys.get(b, 0) + q * per
                thin_list += sc["thin"]
                ok = ok and sc["ok"]
                lines.append(f"[{it.get('base_name')} x{o['qty']:g} à fabriquer : {', '.join(sc['lines'])}]")
            else:
                cost_r += npc * o["qty"]
                cost_p += npc * o["qty"]
                lines.append(f"{it.get('base_name')} x{o['qty']:g} PNJ ~{npc}")
        return dict(cost_r=cost_r, cost_p=cost_p, lines=lines, gather=gather, buys=buys, ok=ok, thin=thin_list)

    # ------------------------------------------------------------ evaluation
    def evaluate(self, recipe, mode, trans="auto"):
        oid = recipe["item_id"]
        sp = self.sell_price(oid)
        ref = self.ref(oid)
        if not sp:
            return None
        masteries = self.cfg.get("masteries", {})
        if (recipe["mastery"] or 0) > masteries.get(recipe["profession"], 999):
            return None
        c = self.recipe_cost(recipe, mode, trans=trans)
        if not c["ok"] or (trans == "force" and not any("transmuté" in l for l in c["lines"])):
            return None                                  # 'force' : seulement les crafts ou l'Od sert vraiment
        q = recipe["output_qty"] or 1
        fees = self.cfg["fees"]
        cost_u, cost_pu = c["cost_r"] / q, c["cost_p"] / q
        net_u = sp["real"] * (1 - fees) - cost_u
        net_pu = sp["pess"] * (1 - fees) - cost_pu
        # ventes mesurees sur mon serveur ; extrapolation depuis Kaisinel seulement a defaut (signalee)
        sl = self.sales(oid)
        vol = sl["units"] if sl else 0
        mine = vol * self.cfg["market_share"]
        res_u = sum(c["gather"].values()) / q
        flags = []
        if not sl:
            flags.append("volume de vente inconnu (aucune mesure)")
        elif sl["source"] == "Kaisinel":
            flags.append("ventes non mesurées sur ton serveur (extrapolées de Kaisinel)")
        elif sl["lot"] is None and sl["listings"]:
            flags.append("taille des annonces inconnue (comptée 1 par annonce)")
        if sp["stale"]:
            flags.append(f"pas en vente en ce moment (dernier prix connu le {paris(sp['stale'], '%d/%m %H:%M')})")
        elif sp["listings"] <= 1:
            flags.append("1 seule annonce en vente")
        if sp["ref"] and sp["ask"] > 5 * sp["ref"]:
            flags.append("prix affiché > 5x le prix habituel")
        if c["thin"]:
            flags.append("ingrédient introuvable en volume : " + ", ".join(sorted(set(c["thin"]))))
        return dict(
            mode=mode, recipe_id=recipe["id"], item_id=oid, objet=self.items[oid]["name"],
            metier=recipe["profession"], maitrise=recipe["mastery"], lot=q,
            ingredients=c["lines"], ressources={k: v / q for k, v in c["gather"].items()},
            achats_u=round(cost_u), achats_pess_u=round(cost_pu),
            prix_affiche=sp["ask"], prix_ref=sp["ref"] and round(sp["ref"]), prix_real=round(sp["real"]),
            annonces=sp["listings"], net_u=round(net_u), net_pess_u=round(net_pu), ref_source=sp["ref_source"],
            net_affiche_u=round(sp["ask"] * (1 - fees) - cost_u),
            marge=round(net_u / cost_u, 3) if cost_u > 0 else None,
            ressources_u=res_u, net_par_ressource=round(net_u / res_u) if res_u else None,
            vol_serveur_j=round(vol), ma_part_j=round(mine), vol_source=sl and sl["source"],
            annonces_vendues_j=round(sl["listings"], 1) if sl and sl["listings"] is not None else None,
            profit_j=round(mine * net_u), profit_pess_j=round(mine * net_pu),
            capital_j=round(mine * cost_u), flags=flags, **self.sizing(oid, mine))

    def spikes(self, buy_rows):
        """Pics de prix : achat -> craft rentable au prix affiche, mais pas au prix habituel (prix en pic depuis peu).
        Opportunites courtes et risquees : a vendre vite, en petite quantite."""
        a = self.cfg["alerts"]
        out = []
        for e in buy_rows:
            u = e["prix_ref"]
            if not u or e["prix_affiche"] < 1.5 * u or not e["achats_u"]:
                continue
            marge = e["net_affiche_u"] / e["achats_u"]
            if marge < a["spike_craft_min_margin"] or e["net_u"] > 0 and not e["flags"]:
                continue                              # pas rentable au prix affiche, ou deja rentable en temps normal
            out.append(dict(e, ratio=round(e["prix_affiche"] / u, 1), marge_affiche=round(marge, 3),
                            net_habituel_u=round(u * (1 - self.cfg["fees"]) - e["achats_u"]),
                            depuis=self.spike_since(e["item_id"], u)))
        out.sort(key=lambda x: -x["net_affiche_u"])
        return out

    def safety(self, e, act, cost, net_usual, since=None):
        """Indice de surete (0-100) d'une opportunite d'achat : peut-on vraiment revendre, et a quel risque ?
        act : activite recente de l'item vendu (nouvelles annonces/h, annonces disparues/h)."""
        score, why = 100, []
        listings = self.listings.get(e["item_id"], 0)
        lot = e.get("lot_vente") or 1
        if act:
            pressure = act["adds_h"] / max(act["drops_h"], 0.1)
            sell_h = listings / max(act["drops_h"], 0.05)
            for lim, pen, txt in ((2, 45, "le stock s'accumule vite"), (1.2, 30, "le stock s'accumule"),
                                  (0.8, 12, "autant d'arrivées que de ventes")):
                if pressure > lim:
                    score -= pen
                    why.append(f"{txt} : {act['adds_h']:.1f} nouvelles annonces/h pour {act['drops_h']:.1f} vendues ({act['window']})")
                    break
            for lim, pen in ((24, 35), (12, 22), (4, 10)):
                if sell_h > lim:
                    score -= pen
                    why.append(f"~{sell_h:.0f} h avant que les {listings} annonces devant toi soient vendues")
                    break
            qmax = 2 * act["drops_h"] * lot                       # ~2 h de ventes du marche
        else:
            score -= 25
            sell_h = None
            why.append("activité du marché inconnue")
            qmax = None
        # plafond : ma part du marche sur 2 h ; pendant un pic, peu d'acheteurs suivent au prix haut
        share = (e.get("ma_part_j") or 0) / 12
        qmax = max(1, round(min(q for q in (qmax, share) if q is not None) / (3 if since else 1))) if (qmax or share) else 1
        if net_usual is not None and net_usual < 0:
            score -= 25
            why.append(f"à perte ({net_usual:,.0f}/u) si le prix revient à la normale".replace(",", " "))
        if since:
            age = (datetime.now(timezone.utc) - _dt(since + ("Z" if len(since) == 19 else ""))).total_seconds() / 3600
            if age > 6:
                score -= 10
                why.append(f"pic vieux de {age:.0f} h : d'autres vendeurs ont eu le temps d'arriver")
        score = max(0, min(100, score))
        return dict(score=score, feu="vert" if score >= 70 else "orange" if score >= 40 else "rouge", raisons=why,
                    qte_max=qmax, prix_plancher=math.ceil(cost / (1 - self.cfg["fees"])) if cost else None,
                    ecoulement_h=round(sell_h, 1) if sell_h is not None else None)

    def gamble_chains(self):
        """Chaines d'amelioration (blanc -> vert -> bleu -> unique) : a chaque etape, le combo donne la version
        « eclatante », seule a pouvoir servir a l'etape suivante. Donnees par etape pour le calcul dans le navigateur
        (reussite selon les niveaux du joueur) : cout des matieres achetees, ressources recoltees, valeur nette de
        vente du resultat normal et du resultat combo, ventes mesurees."""
        fees = self.cfg["fees"]
        combo_cfg = self.cfg.get("combo_rate")
        recs = [r for rs in self.recipes_by_item.values() for r in rs if r["combo_item_id"] and not r["unresolved"]]
        combos = {r["combo_item_id"] for r in recs}
        by_input = {}
        for r in recs:
            for opts in self.ingredients.get(r["id"], {}).values():
                for o in opts:
                    by_input.setdefault(o["item_id"], []).append(r)

        def value(iid):
            u = self.usual_price(iid)
            sl = self.sales(iid)
            return dict(n=self.items[iid]["name"], v=round(u["price"] * (1 - fees)) if u else None,
                        ls=round(sl["listings"], 1) if sl and sl["listings"] is not None else None)
        chains = []
        for r in recs:
            if any(o["item_id"] in combos for opts in self.ingredients.get(r["id"], {}).values() for o in opts):
                continue                                   # pas un debut de chaine
            steps, cur, inp = [], r, None
            while cur and len(steps) < 6:
                c = self.recipe_cost(cur, "harvest", skip={inp} if inp else ())
                plain, ecl = value(cur["item_id"]), value(cur["combo_item_id"])
                steps.append(dict(prof=cur["profession"], m=cur["mastery"] or 0, cv=cur.get("rate_curve"),
                                  c=combo_cfg if combo_cfg is not None else (cur["combo_prob_raw"] or 0) / 10000,
                                  cost=round(c["cost_r"]), res={k: round(v, 2) for k, v in c["gather"].items()},
                                  ok=c["ok"], inp=self.items[inp]["name"] if inp else None, plain=plain, ecl=ecl,
                                  lines=c["lines"]))
                if ecl["v"] is None:
                    break                                  # plus de prix connu : on s'arrete la
                inp = cur["combo_item_id"]
                cur = next((x for x in by_input.get(inp, []) if x["combo_item_id"]), None)
            if len(steps) >= 2 and steps[0]["plain"]["v"] is not None:
                chains.append(dict(name=self.items[r["item_id"]]["name"], steps=steps))
        return chains

    def sizing(self, item_id, per_day):
        """Combien d'annonces poster et de quelle taille, pour ecouler ma part du jour."""
        lot = self.lot_size(item_id)
        if not lot or per_day < 1:
            return dict(lot_vente=lot, nb_lots_j=None)
        lot = min(lot, max(1, round(per_day)))
        return dict(lot_vente=lot, nb_lots_j=max(1, round(per_day / lot)))

    def best_per_item(self, mode, trans="auto"):
        out = []
        for oid, recipes in self.recipes_by_item.items():
            best = None
            for r in recipes:
                if r["unresolved"]:
                    continue
                if mode == "harvest" and not any(self.items.get(o["item_id"], {}).get("is_gather")
                                                  for opts in self.ingredients.get(r["id"], {}).values() for o in opts):
                    continue
                e = self.evaluate(r, mode, trans)
                if e and (best is None or e["profit_j"] > best["profit_j"]):
                    best = e
            if best:
                # toutes les facons de fabriquer l'item (metier, niveau requis, courbe de reussite) : le site choisit
                # celle que le joueur peut faire, selon ses niveaux de metier
                best["alts"] = sorted({(r["profession"], r["mastery"] or 0, r.get("rate_curve"))
                                       for r in recipes if not r["unresolved"]}, key=lambda a: (a[1], a[0]))
                best["vente_net_u"] = round(best["prix_real"] * (1 - self.cfg["fees"]))
                out.append(best)
        out.sort(key=lambda e: -e["profit_j"])
        return out

    def gather_names(self):
        """Toutes les ressources de recolte de ma faction : celles qu'on ne recolte que dans les zones de l'autre
        faction (d'apres les points de recolte de la carte) sont ecartees."""
        other = {"asmodian": "elyos", "elyos": "asmodians"}.get(self.faction)
        zones = {}
        for r in self.con.execute("SELECT DISTINCT g.name, w.grp FROM gather_nodes g JOIN map_worlds w ON w.id = g.world_id"):
            zones.setdefault(r["name"], set()).add(r["grp"])
        names = {it["base_name"] for it in self.items.values() if it["is_gather"] and not it["bound"]}
        return sorted(n for n in names if not (other and zones.get(node_name(n)) == {other}))

    def gather_targets(self, harvest_rows):
        """Pour chaque ressource : meilleur usage (net par ressource) et quantite que le marche absorbe."""
        # toutes les ressources apparaissent ; les usages douteux (drapeaux) ou a perte sont montres apres les fiables
        targets = {}
        for e in harvest_rows:
            if not e["ressources_u"]:
                continue
            for res, per_u in e["ressources"].items():
                net_res = e["net_u"] / e["ressources_u"]
                t = targets.setdefault(res, [])
                t.append(dict(objet=e["objet"], item_id=e["item_id"], net_par_ressource=round(net_res),
                              ressources_j=round(e["ma_part_j"] * per_u), profit_j=e["profit_j"], per_u=per_u,
                              lot=e.get("lot_vente"), fiable=e["net_u"] > 0 and not e["flags"], flags=e["flags"]))
        for target, src in self.transmute.items():
            sname = self.items.get(src, {}).get("base_name")
            if sname and target in targets:
                targets.setdefault(sname, []).extend(
                    dict(u, objet=f"{u['objet']} (Od → {target})", via=target) for u in targets[target])
        out = []
        for res, uses in targets.items():
            uses.sort(key=lambda u: (not u["fiable"], -u["net_par_ressource"]))
            good = [u for u in uses if u["fiable"]]
            out.append(dict(ressource=res, prix_brut=self.price.get(self.by_base.get(res)), usages=uses[:4],
                            meilleur=good[0]["net_par_ressource"] if good else None,
                            absorbable_j=sum(u["ressources_j"] for u in good)))
        out.sort(key=lambda t: (t["meilleur"] is None, -(t["meilleur"] or 0)))
        return out

    def production_plan(self, harvest_rows, harvest):
        """Repartit la recolte quotidienne entre les crafts (glouton par net/ressource), max N produits."""
        stock = {k: float(v) for k, v in (harvest or {}).items()}
        if not stock:
            return []
        cands = [e for e in harvest_rows if e["net_u"] > 0 and not e["flags"] and e["ressources_u"]]
        cands.sort(key=lambda e: -(e["net_u"] / e["ressources_u"]))
        plan = []
        for e in cands:
            if len(plan) >= self.cfg["max_listings"]:
                break
            if any(res not in stock for res in e["ressources"]):
                continue
            n = min([e["ma_part_j"]] + [stock[res] / per for res, per in e["ressources"].items() if per > 0])
            n = int(n)
            if n <= 0:
                continue
            for res, per in e["ressources"].items():
                stock[res] -= n * per
            plan.append(dict(objet=e["objet"], quantite_j=n, prix_conseille=e["prix_real"], net_u=e["net_u"],
                             kinah_j=n * e["net_u"], ressources={r: round(n * p) for r, p in e["ressources"].items()},
                             **self.sizing(e["item_id"], n)))
        return plan


def last_activity(con, server, item_id):
    """Activite 24 h enregistree (repli quand on n'a pas mesure l'activite recente)."""
    since = (datetime.now(timezone.utc) - timedelta(hours=30)).isoformat()[:19]
    r = con.execute("SELECT drops_h, adds_h FROM activity WHERE server=? AND item_id=? AND ts>=? ORDER BY ts DESC LIMIT 1",
                    (str(server), item_id, since)).fetchone()
    return dict(drops_h=r["drops_h"], adds_h=r["adds_h"], window="24 h") if r else None


def watched_items(res, limit=30):
    """Items dont il faut mesurer l'activite recente : opportunites d'achat et mes annonces."""
    ids = [e["item_id"] for e in res["spikes"]] + [e["item_id"] for e in res["buy"] if e["net_u"] > 0 and not e["flags"]][:10]
    ids += [f["item_id"] for f in res["flips"][:10]] + [l["item_id"] for l in res["listings"] if l["item_id"]]
    return list(dict.fromkeys(ids))[:limit]


def add_safety(con, res, acts=None):
    """Ajoute l'indice de surete et les garde-fous aux opportunites (pics, achat -> craft, flips)."""
    m, acts = res["market"], acts or {}
    act = lambda iid: acts.get(iid) or last_activity(con, res["server"], iid)
    fees = m.cfg["fees"]
    for e in res["spikes"]:
        e["surete"] = m.safety(e, act(e["item_id"]), e["achats_u"], e["net_habituel_u"], e.get("depuis"))
    for e in res["buy"] + res.get("buy_direct", []) + res.get("buy_trans", []):
        if e["net_u"] > 0 and not e["flags"] and "surete" not in e:
            usual = e["prix_ref"] * (1 - fees) - e["achats_u"] if e["prix_ref"] else None
            e["surete"] = m.safety(e, act(e["item_id"]), e["achats_u"], usual)
    for f in res["flips"]:
        f["surete"] = m.safety(f, act(f["item_id"]), f["achat_cible"], f["net_u"])
    for l in res["listings"]:
        a = act(l["item_id"]) if l["item_id"] else None
        if a and l.get("quantite"):
            lot = m.lot_size(l["item_id"]) or 1
            l["ecoulement_h"] = round((l["annonces"] + l["quantite"] / lot) / max(a["drops_h"], 0.05), 1)
    return res


def run_all(con, cfg, server=None):
    server = str(server or cfg["my_server"])
    m = Market(con, cfg, server)
    harvest = m.best_per_item("harvest")
    buy = m.best_per_item("buy")
    # achat -> craft en deux facons, pour les comparer : ingredients achetes a l'HDV, ou Od achete puis transmute
    buy_direct, buy_trans = m.best_per_item("buy", "off"), m.best_per_item("buy", "force")
    targets = m.gather_targets(harvest)
    plan = m.production_plan(harvest, cfg.get("harvest_per_day"))
    run_ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    for kind, rows in (("harvest", harvest), ("buy", buy)):
        for e in rows:
            con.execute("INSERT INTO analyses VALUES (?,?,?,?,?,?,?)",
                        (run_ts, server, kind, e["item_id"], e["recipe_id"], e["profit_j"], json.dumps(e, ensure_ascii=False)))
    con.execute("INSERT INTO analyses VALUES (?,?,?,?,?,?,?)",
                (run_ts, server, "targets", None, None, None, json.dumps(targets, ensure_ascii=False)))
    con.execute("INSERT INTO analyses VALUES (?,?,?,?,?,?,?)",
                (run_ts, server, "plan", None, None, None, json.dumps(plan, ensure_ascii=False)))
    con.commit()
    return add_safety(con, dict(run_ts=run_ts, server=server, as_of=m.as_of, ratio=m.ratio, harvest=harvest, buy=buy,
                targets=targets, plan=plan, hours=m.hourly_profile(), uniques=m.uniques(),
                flips=m.flips(), listings=m.my_listings(), gains=m.real_gains() if server == str(cfg["my_server"]) else None, spikes=m.spikes(buy), chains=m.gamble_chains(),
                buy_direct=buy_direct, buy_trans=buy_trans, market=m))
