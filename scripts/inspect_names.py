"""Affiche les items dont le nom francais est a verifier."""
from aionhdv.db import connect

con = connect()
print("== absents de questlog (ressources)")
for r in con.execute("SELECT id, name, name_en FROM items WHERE name_check LIKE '%absent questlog%' ORDER BY name"):
    print(r["id"], "|", r["name"], "|", r["name_en"])
print("== noms questlog sans item correspondant")
for r in con.execute("SELECT name, COUNT(*) n FROM gather_nodes WHERE item_id IS NULL GROUP BY name ORDER BY n DESC"):
    print(r["name"], r["n"])
print("== identiques a l'anglais")
for r in con.execute("SELECT id, name, name_en, on_market FROM items WHERE name_check LIKE '%identique EN%' ORDER BY name"):
    print(r["id"], "|", r["name"], "|", r["name_en"])
