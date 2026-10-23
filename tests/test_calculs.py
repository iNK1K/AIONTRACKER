"""Tests des calculs cles, sur une petite base fabriquee pour l'occasion (aucun acces reseau, base reelle intacte).

Lancer : python -m unittest discover tests
"""
import shutil
import sqlite3
import subprocess
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from aionhdv import alerts
from aionhdv.analysis import Market
from aionhdv.config import from_journal, lot_state
from aionhdv.db import SCHEMA

ROOT = Path(__file__).resolve().parent.parent
ME = "2315"
BOIS, OD, PLANCHE, PLANCHE_ECL, MEUBLE, MEUBLE_ECL = 1, 2, 10, 11, 20, 21


def ts(hours_ago):
    return (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).isoformat()[:19]


def make_db(prices=None):
    """Bois (recolte) <- Od (transmutation) ; Planche = 2 Bois, combo -> Planche eclatante ;
    Meuble = 1 Planche eclatante + 1 Bois, combo -> Meuble eclatant. 13 releves horaires a prix constant par item :
    prix habituel = ce prix, et aucune annonce disparue (pas de vente observee)."""
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    con.execute("ALTER TABLE recipes ADD COLUMN rate_curve INTEGER")
    con.execute("ALTER TABLE recipes ADD COLUMN fail_gauge INTEGER")
    con.executemany("INSERT INTO servers VALUES (?,?,?,?,?,?)",
                    [(ME, "Zemurru", "EU", "Asmodian", "live", 12315)])
    items = [(BOIS, "Bois", 1), (OD, "Od commun", 1), (PLANCHE, "Planche", 0), (PLANCHE_ECL, "Planche éclatante", 0),
             (MEUBLE, "Meuble", 0), (MEUBLE_ECL, "Meuble éclatant", 0)]
    con.executemany("INSERT INTO items (id, name, grade, is_gather, bound, base_name, on_market) VALUES (?,?,?,?,0,?,1)",
                    [(i, n, "Common", g, n) for i, n, g in items])
    recipes = [("r10", PLANCHE, "craft", PLANCHE_ECL, 250000), ("r20", MEUBLE, "craft", MEUBLE_ECL, 250000),
               ("conv", BOIS, "convert", None, None)]
    con.executemany("INSERT INTO recipes (id, item_id, method, profession, mastery, faction, output_qty, visible, "
                    "combo_result, unresolved, combo_item_id, combo_prob_raw) VALUES (?,?,?,'Handicrafting',1,NULL,1,1,0,0,?,?)",
                    recipes)
    con.executemany("INSERT INTO recipe_ingredients VALUES (?,?,?,?,0)",
                    [("r10", 1, BOIS, 2), ("r20", 1, PLANCHE_ECL, 1), ("r20", 2, BOIS, 1), ("conv", 1, OD, 1)])
    prices = prices or {BOIS: 100, OD: 60, PLANCHE: 1000, PLANCHE_ECL: 3000, MEUBLE: 5000, MEUBLE_ECL: 20000}
    for iid, p in prices.items():
        con.executemany("INSERT INTO quotes VALUES (?,?,?,?,?)", [(ME, iid, ts(h), p, 10) for h in range(13)])
    return con


CFG = dict(my_server=ME, market_share=0.20, fees=0.10, npc_reagent_price=50, combo_rate=None)


def market(con, **cfg):
    return Market(con, dict(CFG, **cfg), ME)


class Transmutation(unittest.TestCase):
    def test_od_moins_cher_est_transmute(self):
        m = market(make_db())
        self.assertEqual(m.transmute, {"Bois": OD})
        c = m.recipe_cost({"id": "r10"}, "buy")
        self.assertEqual(c["cost_r"], 2 * 60)                      # 2 Od a 60 au lieu de 2 Bois a 100
        self.assertTrue(any("transmuté en Bois" in l for l in c["lines"]))

    def test_achat_direct_si_transmutation_coupee(self):
        m = market(make_db())
        self.assertEqual(m.recipe_cost({"id": "r10"}, "buy", trans="off")["cost_r"], 2 * 100)

    def test_ressource_moins_chere_que_od(self):
        m = market(make_db({BOIS: 100, OD: 150, PLANCHE: 1000}))
        self.assertEqual(m.recipe_cost({"id": "r10"}, "buy")["cost_r"], 2 * 100)
        self.assertEqual(m.recipe_cost({"id": "r10"}, "buy", trans="force")["cost_r"], 2 * 150)

    def test_recolte_gratuite(self):
        c = market(make_db()).recipe_cost({"id": "r10"}, "harvest")
        self.assertEqual((c["cost_r"], c["gather"]), (0, {"Bois": 2}))

    def test_reactif_pnj_ou_introuvable(self):
        """Ingredient sans prix ni recette : lie = reactif vendu par un PNJ ; echangeable = introuvable (craft ecarte)."""
        con = make_db()
        con.executemany("INSERT INTO items (id, name, grade, is_gather, bound, base_name) VALUES (?,?,'Common',0,?,?)",
                        [(30, "Sel", 1, "Sel"), (31, "Épaulettes éclatantes", 0, "Épaulettes éclatantes")])
        con.executemany("INSERT INTO recipe_ingredients VALUES (?,?,?,?,0)", [("r10", 2, 30, 1), ("r20", 3, 31, 1)])
        m = market(con)
        c = m.recipe_cost({"id": "r10"}, "harvest")
        self.assertEqual((c["ok"], c["cost_r"]), (True, 50))       # npc_reagent_price du test
        self.assertFalse(m.recipe_cost({"id": "r20"}, "buy")["ok"])


class Ventes(unittest.TestCase):
    def test_ventes_mesurees_sur_le_serveur(self):
        con = make_db()
        con.execute("INSERT INTO activity VALUES (?,?,?,24,2.0,1.0,0.5,100,100)", (ME, PLANCHE, ts(1)))
        s = market(con).sales(PLANCHE)
        self.assertEqual((s["source"], s["listings"], s["units"]), ("serveur", 48, 48))

    def test_taille_des_lots_par_type(self):
        con = make_db()
        con.executemany("INSERT INTO items (id, name, grade, category, bound, base_name, max_stack, is_gather) "
                        "VALUES (?,?,?,?,0,?,?,?)",
                        [(40, "Épée", "Common", "Equip", "Épée", None, 0), (41, "Potion", "Common", "Usable", "Potion", 100, 0),
                         (42, "Ticket", "Common", "Misc", "Ticket", 1, 0), (43, "Bois pur", "Legend", "Misc", "Bois pur", None, 1),
                         (610610013, "Od", "Common", "Misc", "Od", None, 1)])
        con.execute("INSERT INTO activity VALUES (?,?,?,24,2.0,1.0,0.5,100,100)", (ME, BOIS, ts(1)))
        m = market(con, lots={"recolte": [200, 50, 10, 3], "materiau": 10, "consommable": 5})
        self.assertEqual([m.lot_size(i) for i in (BOIS, 43, PLANCHE, 40, 41, 42)], [200, 10, 10, 1, 5, 1])
        self.assertEqual(m.lot_size(610610013), 297)                # mesure de Kaisinel prioritaire
        self.assertEqual(m.sales(BOIS)["units"], 48 * 200)         # annonces disparues x taille estimee

    def test_pas_de_mesure(self):
        self.assertIsNone(market(make_db()).sales(PLANCHE))

    def test_prix_habituel_sans_vente_observee(self):
        u = market(make_db()).usual_price(PLANCHE)
        self.assertEqual((u["price"], u["source"]), (1000, "serveur"))

    def test_prix_habituel_depuis_les_ventes(self):
        # 6 annonces disparues, chacune au prix plancher de l'heure precedente (1200) : prix habituel = 1200
        con = make_db()
        con.execute("DELETE FROM quotes WHERE item_id=?", (PLANCHE,))
        con.executemany("INSERT INTO quotes VALUES (?,?,?,?,?)",
                        [(ME, PLANCHE, ts(h), 1200, 10 + h) for h in range(7)])
        u = market(con).usual_price(PLANCHE)
        self.assertEqual((u["price"], u["source"], u["sales"]), (1200, "ventes", 6))


class Surete(unittest.TestCase):
    def setUp(self):
        self.m = market(make_db())
        self.e = dict(item_id=PLANCHE, lot_vente=5, ma_part_j=24)   # 10 annonces en vente

    def test_marche_sain_feu_vert(self):
        s = self.m.safety(self.e, dict(adds_h=1, drops_h=2, window="24 h"), cost=500, net_usual=400)
        self.assertEqual((s["score"], s["feu"]), (100 - 10, "vert"))   # ~5 h d'ecoulement : petite penalite
        self.assertEqual(s["qte_max"], 2)                          # ma part sur 2 h (24/12) < 2 h de marche (20)
        self.assertEqual(s["prix_plancher"], 556)                  # 500 / 0,9 arrondi au-dessus
        self.assertEqual(s["ecoulement_h"], 5.0)                   # 10 annonces / 2 par heure

    def test_stock_qui_s_accumule_et_perte(self):
        s = self.m.safety(self.e, dict(adds_h=5, drops_h=2, window="24 h"), cost=500, net_usual=-100)
        self.assertEqual((s["score"], s["feu"]), (100 - 45 - 10 - 25, "rouge"))

    def test_activite_inconnue_et_vieux_pic(self):
        s = self.m.safety(self.e, None, cost=None, net_usual=None, since=ts(10))
        self.assertEqual(s["score"], 100 - 25 - 10)
        self.assertEqual(s["qte_max"], 1)                          # pendant un pic : ma part / 3


class VraisGains(unittest.TestCase):
    def test_comparaison_aux_estimations(self):
        con = make_db()
        con.execute("INSERT INTO activity VALUES (?,?,?,24,1.0,1.0,0.5,100,100)", (ME, PLANCHE, ts(1)))
        sales = [dict(date=(datetime.now() - timedelta(hours=h)).strftime("%Y-%m-%d %H:%M"), objet="Planche",
                      quantite=1, prix=1100, recu=990) for h in (2, 14, 26)]
        g = market(con, my_sales=sales, my_listings={"Planche": {"prix": 1100, "cout": 1000}}).real_gains()
        p = g["items"][0]
        self.assertEqual((g["ventes"], g["recu"], p["unites"]), (3, 2970, 3))
        self.assertAlmostEqual(p["unites_j"], 2.0)                  # 2 intervalles sur 24 h
        self.assertAlmostEqual(p["part"], 2.0 / 24)                 # 24 annonces vendues par jour sur le marche
        self.assertEqual(p["marge_u"], -10)                         # 990 recus pour un cout de 1000

    def test_part_reelle_remplace_la_part_supposee(self):
        con = make_db()
        for iid in (BOIS, PLANCHE, MEUBLE):
            con.execute("INSERT INTO activity VALUES (?,?,?,24,1.0,1.0,0.5,100,100)", (ME, iid, ts(1)))
        sale = lambda o, h: dict(date=(datetime.now() - timedelta(hours=h)).strftime("%Y-%m-%d %H:%M"), objet=o,
                                 quantite=1, prix=1000, recu=900)
        two = [sale(o, h) for o in ("Planche", "Meuble") for h in (2, 14, 26)]
        m = market(con, my_sales=two)
        self.assertEqual(m.share, 0.20)                             # 2 objets seulement : part supposee
        m = market(con, my_sales=two + [sale("Bois", h) for h in (2, 14, 26)])
        self.assertAlmostEqual(m.share, 2.0 / 24)                   # 2 unites/j sur 24 vendues : part reelle
        self.assertEqual(m._share["source"], "journal")



class Fraicheur(unittest.TestCase):
    def test_alerte_une_fois_si_plus_de_prix(self):
        con = make_db()
        self.assertIsNone(alerts.freshness(con, CFG))                # dernier releve il y a 0 h
        con.execute("DELETE FROM quotes WHERE ts > ?", (ts(4),))
        msg = alerts.freshness(con, CFG)
        self.assertIn("Données périmées", msg)
        self.assertIsNone(alerts.freshness(con, CFG))                # pas de repetition chaque heure


class Flip(unittest.TestCase):
    def flips(self, now):
        """Planche : prix qui alterne 600 / 1000 / 1000 sur 12 h (1er quartile ~600, mediane 1000), `now` a l'instant."""
        con = make_db()
        con.execute("DELETE FROM quotes WHERE item_id = ?", (PLANCHE,))
        con.executemany("INSERT INTO quotes VALUES (?,?,?,?,?)",
                        [(ME, PLANCHE, ts(h), (600, 1000, 1000)[h % 3], 10) for h in range(1, 13)] + [(ME, PLANCHE, ts(0), now, 10)])
        con.execute("INSERT INTO activity VALUES (?,?,?,24,1.0,1.0,0.5,100,100)", (ME, PLANCHE, ts(1)))
        a = dict(flip_min_samples=12, flip_min_margin=0.1, flip_max_ecart=0.5)
        return [f for f in market(con, alerts=a).flips() if f["item_id"] == PLANCHE]

    def test_flip_normal(self):
        f = self.flips(600)
        self.assertEqual((len(f), f[0]["acheter"]), (1, True))

    def test_prix_aberrant_ecarte(self):
        self.assertEqual(self.flips(50), [])                         # 5 % de la mediane : erreur de saisie ou releve faux
        self.assertEqual(self.flips(5000), [])                       # 5 fois la mediane


class PrecisionDesAlertes(unittest.TestCase):
    def test_opportunite_notee_puis_jugee(self):
        con = make_db()
        cfg = dict(CFG, alerts=dict(buy_craft_min_margin=0.3, buy_craft_min_profit_day=1000, unique_ratio=0.6,
                                    unique_min_samples=12, unique_min_median=10000, flip_min_profit_day=1000))
        e = dict(item_id=PLANCHE, objet="Planche", flags=[], marge=2.5, profit_j=10000, net_pess_u=500, achats_u=200,
                 prix_real=1000, net_u=700, surete=dict(feu="vert", qte_max=5))
        res = dict(buy=[e], spikes=[], uniques=[], flips=[])
        alerts.track(con, cfg, res)
        alerts.track(con, cfg, res)                                  # une seule fois par objet et par jour
        self.assertEqual(con.execute("SELECT COUNT(*) FROM opp_track").fetchone()[0], 1)
        self.assertEqual(alerts.precision(con)["attente"], 1)
        con.execute("UPDATE opp_track SET ts = ?", (ts(49) + "+00:00",))   # fenetre de vente (48 h) passee
        alerts.track(con, cfg, dict(res, buy=[]))
        k = alerts.precision(con)["kinds"][0]
        self.assertEqual((k["kind"], k["n"], k["ok"]), ("buy", 1, 1))
        self.assertAlmostEqual(k["reel"], 1000 * 0.9 - 200)          # vendu au prix releve (1000) apres taxe
        self.assertAlmostEqual(k["vs_prevu"], 700 / 700)

class Brut(unittest.TestCase):
    """Brut vendable depuis la MaJ du 21/10/2026 : historique coupe, valeur brute face aux crafts."""
    def test_historique_du_brut_coupe(self):
        con = make_db()
        con.executemany("INSERT INTO quotes VALUES (?,?,?,?,?)",
                        [(ME, i, ts(30 + h), 500, 10) for i in (BOIS, PLANCHE) for h in range(13)])
        m = market(con, brut_vendable_depuis=ts(20))
        self.assertEqual(len(m.price_series(BOIS, 3)), 13)          # releves d'avant la coupure ignores
        self.assertEqual(len(m.price_series(PLANCHE, 3)), 26)       # pas du brut : tout l'historique
        self.assertEqual(m.usual_price(BOIS)["price"], 100)

    def test_craft_face_au_brut(self):
        m = market(make_db())
        e = m.evaluate(m.recipes_by_item[PLANCHE][0], "harvest")
        self.assertEqual((e["net_u"], e["brut_u"], e["vs_brut_u"]), (900, 180, 720))   # 2 Bois a 100 - 10 %
        m = market(make_db({BOIS: 600, OD: 60, PLANCHE: 1000}))
        e = m.evaluate(m.recipes_by_item[PLANCHE][0], "harvest")
        self.assertEqual(e["vs_brut_u"], 900 - 1080)                # le brut rapporte plus

    def test_vente_du_brut_est_un_usage(self):
        m = market(make_db())
        raw = {e["objet"]: e for e in m.raw_rows()}
        self.assertEqual((raw["Bois"]["net_u"], raw["Bois"]["ressources"], raw["Bois"]["brut"]), (90, {"Bois": 1}, True))
        targets = {t["ressource"]: t for t in m.gather_targets(m.best_per_item("harvest") + list(raw.values()))}
        uses = [(u["objet"], u["net_par_ressource"], u["brut"]) for u in targets["Bois"]["usages"]]
        self.assertIn(("Bois", 90, True), uses)
        self.assertIn(("Planche", 450, False), uses)
        # l'Od se vend brut, ou se transmute en Bois vendu brut
        self.assertTrue(any(u["brut"] and u.get("via") == "Bois" for u in targets["Od commun"]["usages"]))


class NouvelItem(unittest.TestCase):
    def test_item_sans_nom(self):
        """Item ajoute par aion2.exchange sans nom (nouvel objet) : l'analyse ne plante pas."""
        con = make_db()
        con.execute("INSERT INTO items (id, on_market) VALUES (99, 1)")
        con.executemany("INSERT INTO quotes VALUES (?,?,?,?,?)", [(ME, 99, ts(h), 700, 3) for h in range(13)])
        m = market(con)
        m.sales(99)


class Journal(unittest.TestCase):
    LOT = dict(id="a", objet="Planche", src="achat", qte=20, prix=1000, cout=600, ev=[
        dict(id="1", t="2026-10-19 10:00", type="poste", prix=1000, qte=20),
        dict(id="2", t="2026-10-19 12:00", type="vendu", prix=1000, qte=8, recu=7200),
        dict(id="3", t="2026-10-19 14:00", type="reliste", prix=900, qte=12, frais=1200),   # 10 % de 12 x 1000, perdus
        dict(id="4", t="2026-10-19 15:00", type="vendu", prix=900, qte=5, recu=4050),
        dict(id="5", t="2026-10-19 16:00", type="vendu", prix=900, qte=2, recu=1620, x=1),   # annule
        dict(id="6", t="2026-10-19 17:00", type="cout", cout=650),
        dict(id="7", t="2026-10-19 17:01", type="src", src="recolte")])

    def test_etat_d_une_annonce(self):
        s = lot_state(self.LOT)
        self.assertEqual(s["src"], "recolte")                       # origine changee apres coup
        self.assertEqual((s["prix"], s["cout"], s["vendus"], s["reste"], s["frais"], s["recu"], s["relistes"]),
                         (900, 650, 13, 7, 1200, 11250, 1))

    def test_correction_sans_frais(self):
        lot = dict(id="c", objet="Planche", qte=10, prix=50, ev=[
            dict(id="1", t="2026-10-19 10:00", type="poste", prix=50, qte=10),     # 50 au lieu de 500 : erreur de clic
            dict(id="2", t="2026-10-19 10:05", type="corrige", prix=500, qte=12)])
        s = lot_state(lot)
        self.assertEqual((s["prix"], s["reste"], s["frais"], s["relistes"]), (500, 12, 0, 0))

    def test_retrait_perd_la_taxe(self):
        lot = dict(id="r", objet="Planche", qte=10, prix=500, ev=[
            dict(id="1", t="2026-10-19 10:00", type="poste", prix=500, qte=10),
            dict(id="2", t="2026-10-19 11:00", type="retire", qte=10, frais=500)])
        s = lot_state(lot)
        self.assertEqual((s["reste"], s["frais"]), (0, 500))

    def test_annonces_et_ventes_pour_l_analyse(self):
        listings, sales = from_journal({"lots": [self.LOT, dict(self.LOT, id="b", del_=0), dict(self.LOT, id="c", **{"del": 1})]})
        self.assertEqual(listings, {"Planche": {"prix": 900, "quantite": 14, "cout": 650}})
        self.assertEqual(len(sales), 4)                                # 2 ventes par annonce, l'annulee ne compte pas
        self.assertEqual(sales[0], dict(date="2026-10-19 15:00", objet="Planche", quantite=5, prix=4500, recu=4050, cout=650, origine="recolte"))


# moteur JavaScript : node, sinon JavaScriptCore (present sur tout Mac)
JSC = "/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc"
NODE = shutil.which("node")


def js_check(path):
    if NODE:
        return subprocess.run([NODE, "--check", str(path)], capture_output=True, text=True)
    return subprocess.run([JSC, "-e", f"checkSyntax({str(path)!r})"], capture_output=True, text=True)


@unittest.skipUnless(NODE or Path(JSC).exists(), "ni node ni JavaScriptCore")
class JavaScript(unittest.TestCase):
    def test_syntaxe(self):
        for f in ("site.js", "scan.js"):
            r = js_check(ROOT / "aionhdv" / f)
            self.assertEqual(r.returncode, 0, r.stderr + r.stdout)


if __name__ == "__main__":
    unittest.main()
