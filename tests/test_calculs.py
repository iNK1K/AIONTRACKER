"""Tests des calculs cles, sur une petite base fabriquee pour l'occasion (aucun acces reseau, base reelle intacte).

Lancer : python -m unittest discover tests
"""
import shutil
import sqlite3
import subprocess
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from aionhdv.analysis import Market
from aionhdv.config import from_journal, lot_state
from aionhdv.db import SCHEMA

ROOT = Path(__file__).resolve().parent.parent
ME, REF = "2310", "1304"
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
                    [(ME, "Hadala", "EU", "Asmodian", "live", 12310), (REF, "Kaisinel", "EU", "Elyos", "live", 11304)])
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


CFG = dict(my_server=ME, reference_server=REF, market_share=0.20, fees=0.10, npc_reagent_price=50, combo_rate=None)


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


class Ventes(unittest.TestCase):
    def test_ventes_mesurees_sur_le_serveur(self):
        con = make_db()
        con.execute("INSERT INTO activity VALUES (?,?,?,24,2.0,1.0,0.5,100,100)", (ME, PLANCHE, ts(1)))
        s = market(con).sales(PLANCHE)
        self.assertEqual((s["source"], s["listings"], s["units"], s["lot"]), ("serveur", 48, 48, None))

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


class Chaines(unittest.TestCase):
    def test_chaine_planche_meuble(self):
        chains = market(make_db()).gamble_chains()
        self.assertEqual([c["name"] for c in chains], ["Planche"])
        a, b = chains[0]["steps"]
        self.assertEqual((a["cost"], a["res"], a["c"]), (0, {"Bois": 2}, 25))
        self.assertEqual((a["plain"]["v"], a["ecl"]["v"]), (900, 2700))      # prix habituel - taxe 10 %
        # etape 2 : la Planche eclatante est deja en main, seule la recolte reste a fournir
        self.assertEqual((b["inp"], b["res"], b["ecl"]["v"]), ("Planche éclatante", {"Bois": 1}, 18000))

    def test_taux_de_combo_de_la_config(self):
        self.assertEqual(market(make_db(), combo_rate=24).gamble_chains()[0]["steps"][0]["c"], 24)


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


class Journal(unittest.TestCase):
    LOT = dict(id="a", objet="Planche", qte=20, prix=1000, cout=600, ev=[
        dict(id="1", t="2026-10-19 10:00", type="poste", prix=1000, qte=20, frais=400),
        dict(id="2", t="2026-10-19 12:00", type="vendu", prix=1000, qte=8, recu=7200),
        dict(id="3", t="2026-10-19 14:00", type="reliste", prix=900, qte=12, frais=216),
        dict(id="4", t="2026-10-19 15:00", type="vendu", prix=900, qte=5, recu=4050),
        dict(id="5", t="2026-10-19 16:00", type="vendu", prix=900, qte=2, recu=1620, x=1),   # annule
        dict(id="6", t="2026-10-19 17:00", type="cout", cout=650)])

    def test_etat_d_une_annonce(self):
        s = lot_state(self.LOT)
        self.assertEqual((s["prix"], s["cout"], s["vendus"], s["reste"], s["frais"], s["recu"], s["relistes"]),
                         (900, 650, 13, 7, 616, 11250, 1))

    def test_annonces_et_ventes_pour_l_analyse(self):
        listings, sales = from_journal({"lots": [self.LOT, dict(self.LOT, id="b", del_=0), dict(self.LOT, id="c", **{"del": 1})]})
        self.assertEqual(listings, {"Planche": {"prix": 900, "quantite": 14, "cout": 650}})
        self.assertEqual(len(sales), 4)                                # 2 ventes par annonce, l'annulee ne compte pas
        self.assertEqual(sales[0], dict(date="2026-10-19 15:00", objet="Planche", quantite=5, prix=4500, recu=4050, cout=650))


@unittest.skipUnless(shutil.which("node"), "node absent")
class JavaScript(unittest.TestCase):
    def test_syntaxe(self):
        for f in ("site.js", "scan.js"):
            r = subprocess.run(["node", "--check", str(ROOT / "aionhdv" / f)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
