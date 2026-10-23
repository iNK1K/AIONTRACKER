"""Onglet 💬 Assistant : chat Claude sur Aion 2 (recherche web + données du tracker).

Le catalogue que l'assistant consulte (objets, prix du serveur suivi, recettes, points de récolte) est écrit dans
assist.js, hors de la page chiffrée et chargé seulement à l'ouverture du chat : ce sont des données du jeu et des prix
publics, rien de personnel (ni journal, ni opportunités). La clé API reste dans le navigateur (site.js, partie assistant).
"""
import hashlib
import json

from ..config import REPORT_DIR


def write_assist_data(con, my, sname):
    """assist.js : window.ASSIST = {asof, server, items: [[id, nom, nom_en, rareté, type, niveau, prix, annonces,
    prix habituel]], recipes: {id: [[métier, maîtrise, quantité, [[id ingrédient, qté], ...]]]}, nodes: {id: {zone: points}}}."""
    m = my["market"]
    recipes = {}
    for iid, rs in m.recipes_by_item.items():
        out = []
        for r in rs:
            slots = m.ingredients.get(r["id"], {})
            ings = [[alts[0]["item_id"], alts[0]["qty"]] for _, alts in sorted(slots.items()) if alts]
            out.append([r["profession"], r["mastery"], r["output_qty"], ings])
        recipes[iid] = out
    nodes = {}
    for r in con.execute("SELECT g.item_id, w.name AS zone, COUNT(*) AS n FROM gather_nodes g "
                         "JOIN map_worlds w ON w.id = g.world_id WHERE g.item_id IS NOT NULL GROUP BY g.item_id, w.name"):
        nodes.setdefault(r["item_id"], {})[r["zone"]] = r["n"]
    used = set(recipes) | set(nodes) | {i for rs in recipes.values() for r in rs for i, _ in r[3]}
    items = []
    for iid, it in m.items.items():
        if iid not in used and (it.get("bound") or not (it.get("on_market") or iid in m.price)):
            continue                                                  # objet lié : seulement comme ingrédient
        price = m.price.get(iid)
        usual = m.usual_price(iid) if price else None
        items.append([iid, it["name"], it.get("name_en") or "", it.get("grade") or "",
                      it.get("sub_category") or it.get("category") or "", it.get("level") or 0,
                      round(price) if price else None, m.listings.get(iid), round(usual["price"]) if usual else None])
    data = dict(asof=my["as_of"], server=sname, items=items, recipes=recipes, nodes=nodes)
    text = "window.ASSIST=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
    (REPORT_DIR / "assist.js").write_text(text, encoding="utf-8")
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def assistant_tab(version):
    """version : empreinte de assist.js (?v=), pour que le navigateur ne garde pas un vieux catalogue."""
    return f'<div id="ai" class="ai" data-v="{version}">' + """<div id="aimsgs" class="aimsgs"><div class="aihello">
<h2>Pose ta question sur Aion 2</h2>
<p class="lead">Loot, donjons, crafts, builds, où récolter, prix à l’HDV… L’assistant cherche sur le web (wikis, bases de données,
patch notes) et consulte les prix et recettes du tracker.</p>
<div class="aisugg">
<button onclick="aiAsk(this.textContent)">Que drop le dernier donjon sorti, et quel loot vaut le coup ?</button>
<button onclick="aiAsk(this.textContent)">Comment crafter une Potion de soin supérieure, et est-ce rentable ?</button>
<button onclick="aiAsk(this.textContent)">Quel équipement viser en priorité pour un Templier niveau max ?</button>
<button onclick="aiAsk(this.textContent)">Où récolter du Bois d'Asvata ?</button>
</div></div></div>
<div id="aikey" class="aikey" hidden></div>
<form class="aibar" onsubmit="event.preventDefault();aiSend()">
<textarea id="aiin" rows="1" placeholder="Demande n’importe quoi sur Aion 2…" oninput="aiGrow(this)"
 onkeydown="if(event.key==='Enter'&&!event.shiftKey&&!event.isComposing){event.preventDefault();aiSend()}"></textarea>
<button id="aigo" type="submit" title="Envoyer (Entrée)">➤</button></form>
<div class="aifoot"><button onclick="aiNew()">＋ Nouvelle conversation</button><span id="aicost"></span>
<button onclick="aiKeyForm(true)">🔑 Clé API</button></div></div>"""
