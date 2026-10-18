"""Affiche le top des analyses pour un serveur : python -X utf8 scripts/show_top.py [server]"""
import sys

from aionhdv.analysis import run_all
from aionhdv.config import load_config
from aionhdv.db import connect

cfg = load_config()
con = connect()
srv = sys.argv[1] if len(sys.argv) > 1 else cfg["my_server"]
r = run_all(con, cfg, srv)
print(f"serveur {srv} prix {r['as_of']} ratio {r['ratio']:.2f}")
for kind in ("harvest", "buy"):
    print(f"\n== {kind}")
    for e in r[kind][:14]:
        print(f"{e['objet'][:38]:38} vol {e['vol_serveur_j']:>6} part {e['ma_part_j']:>5} affiché {e['prix_affiche']:>9,.0f} "
              f"réf {e['prix_ref'] or 0:>9,.0f} net/u {e['net_u']:>9,} pess {e['net_pess_u']:>9,} profit/j {e['profit_j']:>11,} "
              f"{'; '.join(e['flags'])[:60]}")
print("\n== cibles")
for t in r["targets"][:10]:
    u = t["usages"][0]
    print(f"{t['ressource'][:30]:30} -> {u['objet'][:30]:30} {u['net_par_ressource']:>8,}/ressource  absorbable {t['absorbable_j']}/j")
