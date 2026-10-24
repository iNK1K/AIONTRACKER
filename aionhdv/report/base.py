"""Outils communs des pages : mise en forme, contexte (icones, noms), styles."""
import html
import re

from ..catalog import node_name
from ..collect import BOUND_RE
from ..config import DATA_DIR

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
#stale{background:#f064701f;color:var(--bad);border-bottom:1px solid var(--bad);padding:10px 28px;font-weight:600}
nav{position:sticky;top:0;z-index:20;background:rgba(11,13,18,.94);backdrop-filter:blur(6px);border-bottom:1px solid var(--line);
 padding:0 28px;display:flex;gap:2px;overflow-x:auto}
nav button{background:none;border:0;border-bottom:2px solid transparent;color:var(--mut);padding:13px 14px;font:inherit;font-size:14px;font-weight:600;cursor:pointer;white-space:nowrap}
nav button:hover{color:var(--txt)}nav button.on{color:var(--acc);border-bottom-color:var(--acc)}
nav button.tool{display:none}nav.tools button.tool{display:inline-block}nav.tools .toolbtn{color:var(--acc)}
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
.ai{max-width:860px;margin:0 auto;min-height:calc(100vh - 190px);display:flex;flex-direction:column}
.aimsgs{flex:1;display:flex;flex-direction:column;gap:18px;padding-bottom:12px}
.aihello{margin:9vh auto 0;text-align:center;max-width:680px}.aihello h2{font-size:28px;margin-bottom:8px}.aihello .lead{margin:0 auto 22px}
.aisugg{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:10px;text-align:left}
.aisugg button{background:var(--card);border:1px solid var(--line);border-radius:12px;color:var(--txt);padding:12px 14px;font:inherit;font-size:14px;cursor:pointer;text-align:left}
.aisugg button:hover{border-color:var(--acc)}
.aiu{align-self:flex-end;max-width:80%;background:var(--card2);border:1px solid var(--line);border-radius:16px 16px 4px 16px;padding:10px 14px;white-space:pre-wrap}
.aia{line-height:1.6;overflow-wrap:anywhere}.aia p{margin:0 0 10px}.aia ul,.aia ol{margin:0 0 10px;padding-left:24px}.aia li{margin:3px 0}
.aia h1,.aia h2,.aia h3,.aia h4{font-size:16px;margin:16px 0 6px;color:var(--acc);text-transform:none;letter-spacing:0}
.aitbl{max-width:100%;overflow-x:auto;margin:6px 0 12px}.aia table{width:auto;border:1px solid var(--line);border-radius:10px;overflow:hidden;background:var(--card)}
.aia th{position:static;cursor:auto}.aia td{padding:7px 12px;overflow-wrap:normal;min-width:90px}.aia a{color:var(--acc)}
.aia pre{background:var(--card2);padding:10px;border-radius:8px;overflow:auto}.aia blockquote{margin:0 0 10px;padding-left:12px;border-left:3px solid var(--line);color:var(--mut)}
.aistat{color:var(--mut);font-size:13px;display:flex;align-items:center;gap:8px}
.aistat:before{content:"";width:8px;height:8px;border-radius:50%;background:var(--acc);animation:aip 1s infinite alternate}
@keyframes aip{from{opacity:.25}to{opacity:1}}
.aisrc{display:flex;flex-wrap:wrap;gap:6px;margin-top:4px}.aisrc a{font-size:12px;color:var(--mut);background:var(--card);border:1px solid var(--line);
 border-radius:999px;padding:2px 10px;text-decoration:none;max-width:260px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.aisrc a:hover{color:var(--acc)}
.aierr{color:var(--bad);background:#f064701a;border:1px solid #f0647055;border-radius:10px;padding:10px 14px}
.aidock{position:sticky;bottom:0;padding-top:8px;background:linear-gradient(transparent,var(--bg) 14px)}
.aibar{display:flex;gap:8px;align-items:flex-end;background:var(--card);border:1px solid var(--line);border-radius:18px;
 padding:8px 8px 8px 16px;box-shadow:0 -14px 24px var(--bg)}
.aibar:focus-within{border-color:var(--acc)}
.aibar textarea{flex:1;resize:none;border:0;background:none;color:var(--txt);font:inherit;font-size:15.5px;padding:7px 0;max-height:220px;outline:none}
.aibar button{flex:none;width:38px;height:38px;border-radius:50%;border:0;background:var(--acc);color:#111;font-size:16px;font-weight:700;cursor:pointer}
.aibar button:disabled{opacity:.35;cursor:default}
.aifoot{display:flex;gap:12px;align-items:center;justify-content:space-between;padding:8px 4px 0;color:var(--mut);font-size:12.5px}
.aifoot button{background:none;border:0;color:var(--mut);font:inherit;cursor:pointer;padding:0}.aifoot button:hover{color:var(--acc)}
.aikey{background:var(--card);border:1px solid var(--acc);border-radius:12px;padding:14px 16px;margin:0 0 12px}
.aikey input{width:100%;padding:8px 12px;border:1px solid var(--line);border-radius:8px;background:var(--bg2);color:var(--txt);font:inherit;margin:8px 0}
.aikey button{background:var(--acc);color:#111;border:0;border-radius:8px;padding:7px 14px;font:inherit;font-weight:700;cursor:pointer;margin-right:8px}
.aikey button.sec{background:none;color:var(--mut);border:1px solid var(--line)}
.aihome{text-align:left;margin-top:26px}.aihome h3{margin:22px 0 6px}.aihome .sub{margin:8px 0 4px}
.aichip{display:inline-flex;align-items:center;gap:5px;background:var(--card2);border:1px solid var(--line);border-radius:999px;padding:1px 9px 1px 3px;
 cursor:pointer;font-weight:600;font-size:.94em;vertical-align:middle;line-height:1.5}.aichip:hover{border-color:var(--acc)}
.aichip img{width:20px;height:20px;border-radius:50%}.aichip em{font-style:normal;font-weight:500;color:var(--mut);font-size:.9em}
.aicards{display:grid;grid-template-columns:repeat(auto-fill,minmax(205px,1fr));gap:10px;margin:8px 0 14px}
.aicard{display:flex;gap:10px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px;cursor:pointer;min-width:0}
.aicard:hover{border-color:var(--acc)}.aicard>img{width:46px;height:46px;border-radius:9px;background:#0007;border:1px solid var(--line);flex:none}
.aicard>div{min-width:0;flex:1}.aicard .nm{font-weight:700;font-size:14px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.aicard .sub{font-size:11.5px;margin:0}.aicard .pr{font-weight:700;font-size:15px;margin-top:2px}.aicard .pr small{color:var(--mut);font-weight:500}
.aispark{display:block;width:100%;height:26px;margin-top:4px}
.aistats{margin:8px 0 14px}.aistats .v{font-size:22px}
.aisteps{list-style:none;counter-reset:st;padding:0;margin:8px 0 14px;display:flex;flex-direction:column;gap:8px}
.aisteps li{counter-increment:st;position:relative;padding:10px 14px 10px 50px;background:var(--card);border:1px solid var(--line);border-radius:12px;margin:0}
.aisteps li:before{content:counter(st);position:absolute;left:12px;top:10px;width:26px;height:26px;border-radius:50%;background:var(--acc);color:#111;
 font-weight:800;display:flex;align-items:center;justify-content:center;font-size:13px}.aisteps li div{color:var(--mut);font-size:14px}
.aichart{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px;margin:8px 0 14px}
.aichart .t{font-weight:700;margin-bottom:8px}.aichart .r{display:grid;grid-template-columns:minmax(90px,34%) 1fr auto;gap:10px;align-items:center;margin:5px 0;font-size:14px}
.aichart i{display:block;height:12px;background:var(--bg2);border-radius:6px;overflow:hidden}.aichart i b{display:block;height:100%;background:var(--acc);border-radius:6px}
.aichart i b.neg{background:var(--bad)}.aichart em{font-style:normal;font-weight:700;font-variant-numeric:tabular-nums}
.aicall{border-radius:12px;padding:10px 14px;margin:0 0 12px;border:1px solid var(--line);background:var(--card)}
.aicall.tip{border-color:#4ea8ff66;background:#4ea8ff12}.aicall.warn{border-color:#f0a05066;background:#f0a05012}.aicall.ok{border-color:#3ecf8e66;background:#3ecf8e12}
.aiimg{display:inline-block;margin:6px 8px 6px 0;max-width:100%;vertical-align:top}.aiimg img{max-width:100%;max-height:300px;border-radius:12px;border:1px solid var(--line);display:block}
.aiimg figcaption{color:var(--mut);font-size:12.5px;margin-top:4px}
.aifollow{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 4px}.aifollow button{background:var(--card);border:1px solid var(--line);border-radius:999px;color:var(--txt);
 padding:7px 14px;font:inherit;font-size:13.5px;cursor:pointer;text-align:left}.aifollow button:hover{border-color:var(--acc);color:var(--acc)}
.ainews{display:flex;flex-direction:column;gap:6px}.ainews a{display:flex;flex-direction:column;background:var(--card);border:1px solid var(--line);border-radius:10px;
 padding:8px 12px;color:var(--txt);text-decoration:none;font-size:14px}.ainews a:hover{border-color:var(--acc)}.ainews .sub{margin:0}
.aiposts{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px}.aiposts a{display:flex;flex-direction:column;gap:4px;background:var(--card);
 border:1px solid var(--line);border-radius:12px;padding:10px 12px;color:var(--txt);text-decoration:none;font-size:13.5px;overflow:hidden}.aiposts a:hover{border-color:var(--acc)}
.aiposts img{width:calc(100% + 24px);margin:-10px -12px 4px;height:120px;object-fit:cover}.aiposts .sub{margin:0}.aiposts span:last-child{color:var(--mut);display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}
#aimodal{position:fixed;inset:0;background:#000b;display:none;align-items:center;justify-content:center;z-index:56;padding:12px}#aimodal.on{display:flex}
#aimodal .box{width:min(640px,96vw);max-height:90vh;overflow:auto;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px}
.aihead{display:flex;gap:12px;align-items:center}.aihead img{width:56px;height:56px;border-radius:10px;border:1px solid var(--line);background:#0007}.aihead b{font-size:18px}
.aiacts{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 4px}.aiacts .mapbtn{font-size:12.5px;padding:5px 10px;margin:0}
#aimodal h4{margin:14px 0 6px;color:var(--mut);font-size:12px;text-transform:uppercase;letter-spacing:.05em}#aimodal .chips{gap:6px;align-items:center}
.aiatt{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 8px}.aiattc{display:flex;align-items:center;gap:8px;background:var(--card);border:1px solid var(--line);
 border-radius:10px;padding:4px 6px 4px 4px;font-size:13px;max-width:260px}.aiattc img,.aiattc b{width:40px;height:40px;border-radius:7px;object-fit:cover;flex:none;
 display:flex;align-items:center;justify-content:center;background:var(--card2);font-size:11px}.aiattc span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.aiattc button{background:none;border:0;color:var(--mut);cursor:pointer;font-size:14px}.aiattc button:hover{color:var(--bad)}
.aiclip{flex:none;cursor:pointer;font-size:19px;padding:6px 4px 6px 0;opacity:.8;align-self:center}.aiclip:hover{opacity:1}
.ai.drop .aibar{border-color:var(--acc);box-shadow:0 0 0 3px #f0c05033}
.aiuatt{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:6px}.aiuatt img{max-width:180px;max-height:140px;border-radius:8px;border:1px solid var(--line)}
.aiuatt span{font-size:13px;color:var(--mut)}
.aimemo{border:1px solid #b48cff55;background:#b48cff12;border-radius:12px;padding:10px 14px;margin:8px 0 12px;font-size:14px}
.aimemo b{color:#c9a8ff}.aimemo div{margin-top:3px}.aimemo button{background:none;border:0;color:var(--mut);font:inherit;font-size:12.5px;cursor:pointer;padding:0;margin-top:6px}
.aimemo button:hover{color:var(--acc)}.aimemlist{display:flex;flex-direction:column;gap:6px;margin:10px 0}.aimemlist>div{display:flex;gap:8px;align-items:baseline;
 background:var(--bg2);border:1px solid var(--line);border-radius:8px;padding:6px 10px;font-size:14px}.aimemlist button{margin-left:auto;background:none;border:0;
 color:var(--mut);cursor:pointer}.aimemlist button:hover{color:var(--bad)}
.aiopts{display:grid;gap:10px;margin-bottom:8px}.aiopt{border:1px solid var(--line);border-radius:10px;padding:10px 12px}.aiopt.on{border-color:var(--ok)}
.aiperso{border:1px solid #f0c05055;background:#f0c05010;border-radius:12px;padding:10px 14px;margin:8px 0 12px;font-size:14px}
.aiperso b{color:var(--acc)}.aiperso div{margin-top:3px}.aiperso .sub{margin:0}.aiperso button{background:none;border:0;color:var(--mut);font:inherit;
 font-size:12.5px;cursor:pointer;padding:0;margin-top:6px}.aiperso button:hover{color:var(--acc)}
.pz{display:grid;grid-template-columns:minmax(0,1fr);gap:20px;align-items:start}.pz .ai{width:100%}
.psheet{display:flex;flex-direction:column;gap:12px;min-width:0}
.pempty,.phead,.pcard,.plink,.pbody{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 16px}
.pempty{border-style:dashed;text-align:center;padding:24px 20px}.pempty h2{margin:10px 0 6px}.pempty .lead{margin:0 auto 10px}
.pempty ul{text-align:left;color:var(--mut);font-size:14px;margin:0 auto 14px;max-width:340px;padding-left:20px}.pempty .pav{margin:0 auto}
.phead{background:linear-gradient(160deg,#211d14,var(--card) 60%);border-color:#f0c05040}
.phead .who{display:flex;gap:12px;align-items:center}.phead h2{font-size:21px;margin:0;overflow-wrap:anywhere}.phead .sub{margin:0}
.pav{width:54px;height:54px;border-radius:50%;flex:none;display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:800;
 color:#111;background:var(--acc);overflow:hidden}.pav img{width:100%;height:100%;object-fit:cover;object-position:50% 20%}
.ptitle{font-size:12.5px;font-weight:600;margin-top:1px}.pacts{display:flex;gap:6px;margin-left:auto;align-self:flex-start}
.phead .kpis{margin:12px 0 0;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px}.phead .kpi{background:var(--bg2);padding:10px 12px}
.phead .kpi .v{font-size:21px}
.ptags{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}.ptags span{background:var(--bg2);border:1px solid var(--line);border-radius:999px;
 padding:2px 10px;font-size:12.5px;color:var(--mut)}.ptags b{color:var(--txt);font-weight:600}
.pbtn{background:var(--card2);border:1px solid var(--line);border-radius:999px;color:var(--txt);padding:6px 12px;font:inherit;font-size:13px;cursor:pointer;flex:none}
.pbtn:hover{border-color:var(--acc);color:var(--acc)}
.pbody{padding:0 14px 14px}.ptab{display:flex;flex-direction:column;gap:12px;padding-top:12px}
.ptabs{display:flex;gap:2px;overflow-x:auto;scrollbar-width:none;border-bottom:1px solid var(--line);margin:0 -14px;padding:0 6px}
.ptabs button{background:none;border:0;border-bottom:2px solid transparent;color:var(--mut);padding:10px 8px 8px;font:inherit;font-size:13px;font-weight:600;
 cursor:pointer;white-space:nowrap}.ptabs button:hover{color:var(--txt)}.ptabs button.on{color:var(--acc);border-bottom-color:var(--acc)}
.ph5{margin:4px 0 -4px;font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.05em;display:flex;gap:6px;align-items:baseline}
.ph5 small{margin-left:auto;font-weight:500;text-transform:none;letter-spacing:0;font-size:11.5px;text-align:right}
.pcard h4{margin:0 0 8px;font-size:12.5px;color:var(--mut);text-transform:uppercase;letter-spacing:.05em;display:flex;gap:6px;align-items:baseline}
.pcard h4 small{margin-left:auto;font-weight:500;text-transform:none;letter-spacing:0;font-size:11.5px}
.ptab .pcard{background:var(--bg2);border-color:var(--line2);padding:10px 12px}
.pdoll{display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:8px 10px}.pcol{display:flex;flex-direction:column;gap:6px}
.pslot{--g:#596275;position:relative;width:50px;height:50px;flex:none;padding:0;border-radius:9px;overflow:hidden;cursor:pointer;
 border:1px solid color-mix(in srgb,var(--g) 75%,transparent);background:radial-gradient(circle at 50% 30%,color-mix(in srgb,var(--g) 50%,#0b0d12),#0b0d12 80%)}
.pslot img{width:100%;height:100%;object-fit:contain;display:block}
.pslot i,.parc i,.pskills i{position:absolute;right:3px;bottom:1px;font-style:normal;font-weight:800;font-size:12.5px;color:#fff;
 text-shadow:0 1px 2px #000,0 0 5px #000}
.pslot span{display:flex;align-items:center;justify-content:center;height:100%;padding:2px;font-size:9.5px;line-height:1.15;color:var(--mut);text-align:center}
.pslot.empty{border:1px dashed var(--line);background:var(--bg2);cursor:default}
.pslot:not(.empty):hover,.pslot:focus-visible,.parc button:hover,.parc button:focus-visible{outline:2px solid var(--g);outline-offset:1px}
.pfig{position:relative;min-height:220px;border-radius:12px;overflow:hidden;border:1px solid var(--line);background:radial-gradient(circle at 50% 35%,#2a2418,#07080b 75%)}
.pfig img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 18%}
.pfig0{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:56px;opacity:.5}
.pfigb{position:absolute;left:0;right:0;bottom:0;padding:28px 8px 8px;background:linear-gradient(transparent,#000e 55%);font-size:11.5px;color:var(--mut);text-align:center}
.pfigb b{color:var(--txt);font-size:15px}.pfigb div{margin-top:1px}
.prow{grid-column:1/-1;display:flex;justify-content:center;gap:8px}
.parc{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:6px}
.parc button{--g:#596275;position:relative;aspect-ratio:3/4;padding:0;border-radius:8px;overflow:hidden;border:1px solid var(--g);background:#000;cursor:pointer}
.parc img{width:100%;height:100%;object-fit:cover;display:block}
.pmini{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:6px}
.pminic{--g:var(--line);display:flex;gap:8px;align-items:center;background:var(--bg2);border:1px solid var(--line2);border-left:3px solid var(--g);border-radius:10px;
 padding:6px 8px;font-size:13px;min-width:0}.pminic img{width:38px;height:38px;object-fit:contain;flex:none}
.pminic b{display:block;overflow-wrap:anywhere;font-weight:600}.pminic .sub{display:block}
.pmain,.pattr{display:grid;gap:6px}.pmain{grid-template-columns:repeat(auto-fill,minmax(112px,1fr))}.pattr{grid-template-columns:repeat(3,minmax(0,1fr))}
.pmain div,.pattr div{background:var(--bg2);border:1px solid var(--line2);border-radius:9px;padding:6px 9px;min-width:0}
.pmain span,.pattr span{display:block;color:var(--mut);font-size:11.5px}.pmain b{font-size:16px}.pattr b{font-size:15px}.pattr div[data-tip]{cursor:help}
.pgods{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:0 14px}
.pgods div{display:flex;gap:10px;align-items:baseline;padding:5px 0;border-top:1px solid var(--line2);font-size:13.5px;min-width:0}
.pgods b{flex:0 0 26px;text-align:right;font-variant-numeric:tabular-nums;color:var(--acc)}.pgods span{min-width:0}
.pgods em{color:var(--mut);font-style:normal;font-size:12px}.pgods small{display:block;color:var(--mut);font-size:11.5px}
.pdet{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:0 14px}
.pdet div{display:flex;justify-content:space-between;gap:10px;padding:4px 0;border-top:1px solid var(--line2);font-size:13.5px}
.pdet span{color:var(--mut)}.pdet b{font-weight:600;font-variant-numeric:tabular-nums;white-space:nowrap}
.pmain .z,.pattr .z,.pdet .z,.pgods .z{opacity:.45}
.pdaev{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:8px}
.pdv{display:flex;gap:10px;align-items:center;background:var(--bg2);border:1px solid var(--line2);border-radius:10px;padding:8px 10px;font-size:13.5px}
.pring{--p:0;width:52px;height:52px;flex:none;border-radius:50%;display:grid;place-items:center;background:conic-gradient(var(--acc) calc(var(--p)*1%),var(--line) 0)}
.pring b{width:42px;height:42px;border-radius:50%;background:var(--bg2);display:grid;place-items:center;font-size:12px}
.pskills{display:grid;grid-template-columns:repeat(auto-fill,minmax(44px,1fr));gap:6px}
.pskills button{position:relative;aspect-ratio:1;padding:0;border-radius:9px;overflow:hidden;border:1px solid var(--line);background:#000;cursor:pointer}
.pskills button.eq{border-color:var(--acc);box-shadow:0 0 0 1px var(--acc)}.pskills button.off{opacity:.35;filter:grayscale(1)}
.pskills img{width:100%;height:100%;display:block}
.ptitles{display:grid;gap:6px}.ptitles>div{background:var(--bg2);border:1px solid var(--line2);border-radius:10px;padding:7px 10px;font-size:13.5px}
.plink{border-color:#f0c05055;background:linear-gradient(160deg,#211d14,var(--card) 70%)}.plink .sub{margin:4px 0 10px}
.plink form{display:flex;gap:8px}.plink input{flex:1;width:auto;min-width:0}#plres{display:grid;gap:6px;margin-top:8px}#plres:empty{display:none}
.plc{display:flex;gap:10px;align-items:center;background:var(--bg2);border:1px solid var(--line);border-radius:10px;padding:6px 8px;color:var(--txt);
 font:inherit;text-align:left;cursor:pointer}.plc:hover{border-color:var(--acc)}.plc img{width:40px;height:40px;border-radius:50%;object-fit:cover;flex:none}
.plc b{display:block}.plc .sub{display:block}
#ptip{--g:var(--line);position:fixed;top:0;left:0;z-index:200;width:max-content;max-width:min(320px,calc(100vw - 16px));padding:10px 12px;
 border:1px solid var(--g);border-radius:10px;background:#0d1017;box-shadow:0 12px 32px #000b;font-size:13px;line-height:1.45;pointer-events:none;
 opacity:0;visibility:hidden}#ptip.on{opacity:1;visibility:visible}
#ptip .pth{display:flex;gap:10px;align-items:center;margin-bottom:6px}#ptip .pth b{font-size:14.5px}
#ptip .pth img{--g:#596275;width:44px;height:44px;flex:none;border-radius:8px;
 background:radial-gradient(circle at 50% 30%,color-mix(in srgb,var(--g) 50%,#0b0d12),#0b0d12 80%)}
#ptip h5{margin:8px 0 2px;font-size:10.5px;color:var(--mut);text-transform:uppercase;letter-spacing:.06em}
#ptip .ptl{display:flex;justify-content:space-between;gap:16px}#ptip .ptl span{color:var(--mut)}#ptip .ptl b{font-weight:600;white-space:nowrap}
#ptip .ptx{color:var(--mut);font-size:12px;margin-top:6px}
.prows div{display:flex;gap:12px;padding:6px 0;border-top:1px solid var(--line2);font-size:14px}.prows div:first-child{border-top:0;padding-top:0}
.prows span{color:var(--mut);flex:0 0 34%;max-width:150px;overflow-wrap:anywhere}.prows b{font-weight:600;min-width:0;overflow-wrap:anywhere}
.plog div{display:flex;gap:10px;font-size:14px;padding:4px 0}.plog span{color:var(--mut);flex:none;font-variant-numeric:tabular-nums;font-size:12.5px;padding-top:1px}
.ptools{display:flex;flex-wrap:wrap;gap:8px;align-items:center}.ptools .sub{margin:0 0 0 auto}
#pedit textarea{width:100%;min-height:240px;margin:8px 0;padding:8px 10px;border:1px solid var(--line);border-radius:8px;background:var(--bg2);
 color:var(--txt);font:13px/1.5 ui-monospace,Consolas,monospace}#pedit textarea:focus{outline:none;border-color:var(--acc)}
.pmore{display:none}
@media(min-width:1100px){.pz{grid-template-columns:minmax(400px,540px) minmax(0,1fr)}
 .psheet{position:sticky;top:62px;max-height:calc(100vh - 76px);overflow:auto;scrollbar-width:thin;padding-right:2px}}
@media(max-width:1099px){.pmore{display:block;margin:10px 0 0;background:none;border:0;color:var(--acc);font:inherit;font-size:13.5px;cursor:pointer;padding:0}
 .pmore:after{content:"Voir toute la fiche ▾"}.psheet.open .pmore:after{content:"Masquer le détail ▴"}.psheet:not(.open) .pbody{display:none}}
@media(max-width:560px){.phead .who{flex-wrap:wrap}.pacts{order:3;width:100%;margin-left:66px}}
@media(max-width:420px){.pslot{width:44px;height:44px}.pdoll{gap:6px}.pattr{grid-template-columns:repeat(2,minmax(0,1fr))}.pbody{padding:0 10px 10px}
 .ptabs{margin:0 -10px}}
"""


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
        self.data = {}             # grosses donnees de la page (window.<cle>) : data.js, hors de la page chiffree
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
        nm = name or (self.items.get(item_id) or {}).get("name") or str(item_id)      # item pas encore au catalogue
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
    if (e.get("vs_brut_u") or 0) < 0:
        return (f'<span class="badge b-warn">💰 Le brut rapporte plus : +{fmt(-e["vs_brut_u"])}/u en vendant '
                'les ressources brutes</span>')
    if e["net_pess_u"] <= 0:
        return '<span class="badge b-warn">Risqué si les prix baissent</span>'
    return '<span class="badge b-ok">Rentable</span>'


def is_good(e):
    """Rentable, sans doute sur les ventes, et (recolte) plus rentable que de vendre les ressources brutes."""
    return e["net_u"] > 0 and not e["flags"] and (e.get("vs_brut_u") or 0) >= 0


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
            f'data-day="{e["ma_part_j"]}"' + (f' data-brut="{e["brut_u"]}"' if e.get("brut_u") is not None else ""))


def use_name(u):
    """Usage d'une ressource : un craft, ou la vente du brut (jamais apres transmutation : la ressource obtenue est liee)."""
    if u.get("brut"):
        return "💰 Vendre brut"
    return u["objet"]


def lots_txt(e):
    """« 4 annonces de 100 » : comment decouper ce qu'on met en vente dans la journee."""
    n, lot = e.get("nb_lots_j"), e.get("lot_vente")
    if not n:
        return "–"
    return f"{n} annonce{'s' if n > 1 else ''} de {fmt(lot)}"


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


BRUT_BADGE = ' <span class="badge b-mut">💰 vendu brut</span>'


def _md(s):
    """Mise en forme minimale des messages d'alerte (**gras**)."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(s))
