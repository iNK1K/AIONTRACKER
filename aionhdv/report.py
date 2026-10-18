"""Rapport HTML statique (reports/index.html) + carte des ressources (reports/map.html)."""
import html
import json
import re
from datetime import datetime, timezone

from .catalog import node_name
from .collect import BOUND_RE, paris
from .config import DATA_DIR, REPORT_DIR

MAP_DIR = DATA_DIR / "maps"
METIERS = {"Alchemy": "Alchimie", "Handicrafting": "Artisanat", "Armorsmithing": "Forge d'armures",
           "Blacksmithing": "Forge d'armes", "Cooking": "Cuisine", "Tailoring": "Couture", "Weaponsmithing": "Forge d'armes"}

CSS = """
:root{color-scheme:dark;--bg:#0b0d12;--bg2:#10131a;--card:#151922;--card2:#1b202b;--line:#252b38;--line2:#1d222d;
 --txt:#e8eaf0;--mut:#8a93a6;--acc:#f0c050;--ok:#3ecf8e;--bad:#f06470;--warn:#f0a050}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--txt);font:15px/1.5 "Segoe UI",system-ui,Roboto,sans-serif}
header{display:flex;align-items:center;gap:16px;flex-wrap:wrap;padding:18px 28px;background:linear-gradient(180deg,#151a26,var(--bg));border-bottom:1px solid var(--line)}
header h1{font-size:21px;margin:0;font-weight:700}header h1 b{color:var(--acc)}
.meta{color:var(--mut);font-size:13px;margin-left:auto;text-align:right}
nav{position:sticky;top:0;z-index:20;background:rgba(11,13,18,.94);backdrop-filter:blur(6px);border-bottom:1px solid var(--line);
 padding:0 28px;display:flex;gap:2px;overflow-x:auto}
nav button{background:none;border:0;border-bottom:2px solid transparent;color:var(--mut);padding:13px 14px;font:inherit;font-size:14px;font-weight:600;cursor:pointer;white-space:nowrap}
nav button:hover{color:var(--txt)}nav button.on{color:var(--acc);border-bottom-color:var(--acc)}
nav .sep{flex:none;width:1px;background:var(--line);margin:12px 8px}
main{padding:22px 28px 60px;max-width:1600px;margin:0 auto}
section{display:none}section.on{display:block}
h2{font-size:19px;margin:0 0 4px}h3{font-size:15px;margin:26px 0 10px;color:var(--mut);text-transform:uppercase;letter-spacing:.05em}
.lead{color:var(--mut);margin:0 0 16px;font-size:14px;max-width:1000px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin:14px 0 8px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.kpi .l{color:var(--mut);font-size:12px;text-transform:uppercase;letter-spacing:.05em}
.kpi .v{font-size:26px;font-weight:700;margin-top:2px}.kpi .s{color:var(--mut);font-size:13px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;display:flex;flex-direction:column;gap:8px}
.card .row{display:flex;justify-content:space-between;color:var(--mut);font-size:13px}.card .row b{color:var(--txt)}
.card .big{font-size:22px;font-weight:700;color:var(--ok)}
.toolbar{display:flex;gap:14px;align-items:center;margin:0 0 10px;flex-wrap:wrap}
input.search{padding:8px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--txt);width:300px;font:inherit;font-size:14px}
input.search:focus{outline:none;border-color:var(--acc)}
label.tg{color:var(--mut);font-size:13px;display:flex;gap:6px;align-items:center;cursor:pointer;user-select:none}
.wrap{overflow:auto;border:1px solid var(--line);border-radius:12px;background:var(--card);max-height:78vh}
table{border-collapse:separate;border-spacing:0;width:100%}
th{position:sticky;top:0;z-index:2;background:var(--card2);color:var(--mut);font-size:11.5px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;
 text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);cursor:pointer;white-space:nowrap}
th.n{text-align:right}th[title]{cursor:help}th:hover{color:var(--txt)}
td{padding:10px 12px;border-bottom:1px solid var(--line2);vertical-align:middle}
tbody tr:nth-child(even){background:#ffffff04}tbody tr:hover{background:#ffffff0b}
tr.dim td{opacity:.6}
tr.grp td{background:var(--bg2);color:var(--warn);font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:.05em;padding:8px 12px}
td.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
td.big{font-weight:700;font-size:15.5px}td.rank{color:var(--mut);width:36px}
.pos{color:var(--ok)}.neg{color:var(--bad)}.mut{color:var(--mut)}
.x{display:none}body.detail .x{display:table-cell}
.badge{display:inline-block;padding:2px 9px;border-radius:999px;font-size:11.5px;font-weight:600;margin:2px 4px 2px 0;white-space:nowrap}
.b-ok{background:#3ecf8e1f;color:var(--ok)}.b-warn{background:#f0a0501f;color:var(--warn)}.b-bad{background:#f064701f;color:var(--bad)}
.b-mut{background:#ffffff10;color:var(--mut)}
img.ic{width:34px;height:34px;border-radius:7px;background:#0007;border:1px solid var(--line);flex:none}
.it{display:flex;align-items:center;gap:10px}.it .nm{font-weight:600}.sub{color:var(--mut);font-size:12.5px}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{display:inline-flex;align-items:center;gap:6px;background:var(--card2);border:1px solid var(--line);border-radius:8px;padding:3px 8px;font-size:13px;white-space:nowrap}
.chip img.ic{width:22px;height:22px;border-radius:5px}
.ing{font-size:13px;line-height:1.6}.ing div{white-space:nowrap}
.uses{display:flex;flex-direction:column;gap:5px;font-size:13.5px}
.mapbtn{font-size:11px;font-weight:700;padding:2px 8px;margin-left:4px;border:1px solid var(--acc);color:var(--acc);background:transparent;border-radius:6px;cursor:pointer}
.mapbtn:hover{background:var(--acc);color:#111}
code{background:var(--card2);padding:1px 6px;border-radius:5px}
#modal{position:fixed;inset:0;background:#000b;display:none;align-items:center;justify-content:center;z-index:50}
#modal.on{display:flex}
#modal .box{width:min(1200px,96vw);height:min(850px,92vh);background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;display:flex;flex-direction:column}
#modal .bar{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;border-bottom:1px solid var(--line)}
#modal iframe{flex:1;border:0;width:100%}
.hours{display:flex;gap:3px;align-items:flex-end;height:96px;margin-top:4px}
.hb{flex:1;min-width:0;height:100%;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:3px}
.hb i{display:block;width:100%;background:var(--line);border-radius:3px 3px 0 0;min-height:2px}
.hb.on i{background:var(--acc)}.hb span{font-size:10px;color:var(--mut);height:12px;line-height:12px}
"""

JS = """
function show(id){document.querySelectorAll('section').forEach(s=>s.classList.toggle('on',s.id===id));
 document.querySelectorAll('nav button').forEach(b=>b.classList.toggle('on',b.dataset.t===id));try{localStorage.setItem('tab',id)}catch(e){};scrollTo(0,0)}
function openMap(name){document.getElementById('mtitle').textContent='Carte : '+name;
 document.getElementById('mframe').src='map.html?r='+encodeURIComponent(name);document.getElementById('modal').classList.add('on')}
function closeMap(){document.getElementById('modal').classList.remove('on');document.getElementById('mframe').src='about:blank'}
function filt(inp,tid){const q=inp.value.toLowerCase();document.querySelectorAll('#'+tid+' tbody tr').forEach(tr=>{
 tr.style.display=(tr.classList.contains('grp')?!q:tr.textContent.toLowerCase().includes(q))?'':'none'})}
function detail(cb){document.body.classList.toggle('detail',cb.checked);document.querySelectorAll('input.dt').forEach(x=>x.checked=cb.checked);
 try{localStorage.setItem('detail',cb.checked?'1':'')}catch(e){}}
function sortT(th){const t=th.closest('table'),i=[...th.parentNode.children].indexOf(th),b=t.tBodies[0],asc=th.dataset.a!=='1';
 b.querySelectorAll('tr.grp').forEach(r=>r.remove());
 [...b.rows].sort((x,y)=>{const a=x.cells[i].dataset.v??x.cells[i].textContent,c=y.cells[i].dataset.v??y.cells[i].textContent;
 const na=parseFloat(a),nc=parseFloat(c);const r=(!isNaN(na)&&!isNaN(nc))?na-nc:a.localeCompare(c,'fr');return asc?r:-r}).forEach(r=>b.appendChild(r));th.dataset.a=asc?'1':'0'}
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeMap()});
document.addEventListener('DOMContentLoaded',()=>{let t='home';try{t=localStorage.getItem('tab')||t;
 if(localStorage.getItem('detail')){document.body.classList.add('detail');document.querySelectorAll('input.dt').forEach(x=>x.checked=true)}}catch(e){}
 if(!document.getElementById(t))t='home';show(t);document.querySelectorAll('th').forEach(th=>th.onclick=()=>sortT(th))});
"""

MAP_HTML = """<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Carte des ressources</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">
<style>html,body{margin:0;height:100%;background:#0f1115;color:#e6e8ee;font:13px system-ui,Segoe UI,sans-serif}
#map{position:absolute;inset:40px 0 0 0;background:#0b0d10}
#bar{height:40px;display:flex;gap:8px;align-items:center;padding:0 10px;border-bottom:1px solid #262b36}
.zb{background:#171a21;color:#e6e8ee;border:1px solid #262b36;border-radius:5px;padding:4px 10px;cursor:pointer;font:inherit}
.zb.on{border-color:#ffd24a;color:#ffd24a}.zb small{color:#9aa3b2}
.cnt{color:#9aa3b2}</style></head><body>
<div id="bar"><b id="res"></b><span id="world"></span><span class="cnt" id="cnt"></span>
<span class="cnt" style="margin-left:auto">Carte © questlog.gg</span></div><div id="map"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script src="map_data.js"></script>
<script>
const P=new URLSearchParams(location.search),R=P.get('r')||'';document.getElementById('res').textContent=R||'Toutes les ressources';
const nodes=MAPDATA.nodes.filter(n=>!R||n[0]===R);const byW={};nodes.forEach(n=>{(byW[n[1]]=byW[n[1]]||[]).push(n)});
const sel=document.getElementById('world');const grp=w=>(MAPDATA.worlds[w]?.grp||'').startsWith('asmo')?0:1;
const ws=Object.keys(byW).filter(w=>MAPDATA.worlds[w]).sort((a,b)=>grp(a)-grp(b)||byW[b].length-byW[a].length);
ws.forEach(w=>{const o=document.createElement('button');o.className='zb';o.dataset.w=w;
 o.innerHTML=MAPDATA.worlds[w].name+' <small>'+byW[w].length+'</small>';o.onclick=()=>draw(w);sel.appendChild(o)});
const map=L.map('map',{crs:L.CRS.Simple,minZoom:-4,maxZoom:3,zoomSnap:0.25,attributionControl:false});let layer,pts;
function draw(w){const W=MAPDATA.worlds[w];if(layer)map.removeLayer(layer);if(pts)map.removeLayer(pts);if(!W)return;
 const wpx=W.nx*1024,hpx=W.ny*1024,b=[[-hpx,0],[0,wpx]];
 if(W.layer==='image'){layer=L.imageOverlay(W.url,b).addTo(map)}else{
  const T=L.TileLayer.extend({getTileUrl:c=>W.url.replace('{x}',String(c.x).padStart(2,'0')).replace('{y}',String(c.y).padStart(2,'0'))});
  layer=new T('',{tileSize:1024,minNativeZoom:0,maxNativeZoom:0,noWrap:true,bounds:b}).addTo(map)}
 pts=L.layerGroup(byW[w].map(n=>L.circleMarker([-n[3],n[2]],{radius:5,color:'#111',weight:1,fillColor:'#ffd24a',fillOpacity:.95}).bindTooltip(n[0]))).addTo(map);
 const lat=byW[w].map(n=>-n[3]),lng=byW[w].map(n=>n[2]);
 map.fitBounds([[Math.min(...lat),Math.min(...lng)],[Math.max(...lat),Math.max(...lng)]],{padding:[40,40]});
 sel.querySelectorAll('.zb').forEach(b=>b.classList.toggle('on',b.dataset.w===w));
 document.getElementById('cnt').textContent=byW[w].length+' points'}
if(ws.length)draw(ws[0]);else document.getElementById('cnt').textContent='Aucun point connu';
</script></body></html>"""


def fmt(n):
    if n is None:
        return "–"
    return f"{n:,.0f}".replace(",", " ")


def esc(s):
    return html.escape(str(s if s is not None else ""))


class Ctx:
    def __init__(self, con, world_ids):
        self.items = {r["id"]: dict(r) for r in con.execute("SELECT * FROM items")}
        # bouton MAP seulement pour les ressources presentes dans les zones accessibles
        self.gather_counts = {}
        for r in con.execute("SELECT name, world_id, count(*) c FROM gather_nodes GROUP BY name, world_id"):
            if r["world_id"] in set(world_ids):
                self.gather_counts[r["name"]] = self.gather_counts.get(r["name"], 0) + r["c"]
        self.gather_names = set(self.gather_counts)
        self.by_base = {}
        for it in self.items.values():
            if not it["bound"]:
                self.by_base.setdefault(it["base_name"], it)

    def icon(self, item_id=None, name=None):
        it = self.items.get(item_id) if item_id else self.by_base.get(name)
        if not it:
            return ""
        local = it.get("icon_file") and (DATA_DIR / it["icon_file"]).exists()
        src = f"../data/{it['icon_file']}" if local else it.get("icon_url")
        return f'<img class="ic" loading="lazy" src="{esc(src)}" alt="">' if src else ""

    def mapbtn(self, name):
        base = node_name(BOUND_RE.sub("", name or ""))
        if base in self.gather_names:
            return f'<button class="mapbtn" data-r="{esc(base)}" onclick="openMap(this.dataset.r)">MAP</button>'
        return ""

    def label(self, item_id=None, name=None, sub=None):
        nm = name or (self.items.get(item_id) or {}).get("name") or item_id
        s = f'<div class="sub">{esc(sub)}</div>' if sub else ""
        return f'<span class="it">{self.icon(item_id, name)}<span><span class="nm">{esc(nm)}</span>{self.mapbtn(nm)}{s}</span></span>'


def _cls(v):
    return "pos" if (v or 0) > 0 else "neg"


def kfmt(n):
    """Montants en kinah lisibles : 3,74 M / 466 k / 950."""
    if n is None:
        return "–"
    a = abs(n)
    if a >= 1e6:
        return f"{n / 1e6:.2f} M".replace(".", ",")
    if a >= 1e4:
        return f"{n / 1e3:.0f} k"
    return fmt(n)


def _num_td(v, cls="", color=True, k=False, x=False):
    c = " ".join(filter(None, ["n", cls, _cls(v) if color and isinstance(v, (int, float)) else "", "x" if x else ""]))
    return f'<td class="{c}" data-v="{v if v is not None else ""}">{kfmt(v) if k else fmt(v)}</td>'


def _th(label, tip=None, num=False, x=False):
    cls = " ".join(filter(None, ["n" if num else "", "x" if x else ""]))
    return f'<th{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}{f" title={chr(34)}{esc(tip)}{chr(34)}" if tip else ""}>{esc(label)}</th>'


def status(e):
    """Pastilles : rentable / risque / a perte / drapeaux."""
    if e["flags"]:
        return "".join(f'<span class="badge b-warn">⚠ {esc(f)}</span>' for f in e["flags"])
    if e["net_u"] <= 0:
        return '<span class="badge b-bad">À perte</span>'
    if e["net_pess_u"] <= 0:
        return '<span class="badge b-warn">Risqué si les prix baissent</span>'
    return '<span class="badge b-ok">Rentable</span>'


def is_good(e):
    return e["net_u"] > 0 and not e["flags"]


def toolbar(tid, extra=""):
    return (f'<div class="toolbar"><input class="search" placeholder="🔍 Rechercher…" oninput="filt(this,\'{tid}\')">'
            '<label class="tg"><input type="checkbox" class="dt" onchange="detail(this)"> Colonnes détaillées</label>'
            f'{extra}</div>')


def table_crafts(ctx, rows, tid, harvest):
    head = ("<tr>" + _th("#") + _th("Craft") +
            (_th("Ressources / unité") if harvest else _th("Ingrédients achetés")) +
            ("" if harvest else _th("Coût/u", "Coût des ingrédients au prix réaliste", True)) +
            _th("Vendre à", "Prix de vente conseillé (réaliste)", True) +
            _th("Net/u", "Bénéfice par unité après 12 % de taxes et frais", True) +
            (_th("Net/ressource", "Bénéfice par ressource récoltée utilisée", True) if harvest
             else _th("Marge", "Bénéfice / coût", True)) +
            _th("Ventes/j", "Ce que tu peux vendre par jour (20 % du marché)", True) +
            _th("Profit/j", "Ventes/j × Net/u", True) +
            _th("Volume serveur/j", "Ventes estimées sur tout le serveur", True, True) +
            _th("Prix affiché", "Prix le plus bas actuellement en vente", True, True) +
            _th("Prix réf.", "Prix de vente moyen réel sur Kaisinel (7 j)", True, True) +
            _th("Net pess./u", "Bénéfice si on vend au prix le plus bas", True, True) +
            _th("Profit pess./j", None, True, True) +
            ("" if harvest else _th("Capital/j", "Kinah à avancer par jour", True, True)) +
            _th("Statut") + "</tr>")
    good = [e for e in rows if is_good(e)]
    bad = [e for e in rows if not is_good(e)]
    ncol = 16 if not harvest else 14
    body = []
    for i, e in enumerate(good + bad, 1):
        if i == len(good) + 1 and bad:
            body.append(f'<tr class="grp"><td colspan="{ncol}">À vérifier ou à perte ({len(bad)})</td></tr>')
        if harvest:
            res = '<div class="chips">' + "".join(
                f'<span class="chip">{ctx.icon(name=k)}{esc(k)} ×{v:g}{ctx.mapbtn(k)}</span>' for k, v in e["ressources"].items()) + "</div>"
            if e["ingredients"] and any("récolte" not in x for x in e["ingredients"]):
                res += '<div class="sub">+ ' + esc("; ".join(x for x in e["ingredients"] if "récolte" not in x)) + "</div>"
        else:
            res = '<div class="ing">' + "".join(f"<div>{esc(x)}</div>" for x in e["ingredients"]) + "</div>"
        cols = (_num_td(e["net_par_ressource"]) if harvest else
                f'<td class="n {_cls(e["marge"])}" data-v="{e["marge"] or 0}">{(e["marge"] or 0):+.0%}</td>')
        body.append(
            f"<tr class='{'' if is_good(e) else 'dim'}'><td class='n rank'>{i}</td>"
            f"<td>{ctx.label(e['item_id'], sub=f'{METIERS.get(e['metier'], e['metier'])} · maîtrise {e['maitrise']} · lot ×{e['lot']:g}')}</td>"
            f"<td>{res}</td>"
            + ("" if harvest else _num_td(e["achats_u"], color=False))
            + _num_td(e["prix_real"], color=False) + _num_td(e["net_u"]) + cols
            + _num_td(e["ma_part_j"], color=False)
            + _num_td(e["profit_j"], "big", k=True)
            + _num_td(e["vol_serveur_j"], color=False, x=True) + _num_td(e["prix_affiche"], color=False, x=True)
            + _num_td(e["prix_ref"], color=False, x=True) + _num_td(e["net_pess_u"], x=True)
            + _num_td(e["profit_pess_j"], k=True, x=True)
            + ("" if harvest else _num_td(e["capital_j"], color=False, k=True, x=True))
            + f"<td>{status(e)}</td></tr>")
    return toolbar(tid) + f'<div class="wrap"><table id="{tid}"><thead>{head}</thead><tbody>{"".join(body)}</tbody></table></div>'


def table_targets(ctx, targets):
    body = []
    for t in targets:
        uses = '<div class="uses">' + "".join(
            f"<div>{esc(u['objet'])} : <b class='{_cls(u['net_par_ressource'])}'>{fmt(u['net_par_ressource'])}</b> / ressource"
            + (f" <span class='mut'>· ~{fmt(u['ressources_j'])} ressources/j</span>" if u["fiable"] else "")
            + ("" if u["fiable"] else f" <span class='badge b-warn'>⚠ {esc('; '.join(u['flags']) or 'à perte')}</span>")
            + "</div>" for u in t["usages"]) + "</div>"
        body.append(f"<tr class='{'' if t['meilleur'] else 'dim'}'><td>{ctx.label(name=t['ressource'])}</td>"
                    f"{_num_td(t['prix_brut'], color=False)}{_num_td(t['meilleur'], 'big')}"
                    f"<td>{uses}</td>{_num_td(t['absorbable_j'], color=False)}</tr>")
    head = ("<tr>" + _th("Ressource") + _th("Prix brut HDV", "Prix du brut en vente (tu ne peux pas le vendre)", True)
            + _th("Meilleur net / ressource", "Ce que te rapporte chaque ressource récoltée dans son meilleur craft fiable", True)
            + _th("Que fabriquer avec") + _th("Utilisable/j", "Ressources que le marché absorbe par jour via les crafts fiables", True)
            + "</tr>")
    return (toolbar("targets") + f'<div class="wrap"><table id="targets"><thead>{head}</thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


def lots_txt(e):
    """« 4 annonces de 100 » : comment decouper ce qu'on met en vente dans la journee."""
    n, lot = e.get("nb_lots_j"), e.get("lot_vente")
    if not n:
        return "–"
    return f"{n} annonce{'s' if n > 1 else ''} de {fmt(lot)}"


def hours_html(h):
    """Barres des ventes par heure, fenetre de 3 h la plus active en surbrillance."""
    if not h:
        return ('<p class="mut">Heures de vente : pas encore assez d’historique horaire, '
                'il se remplit à chaque passage quotidien.</p>')
    top = max(h["share"])
    bars = "".join(
        f'<div class="hb{" on" if (i - h["best"]) % 24 < 3 else ""}" title="{i}h : {v:.1%} des ventes">'
        f'<i style="height:{v / top * 100:.0f}%"></i><span>{i if i % 3 == 0 else ""}</span></div>'
        for i, v in enumerate(h["share"]))
    return (f'<div class="card"><div class="row"><span>Meilleur moment pour poster : '
            f'<b>{h["best"]}h – {(h["best"] + 3) % 24}h</b> · creux : {h["low"]}h – {(h["low"] + 3) % 24}h</span>'
            f'<span>{fmt(h["sold"])} annonces vendues sur {h["days"]} j · heure de {h["tz"]}</span></div>'
            f'<div class="hours">{bars}</div></div>')


def table_plan(plan):
    if not plan:
        return ('<div class="card"><b>Pas encore de plan.</b><span class="mut">Renseigne <code>harvest_per_day</code> dans '
                '<code>config.json</code>, par exemple <code>{"Bois d\'Asvata": 300, "Azpha": 150}</code>, '
                'pour obtenir ton plan de production du jour.</span></div>')
    body = "".join(f"<tr><td>{esc(p['objet'])}</td>{_num_td(p['quantite_j'], color=False)}{_num_td(p['prix_conseille'], color=False)}"
                   f"{_num_td(p['net_u'])}{_num_td(p['kinah_j'], 'big', k=True)}<td>{lots_txt(p)}</td><td class='sub'>"
                   f"{esc(', '.join(f'{k} ×{v}' for k, v in p['ressources'].items()))}</td></tr>" for p in plan)
    total = sum(p["kinah_j"] for p in plan)
    return (f'<div class="kpis"><div class="kpi"><div class="l">Total estimé</div><div class="v pos">{kfmt(total)}</div>'
            f'<div class="s">kinah par jour</div></div></div><div class="wrap"><table><thead><tr>{_th("Craft")}'
            f'{_th("Quantité/j", None, True)}{_th("Vendre à", None, True)}{_th("Net/u", None, True)}'
            f'{_th("Kinah/j", None, True)}{_th("Mettre en vente", "Taille habituelle des lots vendus sur le marché")}'
            f'{_th("Ressources utilisées")}</tr></thead><tbody>{body}</tbody></table></div>')


def table_market(con, ctx, cfg):
    servers = [str(s) for s in cfg["watch_servers"]]
    names = {r["id"]: r["name"] for r in con.execute("SELECT id, name FROM servers")}
    latest = {}
    for s in servers:
        for r in con.execute("""SELECT item_id, price, listings FROM quotes q WHERE server=? AND ts=(SELECT MAX(ts)
                                FROM quotes q2 WHERE q2.server=q.server AND q2.item_id=q.item_id)""", (s,)):
            latest.setdefault(r["item_id"], {})[s] = (r["price"], r["listings"])
    head = ("<tr>" + _th("Item") + _th("Catégorie") + "".join(
        _th(f"{names.get(s, s)} prix", None, True) + _th("annonces", None, True) for s in servers)
        + _th("Nom anglais", None, False, True) + _th("Contrôle du nom", None, False, True) + "</tr>")
    body = []
    for iid, per in sorted(latest.items(), key=lambda kv: (ctx.items.get(kv[0]) or {}).get("name") or ""):
        it = ctx.items.get(iid) or {}
        cells = "".join(_num_td(per.get(s, (None, None))[0], color=False) + _num_td(per.get(s, (None, None))[1], "mut", color=False)
                        for s in servers)
        chk = it.get("name_check") or ""
        body.append(f"<tr><td>{ctx.label(iid)}</td><td class='sub'>{esc(it.get('auction_category') or it.get('sub_category'))}</td>"
                    f"{cells}<td class='sub x'>{esc(it.get('name_en'))}</td>"
                    f"<td class='x'><span class='badge {'b-ok' if chk == 'ok' else 'b-warn'}'>{esc(chk)}</span></td></tr>")
    return (toolbar("market", f'<span class="mut">{len(latest)} items en vente sur les serveurs suivis</span>')
            + f'<div class="wrap"><table id="market"><thead>{head}</thead><tbody>{"".join(body)}</tbody></table></div>')


def map_world_ids(con, cfg):
    """Zones affichees : celles de la version du jeu du joueur (config map_worlds), sinon toutes."""
    ids = [str(w) for w in cfg.get("map_worlds") or []]
    return ids or [r["id"] for r in con.execute("SELECT id FROM map_worlds")]


def write_map_data(con, cfg):
    allowed = set(map_world_ids(con, cfg))
    worlds = {}
    for r in con.execute("SELECT * FROM map_worlds"):
        if r["id"] not in allowed:
            continue
        local = MAP_DIR / f"{r['map_key']}.webp"
        url = f"../data/maps/{local.name}" if r["layer"] == "image" and local.exists() else r["url"]
        worlds[r["id"]] = dict(name=r["name"], grp=r["grp"], nx=r["nx"], ny=r["ny"], layer=r["layer"], url=url)
    nodes = [[r["name"], r["world_id"], round(r["px"], 1), round(r["py"], 1)]
             for r in con.execute("SELECT name, world_id, px, py FROM gather_nodes WHERE px IS NOT NULL")
             if r["world_id"] in worlds]
    (REPORT_DIR / "map_data.js").write_text("window.MAPDATA=" + json.dumps({"worlds": worlds, "nodes": nodes},
                                                                         ensure_ascii=False) + ";", encoding="utf-8")
    (REPORT_DIR / "map.html").write_text(MAP_HTML, encoding="utf-8")


def _md(s):
    """Mise en forme minimale des messages d'alerte (**gras**)."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(s))


def home(con, cfg, ctx, my, sname):
    """Page d'accueil : uniquement ce qui sert a faire du profit aujourd'hui."""
    m = my["market"]
    good = [e for e in my["harvest"] if is_good(e)]
    top = good[:6]
    total = sum(e["profit_j"] for e in good[:5])
    buys = [e for e in my["buy"] if is_good(e) and e["net_pess_u"] > 0]
    targets = [t for t in my["targets"] if t["meilleur"]][:6]

    kpis = (f'<div class="kpis">'
            f'<div class="kpi"><div class="l">Potentiel du jour</div><div class="v pos">{kfmt(total)}</div>'
            f'<div class="s">kinah/j avec tes 5 meilleurs crafts</div></div>'
            f'<div class="kpi"><div class="l">Meilleur craft</div><div class="v" style="font-size:19px">'
            f'{esc(top[0]["objet"]) if top else "–"}</div><div class="s">{kfmt(top[0]["profit_j"]) + " /j" if top else ""}</div></div>'
            f'<div class="kpi"><div class="l">Achat → craft</div><div class="v {"pos" if buys else "mut"}">{len(buys)}</div>'
            f'<div class="s">{"opportunité(s) sûre(s)" if buys else "rien de sûr aujourd’hui"}</div></div>'
            f'<div class="kpi"><div class="l">Activité {esc(sname)}</div><div class="v">×{my["ratio"]:.2f}</div>'
            f'<div class="s">par rapport à Kaisinel</div></div></div>')

    # 1. fabriquer et vendre
    cards = []
    for e in top:
        med = m.median_price(e["item_id"], 3)
        r = e["prix_affiche"] / med if med else 1
        if r >= cfg["alerts"]["spike_ratio"]:
            tip = '<span class="badge b-ok">📈 Prix haut : vends maintenant</span>'
        elif r <= cfg["alerts"]["dump_ratio"]:
            tip = '<span class="badge b-bad">📉 Prix bas : garde ton stock</span>'
        else:
            tip = '<span class="badge b-mut">Prix stable</span>'
        res = "".join(f'<span class="chip">{ctx.icon(name=k)}{esc(k)} ×{v:g}{ctx.mapbtn(k)}</span>'
                      for k, v in e["ressources"].items())
        cards.append(
            f'<div class="card">{ctx.label(e["item_id"], sub=f"{METIERS.get(e["metier"], e["metier"])} · lot ×{e["lot"]:g}")}'
            f'<div class="chips">{res}</div>'
            f'<div class="row"><span>Vendre à</span><b>{fmt(e["prix_real"])}</b></div>'
            f'<div class="row"><span>Net par unité</span><b class="pos">{fmt(e["net_u"])}</b></div>'
            f'<div class="row"><span>À vendre par jour</span><b>~{fmt(e["ma_part_j"])}</b></div>'
            f'<div class="row"><span>Mettre en vente</span><b>{lots_txt(e)}</b></div>'
            f'<div class="row"><span>Profit/j</span><span class="big">{kfmt(e["profit_j"])}</span></div>{tip}</div>')
    craft_html = f'<div class="cards">{"".join(cards)}</div>' if cards else '<p class="mut">Aucun craft rentable.</p>'

    # 2. quoi recolter
    rows = "".join(
        f"<tr><td>{ctx.label(name=t['ressource'])}</td><td>{esc(t['usages'][0]['objet'])}</td>"
        f"{_num_td(t['meilleur'], 'big')}{_num_td(t['absorbable_j'], color=False)}</tr>" for t in targets)
    gather_html = (f'<div class="wrap"><table><thead><tr>{_th("Ressource")}{_th("La transformer en")}'
                   f'{_th("Gain / ressource", None, True)}{_th("Utilisable/j", "Ressources que le marché absorbe par jour", True)}'
                   f'</tr></thead><tbody>{rows}</tbody></table></div>')

    # 3. achat -> craft
    if buys:
        brow = "".join(f"<tr><td>{ctx.label(e['item_id'])}</td><td class='ing'>{'<br>'.join(esc(x) for x in e['ingredients'])}</td>"
                       f"{_num_td(e['achats_u'], color=False)}{_num_td(e['prix_real'], color=False)}{_num_td(e['net_u'])}"
                       f"{_num_td(e['profit_j'], 'big', k=True)}</tr>" for e in buys[:5])
        buy_html = (f'<div class="wrap"><table><thead><tr>{_th("Craft")}{_th("Acheter")}{_th("Coût/u", None, True)}'
                    f'{_th("Vendre à", None, True)}{_th("Net/u", None, True)}{_th("Profit/j", None, True)}</tr></thead>'
                    f'<tbody>{brow}</tbody></table></div>')
    else:
        buy_html = ('<div class="card"><span class="mut">Aucun achat → craft → revente n’est sûr aux prix actuels '
                    '(les prix de la restriction anti-bot rendent les ingrédients trop chers). Tu seras alerté sur Discord '
                    'dès qu’une opportunité apparaît.</span></div>')

    # 4. alertes du jour
    since = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0).isoformat(timespec="seconds")
    al = con.execute("SELECT ts, message FROM alerts_sent WHERE ts >= ? ORDER BY ts DESC LIMIT 12", (since,)).fetchall()
    alert_html = ('<div class="uses">' + "".join(
        f'<div class="card" style="padding:10px 14px"><span><span class="mut">{esc(paris(a["ts"], "%H:%M"))}</span> · {_md(a["message"])}</span></div>'
        for a in al) + "</div>") if al else '<p class="mut">Aucune alerte aujourd’hui.</p>'

    return (f"<h2>Aujourd’hui sur {esc(sname)}</h2><p class='lead'>Ce qu’il faut faire aujourd’hui pour gagner un maximum de kinah. "
            "Les tableaux complets sont dans les autres onglets.</p>" + kpis
            + "<h3>① Fabriquer et vendre</h3>" + hours_html(my.get("hours")) + "<br>" + craft_html
            + "<h3>② Quoi récolter</h3>" + gather_html
            + "<h3>③ Acheter → fabriquer → revendre</h3>" + buy_html
            + "<h3>④ Alertes du jour</h3>" + alert_html)


def build(con, cfg, results):
    REPORT_DIR.mkdir(exist_ok=True)
    ctx = Ctx(con, map_world_ids(con, cfg))
    write_map_data(con, cfg)
    names = {r["id"]: r["name"] for r in con.execute("SELECT id, name FROM servers")}
    my = next((r for r in results if r["server"] == str(cfg["my_server"])), results[0] if results else None)
    sname = names.get(my["server"], my["server"]) if my else "?"
    sections, navs = [], []

    def add(sid, title, content):
        navs.append(f'<button data-t="{sid}" onclick="show(\'{sid}\')">{title}</button>')
        sections.append(f'<section id="{sid}">{content}</section>')

    def sep():
        navs.append('<span class="sep"></span>')

    hyp = (f"Part de marché {cfg['market_share']:.0%}, taxes et frais {cfg['fees']:.0%}. "
           "« Vendre à » = prix réaliste entre le prix affiché et le prix de vente réel de référence.")
    if my:
        add("home", "🏠 Aujourd’hui", home(con, cfg, ctx, my, sname))
        sep()
        add("harvest", "Mes crafts (récolte)",
            f"<h2>Ma récolte → craft → vente</h2><p class='lead'>Tes ressources récoltées sont gratuites. {hyp} "
            f"Activité ×{my['ratio']:.2f} par rapport à Kaisinel.</p>" + table_crafts(ctx, my["harvest"], "th", True))
        add("targets", "Quoi récolter",
            "<h2>Quoi récolter, et en quoi le transformer</h2><p class='lead'>Classement des ressources par gain réel "
            "une fois transformées. Les usages douteux ou à perte sont indiqués en orange.</p>" + table_targets(ctx, my["targets"]))
        add("buy", "Achat → craft",
            f"<h2>Acheter les ingrédients → fabriquer → revendre</h2><p class='lead'>{hyp}</p>"
            + table_crafts(ctx, my["buy"], "tb", False))
        add("plan", "Plan du jour", "<h2>Plan de production du jour</h2>" + table_plan(my["plan"]))
        sep()
    others = [r for r in results if r is not my]
    if others:
        parts = []
        for r in others:
            on = names.get(r["server"], r["server"])
            parts.append(f"<h2>{esc(on)}</h2><p class='lead'>Activité ×{r['ratio']:.2f} par rapport à Kaisinel.</p>"
                         + table_crafts(ctx, r["harvest"], f"th_{r['server']}", True))
        add("compare", "Autres serveurs", "".join(parts))
    add("market", "Marché", "<h2>Tous les items en vente</h2>" + table_market(con, ctx, cfg))
    gathers = sorted(ctx.gather_names)
    cards = "".join(f'<div class="card" style="flex-direction:row;align-items:center;justify-content:space-between">'
                    f'{ctx.label(name=g, sub=f"{ctx.gather_counts.get(g, 0)} points")}</div>' for g in gathers)
    add("map", "🗺 Carte", "<h2>Ressources de récolte</h2><p class='lead'>Clique sur MAP pour voir les points de récolte.</p>"
        f'<div class="cards">{cards}</div>')
    as_of = my["as_of"] if my else "?"
    page = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HDV Aion 2</title><style>{CSS}</style><script>{JS}</script></head><body>
<header><h1>HDV Aion 2 · <b>{esc(sname)}</b></h1>
<div class="meta">Prix relevés le {esc(paris(as_of) if my and as_of else "?")} (heure de Paris)<br>Page générée le {esc(paris())}</div></header>
<nav>{''.join(navs)}</nav><main>{''.join(sections)}</main>
<div id="modal" onclick="if(event.target===this)closeMap()"><div class="box"><div class="bar"><b id="mtitle"></b>
<button class="mapbtn" onclick="closeMap()">Fermer ✕</button></div><iframe id="mframe"></iframe></div></div>
</body></html>"""
    path = REPORT_DIR / "index.html"
    path.write_text(page, encoding="utf-8")
    return path
