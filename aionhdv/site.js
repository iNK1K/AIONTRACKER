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
 if(on('plan')){e.preventDefault();scanFile(it.getAsFile())}else if(on('gains')){e.preventDefault();jScan(it.getAsFile())}
 else if(on('supply')){e.preventDefault();supplyScan(it.getAsFile())}});

// ======================================================================== journal des ventes
// Mes annonces et ce qu'elles deviennent : postee, vendue (tout ou partie), relistee (nouveau prix = nouveaux frais),
// retiree. Enregistre dans journal.json du depot GitHub (jeton garde dans ce navigateur), sinon dans ce navigateur.
// Meme calcul d'etat que config.lot_state (Python).
let J=null,JSHA=null,JBUSY=false,JOPEN=null;
const JC=()=>window.JCFG||{tax:0.1,repo:null};
const jEsc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function jNow(){const d=new Date(),p=n=>String(n).padStart(2,'0');return d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate())+' '+p(d.getHours())+':'+p(d.getMinutes())}
function jid(){return Date.now().toString(36)+Math.random().toString(36).slice(2,7)}
function jState(l){const ev=(l.ev||[]).filter(e=>!e.x).sort((a,b)=>(a.t||'').localeCompare(b.t||''));
 // frais = taxe de 10 % perdue : payee a chaque mise en vente, elle n'est recuperee (deduite de la vente) que si l'annonce
 // se vend ; relister ou retirer fait perdre celle de l'annonce retiree
 let prix=l.prix,cout=l.cout,src=l.src||null,sold=0,ret=0,frais=0,recu=0,rel=0,poste=null;
 ev.forEach(e=>{if(e.type==='poste'||e.type==='reliste'){prix=e.prix;frais+=e.frais||0;if(e.type==='reliste')rel++;else poste=e.t}
  else if(e.type==='vendu'){sold+=e.qte;recu+=e.recu||0}else if(e.type==='retire'){ret+=e.qte;frais+=e.frais||0}else if(e.type==='cout')cout=e.cout;else if(e.type==='src')src=e.src});
 return {prix,cout,src,vendus:sold,retires:ret,reste:Math.max(0,l.qte-sold-ret),frais,recu,relistes:rel,poste,ev}}
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
async function jApi(method,body){const r=await fetch('https://api.github.com/repos/'+JC().repo+'/contents/journal.json'+(method==='GET'?'?ref=main&t='+Date.now():''),
  {method,headers:{Authorization:'Bearer '+jToken(),Accept:'application/vnd.github+json','Content-Type':'application/json'},body:body&&JSON.stringify(body)});
 if(r.status===404&&method==='GET')return null;if(!r.ok){const e=new Error('GitHub '+r.status);e.status=r.status;throw e}return r.json()}
async function jPull(){const d=await jApi('GET');if(!d){JSHA=null;return null}JSHA=d.sha;return JSON.parse(b64d(d.content))}
// enregistrement : fusion avec la version du depot (un autre appareil a pu ecrire entre-temps), puis ecriture
async function jSync(label){jKeep();
 if(!jToken()||!JC().repo){jStatus('💾 Enregistré dans ce navigateur seulement : ajoute ton jeton GitHub (ci-dessous) pour le garder sur le dépôt et l’utiliser dans les alertes.','neg');jRender();return}
 if(JBUSY)return;JBUSY=true;jStatus('⏳ Enregistrement sur GitHub…');
 try{for(let k=0;k<3;k++){const remote=await jPull();const merged=jMerge(remote,J);merged.maj=jNow();
   if(remote&&jText(remote)===jText({...merged,maj:remote.maj})){J=remote;break}
   try{const r=await jApi('PUT',{message:'Journal : '+(label||'mise à jour'),content:b64e(jText(merged)),branch:'main',...(JSHA?{sha:JSHA}:{})});
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
const lost=(p,q)=>Math.floor(JC().tax*p*q),net=(p,q)=>Math.floor(p*q*(1-JC().tax));
function jLot(id){return J.lots.find(l=>l.id===id)}
// origine d'une annonce : recolte -> craft (cout 0), achat -> craft (cout = ingredients achetes), flip (cout = prix d'achat)
const JSRC={recolte:'🌲 Récolte → craft',achat:'🛒 Achat → craft',ravit:'📦 Ravitaillement',flip:'🔁 Flip'};
// objets de ma derniere capture de ravitaillement (onglet Ravitaillement) : origine proposee « Ravitaillement »
function jSupplyNames(){const d=supplyLoad(),by={};if(!d)return [];(window.SUPPLY||[]).forEach(x=>(by[x.s]=by[x.s]||[]).push(x));
 return d.cards.flatMap(c=>c.items.flatMap(s=>(by[s]||[]).map(x=>x.n)))}
const jSrcDefault=n=>jSupplyNames().includes(n)?'ravit':(window.HARVEST_ITEMS||[]).includes(n)?'recolte':'achat';
// cout propose : ravitaillement = total du craft de l'onglet Ravitaillement (ingredients au plus bas), sinon comme l'achat -> craft
const jCostFor=(src,n)=>{if(src==='recolte')return 0;if(src==='flip')return undefined;
 const sp=src==='ravit'&&(window.SUPPLY||[]).find(x=>x.n===n&&x.c!=null);return sp?sp.c:(window.COSTS||{})[n]}
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
 else if(kind==='reliste'){const p=+g('p').value;if(!(p>0))return;l.ev.push({id:jid(),t:jNow(),type:'reliste',prix:p,qte:s.reste,frais:lost(s.prix,s.reste)})}
 else if(kind==='retire')l.ev.push({id:jid(),t:jNow(),type:'retire',qte:s.reste,frais:lost(s.prix,s.reste)});
 else if(kind==='src'){const src=g('s').value,c=g('c').value;l.ev.push({id:jid(),t:jNow(),type:'src',src});
  if(c!==''&&+c!==s.cout)l.ev.push({id:jid(),t:jNow(),type:'cout',cout:+c})}
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
// ---------------------------------------------------------------- affichage
function jRender(){if(!J)return;const box=document.getElementById('jopen');if(!box)return;
 const F=window.JFLOOR||{},lots=J.lots.filter(l=>!l.del).map(l=>[l,jState(l)]);
 const open=lots.filter(([l,s])=>s.reste>0).sort((a,b)=>a[0].objet.localeCompare(b[0].objet,'fr'));
 const nm=n=>'<span class="nm" title="Cliquer pour copier">'+jEsc(n)+'</span>';
 box.innerHTML=open.length?open.map(([l,s])=>{const f=F[l.objet],bat=f&&f[0]<s.prix;
  const row='<tr><td>'+nm(l.objet)+' <span class="badge b-mut" style="cursor:pointer" title="Changer l’origine" onclick="jAct(\''+l.id+'\',\'src\')">'
   +(JSRC[s.src]||'❔ origine ?')+'</span>'+(bat?' <span class="badge b-bad">battu : '+NF.format(f[0])+'</span>':f?' <span class="badge b-ok">le moins cher</span>':'')+'</td>'
   +'<td class="n">'+s.reste+(s.reste<l.qte?' / '+l.qte:'')+'</td><td class="n">'+NF.format(s.prix)+'</td>'
   +'<td class="n">'+(s.cout!=null?NF.format(s.cout):'–')+'</td><td class="n '+(s.cout!=null?(net(s.prix,1)-s.cout>0?'pos':'neg'):'')+'">'+(s.cout!=null?NF.format(net(s.prix,1)-s.cout):'–')+'</td>'
   +'<td>'+(s.poste?s.poste.slice(8,10)+'/'+s.poste.slice(5,7)+' '+s.poste.slice(11):'<span class="mut">avant le journal</span>')+'</td>'
   +'<td class="n">'+(s.relistes||'–')+'</td><td class="n">'+(s.frais?NF.format(s.frais):'–')+'</td>'
   +'<td style="white-space:nowrap"><button class="mapbtn" onclick="jAct(\''+l.id+'\',\'vendu\')">✅ Vendu</button> '
   +'<button class="mapbtn" onclick="jAct(\''+l.id+'\',\'reliste\')">🔁 Relister</button> '
   +'<button class="mapbtn" onclick="jAct(\''+l.id+'\',\'retire\')">↩ Retirer</button> '
   +'<button class="mapbtn" onclick="jAct(\''+l.id+'\',\'cout\')">Coût</button> '
   +'<button class="mapbtn" title="Annuler la dernière action" onclick="jUndo(\''+l.id+'\')">↶</button></td></tr>';
  if(!JOPEN||JOPEN.id!==l.id)return row;
  const k=JOPEN.kind,inp=(id,v,w,t)=>'<input id="ja'+id+'" class="search" type="'+(t||'number')+'" value="'+v+'" style="width:'+w+'px;display:inline-block">';
  const go='<button class="mapbtn" onclick="jDo(\''+l.id+'\',\''+k+'\')">OK</button>';
  const f2=k==='vendu'?'Vendu '+inp('q',s.reste,80)+' à '+inp('p',s.prix,110)+' /u, le '+inp('t',jNow().replace(' ','T'),190,'datetime-local')+' '+go
   +' <span class="sub">reçu après taxe : '+NF.format(net(s.prix,s.reste))+'</span>'
   :k==='reliste'?'Nouveau prix '+inp('p',f?Math.max(1,f[0]-1):s.prix,110)+' /u '+go+' <span class="sub">tu perds la taxe payée sur l’annonce retirée : <b class="neg">'+NF.format(lost(s.prix,s.reste))+'</b> ('+Math.round(JC().tax*100)+' % de '+s.reste+' × '+NF.format(s.prix)+') ; la nouvelle annonce repaye '+Math.round(JC().tax*100)+' %, déduits de la vente</span>'
   :k==='retire'?'Retirer les '+s.reste+' restants : tu perds la taxe payée, <b class="neg">'+NF.format(lost(s.prix,s.reste))+'</b> '+go
   :k==='src'?'Origine <select id="jas" class="search" style="width:auto;display:inline-block" onchange="jSrcCost(\''+l.id+'\')">'+jSrcOpts(s.src||jSrcDefault(l.objet))+'</select> '
    +'coût '+inp('c',(()=>{const src=s.src||jSrcDefault(l.objet),c=jCostFor(src,l.objet);   // 0 hors recolte = cout oublie
      return (s.cout==null||(s.cout===0&&src!=='recolte'))&&c!=null?c:(s.cout??'')})(),110)+' /u '+go
    +' <span class="sub">le coût suit l’origine choisie : 0 pour ta récolte, ingrédients achetés pour l’achat → craft et le ravitaillement, ton prix d’achat pour un flip</span>'
   :'Coût de revient '+inp('c',s.cout??'',110)+' /u '+go;
  return row+'<tr><td colspan="9" style="background:var(--card2)">'+f2+'</td></tr>'}).join('')
  :'<tr><td colspan="9" class="mut">Aucune annonce en cours : ajoute-les ci-dessous ou colle une capture de ta fenêtre des ventes.</td></tr>';
 jStats(lots);jLog(lots)}
function jStats(lots){const per=+(document.getElementById('jper')||{}).value||0,since=per?new Date(Date.now()-per*864e5):null;
 const p=n=>String(n).padStart(2,'0'),lim=since?since.getFullYear()+'-'+p(since.getMonth()+1)+'-'+p(since.getDate())+' '+p(since.getHours())+':'+p(since.getMinutes()):'';
 const want=(document.getElementById('jsrc')||{}).value||'',acts={};
 const by={},T={recu:0,frais:0,cout:0,vendus:0,ventes:0,relistes:0,retraits:0,sansCout:0};
 const z=()=>({recu:0,brut:0,frais:0,cout:0,vendus:0,ventes:0,relistes:0,retraits:0,sansCout:0});
 lots.forEach(([l,s])=>{const a=s.src||'?',act=acts[a]||(acts[a]=z()),mine=!want||a===want;
  const o=mine?by[l.objet]||(by[l.objet]=z()):z();
  let cout=l.cout;(s.ev).forEach(e=>{if(e.type==='cout'){cout=e.cout;return}if(!e.t||e.t<lim)return;
   if(e.type==='reliste'||e.type==='retire'){act.frais+=e.frais||0}
   else if(e.type==='vendu'){act.recu+=e.recu||0;act.vendus+=e.qte;act.ventes++;if(cout!=null)act.cout+=cout*e.qte;else act.sansCout+=e.qte}
   if(e.type==='reliste'||e.type==='retire'||e.type==='poste'){o.frais+=e.frais||0;if(e.type==='reliste')o.relistes++;if(e.type==='retire')o.retraits++}
   else if(e.type==='vendu'){o.recu+=e.recu||0;o.brut+=e.prix*e.qte;o.vendus+=e.qte;o.ventes++;if(cout!=null)o.cout+=cout*e.qte;else o.sansCout+=e.qte}})});
 Object.values(by).forEach(o=>Object.keys(T).forEach(k=>T[k]+=o[k]));
 const ben=T.recu-T.cout-T.frais,kpi=(l,v,s,c)=>'<div class="kpi"><div class="l">'+l+'</div><div class="v '+(c||'')+'">'+v+'</div><div class="s">'+s+'</div></div>';
 document.getElementById('jkpi').innerHTML=kpi('Kinah reçus',kf(T.recu),T.ventes+' vente(s), '+NF.format(T.vendus)+' unités, après taxe','pos')
  +kpi('Taxe perdue',kf(T.frais),T.relistes+' reliste(s), '+T.retraits+' retrait(s) : 10 % de l’annonce retirée',T.frais?'neg':'')
  +kpi('Bénéfice',kf(ben),T.sansCout?NF.format(T.sansCout)+' unités vendues sans coût connu (comptées gratuites)':'reçu − coût − frais',ben>0?'pos':'neg')
  +kpi('Perte due aux relistes',T.recu?(T.frais/T.recu*100).toFixed(1).replace('.',',')+' %':'–','taxe perdue / kinah reçus');
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
function jLog(lots){const ev=[];lots.forEach(([l,s])=>s.ev.forEach(e=>e.t&&e.type!=='cout'&&ev.push([e,l,ev.length])));ev.sort((a,b)=>b[0].t.localeCompare(a[0].t)||b[2]-a[2]);
 const T={poste:'📦 posté',reliste:'🔁 relisté',vendu:'✅ vendu',retire:'↩ retiré'};
 document.getElementById('jlog').innerHTML=ev.slice(0,40).map(([e,l])=>'<tr><td>'+e.t.slice(8,10)+'/'+e.t.slice(5,7)+' '+e.t.slice(11)+'</td><td>'+T[e.type]+'</td><td>'+jEsc(l.objet)+'</td>'
  +'<td class="n">'+(e.qte||'')+'</td><td class="n">'+(e.prix?NF.format(e.prix):'')+'</td><td class="n '+(e.type==='vendu'?'pos':'neg')+'">'+(e.type==='vendu'?'+'+NF.format(e.recu||0):e.frais?'−'+NF.format(e.frais):'')+'</td></tr>').join('')}
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
  if(cp){const pr=net*day;cp.textContent=kf(pr);cp.dataset.v=pr;cp.classList.toggle('pos',pr>0);cp.classList.toggle('neg',pr<=0)}});
 calc();renderMetiers();todoBuys();if(window.PLANDATA){planSafe();planGamble()}}
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
 importLevelsFromHash();applyLevels();jInit();rateCalc();planSafe();planGamble();document.querySelectorAll('th').forEach(th=>th.onclick=()=>sortT(th))});

// ======================================================================== ravitaillement
// Cases lues sur la capture (icone de chaque objet), gardees dans ce navigateur ; prix du dernier passage (SUPPLY) :
// detail des ingredients, total du craft, annonces, mediane 3 j, prix de vente cible.
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
function supplyRender(){const box=document.getElementById('sbox');if(!box)return;const d=supplyLoad();if(!d){box.innerHTML='';return}
 const byIcon={};(window.SUPPLY||[]).forEach(x=>(byIcon[x.s]=byIcon[x.s]||[]).push(x));
 const n=v=>v==null?'–':NF.format(Math.round(v)),K={hdv:'HDV',od:'Od transmuté',pnj:'PNJ (prix estimé)',craft:'à fabriquer',recolte:'récolte',introuvable:'introuvable'};
 const part=(p,ind)=>'<tr><td style="padding-left:'+(10+ind*18)+'px">'+jEsc(p.n)+(p.via?'<div class="sub">→ transmuté en '+jEsc(p.via)+'</div>':'')+'</td>'
  +'<td class="n">'+NF.format(p.q)+'</td><td class="n">'+(p.p==null?'<span class="neg">introuvable</span>':n(p.p))+'</td>'
  +'<td class="n">'+(p.p==null?'–':n(p.p*p.q))+'</td><td class="sub">'+(K[p.k]||'')+(p.l!=null?' · '+p.l+' annonce(s)':'')+'</td></tr>'
  +(p.sub||[]).map(x=>part(x,ind+1)).join('');
 box.innerHTML='<p class="sub">Capture lue le '+d.t.slice(8,10)+'/'+d.t.slice(5,7)+' à '+d.t.slice(11)+'.</p>'+d.cards.map((c,k)=>
  '<h3>Case '+(k+1)+'</h3>'+c.items.flatMap(s=>byIcon[s]||[]).map(x=>
   '<div class="card" style="margin-top:8px"><div class="toolbar" style="margin:0;gap:14px;flex-wrap:wrap;align-items:center">'
   +'<span class="it"><img src="'+jEsc(x.s)+'" width="38" height="38" style="border-radius:6px" loading="lazy"><span><span class="nm" title="Cliquer pour copier">'+jEsc(x.n)+'</span>'
   +'<div class="sub">'+(PROF[x.prof]||x.prof)+' '+lvTxt(Math.max(1,x.m))+'</div></span></span>'
   +'<span class="badge b-mut">Annonces en vente : <b>'+x.l+'</b></span>'
   +'<span class="badge b-mut">Médiane 3 j : <b>'+n(x.med)+'</b></span>'
   +'<span class="badge b-ok">Prix de vente cible : <b>'+n(x.cible)+'</b></span></div>'
   +'<div class="wrap"><table><thead><tr><th>Ingrédient</th><th class="n">Qté</th><th class="n">Prix /u</th><th class="n">Sous-total</th><th>Origine</th></tr></thead><tbody>'
   +x.parts.map(p=>part(p,0)).join('')
   +'<tr><td><b>Total du craft</b>'+(x.q>1?' <span class="sub">(pour '+x.q+' objets : '+n(x.c*x.q)+')</span>':'')+'</td><td></td><td></td><td class="n"><b>'+(x.c==null?'incomplet':n(x.c))+'</b></td>'
   +'<td class="sub">cible = total × '+(1+SUPPLY_CFG.margin).toFixed(2).replace('.',',')+' ÷ '+(1-SUPPLY_CFG.tax).toFixed(2).replace('.',',')+'</td></tr>'
   +'</tbody></table></div></div>').join('')).join('')}
document.addEventListener('DOMContentLoaded',()=>supplyRender());
