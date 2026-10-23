"""Fichiers annexes du rapport : courbes de prix (prices.js), carte des ressources (map.html, map_data.js)."""
import json
from datetime import datetime, timedelta, timezone

from ..config import DATA_DIR, REPORT_DIR

MAP_DIR = DATA_DIR / "maps"
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


def write_price_data(con, cfg, days=7):
    """Historique horaire du serveur suivi (prix plancher, annonces) pour les courbes, charge a la demande (prices.js).
    Releves horaires a2-tracker, completes par l'historique horaire aion2.exchange."""
    server = str(cfg["my_server"])
    now = datetime.now(timezone.utc)
    t0 = int((now - timedelta(days=days)).timestamp()) // 3600 * 3600
    since = datetime.fromtimestamp(t0, timezone.utc).isoformat()[:19]
    series = {}

    def put(iid, ts, price, listings):
        h = int(datetime.fromisoformat(ts[:19]).replace(tzinfo=timezone.utc).timestamp() - t0) // 3600
        if h >= 0 and price:
            series.setdefault(iid, {})[h] = [h, round(price), int(listings or 0)]
    srv = con.execute("SELECT ax_id FROM servers WHERE id=?", (server,)).fetchone()
    if srv and srv["ax_id"]:
        for r in con.execute("SELECT item_id, ts, close, listings FROM ax_prices WHERE ax_server=? AND bucket='1h' "
                             "AND ts>=?", (srv["ax_id"], since)):
            put(r["item_id"], r["ts"], r["close"], r["listings"])
    for r in con.execute("SELECT item_id, ts, price, listings FROM quotes WHERE server=? AND ts>=?", (server, since)):
        put(r["item_id"], r["ts"], r["price"], r["listings"])     # le releve horaire prime
    data = {str(i): [v[h] for h in sorted(v)] for i, v in series.items() if len(v) >= 2}
    (REPORT_DIR / "prices.js").write_text("window.PRICES=" + json.dumps({"t0": t0, "s": data}, separators=(",", ":"))
                                          + ";", encoding="utf-8")
    return {int(i) for i in data}


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
