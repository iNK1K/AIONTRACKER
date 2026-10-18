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
function normName(s){return s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[’`]/g,"'").replace(/\s+/g,' ').trim().toLowerCase()}
function importStock(){const txt=document.getElementById('paste').value,inputs=[...document.querySelectorAll('#stock input[data-r]')];
 const by={};inputs.forEach(i=>by[normName(i.dataset.r)]=i);const got={},unknown=[];
 txt.split(/\n/).forEach(line=>{const m=line.replace(/\(li[ée]+s?\)/i,'').match(/^\s*[-•*]?\s*(.+?)\s*[:=x×\s]\s*(\d[\d\s.]*)\s*$/i);
  if(!m||line.trim().startsWith('#'))return;const n=normName(m[1]),q=parseInt(m[2].replace(/[\s.]/g,''),10);if(!q)return;
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
 document.getElementById('gjson').value='{\n "_": '+JSON.stringify(window.MY_SALES_HELP||'')+',\n "ventes": [\n'
  +list.map(v=>'  '+JSON.stringify(v).replace(/,"/g,', "').replace(/":/g,'": ')).join(',\n')+'\n ]\n}\n'}
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
 // a egalite : la ressource elle-meme avant l'Od transmute
 slots.sort((a,b)=>(b.n*b.rate-a.n*a.rate)||(a.v-b.v));const plan={};let tot=0;
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
