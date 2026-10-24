function show(id){document.querySelectorAll('section').forEach(s=>s.classList.toggle('on',s.id===id));
 document.querySelectorAll('nav button').forEach(b=>b.classList.toggle('on',b.dataset.t===id));
 const b=document.querySelector('nav button[data-t="'+id+'"]');if(b&&b.classList.contains('tool'))document.querySelector('nav').classList.add('tools');try{localStorage.setItem('tab',id)}catch(e){};scrollTo(0,0);if(id==='chat')aiInit()}
// menu « Outils » : onglets secondaires, deplies au clic ou quand l'un d'eux est ouvert
function toggleTools(){document.querySelector('nav').classList.toggle('tools')}
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
  return `<tr><td><span class="nm" title="Cliquer pour copier">${escH(c.o)}</span>${c.b?' <span class="badge b-mut">💰 vendre brut</span>':''}${c.f?`<div><span class="badge b-warn">⚠ ${escH(c.f)}</span></div>`:''}</td><td class="n">${NF.format(n)}</td>`
  +`<td class="n">${NF.format(c.p)}</td><td class="n pos">${NF.format(c.n)}</td><td class="n big pos">${kf(n*c.n)}</td>`
  +`<td>${l?Math.max(1,Math.round(n/l))+' annonce(s) de '+NF.format(l):'–'}</td>`
  +`<td class="sub">${escH(Object.entries(c.r).map(([k,q])=>k+' ×'+NF.format(Math.ceil(n*q))).join(', ')+(c.trans?' (dont '+NF.format(Math.ceil(c.trans))+' '+c.transFrom+' transmuté)':''))}</td></tr>`}).join('')
  :'<tr><td colspan="7" class="mut">Entre tes quantités de ressources ci-dessus.</td></tr>';
 const rest=Object.entries(left).filter(([k,v])=>v>=1).map(([k,v])=>k+' ×'+NF.format(Math.floor(v)));
 document.getElementById('sleft').textContent=rest.length?'Ressources non utilisées (aucun usage rentable ou limite du marché atteinte) : '+rest.join(', '):''}
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
 if(on('plan')){e.preventDefault();scanFile(it.getAsFile())}else if(on('gains')){e.preventDefault();jScan(it.getAsFile())}
 else if(on('supply')){e.preventDefault();supplyScan(it.getAsFile())}});

// ======================================================================== journal des ventes
// Mes annonces et ce qu'elles deviennent : postee, vendue (tout ou partie), relistee (nouveau prix = nouveaux frais),
// retiree. Enregistre dans journal.json du depot GitHub (jeton garde dans ce navigateur), sinon dans ce navigateur.
// Meme calcul d'etat que config.lot_state (Python).
let J=null,JSHA=null,JBUSY=false,JOPEN=null;
const JC=()=>window.JCFG||{tax:0.1,fee:0.02,repo:null};
const jEsc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function jNow(){const d=new Date(),p=n=>String(n).padStart(2,'0');return d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate())+' '+p(d.getHours())+':'+p(d.getMinutes())}
function jid(){return Date.now().toString(36)+Math.random().toString(36).slice(2,7)}
function jState(l){const ev=(l.ev||[]).filter(e=>!e.x).sort((a,b)=>(a.t||'').localeCompare(b.t||''));
 // frais = frais d'enregistrement de chaque mise en vente (poste, reliste), perdus meme si l'annonce se vend ; la taxe de
 // vente est retenue sur le reglement (recu) ; retirer ne coute rien de plus
 // fe : frais de chaque mise en vente (id de l'evenement) ; une correction (erreur de saisie) recalcule ceux de la derniere
 let prix=l.prix,qte=l.qte,cout=l.cout,src=l.src||null,sold=0,ret=0,frais=0,recu=0,rel=0,poste=null,mq=0,mid=null;const fe={};
 ev.forEach(e=>{if(e.type==='poste'||e.type==='reliste'){prix=e.prix;mq=e.qte||0;mid=e.id;fe[mid]=lost(prix,mq);if(e.type==='reliste')rel++;else poste=e.t}
  else if(e.type==='corrige'){mq+=(e.qte||qte)-qte;prix=e.prix;qte=e.qte||qte;if(mid)fe[mid]=lost(prix,Math.max(0,mq))}
  else if(e.type==='vendu'){sold+=e.qte;recu+=e.recu||0}else if(e.type==='retire')ret+=e.qte;else if(e.type==='cout')cout=e.cout;else if(e.type==='src')src=e.src});
 Object.values(fe).forEach(f=>frais+=f);
 return {prix,qte,cout,src,vendus:sold,retires:ret,reste:Math.max(0,qte-sold-ret),frais,recu,relistes:rel,poste,ev,fe}}
// « debut » : date de remise a zero du journal ; une copie plus ancienne (navigateur, autre appareil) est ignoree
function jMerge(a,b){const lots={},order=[],debut=[(a&&a.debut)||'',(b&&b.debut)||''].sort().pop();
 [a,b].filter(x=>x&&(x.debut||'')===debut).forEach(x=>(x.lots||[]).forEach(l=>{let o=lots[l.id];
  if(!o){o=lots[l.id]=JSON.parse(JSON.stringify(l));order.push(l.id);return}
  if(l.del)o.del=1;const by={};o.ev.forEach(e=>by[e.id]=e);
  (l.ev||[]).forEach(e=>{if(!by[e.id])o.ev.push(JSON.parse(JSON.stringify(e)));else if(e.x)by[e.id].x=1})}));
 return {_:(a&&a._)||(b&&b._)||'',debut,maj:[(a&&a.maj)||'',(b&&b.maj)||''].sort().pop(),lots:order.map(i=>lots[i])}}
function jText(j){return '{\n "_": '+JSON.stringify(j._||'')+',\n "debut": '+JSON.stringify(j.debut||'')+',\n "maj": '+JSON.stringify(j.maj||'')+',\n "lots": [\n'
 +j.lots.map(l=>'  '+JSON.stringify(l)).join(',\n')+'\n ]\n}\n'}
function jLocal(){try{return JSON.parse(localStorage.getItem('journal')||'null')}catch(e){return null}}
function jKeep(){try{localStorage.setItem('journal',JSON.stringify(J))}catch(e){}}
function jToken(){try{return localStorage.getItem('ghtoken')||''}catch(e){return ''}}
function jStatus(t,cls){const el=document.getElementById('jsync');if(el){el.innerHTML=t;el.className='sub '+(cls||'')}}
const b64e=s=>{let b='';new TextEncoder().encode(s).forEach(c=>b+=String.fromCharCode(c));return btoa(b)};
const b64d=s=>new TextDecoder().decode(Uint8Array.from(atob(s.replace(/\s/g,'')),c=>c.charCodeAt(0)));
// le journal vit sur sa propre branche (jamais sur main : l'historique du code reste lisible)
const JBRANCH='journal';
async function jApi(method,body){const r=await fetch('https://api.github.com/repos/'+JC().repo+'/contents/journal.json'+(method==='GET'?'?ref='+JBRANCH+'&t='+Date.now():''),
  {method,headers:{Authorization:'Bearer '+jToken(),Accept:'application/vnd.github+json','Content-Type':'application/json'},body:body&&JSON.stringify(body)});
 if(r.status===404&&method==='GET')return null;if(!r.ok){const e=new Error('GitHub '+r.status);e.status=r.status;throw e}return r.json()}
async function jPull(){const d=await jApi('GET');if(!d){JSHA=null;return null}JSHA=d.sha;return JSON.parse(b64d(d.content))}
// enregistrement : fusion avec la version du depot (un autre appareil a pu ecrire entre-temps), puis ecriture
async function jSync(label){jKeep();
 if(!jToken()||!JC().repo){jStatus('💾 Enregistré dans ce navigateur seulement : ajoute ton jeton GitHub (ci-dessous) pour le garder sur le dépôt et l’utiliser dans les alertes.','neg');jRender();return}
 if(JBUSY)return;JBUSY=true;jStatus('⏳ Enregistrement sur GitHub…');
 try{for(let k=0;k<3;k++){const remote=await jPull();const merged=jMerge(remote,J);merged.maj=jNow();
   if(remote&&jText(remote)===jText({...merged,maj:remote.maj})){J=remote;break}
   try{const r=await jApi('PUT',{message:'Journal : '+(label||'mise à jour'),content:b64e(jText(merged)),branch:JBRANCH,...(JSHA?{sha:JSHA}:{})});
    JSHA=r.content.sha;J=merged;break}catch(e){if(e.status!==409&&e.status!==422)throw e}}
  jKeep();jStatus('✅ Enregistré sur GitHub à '+jNow().slice(11)+' (pris en compte au prochain passage horaire).','pos')}
 catch(e){jStatus('⚠ Pas enregistré sur GitHub ('+jEsc(e.message)+(e.status===401?' : jeton refusé':e.status===403||e.status===404?' : le jeton n’a pas le droit d’écrire dans ce dépôt':'')
  +'). Gardé dans ce navigateur, nouvel essai à la prochaine action.','neg')}
 JBUSY=false;jRender()}
async function jInit(){if(!document.getElementById('jopen'))return;
 J=jMerge(window.JOURNAL||{lots:[]},jLocal());jRender();
 const tk=document.getElementById('jtoken');if(tk)tk.value=jToken()?'••••••••':'';
 if(jToken()&&JC().repo){try{const remote=await jPull();J=jMerge(remote,J);jKeep();jRender();
   if(!remote||jText(jMerge(remote,{lots:[]}))!==jText({...J,maj:remote.maj}))await jSync('synchronisation');
   else jStatus('✅ À jour avec GitHub.','pos')}catch(e){jStatus('⚠ GitHub injoignable ('+jEsc(e.message)+') : modifications gardées dans ce navigateur.','neg')}}
 else jSync()}
function jSetToken(){const v=document.getElementById('jtoken').value.trim();if(!v||v.startsWith('•'))return;
 try{localStorage.setItem('ghtoken',v)}catch(e){}document.getElementById('jtoken').value='••••••••';jInit()}
function jForget(){try{localStorage.removeItem('ghtoken')}catch(e){}document.getElementById('jtoken').value='';jStatus('Jeton oublié dans ce navigateur.')}
// ---------------------------------------------------------------- actions
// frais d'enregistrement (fee x prix total, arrondi a l'inferieur, perdus) et reglement d'une vente (taxe retenue)
const lost=(p,q)=>Math.floor(JC().fee*p*q),net=(p,q)=>Math.floor(p*q*(1-JC().tax));
function jLot(id){return J.lots.find(l=>l.id===id)}
// origine d'une annonce : recolte -> craft ou vendue brute (cout 0), achat -> craft (cout = ingredients achetes), flip (cout = prix d'achat)
const JSRC={recolte:'🌲 Récolte → craft',brut:'💰 Récolte vendue brute',achat:'🛒 Achat → craft',ravit:'📦 Ravitaillement',flip:'🔁 Flip'};
// objets de ma derniere capture de ravitaillement (onglet Ravitaillement) : origine proposee « Ravitaillement »
function jSupplyNames(){const d=supplyLoad(),by={};if(!d)return [];(window.SUPPLY||[]).forEach(x=>(by[x.s]=by[x.s]||[]).push(x));
 return d.cards.flatMap(c=>c.items.flatMap(s=>(by[s]||[]).map(x=>x.n)))}
const jSrcDefault=n=>jSupplyNames().includes(n)?'ravit':(window.RAW_ITEMS||[]).includes(n)?'brut':(window.HARVEST_ITEMS||[]).includes(n)?'recolte':'achat';
// cout propose : ravitaillement = cout du craft de l'onglet Ravitaillement (option la moins chere, echecs compris), sinon comme l'achat -> craft
const jCostFor=(src,n)=>{if(src==='recolte'||src==='brut')return 0;if(src==='flip')return undefined;
 const sp=src==='ravit'&&(window.SUPPLY||[]).find(x=>x.n===n),e=sp&&sEval(sp);return e&&e.best?Math.round(e.best.per):(window.COSTS||{})[n]}
const jSrcOpts=v=>Object.entries(JSRC).map(([k,t])=>'<option value="'+k+'"'+(k===v?' selected':'')+'>'+t+'</option>').join('');
function jPost(){const g=id=>document.getElementById(id),objet=g('jo').value.trim(),q=+g('jq').value,p=+g('jp').value,n=Math.max(1,+g('jn').value||1);
 const c=g('jc').value===''?null:+g('jc').value,src=g('js').value;
 if(!objet||!(q>0)||!(p>0)){toast('Indique l’objet, la quantité et le prix');return}
 for(let k=0;k<n;k++){const id=jid();J.lots.push({id,objet,src,qte:q,prix:p,...(c!=null?{cout:c}:{}),ev:[{id:jid(),t:jNow(),type:'poste',prix:p,qte:q}]})}
 g('jq').value=g('jp').value='';jSync(n+' annonce(s) '+objet)}
function jAct(id,kind){JOPEN=JOPEN&&JOPEN.id===id&&JOPEN.kind===kind?null:{id,kind};jRender()}
function jDo(id,kind){const l=jLot(id),s=jState(l),g=k=>document.getElementById('ja'+k);
 if(kind==='vendu'){const q=Math.min(s.reste,+g('q').value||0),p=+g('p').value,t=(g('t').value||jNow()).replace('T',' ');
  if(!(q>0)||!(p>0))return;l.ev.push({id:jid(),t,type:'vendu',prix:p,qte:q,recu:net(p,q)})}
 else if(kind==='reliste'){const p=+g('p').value;if(!(p>0))return;l.ev.push({id:jid(),t:jNow(),type:'reliste',prix:p,qte:s.reste})}
 else if(kind==='retire')l.ev.push({id:jid(),t:jNow(),type:'retire',qte:s.reste});
 else if(kind==='src'){const src=g('s').value,c=g('c').value;l.ev.push({id:jid(),t:jNow(),type:'src',src});
  if(c!==''&&+c!==s.cout)l.ev.push({id:jid(),t:jNow(),type:'cout',cout:+c})}
 else if(kind==='corrige'){const p=+g('p').value,q=+g('q').value;if(!(p>0)||!(q>=s.vendus+s.retires)||!(q>0))return;
  l.ev.push({id:jid(),t:jNow(),type:'corrige',prix:p,qte:q})}
 else if(kind==='cout'){const c=+g('c').value;if(!(c>=0))return;l.ev.push({id:jid(),t:jNow(),type:'cout',cout:c})}
 JOPEN=null;jSync(kind+' '+l.objet)}
function jUndo(id){const l=jLot(id),ev=l.ev.filter(e=>!e.x&&e.t).sort((a,b)=>a.t.localeCompare(b.t));
 const last=ev[ev.length-1];if(!last)return;if(last.type==='poste'){if(confirm('Supprimer cette annonce du journal ?')){l.del=1;jSync('suppression '+l.objet)}return}
 last.x=1;jSync('annulation '+l.objet)}
// ---------------------------------------------------------------- captures : annonces en cours ou historique des ventes
async function jScan(file){if(!file||!(file.type||'').startsWith('image/'))return;const msg=document.getElementById('jmsg');
 msg.textContent='Lecture de la capture…';
 try{await scanLoad();const url=URL.createObjectURL(file);
  const img=await new Promise((ok,ko)=>{const i=new Image();i.onload=()=>ok(i);i.onerror=()=>ko('image illisible');i.src=url});
  const hist=__historyRows(img).rows.length>0;let added=0,known=0,bad=[];
  if(hist){const rows=await scanHistory(img,{progress:m=>msg.textContent=m});
   rows.forEach(r=>{if(r.check.some(c=>c!=='objet incertain')||!r.name||!r.date){bad.push((r.name||'?')+' '+(r.date||''));return}
    const unit=Math.round(r.total/r.qty);
    const dup=J.lots.some(l=>!l.del&&l.objet===r.name&&l.ev.some(e=>!e.x&&e.type==='vendu'&&e.t===r.date&&e.prix*e.qte===r.total));
    if(dup){known++;return}
    const open=J.lots.filter(l=>!l.del&&l.objet===r.name).map(l=>[l,jState(l)]).filter(([l,s])=>s.reste>=r.qty&&(!s.poste||s.poste<=r.date||l.avant));
    const pick=(open.find(([l,s])=>s.prix===unit)||open[0]||[])[0];
    const ev={id:jid(),t:r.date,type:'vendu',prix:unit,qte:r.qty,recu:r.net};
    if(pick)pick.ev.push(ev);else J.lots.push({id:jid(),objet:r.name,qte:r.qty,prix:unit,avant:1,ev:[ev]});added++})
   msg.textContent=added+' vente(s) ajoutée(s)'+(known?', '+known+' déjà connue(s)':'')+(bad.length?' ; à saisir à la main (lecture incertaine) : '+bad.join(', '):'')+'.'}
  else{const rows=await scanListings(img,{progress:m=>msg.textContent=m});
   rows.forEach(r=>{if(!r.name||r.unit==null||r.check.length){bad.push(r.name||'?');return}
    const same=J.lots.filter(l=>!l.del&&l.objet===r.name).map(l=>jState(l)).filter(s=>s.reste===r.qty&&s.prix===r.unit).length;
    const seen=rows.filter(x=>x!==r&&x.name===r.name&&x.qty===r.qty&&x.unit===r.unit&&rows.indexOf(x)<rows.indexOf(r)).length;
    if(same>seen){known++;return}
    const src=jSrcDefault(r.name),c=jCostFor(src,r.name);
    J.lots.push({id:jid(),objet:r.name,src,qte:r.qty,prix:r.unit,...(c!=null?{cout:c}:{}),ev:[{id:jid(),t:jNow(),type:'poste',prix:r.unit,qte:r.qty}]});added++});
   msg.textContent=added+' annonce(s) ajoutée(s)'+(known?', '+known+' déjà dans le journal':'')+(bad.length?' ; à saisir à la main (lecture incertaine) : '+bad.join(', '):'')+'.'}
  URL.revokeObjectURL(url);if(added)jSync('capture : '+added+(hist?' vente(s)':' annonce(s)'));else jRender()}
 catch(e){msg.textContent='Lecture impossible : '+e+' (la lecture fonctionne sur le site en ligne)'}}
// conseil pour une annonce en cours (f = JFLOOR : plus bas, annonces en vente, prix habituel, annonces vendues/h, taille) :
// garder, relister 1 sous le plus bas (la nouvelle annonce repaye les frais d'enregistrement) ou retirer pour liberer l'annonce
function jAdvice(s,f){if(!f)return '<span class="mut">pas en vente en ce moment</span>';
 const [fl,n,ref,dh,lot]=f,seuil=s.cout!=null?Math.ceil(s.cout/(1-JC().tax-JC().fee)):null,b=(c,t)=>'<span class="badge '+c+'">'+t+'</span> ';
 const ahead=fl<s.prix?n:0,wait=dh?(ahead+s.reste/(lot||1))/dh:null,w=wait!=null?'<span class="sub">vendu en ~'+fmtH(wait)+'</span>':'';
 if(!ahead)return b('b-ok','✅ Garder')+w;
 if(ref&&fl<0.85*ref)return b('b-warn','⏳ Attendre')+'<span class="sub">le plus bas ('+NF.format(fl)+') est sous le prix habituel ('+NF.format(ref)+')</span>';
 const to=fl-1,tax=lost(to,s.reste);
 if(seuil&&to<seuil)return ref&&ref<seuil?b('b-bad','↩ Retirer')+'<span class="sub">le prix habituel ('+NF.format(ref)+') est passé sous ton seuil ('+NF.format(seuil)+') : libère l’annonce</span>'
  :b('b-warn','⏳ Garder')+'<span class="sub">baisser passerait sous ton seuil ('+NF.format(seuil)+')</span>';
 if(wait!=null&&n/dh<3)return b('b-ok','✅ Garder')+'<span class="sub">les '+n+' annonces devant partent en ~'+fmtH(n/dh)+'</span>';
 const gain=s.cout!=null?net(to,s.reste)-s.cout*s.reste-tax:null;
 if(gain!=null&&gain<=0)return b('b-warn','⏳ Garder')+'<span class="sub">relister à '+NF.format(to)+' coûterait plus (frais '+NF.format(tax)+') que ça rapporte</span>';
 return b('b-bad','🔁 Relister à '+NF.format(to))+'<span class="sub">frais '+NF.format(tax)+(gain!=null?', gain restant '+NF.format(gain):'')+'</span>'}
// ---------------------------------------------------------------- affichage
function jRender(){if(!J)return;oppRender();const box=document.getElementById('jopen');if(!box)return;
 const F=window.JFLOOR||{},lots=J.lots.filter(l=>!l.del).map(l=>[l,jState(l)]);
 const open=lots.filter(([l,s])=>s.reste>0).sort((a,b)=>a[0].objet.localeCompare(b[0].objet,'fr'));
 const nm=n=>'<span class="nm" title="Cliquer pour copier">'+jEsc(n)+'</span>';
 box.innerHTML=open.length?open.map(([l,s])=>{const f=F[l.objet],bat=f&&f[0]<s.prix;
  const row='<tr><td>'+nm(l.objet)+' <span class="badge b-mut" style="cursor:pointer" title="Changer l’origine" onclick="jAct(\''+l.id+'\',\'src\')">'
   +(JSRC[s.src]||'❔ origine ?')+'</span>'+(bat?' <span class="badge b-bad">battu : '+NF.format(f[0])+'</span>':f?' <span class="badge b-ok">le moins cher</span>':'')+'</td>'
   +'<td class="n">'+s.reste+(s.reste<s.qte?' / '+s.qte:'')+'</td><td class="n">'+NF.format(s.prix)+'</td>'
   +'<td class="n">'+(s.cout!=null?NF.format(s.cout):'–')+'</td><td class="n '+(s.cout!=null?(net(s.prix,1)-lost(s.prix,1)-s.cout>0?'pos':'neg'):'')+'">'+(s.cout!=null?NF.format(net(s.prix,1)-lost(s.prix,1)-s.cout):'–')+'</td>'
   +'<td>'+jAdvice(s,f)+'</td>'
   +'<td>'+(s.poste?s.poste.slice(8,10)+'/'+s.poste.slice(5,7)+' '+s.poste.slice(11):'<span class="mut">avant le journal</span>')+'</td>'
   +'<td class="n">'+(s.relistes||'–')+'</td><td class="n">'+(s.frais?NF.format(s.frais):'–')+'</td>'
   +'<td style="white-space:nowrap"><button class="mapbtn" onclick="jAct(\''+l.id+'\',\'vendu\')">✅ Vendu</button> '
   +'<button class="mapbtn" onclick="jAct(\''+l.id+'\',\'reliste\')">🔁 Relister</button> '
   +'<button class="mapbtn" onclick="jAct(\''+l.id+'\',\'retire\')">↩ Retirer</button> '
   +'<button class="mapbtn" title="Erreur de saisie du prix ou de la quantité (sans frais)" onclick="jAct(\''+l.id+'\',\'corrige\')">✏ Corriger</button> '
   +'<button class="mapbtn" onclick="jAct(\''+l.id+'\',\'cout\')">Coût</button> '
   +'<button class="mapbtn" title="Annuler la dernière action" onclick="jUndo(\''+l.id+'\')">↶</button></td></tr>';
  if(!JOPEN||JOPEN.id!==l.id)return row;
  const k=JOPEN.kind,inp=(id,v,w,t)=>'<input id="ja'+id+'" class="search" type="'+(t||'number')+'" value="'+v+'" style="width:'+w+'px;display:inline-block">';
  const go='<button class="mapbtn" onclick="jDo(\''+l.id+'\',\''+k+'\')">OK</button>';
  const f2=k==='vendu'?'Vendu '+inp('q',s.reste,80)+' à '+inp('p',s.prix,110)+' /u, le '+inp('t',jNow().replace(' ','T'),190,'datetime-local')+' '+go
   +' <span class="sub">reçu après taxe : '+NF.format(net(s.prix,s.reste))+'</span>'
   :k==='reliste'?'Nouveau prix '+inp('p',f?Math.max(1,f[0]-1):s.prix,110)+' /u '+go+' <span class="sub">la nouvelle annonce repaye les frais d’enregistrement ('+Math.round(JC().fee*100)+' % du prix total, perdus), par ex. <b class="neg">'+NF.format(lost(f?Math.max(1,f[0]-1):s.prix,s.reste))+'</b> pour '+s.reste+' × '+NF.format(f?Math.max(1,f[0]-1):s.prix)+'</span>'
   :k==='retire'?'Retirer les '+s.reste+' restants '+go+' <span class="sub">les frais d’enregistrement déjà payés ('+NF.format(lost(s.prix,s.reste))+') sont perdus</span>'
   :k==='corrige'?'Prix '+inp('p',s.prix,110)+' /u, quantité mise en vente '+inp('q',s.qte,80)+' '+go
    +' <span class="sub">corrige une erreur de saisie, sans frais (pour un vrai changement de prix en jeu, utilise 🔁 Relister)</span>'
   :k==='src'?'Origine <select id="jas" class="search" style="width:auto;display:inline-block" onchange="jSrcCost(\''+l.id+'\')">'+jSrcOpts(s.src||jSrcDefault(l.objet))+'</select> '
    +'coût '+inp('c',(()=>{const src=s.src||jSrcDefault(l.objet),c=jCostFor(src,l.objet);   // 0 hors recolte = cout oublie
      return (s.cout==null||(s.cout===0&&c!==0))&&c!=null?c:(s.cout??'')})(),110)+' /u '+go
    +' <span class="sub">le coût suit l’origine choisie : 0 pour ta récolte (craftée ou vendue brute), ingrédients achetés pour l’achat → craft et le ravitaillement, ton prix d’achat pour un flip</span>'
   :'Coût de revient '+inp('c',s.cout??'',110)+' /u '+go;
  return row+'<tr><td colspan="10" style="background:var(--card2)">'+f2+'</td></tr>'}).join('')
  :'<tr><td colspan="10" class="mut">Aucune annonce en cours : ajoute-les ci-dessous ou colle une capture de ta fenêtre des ventes.</td></tr>';
 jStats(lots);jLog(lots)}
function jStats(lots){const per=+(document.getElementById('jper')||{}).value||0,since=per?new Date(Date.now()-per*864e5):null;
 const p=n=>String(n).padStart(2,'0'),lim=since?since.getFullYear()+'-'+p(since.getMonth()+1)+'-'+p(since.getDate())+' '+p(since.getHours())+':'+p(since.getMinutes()):'';
 const want=(document.getElementById('jsrc')||{}).value||'',acts={};
 const by={},T={recu:0,frais:0,cout:0,vendus:0,ventes:0,relistes:0,retraits:0,sansCout:0};
 const z=()=>({recu:0,brut:0,frais:0,cout:0,vendus:0,ventes:0,relistes:0,retraits:0,sansCout:0});
 lots.forEach(([l,s])=>{const a=s.src||'?',act=acts[a]||(acts[a]=z()),mine=!want||a===want;
  const o=mine?by[l.objet]||(by[l.objet]=z()):z();
  let cout=l.cout;(s.ev).forEach(e=>{if(e.type==='cout'){cout=e.cout;return}if(!e.t||e.t<lim)return;
   if(e.type==='poste'||e.type==='reliste'){act.frais+=s.fe[e.id]||0}
   else if(e.type==='vendu'){act.recu+=e.recu||0;act.vendus+=e.qte;act.ventes++;if(cout!=null)act.cout+=cout*e.qte;else act.sansCout+=e.qte}
   if(e.type==='reliste'||e.type==='retire'||e.type==='poste'){o.frais+=s.fe[e.id]||0;if(e.type==='reliste')o.relistes++;if(e.type==='retire')o.retraits++}
   else if(e.type==='vendu'){o.recu+=e.recu||0;o.brut+=e.prix*e.qte;o.vendus+=e.qte;o.ventes++;if(cout!=null)o.cout+=cout*e.qte;else o.sansCout+=e.qte}})});
 Object.values(by).forEach(o=>Object.keys(T).forEach(k=>T[k]+=o[k]));
 const ben=T.recu-T.cout-T.frais,kpi=(l,v,s,c)=>'<div class="kpi"><div class="l">'+l+'</div><div class="v '+(c||'')+'">'+v+'</div><div class="s">'+s+'</div></div>';
 document.getElementById('jkpi').innerHTML=kpi('Kinah reçus',kf(T.recu),T.ventes+' vente(s), '+NF.format(T.vendus)+' unités, après taxe','pos')
  +kpi('Frais d’enregistrement',kf(T.frais),Math.round(JC().fee*100)+' % de chaque mise en vente, perdus ('+T.relistes+' reliste(s), '+T.retraits+' retrait(s))',T.frais?'neg':'')
  +kpi('Bénéfice',kf(ben),T.sansCout?NF.format(T.sansCout)+' unités vendues sans coût connu (comptées gratuites)':'reçu − coût − frais',ben>0?'pos':'neg')
  +kpi('Poids des frais',T.recu?(T.frais/T.recu*100).toFixed(1).replace('.',',')+' %':'–','frais d’enregistrement / kinah reçus');
 const rows=Object.entries(by).filter(([n,o])=>o.ventes||o.frais).sort((a,b)=>b[1].recu-a[1].recu);
 document.getElementById('jitems').innerHTML=rows.length?rows.map(([n,o])=>{const b=o.recu-o.cout-o.frais;
  return '<tr><td><span class="nm">'+jEsc(n)+'</span></td><td class="n">'+NF.format(o.vendus)+'</td><td class="n">'+(o.vendus?NF.format(Math.round(o.brut/o.vendus)):'–')+'</td>'
   +'<td class="n">'+NF.format(o.recu)+'</td><td class="n">'+(o.cout?NF.format(o.cout):'–')+'</td><td class="n neg">'+(o.frais?NF.format(o.frais):'–')+'</td>'
   +'<td class="n">'+(o.relistes||o.retraits?o.relistes+' / '+o.retraits:'–')+'</td><td class="n '+(b>0?'pos':'neg')+'">'+NF.format(b)+(o.sansCout?' *':'')+'</td></tr>'}).join('')
  :'<tr><td colspan="8" class="mut">Rien sur cette période.</td></tr>';
 const ar=Object.entries(acts).filter(([k,o])=>o.ventes||o.frais).sort((a,b)=>(b[1].recu-b[1].cout-b[1].frais)-(a[1].recu-a[1].cout-a[1].frais));
 document.getElementById('jact').innerHTML=ar.length?ar.map(([k,o])=>{const b=o.recu-o.cout-o.frais;
  return '<tr><td>'+(JSRC[k]||'❔ origine non renseignée')+'</td><td class="n">'+o.ventes+'</td><td class="n">'+NF.format(o.vendus)+'</td><td class="n">'+NF.format(o.recu)+'</td>'
   +'<td class="n">'+(o.cout?NF.format(o.cout):'–')+'</td><td class="n neg">'+(o.frais?NF.format(o.frais):'–')+'</td>'
   +'<td class="n '+(b>0?'pos':'neg')+'">'+NF.format(b)+(o.sansCout?' *':'')+'</td><td class="n">'+(o.recu?Math.round(b/o.recu*100)+' %':'–')+'</td></tr>'}).join('')
  :'<tr><td colspan="8" class="mut">Rien sur cette période.</td></tr>'}
function jLog(lots){const ev=[];lots.forEach(([l,s])=>s.ev.forEach(e=>e.t&&e.type!=='cout'&&ev.push([e,l,s,ev.length])));ev.sort((a,b)=>b[0].t.localeCompare(a[0].t)||b[3]-a[3]);
 const T={poste:'📦 posté',reliste:'🔁 relisté',vendu:'✅ vendu',retire:'↩ retiré',src:'🏷 origine',corrige:'✏ corrigé'};
 document.getElementById('jlog').innerHTML=ev.slice(0,40).map(([e,l,s])=>'<tr><td>'+e.t.slice(8,10)+'/'+e.t.slice(5,7)+' '+e.t.slice(11)+'</td><td>'+T[e.type]+'</td><td>'+jEsc(l.objet)+'</td>'
  +'<td class="n">'+(e.qte||'')+'</td><td class="n">'+(e.prix?NF.format(e.prix):'')+'</td><td class="n '+(e.type==='vendu'?'pos':'neg')+'">'+(e.type==='vendu'?'+'+NF.format(e.recu||0):s.fe[e.id]?'−'+NF.format(s.fe[e.id]):'')+'</td>'
  +'<td><button class="mapbtn" title="Annuler ce mouvement (erreur de clic)" onclick="jUndoEv(\''+l.id+'\',\''+e.id+'\')">↶</button></td></tr>').join('')}
// annule un mouvement precis de « Derniers mouvements » ; annuler la mise en vente supprime l'annonce du journal
function jUndoEv(id,eid){const l=jLot(id),e=l&&l.ev.find(x=>x.id===eid);if(!e)return;
 if(e.type==='poste'){if(confirm('Supprimer l’annonce « '+l.objet+' » du journal ?')){l.del=1;jSync('suppression '+l.objet)}return}
 if(!confirm('Annuler ce mouvement de « '+l.objet+' » ?'))return;e.x=1;jSync('annulation '+l.objet)}
// changement d'origine d'une annonce : le cout propose suit (vide si le site n'a pas d'estimation)
function jSrcCost(id){const l=jLot(id),c=jCostFor(document.getElementById('jas').value,l.objet);document.getElementById('jac').value=c==null?'':c}
// formulaire : l'objet propose son origine (craft de ma recolte ou non), l'origine propose le cout
function jCostFill(fromObj){const n=document.getElementById('jo').value.trim(),sel=document.getElementById('js');
 if(fromObj&&n)sel.value=jSrcDefault(n);const c=jCostFor(sel.value,n);document.getElementById('jc').value=c==null?'':c}
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
  if(cp){const pr=net*day;cp.textContent=kf(pr);cp.dataset.v=pr;cp.classList.toggle('pos',pr>0);cp.classList.toggle('neg',pr<=0)}
  // face a la vente du brut : un echec fait aussi perdre les ressources (1 / reussite par craft reussi)
  const vb=el.querySelector('.cvb');if(vb&&el.dataset.brut!=null){const d=Math.round(net-(st.lose?+el.dataset.brut/info.rate:+el.dataset.brut));
   vb.textContent=NF.format(d);vb.dataset.v=d;vb.classList.toggle('pos',d>0);vb.classList.toggle('neg',d<=0)}});
 calc();renderMetiers();todoBuys();if(window.PLANDATA)planSafe();oppRender();if(window.SUPPLY)supplyRender()}
// « A faire maintenant » : achats -> craft que mes niveaux permettent (metier non renseigne = garde), 2 au plus,
// avec le taux de reussite quand le niveau est connu
function todoBuys(){let n=0;
 document.querySelectorAll('#todo li.buy').forEach(li=>{const sp=li.querySelector('[data-item]'),info=sp&&craftInfo(sp.dataset.item);
  const ok=!info||info.ok;li.style.display=ok&&n<2?'':'none';if(ok)n++;
  const r=li.querySelector('.td-rate');if(r)r.textContent=info&&info.ok&&info.rate!=null?' · réussite '+(info.rate*100).toFixed(0)+' %':''})}
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
 try{localStorage.setItem('rates',JSON.stringify(R))}catch(e){}oppRender()}
 document.querySelectorAll('#targets tr[data-res]').forEach(tr=>{const r=tr.dataset.res,i=tr.querySelector('.rate');
  if(!inp&&R[r]!=null)i.value=R[r];const rate=i.value===''?100:+i.value,best=+tr.dataset.best,abs=+tr.dataset.abs;
  const kh=tr.querySelector('.kh'),hj=tr.querySelector('.hj');
  if(!best||!rate){kh.textContent='–';kh.dataset.v=0;hj.textContent='–';hj.dataset.v=0;return}
  const v=best*rate;kh.textContent=kf(v);kh.dataset.v=v;const h=abs/rate;hj.dataset.v=h;
  hj.textContent=h>=24?'24 h +':(h<1?Math.round(h*60)+' min':h.toFixed(1).replace('.',',')+' h')})}
// ---------------- Planning
function pget(k,d){try{const v=localStorage.getItem(k);return v==null?d:JSON.parse(v)}catch(e){return d}}
function pset(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
const fmtH=h=>h<1?Math.round(h*60)+' min':h.toFixed(1).replace('.',',')+' h';
function planSafe(save){const box=document.getElementById('psafe');if(!box||!window.PLANDATA)return;
 const hEl=document.getElementById('phours');if(save)pset('phours',+hEl.value);else hEl.value=pget('phours',3);
 let left=+hEl.value||0;const R=rates(),st=lvState(),slots=[];
 PLANDATA.targets.forEach(t=>{const rate=R[t.r]!=null?R[t.r]:100;if(!rate)return;
  t.u.forEach(u=>{const info=craftInfo(u.i);if(info&&!info.ok)return;const p=info&&info.rate?info.rate:1;
   slots.push({r:t.r,rate:rate,o:u.o,i:u.i,v:u.v,b:u.b,n:u.n*(st.lose?p:1),cap:u.cap,per:u.per/(st.lose?p:1),lot:u.lot})})});
 // a egalite : la ressource elle-meme avant l'Od transmute
 slots.sort((a,b)=>(b.n*b.rate-a.n*a.rate)||(a.v-b.v));const plan={};let tot=0;
 const used={};                                     // capacite deja prise par craft (partagee Od / ressource)
 for(const s of slots){if(left<=0)break;const room=s.cap-(used[s.i]||0);const h=Math.min(left,room/s.rate);if(h<=0.05)continue;left-=h;
  const res=h*s.rate,units=Math.floor(res/s.per);used[s.i]=(used[s.i]||0)+res;tot+=units*s.per*s.n;
  (plan[s.r]=plan[s.r]||{h:0,res:0,k:0,c:[]});plan[s.r].h+=h;plan[s.r].res+=res;plan[s.r].k+=units*s.per*s.n;
  plan[s.r].c.push({o:s.o,b:s.b,units:units,lot:s.lot,k:units*s.per*s.n})}
 const rows=Object.entries(plan).sort((a,b)=>b[1].k-a[1].k);
 window.SAFEPLAN={tot:tot,hours:(+hEl.value||0)-left,rows:rows};
 const tp=document.getElementById('todo-plan');
 if(tp){const crafts=rows.flatMap(([r,p])=>p.c.filter(c=>c.units>0));
  tp.innerHTML=rows.length?'🌲 Récolter '+rows.slice(0,2).map(([r,p])=>'<b>'+escH(r)+'</b> '+fmtH(p.h)).join(' puis ')
   +' → '+crafts.slice(0,3).map(c=>(c.b?'vendre brut ':'fabriquer ')+'<b>'+NF.format(c.units)+'</b> × '+escH(c.o)).join(', ')
   +' (~<b class="pos">'+kf(tot)+'</b>). 🕘 Mettre en vente entre <b>'+PLANDATA.best+'</b>'
   +(crafts.some(c=>c.lot)?' : '+crafts.slice(0,3).filter(c=>c.lot).map(c=>Math.max(1,Math.round(c.units/Math.min(c.lot,c.units)))+' annonce(s) de '+NF.format(Math.min(c.lot,c.units))+' '+escH(c.o)).join(', '):'')+'.'
   :'Plan du jour : rien de rentable avec ton temps de jeu (Planning).'}
 const kp=document.getElementById('kpot');if(kp){kp.textContent=kf(tot);document.getElementById('kpots').textContent=
  'en '+String(+hEl.value||0).replace('.',',')+' h de jeu (Planning safe, récolte '+(Object.keys(R).length?'saisie':'100/h par défaut')+')'}
 if(!rows.length){box.innerHTML='<p class="mut">Rien de rentable à planifier.</p>';return}

 box.innerHTML='<div class="kpis"><div class="kpi"><div class="l">Gain estimé</div><div class="v pos">'+kf(tot)+'</div><div class="s">kinah, une fois tout vendu</div></div>'
  +'<div class="kpi"><div class="l">Temps utilisé</div><div class="v">'+fmtH((+hEl.value||0)-left)+'</div><div class="s">'+(left>0.05?'au-delà, les marchés sont saturés':'de récolte')+'</div></div>'
  +'<div class="kpi"><div class="l">Mise en vente</div><div class="v" style="font-size:20px">'+PLANDATA.best+'</div><div class="s">meilleur moment pour poster</div></div></div>'
  +'<div class="uses">'+rows.map(([r,p],k)=>`<div class="card" style="padding:12px 16px"><b>${k+1}. Récolter <span class="nm" title="Cliquer pour copier">${escH(r)}</span> pendant ${fmtH(p.h)}</b> <span class="sub">(≈ ${NF.format(Math.round(p.res))} ressources)</span>`
   +p.c.filter(c=>c.units>0).map(c=>`<div class="row"><span>→ ${c.b?'vendre brut':'fabriquer'} <b>${NF.format(c.units)}</b> × <span class="nm" title="Cliquer pour copier">${escH(c.o)}</span>${c.lot?' · '+Math.max(1,Math.round(c.units/Math.min(c.lot,c.units)))+' annonce(s) de '+NF.format(Math.min(c.lot,c.units)):''}</span><b class="pos">${kf(c.k)}</b></div>`).join('')+'</div>').join('')+'</div>'
  +(Object.keys(R).length?'':'<p class="sub">Récolte par heure : 100 par défaut pour chaque ressource ; indique tes vraies valeurs dans « 🌲 Récolte ».</p>')}
// ---------------- Opportunites : recolte, achat -> craft et flip, une annonce chacune (OPPDATA)
// Glouton par kinah/annonce/j, dans la limite des annonces libres, des kinah disponibles et du temps de recolte.
// Un meme objet n'est retenu qu'une fois (meme marche, meme part des ventes).
const OTYPE={r:['🌲','Récolte'],c:['🛒','Achat → craft'],f:['🔁','Flip']};
const delai=c=>c.dh>0?'~'+fmtH(1/c.dh)+' devant<div class="sub">~'+fmtH(c.nl/c.dh)+' à la file</div>':'–';
function lotSet(inp){const L=pget('lots',{}),v=Math.round(+inp.value);if(v>=1)L[inp.dataset.i]=v;else delete L[inp.dataset.i];pset('lots',L);oppRender()}
function oppRender(save){const box=document.getElementById('obox');if(!box||!window.OPPDATA)return;
 const bEl=document.getElementById('obudget'),hEl=document.getElementById('ohours');
 if(save){pset('obudget',bEl.value===''?null:+bEl.value);pset('ohours',+hEl.value)}
 else{const b=pget('obudget',null);bEl.value=b==null?'':b;hEl.value=pget('ohours',3)}
 const open=J?J.lots.filter(l=>!l.del&&jState(l).reste>0).length:0;
 let slots=Math.max(0,OPPDATA.slots-open),budget=bEl.value===''?Infinity:+bEl.value,hours=+hEl.value||0;
 document.getElementById('oslots').textContent=slots+' / '+OPPDATA.slots;
 const R=rates(),st=lvState(),LOTS=pget('lots',{});
 const cands=OPPDATA.rows.map(r0=>{const lot=LOTS[r0.i]||r0.lot,r={...r0,lot:lot,q:Math.round(r0.ql*lot)};if(r.q<1)return null;let n=r.n,p=1;
  if(r.t!=='f'){const info=craftInfo(r.i);if(info&&!info.ok)return null;p=info&&info.rate?info.rate:1}
  if(r.t==='c'&&st.lose)n=r.n+r.k-r.k/p;            // echecs : les ingredients achetes sont perdus
  let resH=0;if(r.t==='r')for(const[res,per]of Object.entries(r.res)){const rate=R[res]!=null?R[res]:100;if(!rate)return null;
   resH+=per/rate/(st.lose?p:1)}
  return n>0?{...r,n:n,resH:resH,day:r.q*n,own:LOTS[r0.i]!=null}:null}).filter(Boolean).sort((a,b)=>b.day-a.day);
 const picks=[],taken=new Set(),rest=[];let tot=0,cap=0,used=0;
 for(const c of cands){if(taken.has(c.i))continue;
  let u=c.q;if(c.k>0&&budget<Infinity)u=Math.min(u,Math.floor(budget/c.k));if(c.resH>0)u=Math.min(u,Math.floor(hours/c.resH));
  if(!slots||u<1){rest.push(c);continue}
  budget-=u*c.k;hours-=u*c.resH;slots--;taken.add(c.i);tot+=u*c.n;cap+=u*c.k;used+=u*c.resH;picks.push({...c,u:u})}
 const what=c=>c.t==='r'?(c.b?'récolter, vendre brut':'récolter '+Object.keys(c.res).map(escH).join(' + ')+' → fabriquer')
  :c.t==='c'?'<span title="'+escH((c.ing||[]).join(' ; '))+'">acheter les ingrédients → fabriquer</span>'
  :'acheter à ≤ <b>'+NF.format(c.k)+'</b>, revendre à '+NF.format(c.p)+(c.now?' <span class="badge b-ok">achetable maintenant</span>':'');
 const feu=c=>c.f?'<span class="badge '+({vert:'b-ok',orange:'b-warn',rouge:'b-bad'}[c.f])+'">'+({vert:'🟢',orange:'🟠',rouge:'🔴'}[c.f])+' '+c.s+'</span>':'';
 const row=(c,k,u)=>'<tr><td class="n">'+k+'</td><td>'+OTYPE[c.t][0]+' '+OTYPE[c.t][1]+'</td><td><b class="nm" title="Cliquer pour copier">'+escH(c.o)+'</b><div class="sub">'+what(c)+'</div></td>'
  +'<td class="n">'+NF.format(u)+'</td><td class="n"><input type="number" min="1" value="'+c.lot+'" data-i="'+c.i+'" title="Unités par annonce'+(c.own?' (ta valeur)':' (estimée par type d’objet)')+'" '
  +'style="width:64px;padding:3px 6px;border:1px solid '+(c.own?'var(--acc)':'var(--line)')+';border-radius:6px;background:var(--bg2);color:var(--txt);font:inherit;text-align:right" onchange="lotSet(this)"></td>'
  +'<td class="n">'+(c.k?kf(u*c.k):'–')+'</td><td class="n">'+(c.resH?fmtH(u*c.resH):'–')+'</td>'
  +'<td class="n">'+delai(c)+'</td><td class="n big pos">'+kf(u*c.n)+'</td><td>'+feu(c)+'</td></tr>';
 const head='<thead><tr><th class="n">#</th><th>Type</th><th>Quoi faire</th><th class="n">Ventes/j</th><th class="n">Lot</th><th class="n">Capital</th><th class="n">Récolte</th><th class="n" title="Devant : tu postes au prix le plus bas. À la file : les annonces déjà en vente partent avant la tienne">Délai de vente</th><th class="n">Kinah / annonce / j</th><th>Sûreté</th></tr></thead>';
 box.innerHTML='<div class="kpis"><div class="kpi"><div class="l">Gain du jour</div><div class="v pos">'+kf(tot)+'</div><div class="s">'+picks.length+' annonce(s), une fois tout vendu</div></div>'
  +'<div class="kpi"><div class="l">Capital engagé</div><div class="v">'+kf(cap)+'</div><div class="s">'+(budget===Infinity?'budget non limité':'reste '+kf(budget))+'</div></div>'
  +'<div class="kpi"><div class="l">Temps de récolte</div><div class="v">'+fmtH(used)+'</div><div class="s">récolte/heure de 🌲 Récolte (100 par défaut)</div></div></div>'
  +(picks.length?'<div class="wrap"><table>'+head+'<tbody>'+picks.map((c,k)=>row(c,k+1,c.u)).join('')+'</tbody></table></div>'
   :'<p class="mut">'+(slots?'Aucune opportunité ne tient dans ton budget et ton temps de récolte.':'Plus d’annonce libre : tes annonces en cours occupent toutes les places.')+'</p>')
  +(rest.length?'<details style="margin-top:10px"><summary class="mut" style="cursor:pointer">Opportunités suivantes ('+Math.min(rest.length,15)+')</summary><div class="wrap"><table>'+head+'<tbody>'
   +rest.slice(0,15).map((c,k)=>row(c,picks.length+k+1,c.q)).join('')+'</tbody></table></div></details>':'')
 // accueil : 5 premieres et indicateurs
 const g=id=>document.getElementById(id);
 if(g('kopp')){g('kopp').textContent=kf(tot);g('kopps').textContent=picks.length+' annonce(s), '+(cap?kf(cap)+' de capital':'sans capital')}
 if(g('kslots'))g('kslots').textContent=document.getElementById('oslots').textContent;
 if(g('hopps'))g('hopps').innerHTML=picks.length?'<div class="wrap"><table>'+head+'<tbody>'+picks.slice(0,5).map((c,k)=>row(c,k+1,c.u)).join('')+'</tbody></table></div>'
  :'<p class="mut">Aucune opportunité avec tes annonces libres, ton budget et ton temps de récolte.</p>'}
// ---------------- Mes procs de recolte (PROCS : ressource blanche -> [[grade, proc, valeur nette]]), gardes dans ce navigateur
function procAdd(){const g=id=>document.getElementById(id),r=g('pres').value,n=+g('pn').value||0;if(!r||n<=0){toast('Indique le nombre de blancs récoltés');return}
 const P=pget('procs',{}),x=P[r]||{n:0,g1:0,g2:0,g3:0};x.n+=n;['g1','g2','g3'].forEach(k=>{x[k]+=+g('p'+k).value||0;g('p'+k).value=''});g('pn').value='';
 P[r]=x;pset('procs',P);procRender()}
function procReset(r){const P=pget('procs',{});delete P[r];pset('procs',P);procRender()}
function procRender(){const box=document.getElementById('pbox');if(!box||!window.PROCS)return;const P=pget('procs',{}),R=rates();
 const rows=Object.entries(P).filter(([r])=>PROCS[r]).map(([r,x])=>{const pc=k=>x.n?x['g'+k]/x.n:0;
  const bonus=PROCS[r].reduce((a,[g,,v])=>a+pc(g)*v,0),rate=R[r]!=null?R[r]:100;
  return '<tr><td><b>'+escH(r)+'</b></td><td class="n">'+NF.format(x.n)+'</td>'+[1,2,3].map(k=>{const p=PROCS[r].find(q=>q[0]===k);
   return '<td class="n">'+(p?(pc(k)*100).toFixed(2).replace('.',',')+' %<div class="sub">'+NF.format(x['g'+k])+' · '+kf(p[2])+'/u</div>':'–')+'</td>'}).join('')
   +'<td class="n pos">+'+kf(bonus)+'</td><td class="n big pos">+'+kf(bonus*rate)+'</td>'
   +'<td>'+(x.n<500?'<span class="badge b-warn">peu de mesures</span> ':'')+'<button class="mapbtn" onclick="procReset(\''+escH(r).replace(/'/g,"\\'")+'\')">effacer</button></td></tr>'});
 box.innerHTML=rows.length?'<div class="wrap"><table><thead><tr><th>Ressource</th><th class="n">Blancs récoltés</th><th class="n">🟢 Vert</th><th class="n">🔵 Bleu</th><th class="n">🟠 Éclatant</th>'
  +'<th class="n" title="Taux de proc × meilleur net de chaque proc">Bonus / ressource</th><th class="n" title="Bonus par ressource × ta récolte par heure">Bonus / heure</th><th></th></tr></thead><tbody>'+rows.join('')+'</tbody></table></div>'
  :'<p class="mut">Pas encore de session notée.</p>'}
document.addEventListener('DOMContentLoaded',()=>procRender());
function segShow(btn,id){const seg=btn.parentNode;seg.querySelectorAll('button').forEach(b=>b.classList.toggle('on',b===btn));
 const sec=seg.closest('section');sec.querySelectorAll('.segp').forEach(p=>p.style.display=p.id===id?'':'none')}
function resCrafts(name,tid){const tb=document.getElementById(tid),inp=tb&&tb.closest('.segp').querySelector('.toolbar input.search[oninput*="'+tid+'"]');
 if(!inp)return;inp.value=name;filt(inp,tid);inp.scrollIntoView({block:'center'})}
function clearStock(){document.querySelectorAll('#stock input[data-r]').forEach(i=>i.value='');calc()}
document.addEventListener('DOMContentLoaded',()=>{let t='chat';try{t=localStorage.getItem('tab')||t;
 if(localStorage.getItem('detail')){document.body.classList.add('detail');document.querySelectorAll('input.dt').forEach(x=>x.checked=true)}}catch(e){}
 if(!document.getElementById(t))t='home';show(t);
 try{const s=JSON.parse(localStorage.getItem('stock')||'null');if(s)document.querySelectorAll('#stock input[data-r]').forEach(i=>i.value=s[i.dataset.r]||'')}catch(e){}
 importLevelsFromHash();applyLevels();jInit();rateCalc();planSafe();oppRender();document.querySelectorAll('th').forEach(th=>th.onclick=()=>sortT(th))});

// ======================================================================== ravitaillement
// Objets lus sur la capture (icone de chaque objet), gardes dans ce navigateur ; prix du dernier passage (SUPPLY) :
// un tableau trie par gain a crafter puis revendre, detail repliable, bouton Poster vers Mes ventes.
function supplyLoad(){try{return JSON.parse(localStorage.getItem('supply')||'null')}catch(e){return null}}
async function supplyScan(file){if(!file||!(file.type||'').startsWith('image/'))return;const msg=document.getElementById('smsg');
 msg.textContent='Lecture de la capture…';
 try{await scanLoad();const url=URL.createObjectURL(file);
  const img=await new Promise((ok,ko)=>{const i=new Image();i.onload=()=>ok(i);i.onerror=()=>ko('image illisible');i.src=url});
  const cards=await scanSupply(img,{progress:m=>msg.textContent=m});URL.revokeObjectURL(url);
  if(!cards.length){msg.textContent='Aucun objet reconnu : capture la fenêtre de ravitaillement (cartes avec les objets demandés).';return}
  try{localStorage.setItem('supply',JSON.stringify({t:jNow(),cards:cards.map(c=>({items:c.items.map(i=>i.s)}))}))}catch(e){}
  msg.textContent=cards.length+' case(s), '+cards.reduce((a,c)=>a+c.items.length,0)+' objet(s) reconnu(s).';supplyRender()}
 catch(e){msg.textContent='Lecture impossible : '+e+' (la lecture fonctionne sur le site en ligne)'}}
let SOPEN=new Set();
function supplyRender(){const box=document.getElementById('sbox');if(!box)return;const d=supplyLoad();if(!d){box.innerHTML='';return}
 const byIcon={},seen=new Set();(window.SUPPLY||[]).forEach(x=>(byIcon[x.s]=byIcon[x.s]||[]).push(x));
 const n=v=>v==null?'–':NF.format(Math.round(v)),K={hdv:'HDV',od:'Od transmuté',pnj:'PNJ (prix estimé)',craft:'à fabriquer',recolte:'récolte',introuvable:'introuvable'};
 const part=(p,ind)=>'<tr><td style="padding-left:'+(10+ind*18)+'px">'+jEsc(p.n)+(p.via?'<div class="sub">→ transmuté en '+jEsc(p.via)+'</div>':'')+'</td>'
  +'<td class="n">'+NF.format(p.q)+'</td><td class="n">'+(p.p==null?'<span class="neg">introuvable</span>':n(p.p))+(sHigh(p.p,p.md)!=null?' <span title="Au-dessus de ses médianes : 3 j '+n(p.md[0])+', 7 j '+n(p.md[1])+'">⚠</span>':'')+'</td>'
  +'<td class="n">'+(p.p==null?'–':n(p.p*p.q))+'</td><td class="sub">'+(K[p.k]||'')+(p.l!=null?' · '+p.l+' annonce(s)':'')+'</td></tr>'
  +(p.sub||[]).map(x=>part(x,ind+1)).join('');
 let pos=false;try{pos=!!localStorage.getItem('supplyPos')}catch(e){}
 const rows=d.cards.flatMap(c=>c.items.flatMap(s=>byIcon[s]||[])).filter(x=>!seen.has(x.i)&&seen.add(x.i)).map(x=>[x,sEval(x)])
  .sort((a,b)=>(!!a[1].rt.lock-!!b[1].rt.lock)||(b[1].gain??-Infinity)-(a[1].gain??-Infinity));
 const shown=rows.filter(([x,e])=>!pos||e.gain>0&&!e.rt.lock);
 box.innerHTML='<div class="toolbar" style="margin:10px 0"><span class="sub">Capture lue le '+d.t.slice(8,10)+'/'+d.t.slice(5,7)+' à '+d.t.slice(11)+' · '+rows.length+' objet(s)</span>'
  +'<label class="tg"><input type="checkbox"'+(pos?' checked':'')+' onchange="try{localStorage.setItem(\'supplyPos\',this.checked?\'1\':\'\')}catch(e){}supplyRender()"> Rentables seulement</label></div>'
  +'<div class="wrap"><table><thead><tr><th>Objet</th><th class="n">Vente /u</th><th class="n" title="Par craft ; pour un objet éclatant, par objet obtenu (plusieurs crafts)">Coût</th><th class="n" title="Objet normal, sans compter le combo">Gain / craft</th><th class="n">Réussite</th><th class="n">Annonces</th><th></th></tr></thead><tbody>'
  +(shown.length?shown.map(([x,e])=>{const b=e.best,g=e.gain,up=x.ask!=null&&x.med?x.ask/x.med-1:null,w=sWarns(x,e);
   const wt=w.map(o=>o.n+' : '+n(o.v)+' (+'+Math.round(o.u*100)+' % ; médiane 3 j '+n(o.md[0])+', 7 j '+n(o.md[1])+')').join('\n');
   const v=e.rt.lock?['🔒','niveau de métier trop bas pour ce craft']:g==null?['❔','prix manquant']
    :g<=0&&e.avg>0?['🎲','à perte avec l’objet normal ; rentable en moyenne seulement grâce au combo ('+Math.round(e.c*100)+' %) : un pari']
    :g>0&&w.length?['⚠','rentable, mais prix au-dessus des médianes 3 j et 7 j de plus de '+Math.round(SUPPLY_CFG.warn*100)+' % :\n'+wt]
    :g>0&&x.l<=2?['⚠','rentable, mais '+x.l+' annonce(s) seulement : prix de vente incertain']:g>0?['✅','rentable']:['❌','à perte'];
   const row='<tr'+(e.rt.lock?' class="locked"':'')+'><td><span class="it"><span title="'+jEsc(v[1])+'">'+v[0]+'</span> <img src="'+jEsc(x.s)+'" width="30" height="30" style="border-radius:5px" loading="lazy"><span><span class="nm" title="Cliquer pour copier">'+jEsc(x.n)+'</span>'
    +'<div class="sub">'+(e.via?'<b>éclatant</b> · combo '+Math.round(e.c*100)+' % de '+jEsc(e.R.n)+' · ':'')+(PROF[x.prof]||x.prof)+' '+lvTxt(Math.max(1,x.m))+(e.cb?' · combo '+Math.round(e.c*100)+' %':'')+'</div></span></span></td>'
    +'<td class="n"><input type="number" min="0" class="search" style="width:115px;display:inline-block;padding:4px 7px;text-align:right" value="'+(e.sell??'')+'" onchange="supplySell('+x.i+',this.value)">'
    +'<div class="sub">'+(e.ov!=null?'saisi · ':e.capped?'<span title="annonce la plus basse anormalement haute : prix réaliste proposé">plafonné · </span>':'')+'min '+n(x.ask)+' · méd. 3 j '+n(x.med)+(up!=null&&up>=0.15?' <span class="badge b-ok">↑ +'+Math.round(up*100)+' %</span>':'')+'</div></td>'
    +'<td class="n">'+(b?n(b.per)+(e.via?'<div class="sub">≈ '+(1/e.c/(lvState().lose?e.rt.r:1)).toFixed(1).replace('.',',')+' crafts / objet</div>':'')+(e.cols.length>1?' <span class="badge b-mut" title="'+(b.k==='A'?'ingrédient éclatant crafté par sa chaîne':'ingrédient éclatant acheté à l’HDV')+'">'+b.k+'</span>':''):'<span class="neg">incomplet</span>')+'</td>'
    +'<td class="n '+(g==null?'':g>0?'pos':'neg')+'"><b>'+(g==null?'–':(g>0?'+':'')+n(g))+'</b>'
    +(e.cb&&e.avg!=null&&!e.vUnk?'<div class="sub" title="Moyenne sur beaucoup de crafts, combo ('+Math.round(e.c*100)+' %) revendu '+n(e.cb.v)+'">moy. avec combo '+(e.avg>0?'+':'')+n(e.avg)+'</div>':'')+(e.vUnk?'<div class="sub" title="'+jEsc(e.cb.n)+' : aucun prix connu, le combo est compté 0">combo sans prix : compté 0</div>':'')
    +(w.length?'<div><span class="badge b-warn" title="'+jEsc('Prix au-dessus des médianes 3 j et 7 j de plus de '+Math.round(SUPPLY_CFG.warn*100)+' % :\n'+wt)+'">⚠ prix > médiane</span></div>':'')+'</td>'
    +'<td class="n">'+(e.rt.lock?'🔒':e.rt.u?'?':(e.rt.r*100).toFixed(0)+' %')+'</td><td class="n">'+x.l+'</td>'
    +'<td style="white-space:nowrap"><button class="mapbtn" onclick="supplyToggle('+x.i+')">'+(SOPEN.has(x.i)?'▾':'▸')+' détail</button> '
    +'<button class="mapbtn" title="Ouvrir Mes ventes avec cet objet, ce prix et ce coût" onclick="supplyPost('+x.i+')">📦 Poster</button></td></tr>';
   if(!SOPEN.has(x.i))return row;
   return row+'<tr><td colspan="7" style="background:var(--card2)"><div class="wrap"><table><thead><tr><th>Ingrédient</th><th class="n">Qté</th><th class="n">Prix /u</th><th class="n">Sous-total</th><th>Origine</th></tr></thead><tbody>'
    +e.R.parts.map(p=>part(p,0)).join('')+'</tbody></table></div>'+supplyCalc(x,e,part)+'</td></tr>'}).join('')
   :'<tr><td colspan="7" class="mut">'+(rows.length?'Aucun objet rentable avec ces prix.':'Aucun objet reconnu.')+'</td></tr>')
  +'</tbody></table></div>'}
function supplyToggle(id){SOPEN.has(id)?SOPEN.delete(id):SOPEN.add(id);supplyRender()}
// 📦 Poster : formulaire de Mes ventes prerempli (objet, prix de vente, cout du craft le moins cher, origine Ravitaillement)
function supplyPost(id){const x=(window.SUPPLY||[]).find(y=>y.i===id);if(!x)return;const e=sEval(x),g=k=>document.getElementById(k);
 show('gains');if(!g('jo'))return;g('jo').value=x.n;g('js').value='ravit';g('jp').value=e.sell??'';g('jc').value=e.best?Math.round(e.best.per):'';
 g('jq').value='';g('jo').scrollIntoView({block:'center'});g('jq').focus();toast('Indique la quantité puis ajoute l’annonce')}
document.addEventListener('DOMContentLoaded',()=>supplyRender());
// Craft avec combo : un ingredient « eclatant » se crafte par sa chaine (A, toute la chaine, objets normaux revendus)
// ou s'achete a l'HDV (B) ; reussite selon mes niveaux (🛠️ Mes metiers) ; resultat = objet normal (prix de vente
// modifiable, par defaut la moins chere des annonces - 1) ou, en combo, la version eclatante.
const SNET=v=>v==null?null:v*(1-SUPPLY_CFG.tax);
// prix au-dessus de ses medianes 3 j et 7 j (md) de plus de SUPPLY_CFG.warn (config : alerts.price_vs_median) : ecart a
// la plus haute des deux (un prix qui monte depuis quelques jours n'est pas signale), sinon null
function sHigh(v,md){const r=v==null||!md?[]:md.filter(m=>m>0).map(m=>v/m-1);const u=r.length?Math.min(...r):null;
 return u!=null&&u>SUPPLY_CFG.warn?u:null}
// prix douteux d'une proposition : vente, ingredients (chaine ou achat, selon l'option retenue), reventes, combo ;
// un prix saisi a la main n'est pas signale
function sWarns(x,e){const out=[],seen=new Set(),ov=supplySellGet();
 const chk=(n,v,md)=>{const u=sHigh(v,md);if(u!=null&&!seen.has(n)){seen.add(n);out.push({n,v,md,u})}};
 const parts=ps=>(ps||[]).forEach(p=>{chk(p.n,p.p,p.md);parts(p.sub)});
 const chain=ch=>{parts(ch.parts);if(ov[ch.i]==null)chk(ch.n+' (revente)',ch.plain,ch.pmd);ch.need.forEach(y=>chain(y.chain))};
 const R=e.R,k=e.best&&e.best.k;
 if(e.ov==null)chk(x.n+' (vente)',e.sell,x.md);
 parts(R.parts);R.need.forEach(y=>{if(k!=='B')chain(y.chain);if(k!=='A')chk(y.n,y.buy,y.md)});
 if(e.via&&ov[R.i]==null)chk(R.n+' (revente)',R.plain,R.pmd);
 if(e.cb)chk(e.cb.n+' (combo)',e.cb.v,e.cb.md);
 return out}
function supplySellGet(){try{return JSON.parse(localStorage.getItem('supplySell')||'{}')}catch(e){return{}}}
function supplySell(id,v){const o=supplySellGet();if(v===''||!(+v>=0))delete o[id];else o[id]=+v;
 try{localStorage.setItem('supplySell',JSON.stringify(o))}catch(e){}supplyRender()}
// taux de reussite d'une recette selon mes niveaux : r = 1 si niveau non renseigne (u) ; lock = niveau trop bas
function sRate(p,m,cv){const lv=lvState().lv[p];if(lv==null||lv==='')return{r:1,u:true};if(lv<m)return{r:1,lock:true};
 const c=cv!=null&&window.CRAFTDATA&&CRAFTDATA.curves[cv];return{r:c?c[Math.min(lv-m,c.length-1)]/1e8:1}}
// cout par craft reussi : echecs compris si les materiaux sont perdus (option de Mes metiers)
const sPer=(K,rt)=>lvState().lose?K/rt.r:K;
// cout d'un objet eclatant obtenu par sa chaine : K = ingredients (+ eclatants de l'etape d'avant, crafts eux aussi)
function chainCost(ch){let K=ch.k;if(K==null)return null;
 for(const x of ch.need){const e=chainCost(x.chain);if(e==null)return null;K+=x.q*e.e}
 const rt=sRate(ch.prof,ch.m,ch.cv),S=sPer(K,rt),pn=SNET(supplySellGet()[ch.i]??ch.plain)||0;
 return{K,S,rt,e:(S-(1-ch.c)*pn)/ch.c,pn}}
function chainHtml(x,part,ind){const ch=x.chain,cc=chainCost(ch),n=v=>v==null?'–':NF.format(Math.round(v)),pad=10+ind*18;
 const row=(t,v,b)=>'<tr><td colspan="3" style="padding-left:'+pad+'px">'+t+'</td><td class="n">'+(b?'<b>'+n(v)+'</b>':n(v))+'</td><td></td></tr>';
 const rt=cc?cc.rt:sRate(ch.prof,ch.m,ch.cv);
 return '<tr><td colspan="5" style="padding-left:'+pad+'px"><b>'+jEsc(ch.n)+'</b> <span class="sub">· '+(PROF[ch.prof]||ch.prof)+' '+lvTxt(Math.max(1,ch.m))
  +(rt.lock?' · 🔒 niveau trop bas':rt.u?' · réussite ? (niveau non renseigné)':' · réussite '+(rt.r*100).toFixed(1).replace('.',',')+' %')
  +' · combo '+Math.round(ch.c*100)+' % → '+jEsc(x.n)+'</span></td></tr>'
  +ch.parts.map(p=>part(p,ind+1)).join('')
  +ch.need.map(y=>'<tr><td colspan="5" style="padding-left:'+(pad+18)+'px" class="sub">'+NF.format(y.q)+' × '+jEsc(y.n)+' (crafté par sa chaîne) :</td></tr>'+chainHtml(y,part,ind+2)).join('')
  +(cc?row('1 craft'+(cc.S!==cc.K?' <span class="sub">(échecs compris : '+n(cc.K)+' ÷ '+(cc.rt.r*100).toFixed(1).replace('.',',')+' %)</span>':''),cc.S)
   +row('combo '+Math.round(ch.c*100)+' % → '+(1/ch.c).toFixed(1).replace('.',',').replace(',0','')+' crafts réussis en moyenne',cc.S/ch.c)
   +row('− '+((1-ch.c)/ch.c).toFixed(1).replace('.',',').replace(',0','')+' '+jEsc(ch.n)+' revendu(s) ('+n(cc.pn)+' net)',-(1-ch.c)/ch.c*cc.pn)
   +row('= coût d’un '+jEsc(x.n),cc.e,true)
   :row('<span class="neg">chaîne incomplète (prix manquant)</span>',null))}
// Deux facons d'obtenir l'objet demande (x) :
// - objet normal : sa recette, quand le craft ne fait pas combo ; le combo (version eclatante revendue) est un bonus,
//   montre a part (gain moyen = pari) ;
// - objet eclatant (x.via = recette de l'objet de base) : seulement par le combo de cette recette ; cout d'un objet =
//   crafts reussis pour obtenir un combo (1 / chance) - objets de base obtenus entre-temps, revendus.
// Ingredient eclatant d'une recette : crafte par sa chaine (A) ou achete (B), la moins chere retenue ; echecs selon mes
// niveaux. Vente proposee : annonce la plus basse - 1, sans depasser le prix realiste ; combo sans prix compte 0.
function sEval(x){const R=x.via||x,via=!!x.via,cb=via?null:R.combo,c=via?R.combo.c:cb?cb.c:0,V=cb?SNET(cb.v)||0:0,ov=supplySellGet()[x.i];
 const sug=x.ask!=null?Math.max(1,Math.min(x.ask-1,x.real??Infinity)):x.real??x.sell,sell=ov!=null?ov:sug,P=SNET(sell),rt=sRate(R.prof,R.m,R.cv),q=R.q||1;
 const B=via?SNET(supplySellGet()[R.i]??R.plain)||0:null;
 const sum=f=>{let K=R.rest;for(const y of R.need){const v=f(y);if(v==null||K==null)return null;K+=y.q*v}return K/q};
 const cols=R.need.length?[{k:'A',t:'A. je crafte',K:sum(y=>{const e=chainCost(y.chain);return e&&e.e})},{k:'B',t:'B. j’achète',K:sum(y=>y.buy)}]
  :[{k:'',t:'Craft',K:R.c}];
 cols.forEach(o=>{if(o.K==null)return;o.S=sPer(o.K,rt);
  if(via){o.per=c>0?o.S/c-(1-c)/c*B:null;o.plain=o.gain=P==null||o.per==null?null:P-o.per;return}
  o.per=o.S;o.res=P==null?null:(1-c)*P+c*V;o.gain=o.res==null?null:o.res-o.S;o.plain=P==null?null:P-o.S});
 // gain retenu = objet demande ; pour un objet normal, le gain moyen avec combo est un pari, affiche a part
 const best=cols.filter(o=>o.per!=null).sort((a,b)=>a.per-b.per)[0]||null,gain=best&&best.plain,avg=via?null:best&&best.gain;
 return{R,via,B,cols,best,gain,avg,cb,c,V,sell,ov,P,rt,capped:x.ask!=null&&x.real!=null&&x.real<x.ask-1,
  vUnk:!!cb&&cb.v==null}}
function supplyCalc(x,e,part){const n=v=>v==null?'–':NF.format(Math.round(v)),{R,via,cols,cb,c,V,rt}=e;
 const tr=(t,f,cls)=>'<tr><td>'+t+'</td>'+cols.map(o=>{const v=o.K==null?null:f(o);return '<td class="n '+(cls?cls(v):'')+'">'+n(v)+'</td>'}).join('')+'</tr>';
 const pn=v=>v==null?'':v>0?'pos':'neg',k1=v=>v.toFixed(1).replace('.',',').replace(',0','');
 let h='<div class="wrap" style="margin-top:10px"><table>';
 if(R.need.length){
  h+='<thead><tr><th>Ingrédient à crafter ou acheter</th><th class="n">Qté</th><th class="n">Prix /u</th><th class="n">Sous-total</th><th>Origine</th></tr></thead><tbody>';
  R.need.forEach(y=>{const ce=chainCost(y.chain);
   h+='<tr><td colspan="5"><b>'+NF.format(y.q)+' × '+jEsc(y.n)+'</b></td></tr>'
    +'<tr><td colspan="5" class="sub" style="padding-left:10px">A. Je le crafte (toute la chaîne) :</td></tr>'+chainHtml(y,part,1)
    +'<tr><td colspan="5" class="sub" style="padding-left:10px">B. Je l’achète à l’HDV : <b>'+n(y.buy)+'</b> (prix d’achat réaliste) · médiane 3 j '+n(y.med)+' · '+y.l+' annonce(s)'
    +(ce&&y.buy!=null?' → '+(ce.e<y.buy?'<span class="pos">le craft revient moins cher de '+n(y.buy-ce.e)+'</span>':'<span class="neg">l’achat revient moins cher de '+n(ce.e-y.buy)+'</span>'):'')+'</td></tr>'});
  h+='<tr><td><b>Autres ingrédients</b> <span class="sub">(communs aux deux options, détail ci-dessus)</span></td><td></td><td></td><td class="n">'+n(R.rest)+'</td><td></td></tr></tbody></table><table style="margin-top:8px">'}
 const rtx=rt.lock?'🔒 niveau trop bas':rt.u?'réussite ? (niveau non renseigné)':'réussite '+(rt.r*100).toFixed(1).replace('.',',')+' %';
 const cost=tr('Coût d’un craft'+(via?' de '+jEsc(R.n):'')+(lvState().lose&&rt.r<1?' <span class="sub">(échecs compris)</span>':'')+((R.q||1)>1?' <span class="sub">(par objet, la recette en donne '+R.q+')</span>':''),o=>o.S);
 if(via)h+='<thead><tr><th>'+jEsc(x.n)+' <span class="sub">· obtenu seulement par combo ('+Math.round(c*100)+' %) en craftant '+jEsc(R.n)+' · '+rtx+'</span></th>'
  +cols.map(o=>'<th class="n">'+o.t+'</th>').join('')+'</tr></thead><tbody>'+cost
  +tr('combo '+Math.round(c*100)+' % → '+k1(1/c)+' crafts réussis en moyenne',o=>o.S/c)
  +tr('− '+k1((1-c)/c)+' '+jEsc(R.n)+' obtenu(s) sans combo, revendu(s) <span class="sub">('+n(e.B)+' net ; prix modifiable sur sa ligne s’il est dans la capture)</span>',o=>-(1-c)/c*e.B)
  +tr('<b>= coût d’un '+jEsc(x.n)+'</b>',o=>o.per)
  +tr('Vente après taxe et frais',()=>e.P)
  +tr('<b>Gain par objet</b>',o=>o.plain,pn);
 else h+='<thead><tr><th>'+jEsc(x.n)+' <span class="sub">· '+rtx+(cb?' · combo '+Math.round(c*100)+' % → '+jEsc(cb.n):'')+'</span></th>'
  +cols.map(o=>'<th class="n">'+o.t+'</th>').join('')+'</tr></thead><tbody>'+cost
  +tr('Vente de l’objet normal après taxe et frais',()=>e.P)
  +tr('<b>Gain par craft</b> <span class="sub">(objet normal, sans combo)</span>',o=>o.plain,pn)
  +(cb?tr('Résultat moyen avec combo <span class="sub">('+Math.round((1-c)*100)+' % objet normal, '+Math.round(c*100)+' % '+jEsc(cb.n)+' à '+n(cb.v)+' → '+n(V)+' net)</span>',o=>o.res)
   +tr('Gain moyen avec combo <span class="sub">(sur beaucoup de crafts : un pari)</span>',o=>o.gain,pn):'');
 return h+'</tbody></table></div>'}
// ---------------------------------------------------------------- fraicheur : prix relevés il y a plus de 3 h, ou page plus regeneree depuis 2 h
function staleCheck(){const el=document.getElementById('stale');if(!el)return;
 const age=v=>v?(Date.now()-new Date(/[zZ]|[+-]\d\d:\d\d$/.test(v)?v:v+'Z'))/36e5:null,p=age(el.dataset.asof),g=age(el.dataset.gen),m=[];
 if(p==null||p>=3)m.push(p==null?'aucun prix relevé':'prix relevés il y a '+Math.floor(p)+' h');
 if(g!=null&&g>=2)m.push('page générée il y a '+Math.floor(g)+' h (les passages horaires ne tournent plus ?)');
 el.hidden=!m.length;if(m.length)el.textContent='⚠ Données périmées : '+m.join(' ; ')+'. Les chiffres ci-dessous peuvent être faux.'}
document.addEventListener('DOMContentLoaded',()=>{staleCheck();setInterval(staleCheck,6e5)});
// ======================================================================== assistant
// Chat Claude, appelé depuis le navigateur (API Anthropic) : recherche web et lecture de pages côté Anthropic, plus l'outil
// tracker_search sur le catalogue du tracker (assist.js : objets, prix du serveur, recettes, récolte, chargé à l'ouverture).
// La clé API reste dans ce navigateur. La conversation (blocs bruts de l'API, renvoyés tels quels) aussi.
const AIMODEL='claude-opus-5-5',AIPRICE={in:4,out:20,cw:5,cr:.2,search:.01};   // $ par million de jetons, $ par recherche
let AIH=[],AIBUSY=null,AIX=null;
function aiKey(){try{return localStorage.getItem('aikey')||''}catch(e){return ''}}
function aiSave(){try{localStorage.setItem('aichat',JSON.stringify(AIH))}catch(e){try{localStorage.removeItem('aichat')}catch(e2){}}}
function aiCostGet(){try{return +localStorage.getItem('aicost')||0}catch(e){return 0}}
function aiCostAdd(u){if(!u)return;const s=u.server_tool_use||{},c=((u.input_tokens||0)*AIPRICE.in+(u.output_tokens||0)*AIPRICE.out
 +(u.cache_creation_input_tokens||0)*AIPRICE.cw+(u.cache_read_input_tokens||0)*AIPRICE.cr)/1e6+(s.web_search_requests||0)*AIPRICE.search;
 try{localStorage.setItem('aicost',String(aiCostGet()+c))}catch(e){}aiCostShow()}
function aiCostShow(){const el=document.getElementById('aicost');if(el)el.textContent=aiCostGet()?'≈ '+aiCostGet().toFixed(2).replace('.',',')+' $ dépensés depuis ce navigateur':''}
function aiLoad(){const v=(document.getElementById('ai')||{dataset:{}}).dataset.v||'';
 return window.ASSIST?Promise.resolve():new Promise(ok=>{const sc=document.createElement('script');sc.src='assist.js?v='+v;sc.onload=ok;sc.onerror=ok;document.head.appendChild(sc)})}
function aiInit(){const box=document.getElementById('aimsgs');if(!box)return;if(aiRenderAll.hello==null)aiRenderAll.hello=box.innerHTML;aiLoad().then(()=>{if(AIH.length)aiRenderAll();else aiHome()});aiCostShow();
 if(!AIH.length){try{AIH=JSON.parse(localStorage.getItem('aichat')||'[]')}catch(e){AIH=[]}if(AIH.length)aiRenderAll()}
 aiServerProbe().then(()=>aiMode()==='local'?aiLocalProbe():0).then(()=>{aiModeShow();if(!aiReady())aiKeyForm();else setTimeout(()=>document.getElementById('aiin').focus(),0)})}
function aiKeyForm(on){const box=document.getElementById('aikey');if(on===false){box.hidden=true;return}box.hidden=false;const m=aiMode(),
  sec=(id,title,sub,body)=>'<div class="aiopt'+(m===id?' on':'')+'"><b>'+title+'</b>'+(m===id?' <span class="badge b-ok">utilisé</span>':'')
   +'<div class="sub">'+sub+'</div>'+body+'</div>';
 box.innerHTML='<div class="aiopts">'
  +(AISERVER?sec('server','Serveur AION Helper','Ce site tourne sur ton serveur : les réponses passent par Claude Code avec ton abonnement Claude. '
   +'Rien à régler.',''):'')
  +sec('local','Claude Code sur ce PC','Ton abonnement Claude, réponse en direct, seulement quand <code>py scripts\\assistant_local.py</code> tourne sur ce PC '
   +'(Chrome demande une fois l’accès au réseau local : accepter).','<button onclick="aiLocalUse()">Utiliser</button>')
  +sec('api','Clé API Anthropic','Payée à l’usage (≈ 0,10 à 0,40 $ par question) : clé <code>sk-ant-api…</code> créée sur '
   +'<a href="https://console.anthropic.com/settings/keys" target="_blank" rel="noopener">console.anthropic.com</a>, avec une limite de dépense mensuelle '
   +'et la recherche web activée. Elle reste dans ce navigateur.',
   '<input id="aikeyin" type="password" autocomplete="off" placeholder="sk-ant-api03-…" value="'+(aiKey()?'••••••••':'')+'">'
   +'<button onclick="aiKeySet()">Utiliser</button>'+(aiKey()?'<button class="sec" onclick="aiKeyForget()">Oublier la clé</button>':''))
  +'</div><div id="aikeymsg" class="sub"></div><button class="sec" onclick="aiKeyForm(false)">Fermer</button>'}
function aiKeySet(){const v=document.getElementById('aikeyin').value.trim(),msg=document.getElementById('aikeymsg');
 if(v.startsWith('•')&&aiKey()){aiSetMode('api');aiKeyForm(false);return}if(!v)return;
 if(v.startsWith('sk-ant-oat')){msg.innerHTML='<span class="neg">C’est un jeton d’abonnement Claude (Pro/Max) : il ne marche pas comme clé API. '
  +'Il va dans le dépôt AION Helper (secret GitHub), puis choisis « AION Helper sur GitHub ».</span>';return}
 if(!v.startsWith('sk-ant-')){msg.innerHTML='<span class="neg">Ce n’est pas une clé Anthropic (elle commence par sk-ant-api).</span>';return}
 try{localStorage.setItem('aikey',v)}catch(e){}aiSetMode('api');aiKeyForm(false);toast('Clé enregistrée dans ce navigateur');document.getElementById('aiin').focus()}
function aiKeyForget(){try{localStorage.removeItem('aikey')}catch(e){}aiKeyForm();toast('Clé oubliée dans ce navigateur')}
function aiGrow(t){t.style.height='auto';t.style.height=Math.min(t.scrollHeight,220)+'px'}
function aiNew(){if(AIBUSY)AIBUSY.abort();AIH=[];aiSave();try{localStorage.removeItem('aisession')}catch(e){}aiRenderAll();document.getElementById('aiin').focus()}
function aiAsk(q){if(AIBUSY)return;document.getElementById('aiin').value=q;aiSend()}

// ---------------------------------------------------------------- outil tracker_search (exécuté dans la page)
const AITOOLS=[{type:'web_search_20260209',name:'web_search',max_uses:8},
 {type:'web_fetch_20260209',name:'web_fetch',max_uses:6,max_content_tokens:25000},
 {name:'tracker_search',eager_input_streaming:true,
  description:'Search the AION HDV tracker catalogue: live auction-house (HDV) data from the players\' own server, refreshed hourly. '
   +'Item names are in French (the game client language); English names are matched too. For each match it returns rarity, type, level, '
   +'current lowest price in kinah, number of listings, usual price (what it really sells for), crafting recipes with ingredient prices, '
   +'what the item is used to craft, and gathering zones with node counts. Use it for any question about an item\'s price, crafting, '
   +'profit, ingredients or where to gather it. One item or keyword per call; call it several times for several items.',
  input_schema:{type:'object',properties:{query:{type:'string',description:'Item name or part of it, French or English (e.g. "Potion de soin", "Asvata wood")'}},
   required:['query'],additionalProperties:false}}];
function aiIdx(){if(AIX||!window.ASSIST)return AIX;const by={},uses={};ASSIST.items.forEach(r=>by[r[0]]=r);
 Object.entries(ASSIST.recipes).forEach(([id,rs])=>rs.forEach(r=>r[3].forEach(([i])=>{(uses[i]=uses[i]||new Set()).add(+id)})));
 AIX={by,uses,list:ASSIST.items.map(r=>[r,normName(r[1]||''),normName(r[2]||'')])};return AIX}
function aiItem(r,full){const X=aiIdx(),o={nom:r[1],nom_en:r[2]||undefined,rarete:r[3]||undefined,type:r[4]||undefined,niveau:r[5]||undefined,
  prix_hdv_actuel:r[6],annonces:r[7],prix_habituel:r[8]};
 if(!full)return o;
 const rs=ASSIST.recipes[r[0]];if(rs)o.recettes=rs.map(([p,m,q,ing])=>({metier:(window.PROF&&PROF[p])||p,maitrise_requise:m,quantite_produite:q,
  ingredients:ing.map(([i,n])=>({nom:(X.by[i]||[0,'#'+i])[1],qte:n,prix_hdv:(X.by[i]||[])[6]}))}));
 const u=X.uses[r[0]];if(u)o.sert_a_crafter=[...u].slice(0,15).map(i=>(X.by[i]||[0,'#'+i])[1]);
 const nd=ASSIST.nodes[r[0]];if(nd)o.recolte_points_par_zone=nd;
 return o}
function aiSearch(q){const X=aiIdx();if(!X)return{erreur:'catalogue du tracker indisponible (assist.js non chargé)'};
 const n=normName(String(q||'')),toks=n.split(' ').filter(Boolean);if(!toks.length)return{erreur:'requête vide'};
 const hits=[];X.list.forEach(([r,fr,en])=>{let s=0;
  if(fr===n||en===n)s=100;else if(fr.startsWith(n)||en.startsWith(n))s=60;else if(toks.every(t=>fr.includes(t))||toks.every(t=>en.includes(t)))s=30;
  if(s)hits.push([s+(r[6]?5:0)-Math.min(fr.length,60)/100,r])});
 hits.sort((a,b)=>b[0]-a[0]);
 return{serveur:ASSIST.server,prix_releves_le:ASSIST.asof,unite:'kinah',resultats:hits.length,
  objets:hits.slice(0,8).map(([s,r],i)=>aiItem(r,i<3))}}
function aiTool(b){if(b.name!=='tracker_search')return{content:'outil inconnu : '+b.name,is_error:true};
 if(!b.input||typeof b.input.query!=='string')return{content:'INVALID_JSON : paramètre query attendu (texte)',is_error:true};
 return{content:JSON.stringify(aiSearch(b.input.query))}}

// ---------------------------------------------------------------- appel de l'API (streaming SSE, blocs reconstitués tels quels)
function aiSystem(){const A=window.ASSIST;
 return 'You are the Aion 2 assistant inside AION HDV, a private tool used by two friends who play Aion 2 (NCSOFT\'s MMORPG) '
  +'on the server '+(A?A.server:'Zemurru')+', with a French game client. They ask anything about the game: loot and drops, dungeons, bosses, '
  +'classes and builds, gear progression, crafting, gathering, quests, the auction house (HDV), events and patches.\n\n'
  +'Your built-in knowledge of Aion 2 is thin and easily confused with the original Aion (2008). Do not answer game facts from memory: '
  +'search the web first and base the answer on what you find. Prefer recent, specific sources (official site and patch notes, game databases '
  +'and wikis, guides, Reddit, Korean or Taiwanese community sites when the global version lacks coverage), fetch a page when search snippets '
  +'are not enough, and say so when sources disagree, are old, or only cover the Korean version.\n\n'
  +'For item prices, crafting recipes and costs, profit, ingredients or gathering locations, call tracker_search first: it is live data '
  +'from their own server (prices in kinah; the auction house keeps a 10% tax on each sale, and each posting or relisting costs a 2% listing fee of the total price that is never refunded). Item names there are French; give French names as they appear in game, with the English '
  +'name in brackets when it helps.\n\n'
  +'Answer in the language of the question. Lead with the direct answer, then the details that matter: short sections, lists, '
  +'and a table when comparing options. Bold key item names and numbers. Be concrete (names, numbers, where, how many), skip filler.'
  +(A&&A.fmt?'\n\n'+A.fmt:'')+aiMemPrompt(aiMemLocal())}
async function aiStream(signal,draw){
 const r=await fetch('https://api.anthropic.com/v1/messages',{method:'POST',signal,headers:{'content-type':'application/json',
   'x-api-key':aiKey(),'anthropic-version':'2023-06-01','anthropic-beta':'server-side-fallback-2026-07-01',
   'anthropic-dangerous-direct-browser-access':'true'},
  body:JSON.stringify({model:AIMODEL,max_tokens:32000,stream:true,thinking:{type:'adaptive'},output_config:{effort:'medium'},
   fallbacks:'default',cache_control:{type:'ephemeral'},system:aiSystem(),tools:AITOOLS,messages:AIH.map(m=>({role:m.role,content:m.content}))})});
 if(!r.ok){let m='';try{const j=await r.json();m=(j.error&&j.error.message)||''}catch(e){}
  const e=new Error(r.status===401?'Clé API refusée ('+m+')':r.status===429?'Limite de débit ou de dépense atteinte, réessaie dans un moment ('+m+')'
   :r.status===529?'API surchargée, réessaie dans un moment':'Erreur '+r.status+' : '+m);e.status=r.status;throw e}
 const rd=r.body.getReader(),dec=new TextDecoder(),blocks=[];let buf='',msg={};
 for(;;){const{done,value}=await rd.read();if(done)break;buf+=dec.decode(value,{stream:true});let i;
  while((i=buf.indexOf('\n\n'))>=0){const data=buf.slice(0,i).split('\n').filter(l=>l.startsWith('data:')).map(l=>l.slice(5).trim()).join('');
   buf=buf.slice(i+2);if(!data)continue;const ev=JSON.parse(data);
   if(ev.type==='message_start')msg=ev.message;
   else if(ev.type==='content_block_start'){const b=ev.content_block;if(b.type==='tool_use'||b.type==='server_tool_use')b._j='';blocks[ev.index]=b;draw(b,blocks)}
   else if(ev.type==='content_block_delta'){const b=blocks[ev.index],d=ev.delta;
    if(d.type==='text_delta')b.text+=d.text;else if(d.type==='input_json_delta')b._j+=d.partial_json;
    else if(d.type==='thinking_delta')b.thinking+=d.thinking;else if(d.type==='signature_delta')b.signature=d.signature;
    else if(d.type==='citations_delta')(b.citations=b.citations||[]).push(d.citation);
    if(d.type==='text_delta')draw(null,blocks)}
   else if(ev.type==='content_block_stop'){const b=blocks[ev.index];
    if('_j' in b){try{b.input=b._j?JSON.parse(b._j):{}}catch(e){b.input=b.type==='tool_use'?null:{}}delete b._j}draw(b,blocks)}
   else if(ev.type==='message_delta'){Object.assign(msg,ev.delta);msg.usage=Object.assign({},msg.usage,ev.usage)}
   else if(ev.type==='error')throw new Error((ev.error&&ev.error.message)||'erreur de l’API')}}
 msg.content=blocks.filter(Boolean);return msg}
async function aiSend(){const inp=document.getElementById('aiin'),q=inp.value.trim();
 if(AIBUSY){AIBUSY.abort();return}if(!q&&!AIATT.length)return;const mode=aiMode();
 if(mode==='server')return aiSendLocal(q,'api');
 if(mode==='local'){if(!AILOCAL)await aiLocalProbe();if(AILOCAL)return aiSendLocal(q);aiKeyForm();aiLocalUse();return}
 if(!aiKey()){aiKeyForm();return}
 await aiLoad();inp.value='';aiGrow(inp);const att=aiAttTake(),qt=q||'Regarde la pièce jointe.';
 const H=AIH,start=H.length;H.push(att.length?{role:'user',content:[...aiAttBlocks(att),{type:'text',text:qt}],q:qt,att:aiAttMeta(att)}:{role:'user',content:q});
 const turn=aiTurn(qt,aiAttMeta(att));AIBUSY=new AbortController();aiBusy(true);
 let note='';
 try{for(let step=0;step<15;step++){
   const msg=await aiStream(AIBUSY.signal,(b,blocks)=>{aiPaint.live=blocks;aiDraw(turn,start,b)});
   aiPaint.live=null;H.push({role:'assistant',content:msg.content});aiCostAdd(msg.usage);
   if(msg.stop_reason==='tool_use'){const calls=msg.content.filter(b=>b.type==='tool_use');
    H.push({role:'user',content:calls.map(b=>Object.assign({type:'tool_result',tool_use_id:b.id},aiTool(b)))});continue}
   if(msg.stop_reason==='pause_turn')continue;
   if(msg.stop_reason==='max_tokens')note='Réponse coupée (trop longue).';
   if(msg.stop_reason==='refusal')note='L’assistant a refusé de répondre à cette question.';
   break}
  if(H===AIH)aiSave()}
 catch(e){if(H===AIH){AIH.length=start;aiSave()}                              // tour annule : l'historique reste valide pour la suite
  note=e.name==='AbortError'?'Interrompu.':e.message;if(e.status===401)aiKeyForm()}
 if(!note&&H===AIH)aiMemKeep(H.slice(start+1).filter(m=>m.role==='assistant').map(m=>m.content.filter(b=>b.type==='text').map(b=>b.text).join('')).join('\n'));
 aiPaint.live=null;AIBUSY=null;aiBusy(false);aiDraw(turn,start,null,true,note)}
function aiBusy(on){const b=document.getElementById('aigo');b.textContent=on?'■':'➤';b.title=on?'Arrêter':'Envoyer (Entrée)'}

// ---------------------------------------------------------------- affichage
function aiTurn(q,att){const box=document.getElementById('aimsgs'),h=box.querySelector('.aihello');if(h)h.remove();
 const u=document.createElement('div');u.className='aiu';u.textContent=q;box.appendChild(u);
 if(att&&att.length){const t=document.createElement('div');t.className='aiuatt';
  t.innerHTML=att.map(a=>a.thumb?'<img src="'+a.thumb+'" alt="'+escH(a.name)+'" title="'+escH(a.name)+'">':'<span>📄 '+escH(a.name)+'</span>').join('');u.prepend(t)}
 const a=document.createElement('div');a.className='aia';a.innerHTML='<div class="aibody"></div><div class="aistat">Réflexion…</div><div class="aisrc"></div>';
 box.appendChild(a);u.scrollIntoView({block:'start',behavior:'smooth'});return a}
function aiSteps(msgs){let s=0,f=0,t=0;msgs.forEach(m=>{Array.isArray(m.content)&&m.content.forEach(b=>{
  if(b.type==='server_tool_use'){if(b.name==='web_search')s++;else if(b.name==='web_fetch')f++}else if(b.type==='tool_use')t++});
  (m.steps||[]).forEach(n=>n==='WebSearch'?s++:n==='WebFetch'?f++:t++)});
 return[s&&s+' recherche'+(s>1?'s':'')+' web',f&&f+' page'+(f>1?'s':'')+' lue'+(f>1?'s':''),t&&t+' recherche'+(t>1?'s':'')+' tracker'].filter(Boolean).join(' · ')}
let AIRAF=0;
function aiDraw(turn,start,b,done,note){
 if(b&&b.type==='server_tool_use'&&b.input&&!('_j' in b)){const st=turn.querySelector('.aistat');
  if(st){st.style.display='';st.textContent=b.name==='web_search'?'Recherche web'+(b.input.query?' : '+b.input.query:'…'):b.name==='web_fetch'?'Lecture'+(b.input.url?' : '+b.input.url:'…'):'Analyse des résultats…'}}
 if(b&&b.type==='tool_use'&&b.input&&!('_j' in b)){const st=turn.querySelector('.aistat');if(st){st.style.display='';st.textContent='Données du tracker : '+(b.input.query||'…')}}
 if(done){cancelAnimationFrame(AIRAF);aiPaint(turn,start,true,note);return}
 if(!AIRAF)AIRAF=requestAnimationFrame(()=>{AIRAF=0;aiPaint(turn,start,false)})}
function aiPaint(turn,start,done,note){
 const ms=AIH.slice(start+1).filter(m=>m.role==='assistant').map(m=>m.content);
 // le message en cours n'est dans AIH qu'une fois fini : on lit aussi ses blocs en direct
 if(!done&&aiPaint.live)ms.push(aiPaint.live.filter(Boolean));
 const text=ms.map(c=>c.filter(b=>b.type==='text').map(b=>b.text).join('')).filter(t=>t.trim()).join('\n\n');
 turn.querySelector('.aibody').innerHTML=aiMd(text);aiSparks(turn);
 const st=turn.querySelector('.aistat');
 if(done){if(st)st.remove();const meta=aiSteps(AIH.slice(start+1));
  // sources : passages cités, sinon pages lues (la recherche filtrée par code ne renvoie pas de citations)
  const src=new Map();ms.forEach(c=>c.forEach(b=>(b.citations||[]).forEach(x=>x.url&&!src.has(x.url)&&src.set(x.url,x.title||x.url))));
  if(!src.size)ms.forEach(c=>c.forEach(b=>{const r=b.type==='web_fetch_tool_result'&&b.content;
   if(r&&r.type==='web_fetch_result'&&r.url&&!src.has(r.url))src.set(r.url,(r.content&&r.content.title)||r.url.replace(/^https?:\/\/(www\.)?/,''))}));
  AIH.slice(start+1).forEach(m=>(m.src||[]).forEach(u=>!src.has(u)&&src.set(u,u.replace(/^https?:\/\/(www\.)?/,''))));
  turn.querySelector('.aisrc').innerHTML=[...src].slice(0,10).map(([u,t])=>'<a href="'+escH(u)+'" target="_blank" rel="noopener" title="'+escH(t)+'">'
   +escH(t)+'</a>').join('')+(meta?'<span class="sub" style="align-self:center">'+meta+'</span>':'');
  if(note){const e=document.createElement('div');e.className='aierr';e.textContent=note;turn.appendChild(e)}}
 else if(st&&text)st.style.display='none'}
function aiRenderAll(){const box=document.getElementById('aimsgs');box.innerHTML='';
 if(!AIH.length){box.innerHTML=aiRenderAll.hello||'';aiHome();return}
 AIH.forEach((m,i)=>{if(m.role==='user'&&(typeof m.content==='string'||m.q!=null)){const t=aiTurn(m.q!=null?m.q:m.content,m.att);aiPaint(t,i,true)}})}

// ---------------------------------------------------------------- réponses en blocs visuels
// Markdown (titres, listes, tableaux, citations, gras, liens http) + blocs que l'assistant écrit d'après aionhdv/assistant_format.md :
// [[objet]] (pastille icône + prix, ouvre la fiche), ```items (cartes avec courbe 3 j), ```stats (chiffres clés), ```steps (étapes),
// ```chart (barres), ```suggest (questions suivantes), citations 💡/⚠️/✅ (encadrés), ![légende](https://…) (images des pages lues).
const AIGRADE={Common:'#c8ccd4',Rare:'#3ecf8e',Legend:'#4ea8ff',Unique:'#f0c050',Epic:'#f08c3e',Mythic:'#e05cf0'};
const aiUnesc=s=>String(s).replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&amp;/g,'&');
function aiFind(name){const X=aiIdx();if(!X||!name)return null;const n=normName(aiUnesc(name));
 let best=null;for(const [r,fr,en] of X.list){if(fr===n||en===n){if(!best||(r[6]&&!best[6]))best=r}}
 if(best)return best;for(const [r,fr,en] of X.list)if(n.length>3&&(fr.startsWith(n)||en.startsWith(n)))return r;return null}
function aiChip(name){const r=aiFind(name);if(!r)return '<b>'+name+'</b>';
 return '<span class="aichip" onclick="aiItemCard('+r[0]+')" title="Fiche de l’objet">'+(r[9]?'<img src="'+escH(r[9])+'" alt="" loading="lazy">':'')
  +'<span style="color:'+(AIGRADE[r[3]]||'inherit')+'">'+escH(r[1])+'</span>'+(r[6]?'<em>'+kf(r[6])+'</em>':'')+'</span>'}
function aiInline(s){return s.replace(/`([^`]+)`/g,'<code>$1</code>').replace(/\[\[([^\]]+)\]\]/g,(m,n)=>aiChip(n))
 .replace(/!\[([^\]]*)\]\((https:\/\/[^)\s]+)\)/g,'<figure class="aiimg"><a href="$2" target="_blank" rel="noopener"><img src="$2" alt="$1" loading="lazy" '
  +'referrerpolicy="no-referrer" onerror="this.closest(\'figure\').remove()"></a><figcaption>$1</figcaption></figure>')
 .replace(/\*\*([^*]+)\*\*/g,'<b>$1</b>').replace(/(^|[^*\w])\*([^*\s][^*]*)\*/g,'$1<i>$2</i>')
 .replace(/(^|[^!])\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g,'$1<a href="$3" target="_blank" rel="noopener">$2</a>')
 .replace(/(^|[\s(])(https?:\/\/[^\s<)"]+)/g,'$1<a href="$2" target="_blank" rel="noopener">$2</a>')}
function aiNum(v){const n=+String(v).replace(/[\s  ]/g,'').replace(',','.');return isFinite(n)?n:null}
function aiCards(names){return '<div class="aicards">'+names.map(n=>{const r=aiFind(n);if(!r)return '';
  const d=r[6]&&r[8]?r[6]/r[8]-1:null;
  return '<div class="aicard" onclick="aiItemCard('+r[0]+')">'+(r[9]?'<img src="'+escH(r[9])+'" alt="" loading="lazy">':'<span></span>')
   +'<div><div class="nm" style="color:'+(AIGRADE[r[3]]||'inherit')+'">'+escH(r[1])+'</div><div class="sub">'+escH([r[3],r[4],r[5]?'niv. '+r[5]:''].filter(Boolean).join(' · '))+'</div>'
   +'<div class="pr">'+(r[6]?kf(r[6])+' <small>kinah</small>':'<span class="mut">pas en vente</span>')
   +(d!=null&&Math.abs(d)>=.03?' <span class="'+(d>0?'pos':'neg')+'">'+(d>0?'+':'')+Math.round(d*100)+' %</span>':'')+'</div>'
   +'<svg class="aispark" data-id="'+r[0]+'" viewBox="0 0 100 26" preserveAspectRatio="none"></svg></div></div>'}).join('')+'</div>'}
function aiWidget(kind,raw){const rows=raw.map(l=>l.trim()).filter(Boolean),cols=l=>l.split('|').map(c=>c.trim());
 if(kind==='items')return aiCards(rows.map(l=>l.replace(/^\[\[|\]\]$/g,'').replace(/^[-*•]\s*/,'')));
 if(kind==='stats')return '<div class="kpis aistats">'+rows.map(l=>{const [a,b,c]=cols(l);
  return '<div class="kpi"><div class="l">'+escH(a||'')+'</div><div class="v">'+aiInline(escH(b||''))+'</div>'+(c?'<div class="s">'+aiInline(escH(c))+'</div>':'')+'</div>'}).join('')+'</div>';
 if(kind==='steps')return '<ol class="aisteps">'+rows.map(l=>{const [a,...b]=cols(l);
  return '<li><b>'+aiInline(escH(a))+'</b>'+(b.length?'<div>'+aiInline(escH(b.join(' | ')))+'</div>':'')+'</li>'}).join('')+'</ol>';
 if(kind==='chart'){let title='';const bars=[];rows.forEach(l=>{const t=l.match(/^title\s*:\s*(.*)/i);if(t){title=t[1];return}
   const c=cols(l),v=aiNum(c[c.length-1]);if(c.length>1&&v!=null)bars.push([c.slice(0,-1).join(' | '),v])});
  const max=Math.max(...bars.map(b=>Math.abs(b[1])),1);
  return '<div class="aichart">'+(title?'<div class="t">'+aiInline(escH(title))+'</div>':'')+bars.map(([a,v])=>'<div class="r"><span>'+aiInline(escH(a))
   +'</span><i><b style="width:'+Math.max(2,Math.abs(v)/max*100)+'%"'+(v<0?' class="neg"':'')+'></b></i><em>'+kf(v)+'</em></div>').join('')+'</div>'}
 if(kind==='memo')return '<div class="aimemo">🧠 <b>Retenu pour la suite</b>'+rows.map(l=>'<div>'+aiInline(escH(l.replace(/^[-*•]\s*/,'')))+'</div>').join('')
  +'<button onclick="aiMemForm()">Voir la mémoire</button></div>';
 if(kind==='suggest')return '<div class="aifollow">'+rows.map(l=>{const q=l.replace(/^[-*•\d.)\s]+/,'');
  return '<button data-q="'+escH(q)+'" onclick="aiAsk(this.dataset.q)">'+escH(q)+'</button>'}).join('')+'</div>';
 return '<pre><code>'+raw.map(escH).join('\n')+'</code></pre>'}
function aiMd(src){const R=(src||'').split('\n'),L=R.map(escH),out=[];let i=0;
 const cells=l=>l.trim().replace(/^\||\|$/g,'').split('|').map(c=>c.trim());
 while(i<L.length){const l=L[i];
  if(/^```/.test(l)){const kind=l.slice(3).trim().toLowerCase(),c=[];i++;while(i<L.length&&!/^```/.test(L[i]))c.push(R[i++]);i++;out.push(aiWidget(kind,c));continue}
  let m=l.match(/^(#{1,4})\s+(.*)/);if(m){out.push('<h'+(m[1].length+1)+'>'+aiInline(m[2])+'</h'+(m[1].length+1)+'>');i++;continue}
  if(/^\s*\|.*\|\s*$/.test(l)&&i+1<L.length&&/^\s*\|?\s*:?-{2,}/.test(L[i+1])){const h=cells(l);i+=2;const rows=[];
   while(i<L.length&&/^\s*\|.*\|\s*$/.test(L[i]))rows.push(cells(L[i++]));
   out.push('<div class="aitbl"><table><thead><tr>'+h.map(c=>'<th>'+aiInline(c)+'</th>').join('')+'</tr></thead><tbody>'
    +rows.map(r=>'<tr>'+r.map(c=>'<td>'+aiInline(c)+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>');continue}
  if(/^\s*([-*•]|\d+[.)])\s+/.test(l)){const ol=/^\s*\d/.test(l),items=[];
   while(i<L.length&&(/^\s*([-*•]|\d+[.)])\s+/.test(L[i])||(/^\s{2,}\S/.test(L[i])&&items.length))){
    if(items.length&&/^(?:[-*•]|\d+[.)])\s+/.test(L[i])&&/^\d/.test(L[i])!==ol)break;   // liste d'un autre type
    const x=L[i].match(/^(\s*)(?:[-*•]|\d+[.)])\s+(.*)/);if(x)items.push([x[1].length>=2,x[2]]);else items[items.length-1][1]+=' '+L[i].trim();i++}
   let h='<'+(ol?'ol':'ul')+'>',sub=false;items.forEach(([n,t])=>{if(n&&!sub){h+='<ul>';sub=true}if(!n&&sub){h+='</ul>';sub=false}h+='<li>'+aiInline(t)+'</li>'});
   out.push(h+(sub?'</ul>':'')+'</'+(ol?'ol':'ul')+'>');continue}
  if(/^&gt;\s?/.test(l)){const q=[];while(i<L.length&&/^&gt;\s?/.test(L[i]))q.push(L[i++].replace(/^&gt;\s?/,''));
   const t=q.join(' ').trim(),k=/^💡/.test(t)?'tip':/^⚠/.test(t)?'warn':/^✅/.test(t)?'ok':'';
   out.push(k?'<div class="aicall '+k+'">'+aiInline(q.join('<br>'))+'</div>':'<blockquote>'+aiInline(q.join('<br>'))+'</blockquote>');continue}
  if(/^\s*(---|\*\*\*)\s*$/.test(l)){i++;continue}
  if(!l.trim()){i++;continue}
  const p=[];while(i<L.length&&L[i].trim()&&!/^(#{1,4}\s|```|\s*([-*•]|\d+[.)])\s|&gt;|\s*\|.*\|\s*$)/.test(L[i]))p.push(L[i++]);
  if(!p.length)p.push(L[i++]);out.push('<p>'+aiInline(p.join('<br>'))+'</p>')}
 return out.join('')}
// courbes des cartes : prices.js (historique horaire du serveur) chargé à la première carte
function aiSparks(root){const svgs=[...(root||document).querySelectorAll('svg.aispark:not([data-done])')];if(!svgs.length)return;
 const draw=()=>svgs.forEach(s=>{s.dataset.done='1';const pts=((window.PRICES&&PRICES.s[s.dataset.id])||[]).slice(-72).filter(p=>p[1]>0);
  if(pts.length<2){s.remove();return}const ys=pts.map(p=>p[1]),lo=Math.min(...ys),hi=Math.max(...ys),x0=pts[0][0],x1=pts[pts.length-1][0]||x0+1;
  const d=pts.map((p,k)=>(k?'L':'M')+((p[0]-x0)/(x1-x0||1)*100).toFixed(1)+' '+(24-(hi>lo?(p[1]-lo)/(hi-lo)*22:11)).toFixed(1)).join('');
  s.innerHTML='<path d="'+d+'" fill="none" stroke="var(--acc)" stroke-width="1.6" vector-effect="non-scaling-stroke"/>'});
 if(window.PRICES)return draw();if(aiSparks.wait)return aiSparks.wait.then(draw);
 aiSparks.wait=new Promise(ok=>{const sc=document.createElement('script');sc.src='prices.js';sc.onload=ok;sc.onerror=ok;document.head.appendChild(sc)});aiSparks.wait.then(draw)}
// fiche d'un objet : prix, recette, utilisations, récolte, courbe, carte
function aiItemCard(id){const X=aiIdx(),r=X&&X.by[id];if(!r)return;let box=document.getElementById('aimodal');
 if(!box){box=document.createElement('div');box.id='aimodal';box.onclick=e=>{if(e.target===box)box.classList.remove('on')};document.body.appendChild(box)}
 const nm=i=>(X.by[i]||[0,'#'+i])[1],chip=i=>X.by[i]?aiChip(escH(nm(i))):escH(nm(i)),rs=ASSIST.recipes[id]||[],nd=ASSIST.nodes[id],uses=X.uses[id];
 box.innerHTML='<div class="box"><div class="aihead">'+(r[9]?'<img src="'+escH(r[9])+'" alt="">':'')+'<div><b style="color:'+(AIGRADE[r[3]]||'inherit')+'">'+escH(r[1])+'</b>'
  +'<div class="sub">'+escH([r[2],r[3],r[4],r[5]?'niv. '+r[5]:''].filter(Boolean).join(' · '))+'</div></div>'
  +'<button class="mapbtn" style="margin-left:auto" onclick="document.getElementById(\'aimodal\').classList.remove(\'on\')">Fermer ✕</button></div>'
  +'<div class="kpis"><div class="kpi"><div class="l">Prix le plus bas</div><div class="v">'+(r[6]?kf(r[6]):'–')+'</div><div class="s">'+(r[7]!=null?r[7]+' annonces':'pas en vente')+'</div></div>'
  +'<div class="kpi"><div class="l">Prix habituel</div><div class="v">'+(r[8]?kf(r[8]):'–')+'</div><div class="s">ce qu’il se vend vraiment</div></div></div>'
  +'<div class="aiacts">'+(r[6]?'<button class="mapbtn" onclick="openChart('+id+',this.dataset.n)" data-n="'+escH(r[1])+'">📈 Courbe de prix</button>':'')
  +(nd?'<button class="mapbtn" onclick="openMap(this.dataset.n)" data-n="'+escH(r[1])+'">MAP</button>':'')
  +'<button class="mapbtn" data-q="'+escH('Parle-moi de '+r[1]+' : où l’obtenir, à quoi il sert, est-ce rentable ?')+'" onclick="document.getElementById(\'aimodal\').classList.remove(\'on\');aiAsk(this.dataset.q)">💬 Demander à l’assistant</button></div>'
  +rs.map(([p,m,q,ing])=>'<h4>Recette · '+escH((window.PROF&&PROF[p])||p)+' (maîtrise '+m+', donne '+q+')</h4><div class="chips">'
   +ing.map(([i,n])=>'<span>'+n+' ×</span> '+chip(i)).join(' ')+'</div>').join('')
  +(uses?'<h4>Sert à crafter</h4><div class="chips">'+[...uses].slice(0,12).map(chip).join(' ')+'</div>':'')
  +(nd?'<h4>Récolte</h4><div class="chips">'+Object.entries(nd).map(([z,c])=>'<span class="chip">'+escH(z)+' · '+c+' points</span>').join(' ')+'</div>':'')+'</div>';
 box.classList.add('on')}
document.addEventListener('keydown',e=>{if(e.key==='Escape'){const b=document.getElementById('aimodal');if(b)b.classList.remove('on')}});
// accueil du chat : marché du serveur (prix anormalement hauts ou bas par rapport au prix habituel) et dernières annonces
function aiHome(){const box=document.getElementById('aihome');if(!box||!window.ASSIST)return;
 const it=ASSIST.items.filter(r=>r[6]&&r[8]&&(r[7]||0)>=2),by=f=>it.map(r=>[r[6]/r[8],r]).filter(([q])=>f(q));
 // écarts de 20 % à x3 : au-delà, c'est presque toujours une annonce isolée ou un prix aberrant
 const up=by(q=>q>=1.2&&q<=3).sort((a,b)=>b[0]-a[0]).slice(0,4),dn=by(q=>q<=.8&&q>=.35).sort((a,b)=>a[0]-b[0]).slice(0,4);
 let h='';
 if(up.length||dn.length)h+='<h3>Ton marché maintenant · '+escH(ASSIST.server)+'</h3>'
  +(up.length?'<div class="sub">Au-dessus du prix habituel : bon moment pour vendre</div>'+aiCards(up.map(([q,r])=>r[1])):'')
  +(dn.length?'<div class="sub">En dessous du prix habituel : bonnes affaires à l’achat</div>'+aiCards(dn.map(([q,r])=>r[1])):'');
 if(ASSIST.news&&ASSIST.news.length)h+='<h3>Dernières annonces</h3><div class="ainews">'+ASSIST.news.slice(0,6).map(([d,src,t,u])=>
  '<a href="'+escH(u)+'" target="_blank" rel="noopener"><span class="sub">'+escH(src)+' · '+escH((d||'').slice(0,10))+'</span>'+escH(t)+'</a>').join('')+'</div>';
 if(AINEWS&&AINEWS.length)h+='<h3>Quoi de neuf sur Aion 2 · résumé par AION Helper</h3><div class="aiposts">'+AINEWS.slice(0,6).map(n=>
  '<a href="'+escH(n.url||'#')+'" target="_blank" rel="noopener">'+(n.image?'<img src="'+escH(n.image)+'" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()">':'')
  +'<span class="sub">'+escH([n.kind,n.date].filter(Boolean).join(' · '))+'</span><b>'+escH(n.title||'')+'</b><span>'+escH(n.summary||'')+'</span></a>').join('')+'</div>';
 box.innerHTML=h;aiSparks(box)}

// ---------------------------------------------------------------- abonnement Claude : pont local (scripts/assistant_local.py)
// Le chat passe par Claude Code sur ce PC (abonnement de la personne connectée) au lieu de l'API : activé à la main,
// pour ne jamais sonder 127.0.0.1 chez quelqu'un qui n'a pas lancé le pont.
const AILOCALURL='http://127.0.0.1:8787';let AILOCAL=false;
function aiLocalWanted(){return aiMode()==='local'}
async function aiLocalProbe(){AILOCAL=false;
 if(aiLocalWanted())try{const r=await fetch(AILOCALURL+'/health',{signal:AbortSignal.timeout(2000)});AILOCAL=r.ok&&(await r.json()).ok}catch(e){}
 aiModeShow();return AILOCAL}
async function aiSendLocal(q,base){base=base||AILOCALURL;const srv=base!==AILOCALURL,inp=document.getElementById('aiin');inp.value='';aiGrow(inp);
 const att=aiAttTake(),qt=q||'Regarde la pièce jointe.';
 const H=AIH,start=H.length;H.push(att.length?{role:'user',content:qt,q:qt,att:aiAttMeta(att)}:{role:'user',content:q});
 const turn=aiTurn(qt,aiAttMeta(att));AIBUSY=new AbortController();aiBusy(true);
 let text='',note='',fin=null;const steps=[];
 try{let session='';try{session=localStorage.getItem('aisession')||''}catch(e){}
  const r=await fetch(base+'/ask',{method:'POST',signal:AIBUSY.signal,headers:{'content-type':'application/json'},body:JSON.stringify({q:qt,session,files:att.map(a=>({name:a.name,kind:a.kind,data:a.data}))})});
  if(!r.ok)throw new Error(r.status===401?'Mot de passe demandé : recharge la page.':r.status===413?'Pièces jointes trop lourdes.'
   :(srv?'Serveur':'Pont local')+' : erreur '+r.status);
  const rd=r.body.getReader(),dec=new TextDecoder();let buf='';
  for(;;){const{done,value}=await rd.read();if(done)break;buf+=dec.decode(value,{stream:true});let i;
   while((i=buf.indexOf('\n'))>=0){const ev=JSON.parse(buf.slice(0,i));buf=buf.slice(i+1);
    if(ev.t==='text'){text+=ev.v;aiPaint.live=[{type:'text',text}];aiDraw(turn,start,null)}
    else if(ev.t==='tool'){steps.push(ev.name);text='';aiPaint.live=null;          // texte d'attente avant un outil : remplacé par le statut
     aiDraw(turn,start,ev.name==='WebSearch'?{type:'server_tool_use',name:'web_search',input:{query:ev.v}}
      :ev.name==='WebFetch'?{type:'server_tool_use',name:'web_fetch',input:{url:ev.v}}:{type:'tool_use',name:'tracker_search',input:{query:ev.v}})}
    else if(ev.t==='done')fin=ev;else if(ev.t==='error')throw new Error('Claude Code : '+ev.v)}}
  if(!fin)throw new Error('Réponse interrompue'+(srv?'.':' (pont local arrêté ?)'));
  try{if(fin.session&&H===AIH)localStorage.setItem('aisession',fin.session)}catch(e){}
  H.push({role:'assistant',content:[{type:'text',text:fin.text||text}],src:fin.sources||[],steps});if(H===AIH)aiSave()}
 catch(e){if(H===AIH){AIH.length=start;aiSave()}
  note=e.name==='AbortError'?'Interrompu.':e instanceof TypeError&&srv?'Serveur AION Helper injoignable, réessaie dans un moment.':e instanceof TypeError?'Pont local injoignable : lance « py scripts\\assistant_local.py » (et accepte l’accès au réseau local si Chrome le demande).':e.message;
  if(e instanceof TypeError&&!srv)aiLocalProbe()}
 aiPaint.live=null;AIBUSY=null;aiBusy(false);aiDraw(turn,start,null,true,note)}

// ---------------------------------------------------------------- mode de réponse : serveur AION Helper (server, automatique quand la page
// est servie par un serveur qui répond à api/health, même protocole que le pont local), Claude Code sur ce PC (local), clé API (api)
let AISERVER=false,AINEWS=null;
async function aiServerProbe(){if(location.protocol==='file:')return false;
 try{const r=await fetch('api/health',{cache:'no-store',signal:AbortSignal.timeout(3000)});AISERVER=r.ok&&!!(await r.json()).ok}catch(e){AISERVER=false}
 if(AISERVER&&!AINEWS)fetch('api/news',{cache:'no-store'}).then(r=>r.ok?r.json():null).then(d=>{AINEWS=d&&d.items;if(AINEWS)aiHome()}).catch(()=>{});
 return AISERVER}
function aiMode(){if(AISERVER)return 'server';let m='';try{m=localStorage.getItem('aimode')||(localStorage.getItem('ailocal')?'local':'')}catch(e){}return m||'api'}
function aiSetMode(m){try{localStorage.setItem('aimode',m);localStorage.removeItem('ailocal')}catch(e){}aiModeShow()}
function aiReady(){const m=aiMode();return m==='server'?true:m==='local'?AILOCAL:!!aiKey()}
async function aiRefresh(btn){btn.disabled=true;btn.textContent='↻ Relevé en cours…';
 try{const r=await fetch('api/refresh',{method:'POST'});const d=await r.json();
  toast(d.started?'Relevé des prix lancé : la page se met à jour dans 1 à 2 min':'Un relevé est déjà en cours');
  const t0=Date.now(),wait=async()=>{const h=await (await fetch('api/health',{cache:'no-store'})).json();
   if(!h.building&&h.last_build!==d.last_build)return location.reload();if(Date.now()-t0<6e5)setTimeout(wait,8000)};setTimeout(wait,8000)}
 catch(e){toast('Serveur injoignable');btn.disabled=false;btn.textContent='↻ Actualiser les prix'}}
function aiModeShow(){const b=document.getElementById('aimode');if(!b)return;const m=aiMode();
 const rf=document.getElementById('airefresh');if(rf)rf.hidden=m!=='server';
 b.textContent='⚙ '+(m==='server'?'Serveur AION Helper':m==='local'?'Claude Code sur ce PC'+(AILOCAL?'':' : pont arrêté'):'Clé API');
 b.style.color=m==='local'&&!AILOCAL?'var(--warn)':''}
async function aiLocalUse(){aiSetMode('local');await aiLocalProbe();
 if(AILOCAL){aiKeyForm(false);toast('Le chat passe par Claude Code sur ce PC (ton abonnement Claude)')}
 else document.getElementById('aikeymsg').innerHTML='<span class="neg">Pont local injoignable : lance « py scripts\\assistant_local.py », '
  +'et si Chrome demande l’accès aux appareils du réseau local, accepte.</span>'}

// ---------------------------------------------------------------- pièces jointes : coller (Ctrl + V), glisser-déposer ou 📎
// Images réduites à 1568 px (JPEG) avant l'envoi, PDF et fichiers texte tels quels. Mode clé API : blocs image/document de l'API ;
// serveur et pont local : fichiers envoyés avec la question, que Claude Code lit dans son dossier de travail.
let AIATT=[];
const AITEXT=/\.(txt|md|csv|json|log|ini|cfg|xml|html?)$/i;
function aiB64(blob){return new Promise((ok,ko)=>{const r=new FileReader();r.onload=()=>ok(String(r.result).split(',')[1]);r.onerror=ko;r.readAsDataURL(blob)})}
function aiShrink(img,max,q){const k=Math.min(1,max/Math.max(img.naturalWidth,img.naturalHeight)),c=document.createElement('canvas');
 c.width=Math.round(img.naturalWidth*k);c.height=Math.round(img.naturalHeight*k);const g=c.getContext('2d');g.fillStyle='#fff';g.fillRect(0,0,c.width,c.height);
 g.drawImage(img,0,0,c.width,c.height);return c.toDataURL('image/jpeg',q).split(',')[1]}
async function aiAddFiles(files){for(const f of files){
  if(AIATT.length>=6){toast('6 pièces jointes au plus');break}
  const name=(f.name||'capture.png').slice(0,80);
  try{if((f.type||'').startsWith('image/')){const url=URL.createObjectURL(f),img=new Image();
     await new Promise((ok,ko)=>{img.onload=ok;img.onerror=ko;img.src=url});
     AIATT.push({name:name.replace(/\.\w+$/,'')+'.jpg',kind:'image',type:'image/jpeg',data:aiShrink(img,1568,.88),thumb:'data:image/jpeg;base64,'+aiShrink(img,160,.7)});
     URL.revokeObjectURL(url)}
   else if(f.type==='application/pdf'||/\.pdf$/i.test(name)){if(f.size>15e6){toast('PDF trop lourd (15 Mo max)');continue}
     AIATT.push({name,kind:'pdf',type:'application/pdf',data:await aiB64(f)})}
   else if((f.type||'').startsWith('text/')||AITEXT.test(name)){if(f.size>5e5){toast('Fichier texte trop lourd (500 Ko max)');continue}
     AIATT.push({name,kind:'text',type:'text/plain',data:await aiB64(f)})}
   else toast('Type de fichier non pris en charge : '+name)}
  catch(e){toast('Impossible de lire '+name)}}
 aiAttShow()}
function aiAttShow(){const box=document.getElementById('aiatt');if(!box)return;box.hidden=!AIATT.length;
 box.innerHTML=AIATT.map((a,i)=>'<span class="aiattc">'+(a.thumb?'<img src="'+a.thumb+'" alt="">':'<b>'+(a.kind==='pdf'?'PDF':'TXT')+'</b>')
  +'<span>'+escH(a.name)+'</span><button type="button" title="Retirer" onclick="AIATT.splice('+i+',1);aiAttShow()">✕</button></span>').join('')}
function aiAttTake(){const a=AIATT;AIATT=[];aiAttShow();return a}
// ce que l'historique garde d'une pièce jointe (vignette pour l'affichage, pas le fichier)
function aiAttMeta(att){return att.map(a=>({name:a.name,kind:a.kind,thumb:a.thumb||''}))}
// blocs de contenu pour l'API Anthropic
function aiAttBlocks(att){return att.map(a=>a.kind==='image'?{type:'image',source:{type:'base64',media_type:a.type,data:a.data}}
 :a.kind==='pdf'?{type:'document',title:a.name,source:{type:'base64',media_type:'application/pdf',data:a.data}}
 :{type:'document',title:a.name,source:{type:'text',media_type:'text/plain',data:new TextDecoder().decode(Uint8Array.from(atob(a.data),c=>c.charCodeAt(0)))}})}
document.addEventListener('DOMContentLoaded',()=>{const ai=document.getElementById('ai'),inp=document.getElementById('aiin');if(!ai)return;
 inp.addEventListener('paste',e=>{const fs=[...(e.clipboardData||{}).files||[]];if(fs.length){e.preventDefault();aiAddFiles(fs)}});
 ai.addEventListener('dragover',e=>{if([...e.dataTransfer.types].includes('Files')){e.preventDefault();ai.classList.add('drop')}});
 ai.addEventListener('dragleave',e=>{if(!ai.contains(e.relatedTarget))ai.classList.remove('drop')});
 ai.addEventListener('drop',e=>{ai.classList.remove('drop');if(e.dataTransfer.files.length){e.preventDefault();aiAddFiles([...e.dataTransfer.files])}})});

// ---------------------------------------------------------------- mémoire des corrections
// Quand le joueur corrige l'assistant (ou lui dit quoi retenir), la réponse contient un bloc ```memo : le serveur ou le pont local
// le garde (memory.json) et le remet dans les consignes de chaque question ; en mode clé API, il est gardé dans ce navigateur.
// Le panneau 🧠 liste ce qui est retenu, pour retirer une erreur ou ajouter un fait à la main.
function aiMemos(text){const out=[];(text||'').replace(/```memo[^\n]*\n([\s\S]*?)(?:```|$)/g,(m,b)=>{b.split('\n').forEach(l=>{l=l.replace(/^[-*•\s]+/,'').trim();if(l)out.push(l)})});return out}
function aiMemLocal(){try{return JSON.parse(localStorage.getItem('aimemo')||'[]')}catch(e){return []}}
function aiMemLocalSet(v){try{localStorage.setItem('aimemo',JSON.stringify(v.slice(-200)))}catch(e){}}
function aiMemKeep(text){const add=aiMemos(text);if(!add.length)return;const L=aiMemLocal(),seen=new Set(L.map(i=>i.t.toLowerCase()));
 add.forEach(t=>{if(!seen.has(t.toLowerCase()))L.push({t:t.slice(0,500),d:new Date().toISOString().slice(0,10)})});aiMemLocalSet(L)}
function aiMemPrompt(L){return L&&L.length?'\n\nWhat the player taught you (corrections and facts from his own game: trust them over web sources and '
 +'your built-in knowledge, and use them whenever relevant):\n'+L.map(i=>'- '+i.d+': '+i.t).join('\n'):''}
function aiMemBase(){const m=aiMode();return m==='server'?'api':m==='local'?AILOCALURL:null}
async function aiMemGet(){const b=aiMemBase();if(!b)return aiMemLocal();
 const r=await fetch(b+'/memory',{cache:'no-store'});return r.ok?(await r.json()).items:[]}
async function aiMemPost(body){const b=aiMemBase();
 if(!b){const L=aiMemLocal();if(body.del!=null)L.splice(body.del,1);if(body.add)L.push({t:body.add.slice(0,500),d:new Date().toISOString().slice(0,10)});aiMemLocalSet(L);return}
 await fetch(b+'/memory',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)})}
async function aiMemForm(){const box=document.getElementById('aikey');box.hidden=false;box.innerHTML='<b>🧠 Ce que l’assistant a retenu</b><div class="sub">Chargement…</div>';
 box.scrollIntoView({block:'nearest'});let L=[];try{L=await aiMemGet()}catch(e){}
 box.innerHTML='<b>🧠 Ce que l’assistant a retenu</b><div class="sub">Tes corrections, ajoutées à chaque question. Quand tu le reprends dans le chat, il '
  +'les retient tout seul ; retire ici ce qui est faux.</div><div class="aimemlist">'
  +(L.length?L.map((i,k)=>'<div><span class="sub">'+escH(i.d||'')+'</span> '+escH(i.t)+'<button title="Oublier" onclick="aiMemDel('+k+')">✕</button></div>').join('')
   :'<div class="mut">Rien pour l’instant.</div>')+'</div>'
  +'<input id="aimemin" placeholder="Ajouter un fait à retenir, ex. « La Calendula fraîche tombe aussi à Morheim »">'
  +'<button onclick="aiMemAdd()">Ajouter</button><button class="sec" onclick="aiKeyForm(false)">Fermer</button>'}
async function aiMemDel(k){await aiMemPost({del:k});aiMemForm()}
async function aiMemAdd(){const v=document.getElementById('aimemin').value.trim();if(!v)return;await aiMemPost({add:v});toast('Retenu');aiMemForm()}
