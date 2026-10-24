"""Rapport HTML statique (reports/index.html) + carte des ressources (reports/map.html)."""
import hashlib
import json
import shutil
from pathlib import Path

from ..alerts import precision
from ..collect import now_iso, paris
from ..config import REPORT_DIR
from .accueil import home
from .assistant import assistant_tab, write_assist_data
from .base import CSS, Ctx, esc
from .fichiers import map_world_ids, write_map_data, write_price_data
from .metiers import metiers_tab
from .opportunites import opportunities_tab, planning_tab
from .ravitaillement import supply_tab
from .recolte import harvest_tab
from .tables import compare_ways, stock_calc, table_crafts, table_flips, table_plan, table_spikes, table_uniques
from .ventes import gains_tab

# onglets toujours visibles, dans cet ordre ; les autres sont des outils (menu « Outils »)
MAIN_TABS = ("chat", "home", "opps", "gains", "supply")


def build(con, cfg, results):
    REPORT_DIR.mkdir(exist_ok=True)
    ctx = Ctx(con, map_world_ids(con, cfg))
    write_map_data(con, cfg)
    ctx.charted = write_price_data(con, cfg)
    shutil.copy(Path(__file__).parent.with_name("scan.js"), REPORT_DIR / "scan.js")   # lecture des captures, chargee a la demande
    # code de la page (fichier a part) ; ?v= change avec son contenu pour que le navigateur ne garde pas une vieille version
    site_js = Path(__file__).parent.with_name("site.js")
    shutil.copy(site_js, REPORT_DIR / "site.js")
    jsv = hashlib.sha1(site_js.read_bytes()).hexdigest()[:8]
    names = {r["id"]: r["name"] for r in con.execute("SELECT id, name FROM servers")}
    my = next((r for r in results if r["server"] == str(cfg["my_server"])), results[0] if results else None)
    sname = names.get(my["server"], my["server"]) if my else "?"
    sections, navs = [], {}

    def add(sid, title, content):
        navs[sid] = (f'<button data-t="{sid}" onclick="show(\'{sid}\')"{"" if sid in MAIN_TABS else " class=tool"}>'
                     f'{title}</button>')
        sections.append(f'<section id="{sid}">{content}</section>')

    share = my["market"].share if my else cfg["market_share"]
    calib = " (ta part réelle, mesurée sur tes ventes du journal)" if my and my["market"]._share["source"] == "journal" else ""
    hyp = (f"Part de marché {share:.0%}{calib}, taxe et frais d’enregistrement {cfg['fees']:.0%}. "
           "« Vendre à » = prix réaliste : le prix affiché, ramené vers le prix habituel sur ton serveur (médiane 3 j) "
           "quand il est anormalement haut.")
    if my:
        add("chat", "💬 Assistant", assistant_tab(write_assist_data(con, my, sname)))
        add("home", "🏠 Aujourd’hui", home(con, cfg, ctx, my, sname))
        add("opps", "🎯 Opportunités", opportunities_tab(cfg, my, precision(con)))
        add("planning", "📅 Planning", planning_tab(cfg, my))
        add("harvest", "🌲 Récolte", harvest_tab(ctx, my, hyp))
        direct, trans = my.get("buy_direct") or [], my.get("buy_trans") or []
        add("buy", "Achat → craft",
            f"<h2>Acheter les ingrédients → fabriquer → revendre</h2><p class='lead'>{hyp} Deux façons d’acheter les "
            "ingrédients récoltables : directement à l’HDV, ou acheter de l’Od de même rareté et le transmuter (gratuit, "
            "sans échec). <b class='pos'>Vert</b> = cette façon rapporte plus que l’autre pour ce craft, "
            "<b class='neg'>rouge</b> = moins.</p>"
            + table_spikes(ctx, my.get("spikes"))
            + '<div class="seg"><button class="on" onclick="segShow(this,\'bdir\')">🏪 Achat à l’HDV → craft → vente</button>'
            f'<button onclick="segShow(this,\'btr\')">🔁 Achat d’Od → transmutation → craft → vente ({len(trans)})</button></div>'
            "<div id='bdir' class='segp'>" + table_crafts(ctx, direct, "tb", False, compare_ways(direct, trans, "via Od"))
            + "</div><div id='btr' class='segp' style='display:none'>"
            + table_crafts(ctx, trans, "tbt", False, compare_ways(trans, direct, "l’achat à l’HDV")) + "</div>")
        add("flips", "🔁 Flip", "<h2>Achat → revente (sans craft)</h2>" + table_flips(ctx, my["flips"], cfg))
        add("uniques", "💎 Uniques", "<h2>Équipements Unique : prix bradés</h2>" + table_uniques(ctx, my["uniques"], cfg))
        add("metiersTab", "🛠️ Mes métiers", metiers_tab(con, my))
        add("plan", "🧮 Mon stock", "<h2>Mon stock → quoi fabriquer ou vendre brut</h2>"
            + stock_calc(ctx, cfg, my["harvest"] + (my.get("raw") or []), my["market"].gather_names(),
                         {t: my["market"].items[s]["base_name"] for t, s in my["market"].transmute.items()})
            + ("<h3>Plan quotidien (config)</h3>" + table_plan(my["plan"]) if my["plan"] else ""))
        add("gains", "💰 Mes ventes", gains_tab(ctx, cfg, my))
        add("supply", "📦 Ravitaillement", supply_tab(ctx, cfg, my))
    gathers = sorted(ctx.gather_names)
    cards = "".join(f'<div class="card" style="flex-direction:row;align-items:center;justify-content:space-between">'
                    f'{ctx.label(name=g, sub=f"{ctx.gather_counts.get(g, 0)} points")}</div>' for g in gathers)
    add("map", "🗺 Carte", "<h2>Ressources de récolte</h2><p class='lead'>Clique sur MAP pour voir les points de récolte.</p>"
        f'<div class="cards">{cards}</div>')
    # onglets de tous les jours en avant, les autres derriere « Outils » (deplies quand l'un d'eux est ouvert)
    nav = ("".join(navs.pop(s) for s in MAIN_TABS if s in navs) + '<span class="sep"></span>'
           + '<button class="toolbtn" onclick="toggleTools()">🧰 Outils</button>' + "".join(navs.values()))
    as_of = my["as_of"] if my else "?"
    # donnees de prix sans rien de personnel : fichier a part, telecharge compresse (la page chiffree ne se compresse pas)
    data_js = "".join(f"window.{k}={json.dumps(v, ensure_ascii=False, separators=(',', ':'))};\n" for k, v in ctx.data.items())
    (REPORT_DIR / "data.js").write_text(data_js, encoding="utf-8")
    dv = hashlib.sha1(data_js.encode("utf-8")).hexdigest()[:8]
    page = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HDV Aion 2</title><style>{CSS}</style><script src="site.js?v={jsv}"></script><script src="data.js?v={dv}"></script></head><body>
<header><h1>HDV Aion 2 · <b>{esc(sname)}</b></h1>
<div class="meta">Prix relevés le {esc(paris(as_of) if my and as_of else "?")} (heure de Paris)<br>Page générée le {esc(paris())}</div></header>
<div id="stale" hidden data-asof="{esc(as_of if my and as_of else "")}" data-gen="{now_iso()}"></div>
<nav>{nav}</nav><main>{''.join(sections)}</main>
<div id="cmodal" onclick="if(event.target===this)closeChart()"><div class="box"><div class="bar"><b id="ctitle"></b>
<button class="mapbtn" onclick="closeChart()">Fermer ✕</button></div><div id="cbody"></div></div></div>
<div id="modal" onclick="if(event.target===this)closeMap()"><div class="box"><div class="bar"><b id="mtitle"></b>
<button class="mapbtn" onclick="closeMap()">Fermer ✕</button></div><iframe id="mframe"></iframe></div></div>
</body></html>"""
    path = REPORT_DIR / "index.html"
    path.write_text(page, encoding="utf-8")
    return path
