"""Rapport HTML statique (reports/index.html) + carte des ressources (reports/map.html)."""
import html
import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

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
tr.better td:first-child{box-shadow:inset 3px 0 0 var(--ok)}tr.worse td:first-child{box-shadow:inset 3px 0 0 var(--bad)}
.seg{display:inline-flex;border:1px solid var(--line);border-radius:9px;overflow:hidden;margin:0 0 12px}
.seg button{background:var(--card);color:var(--mut);border:0;padding:8px 16px;font:inherit;font-size:14px;font-weight:600;cursor:pointer}
.seg button.on{background:var(--card2);color:var(--acc)}
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
.hb.on i{background:var(--acc)}
#cmodal{position:fixed;inset:0;background:#000b;display:none;align-items:center;justify-content:center;z-index:55}
#cmodal.on{display:flex}
#cmodal .box{width:min(980px,96vw);max-height:92vh;overflow:auto;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
#cmodal .bar{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:6px}
.ch{position:relative}.ch svg{display:block;width:100%;overflow:visible}
.ch .cap{color:var(--mut);font-size:12px;text-transform:uppercase;letter-spacing:.05em;margin:10px 0 2px}
#ctip{position:absolute;pointer-events:none;background:var(--card2);border:1px solid var(--line);border-radius:8px;padding:6px 9px;
 font-size:12.5px;white-space:nowrap;display:none;z-index:2}
.locked{opacity:.45}tr.locked td{background:#0000}
.mcard{display:flex;flex-direction:column;gap:8px}.mcard .lv{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.mcard input{width:72px;padding:6px 8px;border:1px solid var(--line);border-radius:7px;background:var(--bg2);color:var(--txt);font:inherit;font-size:18px;font-weight:700;text-align:center}
.mcard .up{font-size:15px;padding:6px 14px}
.todo ol{margin:4px 0 0;padding-left:22px;display:flex;flex-direction:column;gap:6px;font-size:14.5px}
.todo li.td-bad::marker{color:var(--bad)}.todo li.td-warn::marker{color:var(--warn)}.todo li.td-ok::marker{color:var(--ok)}
.nm{cursor:copy}.nm:hover{text-decoration:underline dotted}
#toast{position:fixed;bottom:22px;left:50%;transform:translateX(-50%);background:var(--card2);border:1px solid var(--acc);color:var(--txt);
 padding:8px 14px;border-radius:8px;opacity:0;transition:opacity .2s;pointer-events:none;z-index:60;max-width:90vw}
#toast.on{opacity:1}
.stock{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:8px;margin:0 0 16px}
.sk{display:flex;align-items:center;gap:8px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:6px 10px;font-size:13.5px}
.sk span{flex:1;min-width:0}
.sk input{width:92px;padding:6px 8px;border:1px solid var(--line);border-radius:7px;background:var(--bg2);color:var(--txt);font:inherit;text-align:right}
.sk input:focus{outline:none;border-color:var(--acc)}
#paste{width:100%;min-height:110px;padding:8px 10px;border:1px solid var(--line);border-radius:8px;background:var(--bg2);color:var(--txt);
 font:13px/1.5 ui-monospace,Consolas,monospace;margin:6px 0}
#paste:focus{outline:none;border-color:var(--acc)}.hb span{font-size:10px;color:var(--mut);height:12px;line-height:12px}
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
function toast(msg){let el=document.getElementById('toast');if(!el){el=document.createElement('div');el.id='toast';document.body.appendChild(el)}
 el.textContent=msg;el.classList.add('on');clearTimeout(el._t);el._t=setTimeout(()=>el.classList.remove('on'),1600)}
function copyOld(t,done){const a=document.createElement('textarea');a.value=t;a.style.position='fixed';a.style.opacity='0';
 document.body.appendChild(a);a.select();try{document.execCommand('copy');done()}catch(e){}a.remove()}
document.addEventListener('click',e=>{const n=e.target.closest('.nm');if(!n)return;const t=n.textContent.trim(),done=()=>toast('Copié : '+t);
 if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(t).then(done,()=>copyOld(t,done));else copyOld(t,done)});
const NF=new Intl.NumberFormat('fr-FR',{maximumFractionDigits:0});
function kf(n){const a=Math.abs(n);return a>=1e6?(n/1e6).toFixed(2).replace('.',',')+' M':a>=1e4?Math.round(n/1e3)+' k':NF.format(n)}
function escH(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
function calc(){const box=document.getElementById('stock');if(!box||!window.CRAFTS)return;const st={};
 box.querySelectorAll('input[data-r]').forEach(i=>{const v=parseFloat(i.value);if(v>0)st[i.dataset.r]=v});
 try{localStorage.setItem('stock',JSON.stringify(st))}catch(e){}
 const cap=document.getElementById('cap').checked,risky=document.getElementById('risky').checked,left={...st},rows=[];let tot=0;
 const lose=lvState().lose;
 for(const c0 of CRAFTS){if(c0.f&&!risky)continue;const info=craftInfo(c0.i);if(info&&!info.ok)continue;
  const p=info&&info.rate?info.rate:1,c={...c0,n:c0.s!=null?Math.round(c0.s-(lose?c0.a/p:c0.a)):c0.n,r:{}};
  Object.entries(c0.r).forEach(([k,q])=>c.r[k]=lose?q/p:q);if(c.n<=0)continue;
  const T=window.TRANSMUTE||{},avail=k=>(left[k]||0)+(T[k]?(left[T[k]]||0):0);   // Od transmutable 1 pour 1
  const need=Object.entries(c.r);if(!need.length||need.some(([k])=>!(avail(k)>0)))continue;
  let n=Math.min(...need.map(([k,q])=>avail(k)/q));if(cap&&!c.f)n=Math.min(n,c.c);n=Math.floor(n);if(n<=0)continue;
  need.forEach(([k,q])=>{let want=n*q;const own=Math.min(want,left[k]||0);left[k]=(left[k]||0)-own;want-=own;
   if(want>0&&T[k]){left[T[k]]-=want;c.trans=(c.trans||0)+want;c.transFrom=T[k]}});tot+=n*c.n;rows.push([c,n])}
 document.getElementById('stot').textContent=rows.length?kf(tot):'–';
 document.querySelector('#splan tbody').innerHTML=rows.length?rows.map(([c,n])=>{const l=c.l?Math.min(c.l,n):0;
  return `<tr><td><span class="nm" title="Cliquer pour copier">${escH(c.o)}</span>${c.f?`<div><span class="badge b-warn">⚠ ${escH(c.f)}</span></div>`:''}</td><td class="n">${NF.format(n)}</td>`
  +`<td class="n">${NF.format(c.p)}</td><td class="n pos">${NF.format(c.n)}</td><td class="n big pos">${kf(n*c.n)}</td>`
  +`<td>${l?Math.max(1,Math.round(n/l))+' annonce(s) de '+NF.format(l):'–'}</td>`
  +`<td class="sub">${escH(Object.entries(c.r).map(([k,q])=>k+' ×'+NF.format(Math.ceil(n*q))).join(', ')+(c.trans?' (dont '+NF.format(Math.ceil(c.trans))+' '+c.transFrom+' transmuté)':''))}</td></tr>`}).join('')
  :'<tr><td colspan="7" class="mut">Entre tes quantités de ressources ci-dessus.</td></tr>';
 const rest=Object.entries(left).filter(([k,v])=>v>=1).map(([k,v])=>k+' ×'+NF.format(Math.floor(v)));
 document.getElementById('sleft').textContent=rest.length?'Ressources non utilisées (aucun craft rentable ou limite du marché atteinte) : '+rest.join(', '):''}
function openChart(id,name){document.getElementById('ctitle').textContent=name;document.getElementById('cmodal').classList.add('on');
 const go=()=>drawChart(String(id));if(window.PRICES)return go();const sc=document.createElement('script');sc.src='prices.js';sc.onload=go;
 sc.onerror=()=>{document.getElementById('cbody').textContent='Historique indisponible.'};document.head.appendChild(sc)}
function closeChart(){document.getElementById('cmodal').classList.remove('on')}
function drawChart(id){const box=document.getElementById('cbody'),raw=(PRICES.s[id]||[]);
 if(raw.length<2){box.innerHTML='<p class="mut">Pas encore assez de relevés pour cet item.</p>';return}
 const pts=raw.map(r=>({t:(PRICES.t0+r[0]*3600)*1000,p:r[1],l:r[2]})),W=Math.max(320,box.clientWidth||900),L=64,R=12,pw=W-L-R;
 const t0=pts[0].t,t1=pts[pts.length-1].t,x=t=>L+(t1>t0?(t-t0)/(t1-t0):0)*pw;
 const ps=pts.map(d=>d.p),lo=Math.min(...ps),hi=Math.max(...ps),pad=(hi-lo)*.08||hi*.05||1,y0=lo-pad,y1=hi+pad,H=220;
 const yp=v=>8+(1-(v-y0)/(y1-y0))*(H-30);let path='';pts.forEach((d,i)=>{const gap=i&&d.t-pts[i-1].t>3*3600e3;
  path+=(i===0||gap?'M':'L')+x(d.t).toFixed(1)+' '+yp(d.p).toFixed(1)});
 const grid=[lo,(lo+hi)/2,hi].map(v=>`<line x1="${L}" x2="${W-R}" y1="${yp(v)}" y2="${yp(v)}" stroke="var(--line2)"/>`
  +`<text x="${L-8}" y="${yp(v)+4}" text-anchor="end" fill="var(--mut)" font-size="11">${kf(v)}</text>`).join('');
 const days=[];const d0=new Date(t0);d0.setHours(24,0,0,0);for(let d=d0.getTime();d<=t1;d+=864e5)days.push(d);
 const xl=(h)=>days.map(d=>`<line x1="${x(d)}" x2="${x(d)}" y1="4" y2="${h-22}" stroke="var(--line2)"/>`
  +`<text x="${x(d)}" y="${h-6}" text-anchor="middle" fill="var(--mut)" font-size="11">${new Date(d).toLocaleDateString('fr-FR',{day:'2-digit',month:'2-digit'})}</text>`).join('');
 const ls=pts.map(d=>d.l||0),lm=Math.max(1,...ls),H2=110,bw=Math.max(1,pw/Math.max(1,(t1-t0)/3600e3)-2);
 const yl=v=>4+(1-v/lm)*(H2-30),bars=pts.map(d=>`<rect x="${(x(d.t)-bw/2).toFixed(1)}" y="${yl(d.l||0).toFixed(1)}" width="${bw.toFixed(1)}" height="${(H2-26-yl(d.l||0)).toFixed(1)}" rx="${Math.min(2,bw/2)}" fill="var(--mut)" opacity=".55"/>`).join('');
 box.innerHTML=`<div class="ch"><div class="cap">Prix le plus bas en vente (kinah)</div><svg id="cs1" viewBox="0 0 ${W} ${H}" height="${H}">${grid}${xl(H)}`
  +`<path d="${path}" fill="none" stroke="var(--acc)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>`
  +`<line id="cx1" y1="4" y2="${H-22}" stroke="var(--txt)" opacity=".35" visibility="hidden"/><circle id="cd" r="4.5" fill="var(--acc)" stroke="var(--card)" stroke-width="2" visibility="hidden"/></svg>`
  +`<div class="cap">Nombre d'annonces</div><svg id="cs2" viewBox="0 0 ${W} ${H2}" height="${H2}">`
  +`<text x="${L-8}" y="${yl(lm)+4}" text-anchor="end" fill="var(--mut)" font-size="11">${NF.format(lm)}</text>${xl(H2)}${bars}`
  +`<line id="cx2" y1="4" y2="${H2-22}" stroke="var(--txt)" opacity=".35" visibility="hidden"/></svg><div id="ctip"></div></div>`
  +`<p class="mut" style="font-size:12.5px;margin:8px 0 0">${pts.length} relevés · prix ${kf(lo)} à ${kf(hi)} · heure de ton navigateur</p>`;
 const ch=box.querySelector('.ch'),tip=document.getElementById('ctip');
 const move=e=>{const r=ch.getBoundingClientRect(),sx=(e.clientX-r.left)*W/r.width,t=t0+(sx-L)/pw*(t1-t0);
  let k=0;pts.forEach((d,i)=>{if(Math.abs(d.t-t)<Math.abs(pts[k].t-t))k=i});const d=pts[k],X=x(d.t);
  ['cx1','cx2'].forEach(i=>{const el=document.getElementById(i);el.setAttribute('x1',X);el.setAttribute('x2',X);el.setAttribute('visibility','visible')});
  const c=document.getElementById('cd');c.setAttribute('cx',X);c.setAttribute('cy',yp(d.p));c.setAttribute('visibility','visible');
  tip.innerHTML=`<span class="mut">${new Date(d.t).toLocaleString('fr-FR',{weekday:'short',day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'})}</span><br><b>${NF.format(d.p)}</b> kinah · ${NF.format(d.l||0)} annonce(s)`;
  tip.style.display='block';const px=X*r.width/W;tip.style.left=Math.min(Math.max(0,px+12),r.width-tip.offsetWidth)+'px';tip.style.top='30px'};
 ch.onmousemove=move;ch.ontouchmove=e=>move(e.touches[0]);
 ch.onmouseleave=()=>{tip.style.display='none';['cx1','cx2','cd'].forEach(i=>document.getElementById(i).setAttribute('visibility','hidden'))}}
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeChart()});
function normName(s){return s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').replace(/[’`]/g,"'").replace(/\\s+/g,' ').trim().toLowerCase()}
function importStock(){const txt=document.getElementById('paste').value,inputs=[...document.querySelectorAll('#stock input[data-r]')];
 const by={};inputs.forEach(i=>by[normName(i.dataset.r)]=i);const got={},unknown=[];
 txt.split(/\\n/).forEach(line=>{const m=line.replace(/\\(li[ée]+s?\\)/i,'').match(/^\\s*[-•*]?\\s*(.+?)\\s*[:=x×\\s]\\s*(\\d[\\d\\s.]*)\\s*$/i);
  if(!m||line.trim().startsWith('#'))return;const n=normName(m[1]),q=parseInt(m[2].replace(/[\\s.]/g,''),10);if(!q)return;
  if(by[n])got[n]=(got[n]||0)+q;else unknown.push(m[1].trim())});
 const mode=document.getElementById('pmode').value;if(mode==='replace')inputs.forEach(i=>i.value='');
 Object.entries(got).forEach(([n,q])=>{const i=by[n];i.value=(mode==='add'?(parseFloat(i.value)||0):0)+q});calc();
 document.getElementById('pmsg').textContent=Object.keys(got).length+' ressource(s) remplie(s)'+(unknown.length?' · non reconnues : '+unknown.join(', '):'')}
function scanLoad(){return window.reserveToList?Promise.resolve():new Promise((ok,ko)=>{const sc=document.createElement('script');
 sc.src='scan.js';sc.onload=ok;sc.onerror=()=>ko('outil de lecture introuvable');document.head.appendChild(sc)})}
async function scanFile(file){if(!file||!(file.type||'').startsWith('image/'))return;const msg=document.getElementById('smsg'),box=document.getElementById('sthumbs');
 msg.textContent='Lecture de la capture…';box.innerHTML='';
 try{await scanLoad();const url=URL.createObjectURL(file);
  const img=await new Promise((ok,ko)=>{const i=new Image();i.onload=()=>ok(i);i.onerror=()=>ko('image illisible');i.src=url});
  const r=await reserveToList(img,m=>msg.textContent=m);URL.revokeObjectURL(url);
  document.getElementById('paste').value=r.text;document.getElementById('pdet').open=true;
  msg.textContent=r.found+' ressource(s) reconnue(s), '+r.ignored+' case(s) ignorée(s) (autres objets ou cases vides). '
   +'Compare chaque case avec la quantité lue (⚠ = à vérifier en priorité), corrige la liste si besoin, puis clique sur Remplir.';
  r.thumbs.forEach(t=>{const d=document.createElement('span');d.className='chip';if(t.c.checkQty)d.style.borderColor='var(--warn)';
   d.appendChild(t.cv);d.appendChild(document.createTextNode((t.c.checkQty?'⚠ ':'')+t.c.name+' : '+(t.c.qty==null?'?':t.c.qty)));box.appendChild(d)})
 }catch(e){msg.textContent='Lecture impossible : '+e+' (la lecture fonctionne sur le site en ligne)'}}
document.addEventListener('paste',e=>{const it=[...((e.clipboardData||{}).items||[])].find(i=>(i.type||'').startsWith('image/'));if(!it)return;
 const on=id=>{const sec=document.getElementById(id);return sec&&sec.classList.contains('on')};
 if(on('plan')){e.preventDefault();scanFile(it.getAsFile())}else if(on('home')){e.preventDefault();scanSales(it.getAsFile())}
 else if(on('gains')){e.preventDefault();scanHist(it.getAsFile())}});
let SALES=[];
async function scanSales(file){if(!file||!(file.type||'').startsWith('image/'))return;const msg=document.getElementById('vmsg');
 msg.textContent='Lecture de la capture…';
 try{await scanLoad();const url=URL.createObjectURL(file);
  const img=await new Promise((ok,ko)=>{const i=new Image();i.onload=()=>ok(i);i.onerror=()=>ko('image illisible');i.src=url});
  const rows=await scanListings(img,{progress:m=>msg.textContent=m});URL.revokeObjectURL(url);
  rows.forEach(r=>{const cv=document.createElement('canvas');cv.width=cv.height=40;cv.getContext('2d').drawImage(img,r.x,r.y,r.w,r.h,0,0,40,40);r.cv=cv});
  SALES=SALES.concat(rows);renderSales();
  msg.textContent=rows.length+' annonce(s) lue(s)'+(SALES.length>rows.length?' (ajoutées aux précédentes : colle d’autres captures si tes ventes tiennent sur plusieurs écrans)':'')
   +'. Vérifie, corrige le coût si besoin, puis copie le fichier.'}catch(e){msg.textContent='Lecture impossible : '+e+' (la lecture fonctionne sur le site en ligne)'}}
function renderSales(){const box=document.getElementById('vrows');box.innerHTML='';
 SALES.forEach((r,k)=>{const d=document.createElement('span');d.className='chip';if(r.check.length)d.style.borderColor='var(--warn)';d.title=r.check.join(', ');
  d.appendChild(r.cv);d.appendChild(document.createTextNode((r.check.length?'⚠ ':'')+(r.name||'?')+' × '+r.qty+' à '+(r.unit==null?'?':NF.format(r.unit))));box.appendChild(d)});
 const agg={};SALES.forEach(r=>{if(!r.name)return;const a=agg[r.name]||(agg[r.name]={prix:r.unit,quantite:0});a.quantite+=r.qty;
  if(r.unit!=null&&(a.prix==null||r.unit<a.prix))a.prix=r.unit});
 const keep=document.getElementById('vmode').value==='add'?{...(window.MY_LISTINGS||{})}:{};
 Object.entries(agg).forEach(([n,a])=>{const old=keep[n]&&typeof keep[n]==='object'?keep[n]:{};const cost=old.cout??(window.COSTS||{})[n];
  keep[n]={prix:a.prix,quantite:a.quantite,...(cost!=null?{cout:cost}:{})}});
 const file={_:(window.MY_LISTINGS_HELP||''),annonces:keep};document.getElementById('vjson').value=JSON.stringify(file,null,2)}
// historique des ventes -> mes_ventes.json (ventes deja connues + ventes lues, sans doublon, de la plus recente a la plus ancienne)
let HIST=[];
async function scanHist(file){if(!file||!(file.type||'').startsWith('image/'))return;const msg=document.getElementById('gmsg');
 msg.textContent='Lecture de la capture…';
 try{await scanLoad();const url=URL.createObjectURL(file);
  const img=await new Promise((ok,ko)=>{const i=new Image();i.onload=()=>ok(i);i.onerror=()=>ko('image illisible');i.src=url});
  const rows=await scanHistory(img,{progress:m=>msg.textContent=m});URL.revokeObjectURL(url);
  if(!rows.length){msg.textContent='Aucune vente trouvée : capture la liste de l’historique des ventes (prix, montant reçu et date sur chaque ligne).';return}
  rows.forEach(r=>{const cv=document.createElement('canvas');cv.width=cv.height=40;cv.getContext('2d').drawImage(img,r.x,r.y,r.w,r.h,0,0,40,40);r.cv=cv});
  HIST=HIST.concat(rows);renderHist();const bad=rows.filter(r=>r.check.length).length;
  msg.textContent=rows.length+' vente(s) lue(s)'+(bad?', dont '+bad+' à vérifier (en orange : corrige-les dans le texte ci-dessous)':'')
   +'. Colle d’autres captures si ton historique est plus long, puis copie le fichier.'}catch(e){msg.textContent='Lecture impossible : '+e+' (la lecture fonctionne sur le site en ligne)'}}
function renderHist(){const box=document.getElementById('grows');box.innerHTML='';
 HIST.forEach(r=>{const d=document.createElement('span');d.className='chip';if(r.check.length)d.style.borderColor='var(--warn)';d.title=r.check.join(', ');
  d.appendChild(r.cv);d.appendChild(document.createTextNode((r.check.length?'⚠ ':'')+(r.date||'date ?')+' · '+(r.name||'?')+' × '+r.qty+' : '+(r.total==null?'?':NF.format(r.total))));box.appendChild(d)});
 const all={},key=v=>v.date+'|'+v.objet+'|'+v.prix;
 (window.MY_SALES||[]).forEach(v=>all[key(v)]=v);
 HIST.forEach(r=>{const v={date:r.date||'?',objet:r.name||'?',quantite:r.qty,prix:r.total,recu:r.net};all[key(v)]=v});
 const list=Object.values(all).sort((a,b)=>b.date.localeCompare(a.date));
 document.getElementById('gjson').value='{\\n "_": '+JSON.stringify(window.MY_SALES_HELP||'')+',\\n "ventes": [\\n'
  +list.map(v=>'  '+JSON.stringify(v).replace(/,"/g,', "').replace(/":/g,'": ')).join(',\\n')+'\\n ]\\n}\\n'}
function copyHist(){const t=document.getElementById('gjson').value;const done=()=>toast('Contenu de mes_ventes.json copié');
 if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(t).then(done,()=>copyOld(t,done));else copyOld(t,done)}
function copySales(){const t=document.getElementById('vjson').value;const done=()=>toast('Contenu de mes_annonces.json copié');
 if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(t).then(done,()=>copyOld(t,done));else copyOld(t,done)}
const PROF={Alchemy:'Alchimie',Handicrafting:'Artisanat',Armorsmithing:"Forge d'armures",Blacksmithing:"Forge d'armes",Cooking:'Cuisine'};
function lvState(){let st={};try{st=JSON.parse(localStorage.getItem('metiers')||'{}')}catch(e){}st.lv=st.lv||{};if(st.lose===undefined)st.lose=true;return st}
function lvSave(st){try{localStorage.setItem('metiers',JSON.stringify(st))}catch(e){}}
function lvTxt(l){return l>50?'Spécialiste '+(l-50):'Débutant '+l}   // jeu : Débutant 1-50 puis Spécialiste 1-50 (= 51-100)
// meilleure facon de fabriquer un item selon mes niveaux : {ok, rate} ; rate null = metier non renseigne
function craftInfo(id){const st=lvState(),alts=(window.CRAFTDATA&&CRAFTDATA.items[id])||[];if(!alts.length)return null;
 let best=null,unknown=false,need=null;
 alts.forEach(([p,m,cv])=>{const lv=st.lv[p];if(lv==null||lv===''){unknown=true;return}
  if(lv<m){if(!need||m<need.m)need={p:p,m:m};return}
  const c=cv!=null&&CRAFTDATA.curves[cv],rate=c?c[Math.min(lv-m,c.length-1)]/1e8:1;if(!best||rate>best.rate)best={p:p,m:m,rate:rate}});
 if(best)return{ok:true,rate:best.rate,p:best.p,m:best.m};if(unknown)return{ok:true,rate:null};return{ok:false,need:need}}
function applyLevels(){const st=lvState();
 document.querySelectorAll('[data-craft]').forEach(el=>{const info=craftInfo(el.dataset.craft),sr=el.querySelector('.csr');
  el.classList.remove('locked');el.style.display='';
  if(info&&!info.ok){el.classList.add('locked');if(st.hide)el.style.display='none';
   if(sr)sr.textContent='🔒 '+(info.need?PROF[info.need.p]+' '+lvTxt(info.need.m):'');return}
  if(!info||info.rate==null){if(sr)sr.textContent='–';return}
  if(sr)sr.textContent=(info.rate*100).toFixed(1).replace('.',',')+' %';
  const sell=+el.dataset.sell,cost=+el.dataset.cost,day=+el.dataset.day;
  const net=Math.round(sell-(st.lose?cost/info.rate:cost)),cn=el.querySelector('.cnet'),cp=el.querySelector('.cprof');
  if(cn){cn.textContent=NF.format(net);cn.dataset.v=net;cn.classList.toggle('pos',net>0);cn.classList.toggle('neg',net<=0)}
  if(cp){const pr=net*day;cp.textContent=kf(pr);cp.dataset.v=pr;cp.classList.toggle('pos',pr>0);cp.classList.toggle('neg',pr<=0)}});
 calc();renderMetiers();if(window.PLANDATA){planSafe();planGamble()}}
function setLevel(p,v){const st=lvState();if(v===''||v==null||isNaN(v))delete st.lv[p];else st.lv[p]=Math.max(0,Math.min(100,Math.round(v)));lvSave(st);applyLevels()}
function bumpLevel(p,d){const st=lvState();setLevel(p,(st.lv[p]||0)+d);toast(PROF[p]+' : '+lvTxt(lvState().lv[p]))}
function setGrade(p,g,n){const st=lvState(),cur=st.lv[p];if(n===undefined)n=cur==null?'':(cur>50?cur-50:cur);
 if(n===''){setLevel(p,'');return}n=Math.max(0,Math.min(50,+n));setLevel(p,g==='S'?50+Math.max(1,n):n)}
function setOpt(k,v){const st=lvState();st[k]=v;lvSave(st);applyLevels()}
function shareLevels(){const st=lvState(),code=Object.entries(st.lv).map(([p,l])=>p+'-'+l).join('.');
 const url=location.href.split('#')[0]+'#metiers='+code;const done=()=>toast('Lien copié : ouvre-le sur ton autre appareil');
 if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(url).then(done,()=>copyOld(url,done));else copyOld(url,done)}
function renderMetiers(){const box=document.getElementById('metiers');if(!box||!window.CRAFTDATA)return;const st=lvState();
 const good=CRAFTDATA.good||[];
 box.innerHTML=Object.keys(PROF).map(p=>{const lv=st.lv[p];const mine=good.filter(g=>g.a.some(a=>a[0]===p));
  const open=lv==null?null:mine.filter(g=>g.a.some(a=>a[0]===p&&a[1]<=lv)).length;
  const sp=lv!=null&&lv>50;
  return `<div class="card mcard"><b>${PROF[p]}</b><div class="lv"><select class="search" style="width:auto;padding:6px 8px" onchange="setGrade('${p}',this.value)">`
   +`<option value="D"${sp?'':' selected'}>Débutant</option><option value="S"${sp?' selected':''}>Spécialiste</option></select>`
   +`<input type="number" min="0" max="50" value="${lv==null?'':(sp?lv-50:lv)}" placeholder="?" onchange="setGrade('${p}',this.previousElementSibling.value,this.value)">`
   +`<button class="mapbtn up" title="J'ai monté d'un niveau" onclick="bumpLevel('${p}',1)">+1</button></div>`
   +`<span class="sub">${lv==null?'Niveau non renseigné : tous les crafts restent proposés':lvTxt(lv)+' · '+open+' / '+mine.length+' crafts rentables débloqués'}</span></div>`}).join('');
 document.getElementById('mlose').checked=st.lose;document.getElementById('mhide').checked=!!st.hide;
 const soon=[];good.forEach(g=>g.a.forEach(([p,m])=>{const lv=st.lv[p];if(lv!=null&&m>lv&&m<=lv+10&&!g.a.some(a=>st.lv[a[0]]!=null&&a[1]<=st.lv[a[0]]))soon.push({o:g.o,p:p,m:m,d:m-lv,j:g.j})}));
 const seen=new Set(),list=soon.sort((x,y)=>y.j-x.j).filter(x=>!seen.has(x.o)&&seen.add(x.o)).slice(0,12);
 document.getElementById('soon').innerHTML=list.length?'<div class="uses">'+list.map(x=>`<div class="card" style="padding:9px 14px;flex-direction:row;justify-content:space-between"><span><span class="nm" title="Cliquer pour copier">${escH(x.o)}</span> <span class="sub">· ${PROF[x.p]} ${lvTxt(x.m)} (dans ${x.d} niveau${x.d>1?'x':''})</span></span><b class="pos">~${kf(x.j)} /j</b></div>`).join('')+'</div>'
  :'<p class="mut">'+(Object.keys(st.lv).length?'Aucun craft rentable à débloquer dans les 10 prochains niveaux.':'Renseigne tes niveaux ci-dessus.')+'</p>'}
function importLevelsFromHash(){const h=decodeURIComponent(location.hash||'');if(!h.startsWith('#metiers='))return;
 const st=lvState();h.slice(9).split('.').forEach(x=>{const [p,l]=x.split('-');if(PROF[p]&&l!=='')st.lv[p]=+l});lvSave(st);
 history.replaceState(null,'',location.pathname+location.search);toast('Niveaux de métier importés');show('metiersTab')}
// Quoi recolter : kinah par heure de recolte, selon ce que je recolte par heure (100 par defaut)
function rates(){try{return JSON.parse(localStorage.getItem('rates')||'{}')}catch(e){return{}}}
function rateCalc(inp){const R=rates();if(inp){const r=inp.closest('tr').dataset.res;if(inp.value==='')delete R[r];else R[r]=+inp.value;
 try{localStorage.setItem('rates',JSON.stringify(R))}catch(e){}}
 document.querySelectorAll('#targets tr[data-res]').forEach(tr=>{const r=tr.dataset.res,i=tr.querySelector('.rate');
  if(!inp&&R[r]!=null)i.value=R[r];const rate=i.value===''?100:+i.value,best=+tr.dataset.best,abs=+tr.dataset.abs;
  const kh=tr.querySelector('.kh'),hj=tr.querySelector('.hj');
  if(!best||!rate){kh.textContent='–';kh.dataset.v=0;hj.textContent='–';hj.dataset.v=0;return}
  const v=best*rate;kh.textContent=kf(v);kh.dataset.v=v;const h=abs/rate;hj.dataset.v=h;
  hj.textContent=h>=24?'24 h +':(h<1?Math.round(h*60)+' min':h.toFixed(1).replace('.',',')+' h')})}
// ---------------- Planning
function pget(k,d){try{const v=localStorage.getItem(k);return v==null?d:JSON.parse(v)}catch(e){return d}}
function pset(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function stepRate(st,s){const lv=st.lv[s.prof],c=s.cv!=null&&window.CRAFTDATA&&CRAFTDATA.curves[s.cv];
 if(lv==null||lv==='')return{p:c?c[0]/1e8:1,known:false};if(lv<s.m)return{p:0,known:true,locked:true};
 return{p:c?c[Math.min(lv-s.m,c.length-1)]/1e8:1,known:true}}
const fmtH=h=>h<1?Math.round(h*60)+' min':h.toFixed(1).replace('.',',')+' h';
function planSafe(save){const box=document.getElementById('psafe');if(!box||!window.PLANDATA)return;
 const hEl=document.getElementById('phours');if(save)pset('phours',+hEl.value);else hEl.value=pget('phours',3);
 let left=+hEl.value||0;const R=rates(),st=lvState(),slots=[];
 PLANDATA.targets.forEach(t=>{const rate=R[t.r]!=null?R[t.r]:100;if(!rate)return;
  t.u.forEach(u=>{const info=craftInfo(u.i);if(info&&!info.ok)return;const p=info&&info.rate?info.rate:1;
   slots.push({r:t.r,rate:rate,o:u.o,i:u.i,v:u.v,n:u.n*(st.lose?p:1),cap:u.cap,per:u.per/(st.lose?p:1),lot:u.lot})})});
 slots.sort((a,b)=>(b.n*b.rate-a.n*a.rate)||(a.v-b.v));   // a egalite : la ressource elle-meme avant l'Od transmuteconst plan={};let tot=0;
 const used={};                                     // capacite deja prise par craft (partagee Od / ressource)
 for(const s of slots){if(left<=0)break;const room=s.cap-(used[s.i]||0);const h=Math.min(left,room/s.rate);if(h<=0.05)continue;left-=h;
  const res=h*s.rate,units=Math.floor(res/s.per);used[s.i]=(used[s.i]||0)+res;tot+=units*s.per*s.n;
  (plan[s.r]=plan[s.r]||{h:0,res:0,k:0,c:[]});plan[s.r].h+=h;plan[s.r].res+=res;plan[s.r].k+=units*s.per*s.n;
  plan[s.r].c.push({o:s.o,units:units,lot:s.lot,k:units*s.per*s.n})}
 const rows=Object.entries(plan).sort((a,b)=>b[1].k-a[1].k);
 window.SAFEPLAN={tot:tot,hours:(+hEl.value||0)-left,rows:rows};
 const tp=document.getElementById('todo-plan');
 if(tp){const crafts=rows.flatMap(([r,p])=>p.c.filter(c=>c.units>0));
  tp.innerHTML=rows.length?'🌲 Récolter '+rows.slice(0,2).map(([r,p])=>'<b>'+escH(r)+'</b> '+fmtH(p.h)).join(' puis ')
   +' → fabriquer '+crafts.slice(0,3).map(c=>'<b>'+NF.format(c.units)+'</b> × '+escH(c.o)).join(', ')
   +' (~<b class="pos">'+kf(tot)+'</b>). 🕘 Mettre en vente entre <b>'+PLANDATA.best+'</b>'
   +(crafts.some(c=>c.lot)?' : '+crafts.slice(0,3).filter(c=>c.lot).map(c=>Math.max(1,Math.round(c.units/Math.min(c.lot,c.units)))+' annonce(s) de '+NF.format(Math.min(c.lot,c.units))+' '+escH(c.o)).join(', '):'')+'.'
   :'Plan du jour : aucun craft rentable avec ton temps de jeu (Planning).'}
 const kp=document.getElementById('kpot');if(kp){kp.textContent=kf(tot);document.getElementById('kpots').textContent=
  'en '+String(+hEl.value||0).replace('.',',')+' h de jeu (Planning safe, récolte '+(Object.keys(R).length?'saisie':'100/h par défaut')+')'}
 if(!rows.length){box.innerHTML='<p class="mut">Aucun craft rentable à planifier.</p>';return}

 box.innerHTML='<div class="kpis"><div class="kpi"><div class="l">Gain estimé</div><div class="v pos">'+kf(tot)+'</div><div class="s">kinah, une fois tout vendu</div></div>'
  +'<div class="kpi"><div class="l">Temps utilisé</div><div class="v">'+fmtH((+hEl.value||0)-left)+'</div><div class="s">'+(left>0.05?'au-delà, les marchés sont saturés':'de récolte')+'</div></div>'
  +'<div class="kpi"><div class="l">Mise en vente</div><div class="v" style="font-size:20px">'+PLANDATA.best+'</div><div class="s">meilleur moment pour poster</div></div></div>'
  +'<div class="uses">'+rows.map(([r,p],k)=>`<div class="card" style="padding:12px 16px"><b>${k+1}. Récolter <span class="nm" title="Cliquer pour copier">${escH(r)}</span> pendant ${fmtH(p.h)}</b> <span class="sub">(≈ ${NF.format(Math.round(p.res))} ressources)</span>`
   +p.c.filter(c=>c.units>0).map(c=>`<div class="row"><span>→ fabriquer <b>${NF.format(c.units)}</b> × <span class="nm" title="Cliquer pour copier">${escH(c.o)}</span>${c.lot?' · '+Math.max(1,Math.round(c.units/Math.min(c.lot,c.units)))+' annonce(s) de '+NF.format(Math.min(c.lot,c.units)):''}</span><b class="pos">${kf(c.k)}</b></div>`).join('')+'</div>').join('')+'</div>'
  +(Object.keys(R).length?'':'<p class="sub">Récolte par heure : 100 par défaut pour chaque ressource ; indique tes vraies valeurs dans « 🌲 Récolte ».</p>')}
function planGamble(save){const box=document.getElementById('pgamble');if(!box||!window.PLANDATA)return;
 const cEl=document.getElementById('pcombo'),oEl=document.getElementById('popp');
 const def=PLANDATA.chains.length?Math.round(PLANDATA.chains[0].steps[0].c*100):25;
 if(save){pset('pcombo2',+cEl.value);pset('popp',oEl.checked)}else{cEl.value=pget('pcombo2',def);oEl.checked=pget('popp',true)}
 const c=(+cEl.value||0)/100,st=lvState(),safe={};PLANDATA.targets.forEach(t=>safe[t.r]=t.avg);
 const stock=pget('stock',{}),opp=s=>oEl.checked?Object.entries(s.res).reduce((a,[r,q])=>a+q*(safe[r]||0),0):0;
 const out=PLANDATA.chains.map(ch=>{const S=[];
  for(const s of ch.steps){if(s.plain.v==null||s.ecl.v==null||!s.ok)break;const r=stepRate(st,s);S.push({...s,p:r.p,known:r.known,locked:r.locked,cost:s.cost+opp(s)})}
  if(S.length<2)return null;                       // une seule etape : pas une chaine a jouer
  const weird=S.some(s=>s.plain.v>s.ecl.v);         // objet normal plus cher que sa version eclatante : prix douteux
  // valeur de garder l'eclatant de l'etape k (H) et decision : vendre ou tenter l'etape suivante
  for(let k=S.length-1;k>=0;k--){const s=S[k],nx=S[k+1];const sell=s.ecl.v==null?0:s.ecl.v;
   const cont=nx&&!nx.locked?nx.p*(1-c)*nx.plain.v+nx.p*c*nx.H-nx.cost:-Infinity;
   s.H=Math.max(sell,cont);s.go=cont>sell;s.cont=cont}
  const s0=S[0],ev=s0.locked?null:s0.p*(1-c)*s0.plain.v+s0.p*c*s0.H-s0.cost;
  let pj=1,cj=0;S.forEach(s=>{pj*=s.p*c;cj+=s.cost});const last=S[S.length-1],lockAt=S.find(s=>s.locked);
  const n0=Object.keys(s0.res).length?Math.min(...Object.entries(s0.res).map(([r,q])=>Math.floor((stock[r]||0)/q))):0;
  return{ch:ch,S:S,ev:ev,pj:pj,jack:(last.ecl.v||0)-cj,n0:n0,weird:weird,lockAt:lockAt}}).filter(Boolean);
 out.sort((a,b)=>(a.weird-b.weird)||((b.ev??-1e18)-(a.ev??-1e18)));
 const pct=x=>(x*100).toFixed(x<0.01?2:1).replace('.',',')+' %',sg=x=>(x>=0?'+':'')+kf(x);
 box.innerHTML=out.map(o=>{const s0=o.S[0];
  return `<details class="card" style="margin:0 0 10px"><summary style="cursor:pointer;display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap">`
   +`<b>${escH(o.ch.name)} <span class="sub">→ ${escH(o.S[o.S.length-1].ecl.n)}</span></b>`
   +`<span>${o.ev==null?'<span class="badge b-mut">🔒 '+PROF[s0.prof]+' '+lvTxt(s0.m)+'</span>':'Espérance par essai : <b class="'+(o.ev>0?'pos':'neg')+'">'+sg(o.ev)+'</b>'}`
   +` · ${o.lockAt?'jackpot 🔒 '+PROF[o.lockAt.prof]+' '+lvTxt(o.lockAt.m):'jackpot '+pct(o.pj)+' → <b>'+kf(o.jack)+'</b>'}${o.n0?' · ton stock : '+o.n0+' essai(s)':''}`
   +`${o.weird?' <span class="badge b-warn" title="Un objet normal est plus cher que sa version éclatante : prix habituel probablement faussé par une annonce aberrante">⚠ prix douteux</span>':''}</span></summary>`
   +'<div class="wrap" style="max-height:none;margin-top:8px"><table><thead><tr><th>Étape</th><th class="n">Réussite</th><th class="n">Coût de l’essai</th>'
   +'<th>Si échec</th><th>Si réussite sans combo</th><th>Si le combo procque</th><th>Conseil</th></tr></thead><tbody>'
   +o.S.map((s,k)=>{const prev=k?o.S[k-1]:null,lose=s.cost+(prev?(prev.ecl.v||0):0);
    return `<tr${s.locked?' class="locked"':''}><td><b>${k+1}.</b> ${PROF[s.prof]} ${lvTxt(s.m)}${s.inp?'<div class="sub">avec '+escH(s.inp)+'</div>':''}</td>`
     +`<td class="n">${s.locked?'🔒':pct(s.p)}${s.known?'':'<div class="sub">niveau non renseigné</div>'}</td>`
     +`<td class="n">${kf(s.cost)}<div class="sub">${escH((s.lines||[]).filter(l=>!l.includes('récolte')).slice(0,3).join(' · '))}</div></td>`
     +`<td><span class="neg">${pct(1-s.p)}</span> : tu perds ${kf(lose)}</td>`
     +`<td>${pct(s.p*(1-c))} : ${escH(s.plain.n)} <b>${kf(s.plain.v)}</b><div class="sub">${s.plain.ls!=null?NF.format(s.plain.ls)+' annonce(s) vendue(s)/j':'ventes non mesurées'}</div></td>`
     +`<td>${pct(s.p*c)} : ${escH(s.ecl.n)} <b class="pos">${s.ecl.v==null?'prix inconnu':kf(s.ecl.v)}</b><div class="sub">gain du proc : ${s.ecl.v==null?'?':sg(s.ecl.v-s.plain.v)}${s.ecl.ls!=null?' · '+NF.format(s.ecl.ls)+' ann. vendue(s)/j':' · ventes non mesurées'}</div></td>`
     +`<td>${k===o.S.length-1?'Vendre':(s.go?'<span class="badge b-ok">Tenter l’étape '+(k+2)+'</span><div class="sub">espérance '+sg(s.cont)+' contre vente '+kf(s.ecl.v)+'</div>':'<span class="badge b-warn">Vendre l’éclatant</span><div class="sub">tenter plus haut : '+(s.cont===-Infinity?'impossible (niveau)':sg(s.cont))+'</div>')}</td></tr>`}).join('')
   +'</tbody></table></div><p class="sub" style="margin-top:6px">Espérance = gain moyen par essai de l’étape 1 en suivant les conseils. Jackpot = chance de passer toutes les étapes avec combo, et gain si ça arrive (valeur finale − coûts de tous les essais).</p></details>'}).join('')
  ||'<p class="mut">Aucune chaîne avec des prix connus.</p>'}
function segShow(btn,id){const seg=btn.parentNode;seg.querySelectorAll('button').forEach(b=>b.classList.toggle('on',b===btn));
 const sec=seg.closest('section');sec.querySelectorAll('.segp').forEach(p=>p.style.display=p.id===id?'':'none')}
function resCrafts(name){const sec=document.getElementById('harvest');segShow(sec.querySelectorAll('.seg button')[1],'hcraft');
 const inp=document.querySelector('#hcraft input.search');inp.value=name;filt(inp,'th');inp.scrollIntoView({block:'center'})}
function clearStock(){document.querySelectorAll('#stock input[data-r]').forEach(i=>i.value='');calc()}
document.addEventListener('DOMContentLoaded',()=>{let t='home';try{t=localStorage.getItem('tab')||t;
 if(localStorage.getItem('detail')){document.body.classList.add('detail');document.querySelectorAll('input.dt').forEach(x=>x.checked=true)}}catch(e){}
 if(!document.getElementById(t))t='home';show(t);
 try{const s=JSON.parse(localStorage.getItem('stock')||'null');if(s)document.querySelectorAll('#stock input[data-r]').forEach(i=>i.value=s[i.dataset.r]||'')}catch(e){}
 importLevelsFromHash();applyLevels();rateCalc();planSafe();planGamble();document.querySelectorAll('th').forEach(th=>th.onclick=()=>sortT(th))});
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
        self.charted = set()       # items dont la courbe de prix est disponible (prices.js)
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

    def market_icons(self):
        """Icones locales des items vus en vente (nom de base, chemin) : reference pour lire une capture de ventes."""
        seen, out = set(), []
        for it in self.items.values():
            if it.get("on_market") and not it["bound"] and it.get("icon_file") and it["base_name"] not in seen \
                    and (DATA_DIR / it["icon_file"]).exists():
                seen.add(it["base_name"])
                out.append(dict(n=it["base_name"], s=f"../data/{it['icon_file']}"))
        return out

    def icon_src(self, name):
        """Image locale d'une ressource (meme origine que la page : necessaire pour lire ses pixels)."""
        it = self.by_base.get(name)
        if it and it.get("icon_file") and (DATA_DIR / it["icon_file"]).exists():
            return f"../data/{it['icon_file']}"
        return None

    def mapbtn(self, name):
        base = node_name(BOUND_RE.sub("", name or ""))
        if base in self.gather_names:
            return f'<button class="mapbtn" data-r="{esc(base)}" onclick="openMap(this.dataset.r)">MAP</button>'
        return ""

    def chartbtn(self, item_id, name):
        iid = item_id or (self.by_base.get(name) or {}).get("id")
        if iid not in self.charted:
            return ""
        return (f'<button class="mapbtn" title="Courbe de prix sur 7 jours" '
                f'onclick="openChart({iid},this.dataset.n)" data-n="{esc(name)}">📈</button>')

    def label(self, item_id=None, name=None, sub=None):
        nm = name or (self.items.get(item_id) or {}).get("name") or item_id
        s = f'<div class="sub">{esc(sub)}</div>' if sub else ""
        return (f'<span class="it">{self.icon(item_id, name)}<span><span class="nm" title="Cliquer pour copier">{esc(nm)}</span>'
                f'{self.chartbtn(item_id, nm)}{self.mapbtn(nm)}{s}</span></span>')


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


def niveau(m):
    """Niveau de metier tel qu'affiche en jeu : Debutant 1-50, puis Specialiste 1-50 (= 51-100)."""
    m = m or 0
    return f"Spécialiste {m - 50}" if m > 50 else f"Débutant {m}"


def craft_attrs(e):
    """Donnees pour recalculer la ligne dans le navigateur selon les niveaux de metier."""
    return (f'data-craft="{e["item_id"]}" data-sell="{e.get("vente_net_u", 0)}" data-cost="{e["achats_u"]}" '
            f'data-day="{e["ma_part_j"]}"')


def planning_tab(cfg, my):
    """Onglet Planning : plan « safe » (recolte -> crafts qui se vendent) et plan « gamble » (chaines d'amelioration
    avec combo). Calcul dans le navigateur : niveaux de metier, recolte par heure et stock du joueur."""
    targets = []
    for t in my["targets"]:
        uses = [dict(o=u["objet"], i=u["item_id"], n=u["net_par_ressource"], cap=u["ressources_j"], per=round(u["per_u"], 4),
                     v=1 if u.get("via") else 0,
                     lot=u.get("lot")) for u in t["usages"] if u["fiable"] and u["ressources_j"]]
        if uses:
            avg = sum(u["n"] * u["cap"] for u in uses) / sum(u["cap"] for u in uses)
            targets.append(dict(r=t["ressource"], u=uses, avg=round(avg)))
    hours = my.get("hours")
    best = f"{hours['best']}h – {(hours['best'] + 3) % 24}h" if hours else "21h – 0h"
    data = json.dumps(dict(targets=targets, chains=my.get("chains") or [], best=best), ensure_ascii=False,
                      separators=(",", ":"))
    return ("<h2>Planning de la journée</h2><p class='lead'>Deux façons de jouer ta récolte (jamais vendue brute). "
            "Les calculs utilisent tes niveaux de métier (🛠️ Mes métiers), ta récolte par heure (🌲 Récolte, "
            "100 par défaut) et ton stock (🧮 Mon stock).</p>"
            "<h3>🛡️ Planning safe : récolter ce qui rapporte et se vend</h3>"
            '<div class="toolbar"><label class="tg">Temps de jeu aujourd’hui : <input type="number" id="phours" min="0.5" '
            'step="0.5" value="3" style="width:70px;padding:5px 7px;border:1px solid var(--line);border-radius:7px;'
            'background:var(--bg2);color:var(--txt);font:inherit" oninput="planSafe(true)"> h</label></div>'
            '<div id="psafe"></div>'
            "<h3>🎲 Planning gamble : blanc → vert → bleu → unique</h3>"
            "<p class='lead'>À chaque craft d’une chaîne, si la fabrication réussit, le <b>combo</b> donne la version "
            "<b>éclatante</b> (grade supérieur), seule à pouvoir servir à l’étape suivante ; sinon tu obtiens l’objet normal. "
            "Un échec fait perdre les matières <b>et</b> l’objet éclatant mis dedans. À chaque palier, le calcul compare "
            "« vendre l’éclatant » et « le risquer plus haut ». Prix = prix habituel sur ton serveur, après la taxe de 10 %.</p>"
            '<div class="toolbar"><label class="tg">Chance de combo : <input type="number" id="pcombo" min="1" max="100" '
            'step="1" style="width:64px;padding:5px 7px;border:1px solid var(--line);border-radius:7px;background:var(--bg2);'
            'color:var(--txt);font:inherit" oninput="planGamble(true)"> %</label>'
            '<label class="tg"><input type="checkbox" id="popp" checked onchange="planGamble(true)"> Compter mes ressources à '
            'ce qu’elles rapportent en safe (coût d’opportunité)</label></div>'
            '<div id="pgamble"></div>'
            f"<script>window.PLANDATA={data};</script>")


def metiers_tab(con, my):
    """Onglet Mes metiers : niveaux enregistres dans le navigateur, + tables de reussite du jeu."""
    curves = {r["id"]: json.loads(r["rates"]) for r in con.execute("SELECT * FROM rate_curves")}
    items, good = {}, []
    for e in my["harvest"] + my["buy"] + (my.get("spikes") or []):
        items[e["item_id"]] = [list(a) for a in e.get("alts") or []]
        if is_good(e) and e["profit_j"] > 0:
            good.append(dict(o=e["objet"], a=items[e["item_id"]], j=e["profit_j"]))
    gaps = (0, 5, 10, 20, 30, 50)
    rows = []
    for k, c in sorted(curves.items(), key=lambda kv: kv[0]):
        # qui utilise cette courbe : metiers, niveaux requis, exemples (recettes visibles, objets echangeables)
        used = con.execute("SELECT DISTINCT r.profession, r.mastery, i.base_name FROM recipes r JOIN items i ON i.id = r.item_id "
                           "WHERE r.rate_curve = ? AND r.visible = 1 AND r.combo_result = 0 AND r.method = 'craft'", (k,)).fetchall()
        if not used:
            continue
        profs = ", ".join(METIERS.get(p, p) for p in sorted({u["profession"] for u in used}))
        levels = sorted({u["mastery"] or 0 for u in used})
        examples = ", ".join(list(dict.fromkeys(u["base_name"] for u in used))[:3])
        rows.append(f"<tr><td><b>{esc(examples)}</b>…<div class='sub'>{esc(profs)} · {niveau(levels[0])} à {niveau(levels[-1])}</div></td>"
                    + "".join(f"<td class='n'>{c[min(g, len(c) - 1)] / 1e6:.1f} %</td>".replace(".", ",") for g in gaps) + "</tr>")
    rows = "".join(rows)
    table = (f'<div class="wrap" style="max-height:none"><table><thead><tr>{_th("Recettes concernées (exemples)")}'
             + "".join(_th(f"Écart {g}" + ("+" if g == gaps[-1] else ""), None, True) for g in gaps)
             + f'</tr></thead><tbody>{rows}</tbody></table></div>') if curves else '<p class="mut">Tables pas encore chargées.</p>'
    data = json.dumps(dict(curves={str(k): v for k, v in curves.items()}, items=items, good=good), separators=(",", ":"))
    return ("<h2>Mes métiers</h2><p class='lead'>Renseigne le niveau de tes métiers : les crafts que tu ne peux pas faire "
            "sont grisés partout sur le site, et le profit tient compte de ta chance de réussite. Tes niveaux restent "
            "enregistrés dans ce navigateur ; clique sur <b>+1</b> quand tu montes.</p>"
            '<div class="cards" id="metiers"></div>'
            '<div class="toolbar" style="margin-top:12px"><label class="tg"><input type="checkbox" id="mlose" '
            'onchange="setOpt(\'lose\',this.checked)"> En cas d’échec, les ingrédients sont perdus</label>'
            '<label class="tg"><input type="checkbox" id="mhide" onchange="setOpt(\'hide\',this.checked)"> '
            'Masquer les crafts que je ne peux pas faire</label>'
            '<button class="mapbtn" onclick="shareLevels()">🔗 Copier le lien de mes niveaux (autre appareil)</button></div>'
            "<h3>Bientôt débloqué (10 prochains niveaux)</h3><div id='soon'></div>"
            "<h3>Chances de réussite du jeu selon l’écart de niveau</h3><p class='lead'>Écart = ton niveau − niveau requis "
            "par la recette. Valeurs du jeu (identiques à la fenêtre « Chances de fabrication »). Les recettes de niveau 0 "
            "sans table réussissent toujours. Niveaux : Débutant 1 à 50, puis Spécialiste 1 à 50.</p>" + table
            + f"<script>window.CRAFTDATA={data};</script>")


def cmp_class(compare, e):
    c = (compare or {}).get(e["item_id"])
    return "" if not c else ("better" if c[0] else "worse")


def cmp_badge(compare, e):
    c = (compare or {}).get(e["item_id"])
    if not c:
        return ""
    better, diff, other = c
    return (f'<span class="badge b-ok">✔ mieux que {esc(other)} (+{fmt(diff)}/u)</span>' if better
            else f'<span class="badge b-bad">✖ moins bien que {esc(other)} (−{fmt(diff)}/u)</span>')


def compare_ways(a, b, label_b):
    """Pour chaque craft present dans les deux listes : meilleur ou moins bien que l'autre facon (net par unite)."""
    other = {e["item_id"]: e for e in b}
    out = {}
    for e in a:
        o = other.get(e["item_id"])
        if o and o["net_u"] != e["net_u"]:
            out[e["item_id"]] = (e["net_u"] > o["net_u"], abs(e["net_u"] - o["net_u"]), label_b)
    return out


def table_crafts(ctx, rows, tid, harvest, compare=None):
    """compare : {item_id: (meilleur?, ecart net/u, nom de l'autre facon)} pour colorer vert/rouge face a l'autre categorie."""
    head = ("<tr>" + _th("#") + _th("Craft") +
            (_th("Ressources / unité") if harvest else _th("Ingrédients achetés")) +
            ("" if harvest else _th("Coût/u", "Coût des ingrédients au prix réaliste", True)) +
            _th("Réussite", "Chance de réussite selon tes niveaux (onglet Mes métiers) ; 🔒 = niveau insuffisant", True) +
            _th("Vendre à", "Prix de vente conseillé (réaliste)", True) +
            _th("Net/u", "Bénéfice par unité après la taxe de l’HDV (10 %) (et échecs, selon tes niveaux)", True) +
            (_th("Net/ressource", "Bénéfice par ressource récoltée utilisée", True) if harvest
             else _th("Marge", "Bénéfice / coût", True)) +
            _th("Ventes/j", "Ta part (20 %) des ventes mesurées sur ton serveur : annonces disparues sur 24 h × taille "
                "habituelle des annonces", True) +
            _th("Profit/j", "Ventes/j × Net/u", True) +
            _th("Volume serveur/j", "Unités vendues par jour sur ton serveur (mesurées)", True, True) +
            _th("Annonces vendues/j", "Annonces disparues sur 24 h sur ton serveur (achats ; une annonce retirée compte aussi)",
                True, True) +
            _th("Prix affiché", "Prix le plus bas actuellement en vente", True, True) +
            _th("Prix habituel", "Prix plancher médian sur ton serveur (3 j) ; à défaut, prix de vente moyen sur Kaisinel", True, True) +
            _th("Net pess./u", "Bénéfice si on vend au prix le plus bas", True, True) +
            _th("Profit pess./j", None, True, True) +
            ("" if harvest else _th("Capital/j", "Kinah à avancer par jour", True, True)) +
            _th("Statut") + "</tr>")
    good = [e for e in rows if is_good(e)]
    bad = [e for e in rows if not is_good(e)]
    ncol = 18 if not harvest else 16
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
            f"<tr class='{'' if is_good(e) else 'dim'} {cmp_class(compare, e)}' {craft_attrs(e)}><td class='n rank'>{i}</td>"
            f"<td>{ctx.label(e['item_id'], sub=f'{METIERS.get(e['metier'], e['metier'])} {niveau(e['maitrise'])} · lot ×{e['lot']:g}')}</td>"
            f"<td>{res}</td>"
            + ("" if harvest else _num_td(e["achats_u"], color=False))
            + '<td class="n csr">–</td>'
            + _num_td(e["prix_real"], color=False) + _num_td(e["net_u"], "cnet") + cols
            + _num_td(e["ma_part_j"], color=False)
            + _num_td(e["profit_j"], "big cprof", k=True)
            + _num_td(e["vol_serveur_j"], color=False, x=True) + _num_td(e.get("annonces_vendues_j"), color=False, x=True)
            + _num_td(e["prix_affiche"], color=False, x=True)
            + _num_td(e["prix_ref"], color=False, x=True) + _num_td(e["net_pess_u"], x=True)
            + _num_td(e["profit_pess_j"], k=True, x=True)
            + ("" if harvest else _num_td(e["capital_j"], color=False, k=True, x=True))
            + f"<td>{cmp_badge(compare, e)}{status(e)}{surete_html(e)}</td></tr>")
    return toolbar(tid) + f'<div class="wrap"><table id="{tid}"><thead>{head}</thead><tbody>{"".join(body)}</tbody></table></div>'


def table_targets(ctx, targets):
    body = []
    for t in targets:
        # gain moyen par ressource quand la recolte du jour est repartie sur les crafts fiables, selon ce que chacun absorbe
        ok = [u for u in t["usages"] if u["fiable"] and u["ressources_j"]]
        avg = round(sum(u["net_par_ressource"] * u["ressources_j"] for u in ok) / sum(u["ressources_j"] for u in ok)) if ok else 0
        uses = '<div class="uses">' + "".join(
            f"<div>{esc(u['objet'])} : <b class='{_cls(u['net_par_ressource'])}'>{fmt(u['net_par_ressource'])}</b> / ressource"
            + (f" <span class='mut'>· ~{fmt(u['ressources_j'])} ressources/j</span>" if u["fiable"] else "")
            + ("" if u["fiable"] else f" <span class='badge b-warn'>⚠ {esc('; '.join(u['flags']) or 'à perte')}</span>")
            + "</div>" for u in t["usages"]) + "</div>"
        body.append(f"<tr class='{'' if t['meilleur'] else 'dim'}' data-res=\"{esc(t['ressource'])}\" "
                    f"data-best='{avg}' data-abs='{t['absorbable_j'] or 0}'><td>{ctx.label(name=t['ressource'])}"
                    f"<button class='mapbtn' style='margin-top:4px' onclick=\"resCrafts(this.closest('tr').dataset.res)\">crafts</button></td>"
                    f"<td class='n'><input type='number' min='0' step='10' class='rate' placeholder='100' "
                    f"style='width:74px;padding:5px 7px;border:1px solid var(--line);border-radius:7px;background:var(--bg2);"
                    f"color:var(--txt);font:inherit;text-align:right' oninput='rateCalc(this)'></td>"
                    f"<td class='n big pos kh' data-v='0'>–</td><td class='n hj' data-v='0'>–</td>"
                    f"{_num_td(t['meilleur'], 'big')}<td>{uses}</td>{_num_td(t['absorbable_j'], color=False)}"
                    f"{_num_td(t['prix_brut'], color=False, x=True)}</tr>")
    head = ("<tr>" + _th("Ressource")
            + _th("Récolte / heure", "Ce que tu récoltes en une heure (100 par défaut) : modifiable, enregistré dans ce navigateur")
            + _th("Kinah / heure", "Récolte par heure × gain moyen par ressource, la récolte étant répartie sur les crafts "
                  "fiables selon ce que chacun absorbe (après frais)", True)
            + _th("Heures / jour", "Heures de récolte avant de saturer ce que le marché absorbe par jour", True)
            + _th("Meilleur net / ressource", "Ce que te rapporte chaque ressource récoltée dans son meilleur craft fiable", True)
            + _th("Que fabriquer avec") + _th("Utilisable/j", "Ressources que le marché absorbe par jour via les crafts fiables", True)
            + _th("Prix brut HDV", "Prix du brut en vente (non vendable pour toi : toujours transformer)", True, True)
            + "</tr>")
    return (toolbar("targets") + f'<div class="wrap"><table id="targets"><thead>{head}</thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


def lots_txt(e):
    """« 4 annonces de 100 » : comment decouper ce qu'on met en vente dans la journee."""
    n, lot = e.get("nb_lots_j"), e.get("lot_vente")
    if not n:
        return "–"
    return f"{n} annonce{'s' if n > 1 else ''} de {fmt(lot)}"


def todo_html(con, my):
    """« A faire maintenant » : les actions du jour, par ordre d'importance. Plan de recolte et mise en vente sont
    completes dans le navigateur (Planning safe : temps de jeu, recolte/heure, niveaux)."""
    items = []
    for l in my.get("listings") or []:                       # 1. mes annonces
        if not l["item_id"] or l["plancher"] is None:
            continue
        if l.get("chute"):
            items.append(("bad", f"📉 <b>{esc(l['nom'])}</b> : le prix chute ({fmt(l['plancher'])}). Si tu veux vendre, c’est maintenant."))
        if l.get("sous_seuil"):
            items.append(("bad", f"⛔ <b>{esc(l['nom'])}</b> : le plus bas ({fmt(l['plancher'])}) est sous ton seuil "
                                 f"({fmt(l['seuil'])}). Ne baisse pas ; garde ou coupe la perte."))
        elif l.get("conseil"):
            items.append(("warn", f"⚔️ <b>{esc(l['nom'])}</b> : tu es battu. Repasse devant à <b>{fmt(l['conseil'])}</b>."))
        if (l.get("ecoulement_h") or 0) > 24:
            items.append(("warn", f"🐢 <b>{esc(l['nom'])}</b> : ~{l['ecoulement_h']:.0f} h pour écouler ton stock : "
                                  "mets moins d’annonces à la fois."))
    seen = set()                                              # 2. achats surs (vert)
    for e in (my.get("buy_trans") or []) + (my.get("buy_direct") or []):
        s_ = e.get("surete") or {}
        if s_.get("feu") == "vert" and e["net_u"] > 0 and not e["flags"] and e["item_id"] not in seen:
            seen.add(e["item_id"])
            how = "via Od transmuté" if any("transmuté" in x for x in e["ingredients"]) else "à l’HDV"
            items.append(("ok", f"🟢 Achat → craft <b>{esc(e['objet'])}</b> ({how}) : +{fmt(e['net_u'])}/u, "
                                f"max ~{fmt(s_['qte_max'])} u, ne vends pas sous {fmt(s_['prix_plancher'])}."))
        if len(seen) >= 2:
            break
    since = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()[:19]
    for n in con.execute("SELECT * FROM news WHERE key LIKE 'update%' AND posted >= ? ORDER BY posted DESC LIMIT 2", (since,)):
        items.append(("mut", f"🛠️ Nouvelle note de version : <a href=\"{esc(n['url'])}\" target=\"_blank\" rel=\"noopener\" "
                             f"style=\"color:var(--acc)\">{esc(n['title'])}</a>"))
    order = {"bad": 0, "warn": 1, "ok": 2, "mut": 3}
    rows = "".join(f'<li class="td-{k}">{t}</li>' for k, t in sorted(items, key=lambda x: order[x[0]]))
    return ('<div class="card todo"><b>✅ À faire maintenant</b><ol id="todo">' + rows
            + '<li id="todo-plan" class="td-plan">Plan du jour : calcul en cours…</li></ol></div>')


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


def stock_calc(ctx, cfg, harvest, names, transmute=None):
    """Je saisis mes ressources, la page calcule quoi fabriquer et combien ca rapporte (calcul dans le navigateur).
    Les crafts fiables passent d'abord ; les douteux (drapeaux) seulement si on coche l'option."""
    crafts = [e for e in harvest if e["net_u"] > 0 and e["ressources_u"]]
    crafts.sort(key=lambda e: (bool(e["flags"]), -(e["net_u"] / e["ressources_u"])))
    data = [dict(o=e["objet"], i=e["item_id"], s=e.get("vente_net_u"), a=e["achats_u"],
                 n=e["net_u"], p=e["prix_real"], c=e["ma_part_j"], l=e.get("lot_vente"),
                 f="; ".join(e["flags"]), r={k: round(v, 4) for k, v in e["ressources"].items()}) for e in crafts]
    names = sorted(set(names) | {k for e in crafts for k in e["ressources"]})
    preset = cfg.get("harvest_per_day") or {}
    inputs = "".join(f'<label class="sk">{ctx.icon(name=n)}<span>{esc(n)}</span><input type="number" min="0" step="1" '
                     f'inputmode="numeric" data-r="{esc(n)}" value="{esc(preset.get(n, ""))}" oninput="calc()"></label>'
                     for n in names)
    head = (f'<tr>{_th("Craft")}{_th("Quantité", None, True)}{_th("Vendre à", None, True)}{_th("Net/u", None, True)}'
            f'{_th("Kinah", None, True)}{_th("Mettre en vente", "Taille habituelle des lots vendus sur le marché")}'
            f'{_th("Ressources utilisées")}</tr>')
    return ('<p class="lead">Entre les ressources que tu possèdes : la page choisit les crafts qui rapportent le plus '
            'par ressource et calcule le gain. Tes quantités restent enregistrées dans ce navigateur.</p>'
            '<div class="toolbar"><label class="tg"><input type="checkbox" id="cap" checked onchange="calc()"> '
            'Ne pas dépasser ce que le marché absorbe en un jour</label>'
            '<label class="tg"><input type="checkbox" id="risky" onchange="calc()"> '
            'Inclure les crafts douteux (volume inconnu, prix suspect)</label>'
            '<button class="mapbtn" onclick="clearStock()">Tout effacer</button></div>'
            '<div class="card" id="sdrop" style="margin:0 0 12px" ondragover="event.preventDefault()" '
            'ondrop="event.preventDefault();scanFile(event.dataTransfer.files[0])"><b>📷 Lire une capture de ta réserve</b>'
            '<span class="mut">Fais une capture de ta réserve (Win + Maj + S), recadrée au plus près de la grille, puis colle-la '
            'ici avec <b>Ctrl + V</b>, glisse le fichier sur ce cadre, ou <label style="color:var(--acc);cursor:pointer;'
            'text-decoration:underline">choisis un fichier<input type="file" accept="image/*" hidden '
            'onchange="scanFile(this.files[0])"></label>. La capture reste dans ton navigateur.</span>'
            '<span id="smsg" class="mut"></span><div class="chips" id="sthumbs"></div></div>'
            f'<script>window.GATHER={json.dumps([dict(n=n, s=ctx.icon_src(n)) for n in names if ctx.icon_src(n)], ensure_ascii=False)};</script>'
            '<details class="card" id="pdet" style="margin:0 0 12px"><summary style="cursor:pointer"><b>📋 Coller une liste</b> '
            '<span class="mut">— une ligne par ressource : « Bois d\'Asvata 300 » ou « Saphir brut : 96 ». '
            'Rempli automatiquement par la lecture de capture ci-dessus, modifiable avant de cliquer sur Remplir.</span></summary>'
            '<textarea id="paste" placeholder="Bois d\'Asvata 300&#10;Saphir brut : 96&#10;Rubis brut d\'une grande pureté x169"></textarea>'
            '<div class="toolbar" style="margin:0"><select id="pmode" class="search" style="width:auto">'
            '<option value="replace">Remplacer tout le stock</option><option value="add">Ajouter au stock</option></select>'
            '<button class="mapbtn" onclick="importStock()">Remplir</button><span class="mut" id="pmsg"></span></div></details>'
            f'<div class="stock" id="stock">{inputs}</div>'
            '<div class="kpis"><div class="kpi"><div class="l">Total estimé</div><div class="v pos" id="stot">–</div>'
            '<div class="s">kinah une fois tout vendu</div></div></div>'
            f'<div class="wrap"><table id="splan"><thead>{head}</thead><tbody></tbody></table></div>'
            '<p class="mut" id="sleft"></p>'
            f'<script>window.CRAFTS={json.dumps(data, ensure_ascii=False).replace("</", "<\\/")};'
            f'window.TRANSMUTE={json.dumps(transmute, ensure_ascii=False)};</script>')


def surete_html(e, details=True):
    """Badge de l'indice de surete (raisons au survol) + garde-fous (quantite max, prix plancher)."""
    s = e.get("surete")
    if not s:
        return ""
    cls, dot = {"vert": ("b-ok", "🟢"), "orange": ("b-warn", "🟠"), "rouge": ("b-bad", "🔴")}[s["feu"]]
    tip = " · ".join(s["raisons"]) or "marché fluide"
    out = f'<span class="badge {cls}" title="{esc(tip)}">{dot} Sûreté {s["score"]}</span>'
    if details:
        guard = f"max ~{fmt(s['qte_max'])} u"
        if s.get("prix_plancher"):
            guard += f" · ne vends pas sous {fmt(s['prix_plancher'])}"
        out += f'<div class="sub">{guard}</div>'
    return out


def position_advice(l):
    """Conseil pour une de mes annonces."""
    if not l["item_id"] or l["plancher"] is None:
        return ""
    tips = []
    if l["conseil"]:
        tips.append(f"Repasse devant à {fmt(l['conseil'])}")
    elif l["battu"] and l.get("seuil"):
        tips.append("Ne baisse pas : le plus bas est sous ton seuil")
    if l.get("chute"):
        tips.append("le prix chute : vends maintenant ou garde")
    if l.get("ecoulement_h"):
        tips.append(f"écoulement ~{l['ecoulement_h']:.0f} h")
    return esc(" · ".join(tips))


def table_spikes(ctx, spikes):
    """Pics de prix : rentable au prix affiche seulement."""
    if not spikes:
        return ""
    rows = "".join(
        f"<tr {craft_attrs(e)}><td>{ctx.label(e['item_id'])}</td>{_num_td(e['prix_affiche'], 'big', color=False)}"
        f"{_num_td(e['prix_ref'], color=False)}<td class='n' data-v='{e['ratio']}'><span class='badge b-warn'>×{e['ratio']}</span></td>"
        f"<td class='sub'>{esc(paris(e['depuis'], '%d/%m %H:%M') if e['depuis'] else '–')}</td>"
        f"{_num_td(e['achats_u'], color=False)}{_num_td(e['net_affiche_u'])}{_num_td(e['net_habituel_u'])}"
        f"{_num_td(e['annonces'], 'mut', color=False)}<td data-v='{(e.get('surete') or {}).get('score', 0)}'>{surete_html(e)}</td>"
        f"<td class='ing'>{'<br>'.join(esc(x) for x in e['ingredients'])}</td></tr>"
        for e in spikes)
    head = ("<tr>" + _th("Craft") + _th("Prix affiché", None, True) + _th("Prix habituel", "Médiane 3 j sur ton serveur", True)
            + _th("Pic", None, True) + _th("Depuis") + _th("Coût/u", None, True)
            + _th("Net/u si vendu au prix affiché", None, True) + _th("Net/u si le prix redescend", None, True)
            + _th("Annonces", None, True)
            + _th("Sûreté", "Peut-on revendre ? Pression de l'offre, temps d'écoulement, perte si le prix redescend (détail au survol)")
            + _th("Acheter") + "</tr>")
    return ("<h3>⚡ Pics de prix : rentable seulement tant que le prix reste haut</h3>"
            "<p class='lead'>Le prix affiché est bien au-dessus du prix habituel depuis peu. Fabriquer et vendre maintenant "
            "rapporte, mais si le prix redescend avant la vente, c’est à perte. Petite quantité, à vendre vite, et "
            "regarde la courbe 📈 avant de te lancer. 🔴 = d’autres vendeurs arrivent déjà : à éviter.</p>"
            f'<div class="wrap"><table><thead>{head}</thead><tbody>{rows}</tbody></table></div><h3>Toujours rentables</h3>')


def table_flips(ctx, flips, cfg):
    a = cfg["alerts"]
    body = []
    for f in flips:
        st = ('<span class="badge b-ok">Acheter maintenant</span>' if f["acheter"]
              else '<span class="badge b-mut">Attendre</span>') + surete_html(f)
        body.append(f"<tr><td>{ctx.label(f['item_id'])}</td><td data-v='{0 if f['acheter'] else 1}'>{st}</td>"
                    f"{_num_td(f['prix'], color=False)}{_num_td(f['achat_cible'], 'big', color=False)}"
                    f"{_num_td(f['revente_cible'], color=False)}{_num_td(f['net_u'])}"
                    f"<td class='n' data-v='{f['marge']}'>{f['marge']:.0%}</td>{_num_td(f['ma_part_j'], color=False)}"
                    f"{_num_td(f['profit_j'], 'big', k=True)}<td>{lots_txt(f)}</td>"
                    f"{_num_td(f['capital_j'], 'x', color=False, k=True)}{_num_td(f['annonces'], 'mut x', color=False)}"
                    f"{_num_td(f['releves'], 'mut x', color=False)}</tr>")
        if f["releves"] < 48:
            body[-1] = body[-1].replace("</td><td data-v=", "<div><span class='badge b-mut' title='Moins de 48 prix relevés : "
                                        "fourchette encore peu fiable'>historique court</span></div></td><td data-v=", 1)
    head = ("<tr>" + _th("Item") + _th("Statut") + _th("Prix actuel", "Prix le plus bas en vente", True)
            + _th("Acheter à ≤", "Prix d'achat cible : bas de la fourchette habituelle (1er quartile sur 3 j)", True)
            + _th("Revendre à", "Prix plancher médian des 3 derniers jours", True)
            + _th("Net/u", "Après la taxe de l’HDV (10 %)", True) + _th("Marge", None, True)
            + _th("Ventes/j", "Ta part du marché (20 %)", True) + _th("Profit/j", None, True)
            + _th("Mettre en vente", "Taille habituelle des lots vendus")
            + _th("Capital/j", "Kinah à immobiliser par jour", True, True) + _th("Annonces", None, True, True)
            + _th("Relevés", "Prix relevés sur 3 j", True, True) + "</tr>")
    lead = ("<p class='lead'>Acheter un item quand il passe en bas de sa fourchette de prix habituelle, le revendre "
            "au prix médian, sans rien fabriquer. Calcul sur les 3 derniers jours ; les items dont le prix monte ou "
            "baisse durablement, le brut (invendable) et les items sans volume de vente connu sont écartés. "
            "🛡️ Sûreté : 🟢 marché fluide, 🟠 prudence, 🔴 stock qui s’accumule (détail au survol). "
            f"Alerte Discord quand un item passe sous son prix d’achat cible (marge ≥ {a['flip_min_margin']:.0%}, "
            f"profit ≥ {fmt(a['flip_min_profit_day'])}/j).</p>")
    if not flips:
        return lead + ('<div class="card"><span class="mut">Rien pour l’instant : il faut au moins '
                       f'{a["flip_min_samples"]} prix relevés par item, l’historique se remplit à chaque passage.</span></div>')
    return lead + toolbar("flips") + (f'<div class="wrap"><table id="flips"><thead>{head}</thead>'
                                      f'<tbody>{"".join(body)}</tbody></table></div>')


def table_uniques(ctx, uniques, cfg):
    a = cfg["alerts"]
    body = []
    for u in uniques:
        deal = u["ratio"] <= a["unique_ratio"] and u["releves"] >= a["unique_min_samples"]
        badge = (f'<span class="badge {"b-ok" if deal else "b-mut"}">{u["ratio"]:.0%}</span>')
        body.append(f"<tr><td>{ctx.label(u['item_id'])}</td><td class='sub'>{esc(u['categorie'])}</td>"
                    f"{_num_td(u['prix'], 'big', color=False)}{_num_td(u['mediane'], color=False)}"
                    f"<td class='n' data-v='{u['ratio']}'>{badge}</td>{_num_td(u['plus_bas'], color=False)}"
                    f"{_num_td(u['annonces'], 'mut', color=False)}{_num_td(u['releves'], 'mut', color=False)}</tr>")
    head = ("<tr>" + _th("Équipement Unique") + _th("Type", "L'harmonisation consomme une pièce de même rang et de même type") + _th("Prix actuel", None, True)
            + _th("Médiane 7 j", "Prix plancher médian des 7 derniers jours", True)
            + _th("Prix / médiane", "Plus c'est bas, plus c'est une affaire", True)
            + _th("Plus bas vu", "Prix plancher le plus bas des 7 derniers jours", True)
            + _th("Annonces", None, True) + _th("Relevés", "Nombre de prix relevés sur 7 j (fiabilité de la médiane)", True)
            + "</tr>")
    lead = (f"<p class='lead'>Équipements Unique en vente (armes, armures, accessoires), utilisables pour l’harmonisation "
            f"(une pièce de même rang et de même type). Les moins chers par rapport à leur prix habituel d’abord ; "
            f"tape un type (ex. « Épée ») dans la recherche pour ne voir que celui-là. "
            f"Alerte Discord quand un Unique passe sous <b>{a['unique_ratio']:.0%}</b> de sa médiane 7 j "
            f"(médiane d’au moins {fmt(a['unique_min_median'])} kinah, au moins {a['unique_min_samples']} relevés).</p>")
    return (lead + toolbar("uniques", f'<span class="mut">{len(uniques)} équipements Unique en vente</span>')
            + f'<div class="wrap"><table id="uniques"><thead>{head}</thead><tbody>{"".join(body)}</tbody></table></div>')


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


def _md(s):
    """Mise en forme minimale des messages d'alerte (**gras**)."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(s))


def home(con, cfg, ctx, my, sname):
    """Page d'accueil : uniquement ce qui sert a faire du profit aujourd'hui."""
    m = my["market"]
    good = [e for e in my["harvest"] if is_good(e)]
    top = good[:12]
    buys = [e for e in my["buy"] if is_good(e) and e["net_pess_u"] > 0]
    targets = [t for t in my["targets"] if t["meilleur"]][:6]

    kpis = (f'<div class="kpis">'
            '<div class="kpi"><div class="l">Potentiel du jour</div><div class="v pos" id="kpot">–</div>'
            '<div class="s" id="kpots">selon le Planning safe</div></div>'
            f'<div class="kpi"><div class="l">Meilleur craft</div><div class="v" style="font-size:19px">'
            f'{esc(top[0]["objet"]) if top else "–"}</div><div class="s">{kfmt(top[0]["profit_j"]) + " /j" if top else ""}</div></div>'
            f'<div class="kpi"><div class="l">Achat → craft</div><div class="v {"pos" if buys else "mut"}">{len(buys)}</div>'
            f'<div class="s">{"opportunité(s) sûre(s)" if buys else "rien de sûr aujourd’hui"}</div></div>'
            f'<div class="kpi"><div class="l">Ventes mesurées sur {esc(sname)}</div>'
            f'<div class="v">{sum(1 for e in my["harvest"] if e.get("vol_source") == "serveur")} / {len(my["harvest"])}</div>'
            f'<div class="s">crafts comparés (annonces disparues sur 24 h)</div></div></div>')

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
        res = "".join(f'<span class="chip">{ctx.icon(name=k)}<span class="nm" title="Cliquer pour copier">{esc(k)}</span> ×{v:g}{ctx.mapbtn(k)}</span>'
                      for k, v in e["ressources"].items())
        cards.append(
            f'<div class="card" {craft_attrs(e)}>{ctx.label(e["item_id"], sub=f"{METIERS.get(e["metier"], e["metier"])} {niveau(e["maitrise"])} · lot ×{e["lot"]:g}")}'
            f'<div class="chips">{res}</div>'
            f'<div class="row"><span>Vendre à</span><b>{fmt(e["prix_real"])}</b></div>'
            f'<div class="row"><span>Réussite</span><b class="csr">–</b></div>'
            f'<div class="row"><span>Net par unité</span><b class="pos cnet">{fmt(e["net_u"])}</b></div>'
            f'<div class="row"><span>À vendre par jour</span><b>~{fmt(e["ma_part_j"])}</b></div>'
            f'<div class="row"><span>Mettre en vente</span><b>{lots_txt(e)}</b></div>'
            f'<div class="row"><span>Profit/j</span><span class="big cprof">{kfmt(e["profit_j"])}</span></div>{tip}</div>')
    craft_html = (f'<div class="cards">{"".join(cards)}</div>' if cards else '<p class="mut">Aucun craft rentable.</p>')
    craft_html += (f'<p class="mut" style="margin-top:8px">{len(good)} crafts rentables au total, {len(my["harvest"])} comparés : '
                   '<a href="#" onclick="show(\'harvest\');return false" style="color:var(--acc)">voir la liste complète</a>.</p>')

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
                       f"{_num_td(e['profit_j'], 'big', k=True)}<td>{surete_html(e)}</td></tr>" for e in buys[:5])
        buy_html = (f'<div class="wrap"><table><thead><tr>{_th("Craft")}{_th("Acheter")}{_th("Coût/u", None, True)}'
                    f'{_th("Vendre à", None, True)}{_th("Net/u", None, True)}{_th("Profit/j", None, True)}{_th("Sûreté")}</tr></thead>'
                    f'<tbody>{brow}</tbody></table></div>')
    else:
        buy_html = ('<div class="card"><span class="mut">Aucun achat → craft → revente n’est sûr aux prix actuels '
                    '(les prix de la restriction anti-bot rendent les ingrédients trop chers). Tu seras alerté sur Discord '
                    'dès qu’une opportunité apparaît.</span></div>')

    spikes = my.get("spikes") or []
    if spikes:
        buy_html += (f'<div class="card" style="margin-top:10px;border-color:var(--warn)"><span>⚡ <b>{len(spikes)} pic(s) de prix</b> '
                     f'en cours ({esc(", ".join(e["objet"] for e in spikes[:3]))}) : rentable seulement en vendant vite. '
                     f'<a href="#" onclick="show(\'buy\');return false" style="color:var(--acc)">Voir l’onglet Achat → craft</a></span></div>')

    # 4. alertes du jour
    since = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0).isoformat(timespec="seconds")
    al = con.execute("SELECT ts, message FROM alerts_sent WHERE ts >= ? ORDER BY ts DESC LIMIT 12", (since,)).fetchall()
    alert_html = ('<div class="uses">' + "".join(
        f'<div class="card" style="padding:10px 14px"><span><span class="mut">{esc(paris(a["ts"], "%H:%M"))}</span> · {_md(a["message"])}</span></div>'
        for a in al) + "</div>") if al else '<p class="mut">Aucune alerte aujourd’hui.</p>'

    # 5. mes annonces
    costs = {e["objet"]: e["achats_u"] for e in my["buy"] if e.get("achats_u")}   # cout estime : achat des ingredients
    mine = my.get("listings") or []
    if mine:
        rows = "".join(
            f"<tr><td>{ctx.label(l['item_id']) if l['item_id'] else esc(l['nom']) + ' <span class=\"badge b-warn\">nom introuvable</span>'}</td>"
            f"{_num_td(l['mon_prix'], color=False)}{_num_td(l['plancher'], color=False)}"
            f"<td>{'<span class=\"badge b-bad\">Battu de ' + fmt(l['ecart']) + '</span>' if l['battu'] else ('<span class=\"badge b-ok\">Le moins cher</span>' if l['plancher'] is not None else '<span class=\"badge b-mut\">Pas en vente</span>')}"
            f"{'<span class=\"badge b-bad\">⛔ sous ton seuil</span>' if l.get('sous_seuil') else ''}"
            f"{'<span class=\"badge b-bad\">📉 chute</span>' if l.get('chute') else ''}</td>"
            f"{_num_td(l.get('seuil'), color=False)}{_num_td(l.get('marge_u'))}"
            f"<td class='sub'>{position_advice(l)}</td></tr>"
            for l in mine)
        mine_html = (f'<div class="wrap"><table><thead><tr>{_th("Mon annonce")}{_th("Mon prix", None, True)}'
                     f'{_th("Prix le plus bas", None, True)}{_th("Statut")}'
                     f'{_th("Seuil de rentabilité", "Coût de revient + taxe de 10 % : ne vends pas en dessous", True)}'
                     f'{_th("Gain/u au plus bas", None, True)}{_th("Conseil")}</tr></thead><tbody>{rows}</tbody></table></div>')
    else:
        mine_html = ('<p class="mut">Liste tes annonces dans <code>mes_annonces.json</code> (nom exact : prix, ou prix + coût '
                     'de revient + quantité) pour être alerté quand quelqu’un vend moins cher que toi ou sous ton seuil.</p>')

    edit = cfg.get("_github_edit_url")
    mine_html += ('<div class="card" id="vdrop" style="margin-top:10px" ondragover="event.preventDefault()" '
                  'ondrop="event.preventDefault();scanSales(event.dataTransfer.files[0])"><b>📷 Remplir depuis une capture de mes ventes</b>'
                  '<span class="mut">En jeu, fais une capture de ta fenêtre des ventes (Win + Maj + S), puis colle-la ici avec '
                  '<b>Ctrl + V</b> (sur cet onglet), glisse le fichier, ou <label style="color:var(--acc);cursor:pointer;'
                  'text-decoration:underline">choisis un fichier<input type="file" accept="image/*" hidden '
                  'onchange="scanSales(this.files[0])"></label>. Plusieurs captures s’ajoutent. Le coût de revient est '
                  'prérempli avec l’estimation du site (achat des ingrédients) : corrige-le si tu as récolté.</span>'
                  '<span id="vmsg" class="mut"></span><div class="chips" id="vrows"></div>'
                  '<div class="toolbar" style="margin:0"><select id="vmode" class="search" style="width:auto" onchange="renderSales()">'
                  '<option value="replace">Remplacer mes annonces</option><option value="add">Ajouter à mes annonces actuelles</option></select>'
                  '<button class="mapbtn" onclick="copySales()">📋 Copier le fichier</button>'
                  + (f'<a class="mapbtn" style="text-decoration:none" href="{esc(edit)}" target="_blank" rel="noopener">'
                     '✏️ Ouvrir mes_annonces.json sur GitHub</a>' if edit else '')
                  + '<button class="mapbtn" onclick="SALES=[];renderSales();document.getElementById(\'vmsg\').textContent=\'\'">Effacer</button></div>'
                  '<textarea id="vjson" spellcheck="false" style="width:100%;min-height:120px;padding:8px 10px;border:1px solid var(--line);'
                  'border-radius:8px;background:var(--bg2);color:var(--txt);font:12.5px/1.5 ui-monospace,Consolas,monospace"></textarea>'
                  '<span class="sub">Colle ce contenu à la place de celui du fichier sur GitHub, puis « Commit changes » : '
                  'le prochain passage horaire suivra tes annonces.</span></div>'
                  f'<script>window.MY_LISTINGS={json.dumps(cfg.get("my_listings") or {}, ensure_ascii=False)};'
                  f'window.MY_LISTINGS_HELP={json.dumps(cfg.get("_my_listings_help") or "", ensure_ascii=False)};'
                  f'window.COSTS={json.dumps(costs, ensure_ascii=False)};'
                  f'window.MARKET_ICONS={json.dumps(ctx.market_icons(), ensure_ascii=False)};</script>')

    # 6. annonces officielles
    news = con.execute("SELECT * FROM news WHERE key NOT LIKE 'reddit|%' ORDER BY posted DESC LIMIT 6").fetchall()
    news_html = ('<div class="uses">' + "".join(
        f'<div class="card" style="padding:10px 14px"><span><span class="mut">{esc(paris(n["posted"], "%d/%m %H:%M"))}</span> · '
        f'{_md(n["label"])} : <a href="{esc(n["url"])}" target="_blank" rel="noopener" style="color:var(--acc)">'
        f'{esc(n["title"])}</a></span></div>' for n in news) + "</div>") if news else \
        '<p class="mut">Les annonces officielles apparaîtront ici après le prochain passage.</p>'

    return (f"<h2>Aujourd’hui sur {esc(sname)}</h2><p class='lead'>Ce qu’il faut faire aujourd’hui pour gagner un maximum de kinah. "
            "Les tableaux complets sont dans les autres onglets.</p>" + kpis + todo_html(con, my)
            + "<h3>① Fabriquer et vendre</h3>" + hours_html(my.get("hours")) + "<br>" + craft_html
            + "<h3>② Quoi récolter</h3>" + gather_html
            + "<h3>③ Acheter → fabriquer → revendre</h3>" + buy_html
            + "<h3>④ Mes annonces</h3>" + mine_html
            + "<h3>⑤ Alertes du jour</h3>" + alert_html
            + "<h3>⑥ Annonces officielles</h3>" + news_html)


def gains_tab(ctx, cfg, my):
    """💰 Mes gains : mes vraies ventes (mes_ventes.json) face aux estimations de l'outil, et remplissage depuis une
    capture de l'historique des ventes en jeu."""
    g = my.get("gains")
    head = ("<h2>Mes gains réels</h2><p class='lead'>Tes ventes réelles (historique des ventes en jeu) comparées à ce que "
            "l’outil prévoit, pour vérifier ses estimations : combien tu vends par jour, à quel prix, et ta vraie part du "
            "marché. Une ligne de l’historique = un achat (un acheteur peut ne prendre qu’une partie d’une annonce).</p>")
    if g:
        pct = lambda v: f"{v:.0%}" if v is not None else "–"
        kpis = (f'<div class="kpis">'
                f'<div class="kpi"><div class="l">Kinah reçus</div><div class="v pos">{kfmt(g["recu"])}</div>'
                f'<div class="s">{g["ventes"]} ventes du {esc(paris(g["debut"].isoformat(), "%d/%m %H:%M"))} au '
                f'{esc(paris(g["fin"].isoformat(), "%d/%m %H:%M"))}</div></div>'
                f'<div class="kpi"><div class="l">Par jour</div><div class="v pos">{kfmt(g["recu_j"])}</div>'
                f'<div class="s">après la taxe de 10 %, sur {g["jours"]:.1f} j</div></div>'
                f'<div class="kpi"><div class="l">Ma part réelle du marché</div><div class="v">{pct(g["part"])}</div>'
                f'<div class="s">l’outil suppose {pct(g["part_supposee"])}</div></div>'
                f'<div class="kpi"><div class="l">Ventes réelles / prévues</div>'
                f'<div class="v">{"×" + format(g["ratio"], ".2f").replace(".", ",") if g["ratio"] else "–"}</div>'
                f'<div class="s">unités par jour, objets vendus 3 fois ou plus</div></div></div>')
        notes = []
        if g["n_cal"]:
            n = g["n_cal"]
            if g["ratio"]:
                notes.append(f"Tu vends <b>{g['ratio']:.2f}".replace(".", ",") + "×</b> ce que l’outil prévoit (ta part de "
                             f"{pct(g['part_supposee'])} des ventes mesurées), ce qui fait une part réelle de <b>{pct(g['part'])}</b>.")
            if g["prix_ratio"]:
                notes.append(f"Prix obtenu = <b>{g['prix_ratio']:.2f}".replace(".", ",") + "×</b> le prix des ventes "
                             "observées sur le marché pendant la même période.")
            if g["achat"]:
                notes.append(f"Tes acheteurs prennent en moyenne <b>{g['achat']:.1f}".replace(".", ",") + "×</b> la taille "
                             "d’annonce que l’outil utilise (mesurée sur Kaisinel).")
            notes.append(f"Calcul sur {n} objet{'s' if n > 1 else ''} vendu{'s' if n > 1 else ''} au moins 3 fois : "
                         + ("attends d’en avoir au moins 3 avant de changer les hypothèses de l’outil." if n < 3 else
                            "assez pour ajuster les hypothèses (part de marché dans config.json)."))
        else:
            notes.append("Pas encore d’objet vendu au moins 3 fois : ajoute des captures pour comparer aux estimations.")
        loss = [x for x in g["items"] if x["marge_u"] is not None and x["marge_u"] < 0]
        for x in loss:
            notes.append(f"<b class='neg'>⚠ {esc(x['objet'])} : vendu à perte</b> (reçu {fmt(round(x['recu_u']))} /u après "
                         f"taxe, coût {fmt(x['cout'])} /u dans mes_annonces.json, soit {fmt(round(x['marge_u']))} /u).")
        rows = "".join(
            f"<tr><td>{ctx.label(x['item_id'], x['objet'])}</td>"
            f"{_num_td(x['lots'], color=False)}{_num_td(x['unites'], color=False)}{_num_td(x['recu'], color=False, k=True)}"
            f"{_num_td(round(x['prix_u']), color=False)}{_num_td(round(x['prix_marche']) if x['prix_marche'] else None, color=False)}"
            f"{_num_td(round(x['marge_u']) if x['marge_u'] is not None else None)}"
            f"{_num_td(round(x['unites_j'], 1) if x['unites_j'] else None, color=False)}"
            f"{_num_td(round(x['estime_unites_j'], 1) if x['estime_unites_j'] else None, color=False)}"
            f"<td class='n'>{pct(x['part']) if x['part'] else '–'}</td>"
            f"{_num_td(round(x['achat_moyen'], 1), color=False)}{_num_td(x['lot_outil'], color=False)}</tr>"
            for x in g["items"])
        table = (f'<div class="wrap"><table><thead><tr>{_th("Objet")}{_th("Ventes", "Achats (lignes de l’historique)", True)}'
                 f'{_th("Unités", None, True)}{_th("Reçu", "Après la taxe de 10 %", True)}'
                 f'{_th("Prix obtenu /u", "Prix de vente moyen par unité", True)}'
                 f'{_th("Prix du marché /u", "Médiane des ventes observées sur le marché pendant la même période", True)}'
                 f'{_th("Marge /u", "Reçu par unité − coût de revient (mes_annonces.json)", True)}'
                 f'{_th("Unités /j réel", "À partir de 3 ventes : (n − 1) achats entre le premier et le dernier", True)}'
                 f'{_th("Unités /j prévu", "Ventes mesurées sur le serveur × ta part supposée", True)}'
                 f'{_th("Part réelle", "Mes unités vendues / unités vendues sur le marché", True)}'
                 f'{_th("Achat moyen", "Unités par achat", True)}{_th("Taille d’annonce outil", None, True)}'
                 f'</tr></thead><tbody>{rows}</tbody></table></div>')
        body = kpis + "<div class='card' style='margin:12px 0'>" + "".join(f"<div>{n}</div>" for n in notes) + "</div>" + table
    else:
        body = "<p class='mut'>Aucune vente enregistrée : colle une capture de ton historique des ventes ci-dessous.</p>"
    edit = cfg.get("_github_sales_edit_url")
    paste = ('<div class="card" style="margin-top:14px" ondragover="event.preventDefault()" '
             'ondrop="event.preventDefault();scanHist(event.dataTransfer.files[0])"><b>📷 Ajouter des ventes depuis une capture</b>'
             '<span class="mut">En jeu, ouvre l’historique des ventes et fais une capture de la liste (Win + Maj + S), puis colle-la '
             'ici avec <b>Ctrl + V</b> (sur cet onglet), glisse le fichier, ou <label style="color:var(--acc);cursor:pointer;'
             'text-decoration:underline">choisis un fichier<input type="file" accept="image/*" hidden '
             'onchange="scanHist(this.files[0])"></label>. Plusieurs captures s’ajoutent, les ventes déjà connues ne sont pas '
             'doublées. Contrôles automatiques : reçu = prix − 10 %, prix = unitaire × quantité, dates dans l’ordre.</span>'
             '<span id="gmsg" class="mut"></span><div class="chips" id="grows"></div>'
             '<div class="toolbar" style="margin:0"><button class="mapbtn" onclick="copyHist()">📋 Copier le fichier</button>'
             + (f'<a class="mapbtn" style="text-decoration:none" href="{esc(edit)}" target="_blank" rel="noopener">'
                '✏️ Ouvrir mes_ventes.json sur GitHub</a>' if edit else '')
             + '<button class="mapbtn" onclick="HIST=[];renderHist();document.getElementById(\'gmsg\').textContent=\'\'">Effacer</button></div>'
             '<textarea id="gjson" spellcheck="false" style="width:100%;min-height:120px;padding:8px 10px;border:1px solid var(--line);'
             'border-radius:8px;background:var(--bg2);color:var(--txt);font:12.5px/1.5 ui-monospace,Consolas,monospace"></textarea>'
             '<span class="sub">Colle ce contenu à la place de celui du fichier sur GitHub, puis « Commit changes » : '
             'le prochain passage horaire met à jour cet onglet.</span></div>'
             f'<script>window.MY_SALES={json.dumps(cfg.get("my_sales") or [], ensure_ascii=False)};'
             f'window.MY_SALES_HELP={json.dumps(cfg.get("_my_sales_help") or "", ensure_ascii=False)};</script>')
    return head + body + paste


def build(con, cfg, results):
    REPORT_DIR.mkdir(exist_ok=True)
    ctx = Ctx(con, map_world_ids(con, cfg))
    write_map_data(con, cfg)
    ctx.charted = write_price_data(con, cfg)
    shutil.copy(Path(__file__).with_name("scan.js"), REPORT_DIR / "scan.js")   # lecture des captures, chargee a la demande
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
           "« Vendre à » = prix réaliste : le prix affiché, ramené vers le prix habituel sur ton serveur (médiane 3 j) "
           "quand il est anormalement haut.")
    if my:
        add("home", "🏠 Aujourd’hui", home(con, cfg, ctx, my, sname))
        sep()
        add("planning", "📅 Planning", planning_tab(cfg, my))
        add("harvest", "🌲 Récolte",
            "<h2>Récolte → craft → vente</h2><p class='lead'>Ta récolte est gratuite et toujours transformée "
            "(jamais vendue brute). Deux façons de voir les mêmes calculs.</p>"
            '<div class="seg"><button class="on" data-v="res" onclick="segShow(this,\'hres\')">Par ressource</button>'
            '<button data-v="craft" onclick="segShow(this,\'hcraft\')">Par craft</button></div>'
            "<div id='hres' class='segp'><p class='lead'>Indique ce que tu récoltes par heure pour chaque ressource "
            "(100 par défaut) : <b>Kinah / heure</b> dit où passer ton temps, <b>Heures / jour</b> combien de temps de récolte "
            "le marché absorbe avant que les prix baissent. Clique sur « crafts » pour voir le détail d’une ressource. "
            "Les usages douteux ou à perte sont indiqués en orange.</p>" + table_targets(ctx, my["targets"]) + "</div>"
            f"<div id='hcraft' class='segp' style='display:none'><p class='lead'>{hyp} Ventes/j = ta part des ventes "
            "mesurées sur ton serveur (annonces disparues sur 24 h × taille habituelle des annonces).</p>"
            + table_crafts(ctx, my["harvest"], "th", True) + "</div>")
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
        add("plan", "🧮 Mon stock", "<h2>Mon stock → quoi fabriquer</h2>" + stock_calc(ctx, cfg, my["harvest"], my["market"].gather_names(),
                         {t: my["market"].items[s]["base_name"] for t, s in my["market"].transmute.items()})
            + ("<h3>Plan quotidien (config)</h3>" + table_plan(my["plan"]) if my["plan"] else ""))
        add("gains", "💰 Mes gains", gains_tab(ctx, cfg, my))
        sep()
    others = [r for r in results if r is not my]
    if others:
        parts = []
        for r in others:
            on = names.get(r["server"], r["server"])
            parts.append(f"<h2>{esc(on)}</h2><p class='lead'>Ventes mesurées sur ce serveur.</p>"
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
<div id="cmodal" onclick="if(event.target===this)closeChart()"><div class="box"><div class="bar"><b id="ctitle"></b>
<button class="mapbtn" onclick="closeChart()">Fermer ✕</button></div><div id="cbody"></div></div></div>
<div id="modal" onclick="if(event.target===this)closeMap()"><div class="box"><div class="bar"><b id="mtitle"></b>
<button class="mapbtn" onclick="closeMap()">Fermer ✕</button></div><iframe id="mframe"></iframe></div></div>
</body></html>"""
    path = REPORT_DIR / "index.html"
    path.write_text(page, encoding="utf-8")
    return path
