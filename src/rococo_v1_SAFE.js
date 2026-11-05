(()=>{
/* ===================================================================================================
   rococo v1 — one shell, one turn engine.
   The approved pieces (v11 empty, v12 落笔中, tools_v2 notes/proof sheets, approval_v2 slip/question, sessions_v2 drawer and
   model layer) are already in the page; this script wires them into one app:
     views:  empty (v11)  ->  live (the scripted turn)  |  hist (finished v8 conversation)
     turn:   a mock event script (SCRIPT) is resolved into a timeline T; every visual is a function of turn time t
             (frame(t)), so a still is just frame(x). The two decisions (permission, question) are open entries in the
             script: until the user answers, their time is Infinity and nothing after them exists yet.
   =================================================================================================== */
const RM=matchMedia('(prefers-reduced-motion: reduce)');
const $=id=>document.getElementById(id);
const b=document.body;
const HASH=decodeURIComponent(location.hash.slice(1)).split(/[&,]/).filter(Boolean);
const has=k=>HASH.includes(k);
const cl=u=>Math.max(0,Math.min(1,u)),eo=u=>1-Math.pow(1-cl(u),3),eio=u=>{u=cl(u);return u<.5?4*u*u*u:1-Math.pow(-2*u+2,3)/2},sm=u=>{u=cl(u);return u*u*(3-2*u)};
const back=u=>{u=cl(u);const c=1.5;return 1+(c+1)*Math.pow(u-1,3)+c*Math.pow(u-1,2)};
const spring=(z,w,t)=>{if(t<=0)return 1;const wd=w*Math.sqrt(1-z*z);return Math.exp(-z*w*t)*(Math.cos(wd*t)+(z*w/wd)*Math.sin(wd*t))};
const now=()=>performance.now()/1000;
const EO='cubic-bezier(.22,1,.36,1)';

/* ================================ shell & views ================================ */
const stage=document.querySelector('.stage'),composer=document.querySelector('.composer');
const V={empty:$('vEmpty'),live:$('vLive'),hist:$('vHist')};
const thread=$('thLive'),scrollEl=V.live,thH=$('thHist');
const dsL=$('dsLive'),dsH=$('dsHist'),capB=$('rkCap');
const setCH=()=>stage.style.setProperty('--cH',composer.offsetHeight+'px');setCH();addEventListener('resize',setCH);
const LIVE_TITLE='流式渲染 · 合批与去重';
let view='empty',histTitle='重构聊天工作台的流式渲染';
const curSlip=()=>document.querySelector('.dw-ses.cur .dw-t');
const railIts=[...document.querySelectorAll('.rail .grp .it')];
const railOn=i=>railIts.forEach((e,k)=>e.classList.toggle('on',k===i));
let outT=0;
const showView=(v,o={})=>{
  capB.textContent=v==='hist'?(histTitle==='重构聊天工作台的流式渲染'?'流式渲染的重构':histTitle):v==='live'?LIVE_TITLE:'新的信笺';
  if(v===view)return;
  const from=V[view],to=V[v],fromEmpty=view==='empty';view=v;
  b.classList.remove('v-empty','v-live','v-hist');b.classList.add('v-'+v);
  dsL.style.display=v==='hist'?'none':'';dsH.style.display=v==='hist'?'':'none';
  if(v==='hist')histScroll(true);
  clearTimeout(outT);
  [from,to,...V.empty.querySelectorAll('.dsep,.invite,.tagcap,.tag')].forEach(e=>e.getAnimations().forEach(a=>a.cancel()));
  Object.values(V).forEach(e=>e.classList.remove('out'));
  if(v==='empty'&&window.__v11restart)window.__v11restart();
  if(RM.matches||o.instant){from.classList.remove('on');to.classList.add('on');return}
  from.classList.remove('on');from.classList.add('out');to.classList.add('on');
  let dly=120,hold=300;
  if(fromEmpty){ /* the empty letter lifts off like paper; the tags drop back */
    const hall=V.empty.querySelector('.hall');dly=250;hold=760;
    hall.querySelector('.dsep').animate([{opacity:1,translate:'0 0'},{opacity:0,translate:'0 -8px'}],{duration:300,easing:'cubic-bezier(.4,0,1,1)',fill:'forwards'});
    $('invite').animate([{opacity:1,translate:'0 0',rotate:'0deg',scale:'1'},{opacity:.9,translate:'0 -6px',rotate:'-.4deg',scale:'1.004',offset:.3},
      {opacity:0,translate:'0 -34px',rotate:'-1.4deg',scale:'.985'}],{duration:560,easing:'cubic-bezier(.45,0,.2,1)',fill:'forwards'});
    [hall.querySelector('.tagcap'),...hall.querySelectorAll('.tag')].forEach((e,k)=>e.animate([{opacity:1,translate:'0 0'},{opacity:0,translate:'0 10px'}],
      {duration:260,delay:30*k,easing:'cubic-bezier(.4,0,1,1)',fill:'forwards'}))}
  else from.animate([{opacity:1,translate:'0 0'},{opacity:0,translate:'0 6px'}],{duration:240,easing:'cubic-bezier(.4,0,1,1)',fill:'forwards'});
  to.animate([{opacity:0,translate:'0 10px'},{opacity:1,translate:'0 0'}],{duration:420,delay:dly,easing:EO,fill:'backwards'});
  outT=setTimeout(()=>{from.classList.remove('out');from.getAnimations().forEach(a=>a.cancel());
    V.empty.querySelectorAll('.dsep,.invite,.tagcap,.tag').forEach(e=>e.getAnimations().forEach(a=>a.cancel()))},hold)};

/* past conversation: wheel to read back, opens at its end */
let hs=0,hsT=0,hsRaf=0;
const hsMax=()=>{const l=thH.lastElementChild;if(!l)return 0;const h=l.getBoundingClientRect().bottom-thH.getBoundingClientRect().top;return Math.max(0,h-(V.hist.clientHeight-36-66))};
const histPaint=()=>{thH.style.transform=`translateY(${(-hs).toFixed(2)}px)`};
const histScroll=snap=>{if(snap){hsT=hs=hsMax();histPaint();return}
  if(!hsRaf){let l=now();const st=()=>{const n=now(),a=RM.matches?1:1-Math.exp(-(n-l)/.11);l=n;hs+=(hsT-hs)*a;if(Math.abs(hsT-hs)<.2)hs=hsT;histPaint();hsRaf=hs!==hsT?requestAnimationFrame(st):0};hsRaf=requestAnimationFrame(st)}};
V.hist.addEventListener('wheel',e=>{e.preventDefault();hsT=Math.max(0,Math.min(hsMax(),hsT+e.deltaY));histScroll()},{passive:false});

/* ================================ stickers ================================ */
/* the collage stickers are picked once per load (v8 script, plus two controlled ones from tools v2);
   they may sit on the user's words, never on Kimi's: guard pushes any that touch Kimi's text outward. */
(()=>{const pool=[...new Set([...document.querySelectorAll('.thread .rnd')].map(i=>i.src))];if(!pool.length)return;
 const R=(a,z)=>a+Math.random()*(z-a);const pick=()=>pool.splice(Math.floor(Math.random()*pool.length),1)[0]||pool[0];
 const put=(el,side,w)=>{const im=new Image();im.src=pick();im.className='rnd tv-stk v8pop';im.style.width=w+'px';im.style.setProperty('--r',R(-16,16).toFixed(1)+'deg');
  im.style[side]=(-w*R(.8,.9)).toFixed(0)+'px';im.style.top=(-w*R(.15,.35)).toFixed(0)+'px';el.appendChild(im)};
 put($('tvG'),'left',Math.round(R(38,46)));put($('tvSum'),'right',Math.round(R(42,52)))})();
thread.querySelectorAll('.rnd').forEach(im=>{im.style.setProperty('--pd','140ms');im.classList.add('v8pop')});
const guardIm=im=>{const el=im.parentNode;if(!el||!im.offsetWidth)return;
  const er=el.getBoundingClientRect();const rs=[];const tw=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);
  while(tw.nextNode()){const n=tw.currentNode;if(!n.data.trim())continue;const rg=document.createRange();rg.selectNodeContents(n);
    for(const q of rg.getClientRects())if(q.width>0)rs.push({l:q.left-er.left-4,r:q.right-er.left+4,t:q.top-er.top-3,b:q.bottom-er.top+3})}
  const sh=.1*im.offsetWidth;let L=im.offsetLeft+sh,Rr=im.offsetLeft+im.offsetWidth-sh;const Tt=im.offsetTop+sh,Bb=im.offsetTop+im.offsetHeight-sh;
  const hit=rs.filter(q=>q.r>L&&q.l<Rr&&q.b>Tt&&q.t<Bb);if(!hit.length)return;
  if(im.style.left!==''){const need=Rr-Math.min(...hit.map(q=>q.l));im.style.left=(parseFloat(im.style.left)-need).toFixed(0)+'px'}
  else{const need=Math.max(...hit.map(q=>q.r))-L;im.style.right=(parseFloat(im.style.right)-need).toFixed(0)+'px'}};
const guard=root=>(root?[...root.querySelectorAll(':scope>.rnd:not(.tv-stk)')]:[...document.querySelectorAll('.thread .row.in .rnd:not(.tv-stk)')]).forEach(guardIm);

/* ================================ the turn: elements ================================ */
const uRow=$('rkU'),uB=$('rkUb'),row=$('rkRow'),col=row.querySelector('.col'),who=$('rkWho'),pen=$('pen12'),penDots=[...pen.querySelectorAll('i b')];
const BB=[1,2,3,4,5,6].map(k=>$('rkB'+k));
const NT=id=>{const el=$(id),p=el.querySelector('.tn-p');return {el,p,h:el.querySelector('.tn-h'),ink:el.querySelector('.tv-tr .ink'),
  run:el.querySelector('.s-run'),ok:el.querySelector('.s-ok'),fail:el.querySelector('.s-fail'),tk:el.querySelector('.tv-tk'),x:el.querySelector('.tv-x'),
  hb:el.querySelector('.tv-ink'),meta:el.querySelector('.tn-h .meta'),cv:el.querySelector('.tv-cv'),pf:el.querySelector('.prf-w'),so:el.querySelector('.so-w'),tag:el.querySelector('.tv-ftag')}};
const R1=NT('tvR1'),R2=NT('tvR2'),R3=NT('tvR3'),A1=NT('rkA1'),E1=NT('tvE1'),E2=NT('tvE2'),S1=NT('tvS1'),S2=NT('tvS2'),E3=NT('tvE3'),S3=NT('tvS3');
const G=$('tvG'),GL=$('tvGL'),GB=$('tvGB'),SUM=$('tvSum'),SH=SUM.querySelector('.ts-h'),SW=$('tvSL'),scv=SH.querySelector('.tv-cv');
const fxC=$('rkFxC'),fxA=$('tvFxA'),fxB=$('tvFxB'),fxAa=$('tvFxAa'),fxAd=$('tvFxAd'),none=$('tvNone'),tot=$('tvTot'),tA=$('tvTa'),tD=$('tvTd');
const tds=[...dsL.querySelectorAll('.rk-td')],planNone=$('rkPlanNone'),planH=$('rkPlanH'),leaves=$('rkLeaves'),wts=[null,$('rkWt1'),$('rkWt2'),null];
const pcEl=$('rkPc'),ofEl=$('rkOf'),grI=$('rkGi'),grB=$('rkGb');
const flw=$('tvFlw'),flRot=$('tvFlRot'),pos=[...flw.querySelectorAll('.po')];
const slip=$('slip'),slPaper=$('slPaper'),slFull=$('slFull'),slRec=$('slRec'),slHair=$('slHair'),seal=$('seal');
const okB=$('slOk'),allB=$('slAll'),noB=$('slNo'),stOk=slip.querySelector('.sl-stamp.ok'),stNo=slip.querySelector('.sl-stamp.no');
const qc=$('qc'),qPaper=$('qPaper'),qFull=$('qFull'),qRec=$('qRec'),qHair=$('qHair'),qAns=$('qAns');
const opts=[...qc.querySelectorAll('.q-opt')],qSkip=$('qSkip'),qIn=$('qIn');
const qTick=$('qTick'),tkPen=qTick.querySelector('.pen'),tkBl=qTick.querySelector('.bleed'),qHead=[...qFull.children].filter(e=>!e.classList.contains('q-opts'));
const send=document.querySelector('.send'),sl0=send.querySelector('.sl.s0'),sl1=send.querySelector('.sl.s1'),sl2=send.querySelector('.sl.s2');
const stopI=$('apStop'),waitI=$('apWait'),stArc=$('apStArc'),wRing=$('apWRing'),hgG=$('apHg'),sandT=$('apSandT'),sandB=$('apSandB');
const sumH=$('rkSumH'),sumA=$('rkSumA'),sumD=$('rkSumD'),sumR=$('rkSumR');

/* ================================ text streaming (seeded chunks, ink settle — as approved) ================================ */
const setTxt=(el,txt)=>{const ims=[...el.querySelectorAll(':scope>img')];el.textContent=txt;ims.forEach(i=>el.appendChild(i))};
const wrap=root=>{const out=[];const tw=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);const ns=[];while(tw.nextNode())ns.push(tw.currentNode);
  ns.forEach(n=>{const f=document.createDocumentFragment();for(const c of n.data){const e=document.createElement('span');e.className='ch';e.textContent=c;f.appendChild(e);out.push({el:e,c})}
   n.parentNode.replaceChild(f,n)});return out};
const sched=(chars,sd)=>{let seed=sd;const rnd=()=>{seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296};
  let t=0,i=0;const P='，。：；！？、';
  while(i<chars.length){const n=P.includes(chars[i].c)?1:(rnd()<.45?1:(rnd()<.7?2:3));const d=n*.034;
    for(let k=0;k<n&&i<chars.length;k++,i++)chars[i].r=t+d*(k+1)/n;
    t+=d+n*.022*(.7+rnd()*.8)+(P.includes(chars[i-1].c)?.2:0)+(rnd()<.08?.15:0)}
  const end=chars[chars.length-1].r;chars.forEach(c=>c.r/=end);return chars};
const place=(chars,a,z)=>chars.forEach(c=>c.a=isFinite(a)&&isFinite(z)?a+c.r*(z-a):Infinity);
const TXT0=BB.map(e=>e.textContent);
const C=BB.map((e,k)=>sched(wrap(e),20261427+k*97));
const reTxt=(k,txt)=>{setTxt(BB[k],txt);C[k]=sched(wrap(BB[k]),20261427+k*97);BB[k]._guard=1};
const charFrame=(chars,t)=>{const rm=RM.matches;let last=null;
  for(const c of chars){const age=t-c.a,e=c.el;
    if(!(age>=0)){if(e._s!==0){e.className='ch';e.removeAttribute('style');e._s=0}continue}
    last=c;const D=rm?.12:.27;
    if(age>=D){if(e._s!==2){e.className='ch on';e.removeAttribute('style');e._s=2}continue}
    const k=eo(age/D);e.className='ch on';e._s=1;
    if(rm){e.style.cssText=`opacity:${k.toFixed(3)}`;continue}
    e.style.cssText=`opacity:${Math.pow(k,.7).toFixed(3)};position:relative;top:${(-1.6*(1-k)).toFixed(2)}px;`+
      `-webkit-text-fill-color:color-mix(in srgb,currentColor ${(k*k*100).toFixed(0)}%,transparent);`+
      `text-shadow:0 0 ${(5*(1-k)).toFixed(2)}px color-mix(in srgb,currentColor ${(70*(1-k)).toFixed(0)}%,transparent)`}
  return last};

/* ================================ the mock event script ================================
   [key, anchor (null = previous entry), offset s, event, payload]. Entries with payload.wait are the user's decisions:
   until answered their time is Infinity (interactive) or the auto default (stills / AUTO). A real backend would push these
   same events (assistant.delta / tool.start / tool.end / permission.request / question ...) instead of the fixed offsets. */
const SCRIPT=[
 ['u',null,.35,'user.message'],
 ['b1',null,.65,'assistant.delta',{el:'rkB1'}],['c1a',null,.1],['c1z',null,.65],
 ['r1',null,.15,'tool.start',{el:'tvR1',tool:'ReadFile'}],['r1d',null,.55,'tool.end',{el:'tvR1'}],
 ['r2',null,.1,'tool.start',{el:'tvR2',tool:'Grep'}],['r2d',null,.45,'tool.end',{el:'tvR2'}],
 ['r3',null,.1,'tool.start',{el:'tvR3',tool:'ReadFile'}],['r3d',null,.45,'tool.end',{el:'tvR3'}],
 ['gf0',null,.2,'tools.gather',{el:'tvG'}],['gf1',null,.55],
 ['b2',null,.05,'assistant.delta',{el:'rkB2'}],['c2a',null,.1],['c2z',null,1.6],
 ['sl',null,.3,'permission.request',{el:'slip',tool:'StrReplaceFile',path:'src/renderer/engine/adapter.ts'}],
 ['pr','sl',3.1,'permission.reply',{wait:'verdict'}],
 ['lift','pr',.12],['trav','pr',.32],['press','pr',.6],['ink','pr',.65],['back','pr',.82],['rest','pr',1.45],['cp0','pr',1.95],['cp1','pr',2.55],
 ['a1','cp1',.05,'tool.start',{el:'rkA1',tool:'StrReplaceFile',if:'allowed'}],['a1d',null,.55,'tool.end',{el:'rkA1'}],
 ['b3',null,.15,'assistant.delta',{el:'rkB3'}],['c3a',null,.1],['c3z',null,1.2],
 ['q',null,.2,'question',{el:'qc'}],
 ['sel','q',2.55,'question.reply',{wait:'choice'}],
 ['tk0','sel',.1],['tk1','sel',.55],['stk','sel',.42],['tag','sel',.46],['g0','sel',1.65],['g1','sel',2.2],['qc0','sel',2.08],['qc1','sel',2.58],
 ['b4','qc1',.12,'assistant.delta',{el:'rkB4'}],['c4a',null,.1],['c4z',null,1.0],
 ['e1','c4z',.1,'tool.start',{el:'tvE1',tool:'StrReplaceFile'}],['e1d','e1',.6,'tool.end',{el:'tvE1'}],
 ['p1o0','e1',.65,'diff.open',{el:'tvP1'}],['p1o1','e1',1.35],['p1c0','e1',2.75,'diff.fold'],['p1c1','e1',3.2],
 ['e2','e1',3.3,'tool.start',{el:'tvE2',tool:'StrReplaceFile'}],['e2d','e1',3.75,'tool.end',{el:'tvE2'}],
 ['s1','e1',3.85,'tool.start',{el:'tvS1',tool:'Shell'}],['s1l0','e1',4.02],['s1l1','e1',4.2],['s1l2','e1',4.55],['s1d','e1',4.55,'tool.end',{el:'tvS1'}],['s1f0','e1',4.95],['s1f1','e1',5.35],
 ['s2','e1',5.0,'tool.start',{el:'tvS2',tool:'Shell'}],['s2l0','e1',5.25],['s2l1','e1',5.55],['s2l2','e1',5.78],['s2l3','e1',6.0],['s2d','e1',6.0,'tool.fail',{el:'tvS2'}],
 ['b5','e1',6.65,'assistant.delta',{el:'rkB5'}],['c5a','e1',6.75],['c5z','e1',7.65],
 ['e3','e1',7.75,'tool.start',{el:'tvE3',tool:'StrReplaceFile'}],['e3d','e1',8.15,'tool.end',{el:'tvE3'}],
 ['s3','e1',8.25,'tool.start',{el:'tvS3',tool:'Shell'}],['s3l0','e1',8.45],['s3l1','e1',8.7],['s3l2','e1',9.0],['s3d','e1',9.0,'tool.end',{el:'tvS3'}],
 ['b6','e1',9.2,'assistant.delta',{el:'rkB6'}],['c6a','e1',9.3],['c6z','e1',10.8],
 ['sum','e1',10.9,'turn.summary',{el:'tvSum'}],['so0','e1',11.55],['so1','e1',12.0],['END','e1',12.8,'turn.end']];
const DEC={verdict:null,choice:null};let AUTO=false;
const mkT=()=>{const T={};let prev=0;for(const [k,an,off,,p] of SCRIPT){const base=an?T[an]:prev;let v=base+off;
    if(p&&p.wait){const d=DEC[p.wait];v=d?d.t:(AUTO?base+off:Infinity)}T[k]=v;prev=v}return T};
let T={};
const rebuild=()=>{T=mkT();C.forEach((c,k)=>place(c,T['c'+(k+1)+'a'],T['c'+(k+1)+'z']))};
let verdict='ok',choice=1;

/* ================================ shared frame helpers (tools v2 / approval v2) ================================ */
const arrive=(el,t,t0,dur=.5,dy=18)=>{
  if(!(t>=t0)){if(el.style.display!=='none')el.style.display='none';return false}
  if(el.style.display==='none')el.style.display='';const u=(t-t0)/dur;
  if(RM.matches){el.style.opacity=cl(u*2.5).toFixed(3);el.style.transform='none';return true}
  if(u>=1.6){el.style.opacity='';el.style.transform='';return true}
  const y=dy*spring(.8,11,(t-t0)),r=-.5*spring(.5,13,(t-t0));
  el.style.opacity=cl(u*1.9).toFixed(3);el.style.transform=`translateY(${y.toFixed(2)}px) rotate(${r.toFixed(3)}deg)`;return true};
const M={},H={};
const hideable=()=>[uRow,who,...col.children,...GB.querySelectorAll('.tn')];
const showAll=fn=>{const hid=hideable().filter(e=>e.style.display==='none');hid.forEach(e=>e.style.display='');const r=fn();hid.forEach(e=>e.style.display='none');return r};
const measure=()=>showAll(()=>{
  const ws=[...col.querySelectorAll('.prf-w, .so-w'),SW,GB];const hs0=ws.map(w=>w.style.height);ws.forEach(w=>w.style.height='auto');
  M.p1=E1.pf.firstElementChild.offsetHeight+3;M.p2=E2.pf.firstElementChild.offsetHeight+3;M.p3=E3.pf.firstElementChild.offsetHeight+3;
  M.sl=SW.firstElementChild.offsetHeight+12;M.gb=GB.offsetHeight;M.nt=R1.el.offsetHeight;
  [S1,S2,S3].forEach(S=>{const so=S.so.firstElementChild;S._pad=so.offsetHeight-so.children.length*19+11;S._n=so.children.length});
  ws.forEach((w,k)=>w.style.height=hs0[k]);
  const tr=[slip,qc,...opts].map(e=>e.style.transform);[slip,qc,...opts].forEach(e=>e.style.transform='');
  const ph=[slPaper.style.height,qPaper.style.height];slPaper.style.height='';qPaper.style.height='';
  H.sl=slFull.offsetHeight;H.q=qFull.offsetHeight;
  const sx=slip.offsetWidth-20-32,sy=-18+32;const sr=slip.getBoundingClientRect(),ir=stOk.getBoundingClientRect();H.dx=ir.left-sr.left+ir.width/2-sx;H.dy=ir.top-sr.top+ir.height/2-sy;
  const qr=qc.getBoundingClientRect();H.op=opts.map(o=>{const r=o.getBoundingClientRect();return {x:r.left-qr.left,y:r.top-qr.top,w:r.width,h:r.height}});
  const kr=qRec.querySelector('.rk').getBoundingClientRect();H.rk={x:kr.left-qr.left+kr.width/2,y:kr.top-qr.top+kr.height/2};
  H.tl=tkPen.getTotalLength();
  slPaper.style.height=ph[0];qPaper.style.height=ph[1];[slip,qc,...opts].forEach((e,k)=>e.style.transform=tr[k])});
/* user toggles on notes / lines / bar: openness glides from where it was (tools v2) */
const TG={};let NOW=0;
const open=(key,auto)=>{const g=TG[key];let v=auto;if(g){const u=RM.matches?1:eio((NOW-g.t0)/.5);v=g.from+(g.to-g.from)*u}TG['_'+key]=v;return v};
const toggle=key=>{const v=TG['_'+key]||0;TG[key]={from:v,to:v>.5?0:1,t0:NOW}};
const runP=(t,t0,td)=>t<td?92*(1-Math.exp(-3*(t-t0)/Math.max(.2,td-t0))):92+8*eo((t-td)/.22);
const noteFrame=(N,t,t0,td,fail)=>{
  const on=arrive(N.el,t,t0,.42,14);if(!on)return false;const rm=RM.matches;
  const running=t<td,done=!running;
  N.el.classList.toggle('failed',!!fail&&done);
  const p=runP(t,t0,td),fade=done?cl((t-td-.22)/.4):0;
  const per=2*(N.p.offsetWidth+N.p.offsetHeight);
  if(rm){N.ink.style.opacity=running?.9:0;N.ink.style.strokeDasharray=per+' 0'}
  else{N.ink.style.strokeDasharray=`${(p/100*per).toFixed(1)} ${((100-p)/100*per+1).toFixed(1)}`;N.ink.style.opacity=((running?cl((t-t0)/.15):1-fade)*.85).toFixed(3);
   N.ink.style.stroke=fail&&done?'#B07A8C':'#6A7EA8'}
  if(N.meta)N.meta.style.opacity=done?(rm?1:cl((t-td-.1)/.35)).toFixed(3):0;
  const hd=N.el._hd||(N.el._hd=N.el.querySelector('.tv-tr .hd')),hb2=N.el._hb2||(N.el._hb2=N.el.querySelector('.tv-tr .hb2'));
  if(!rm&&running){const w=N.p.offsetWidth-1.2,h=N.p.offsetHeight-1.2;let d=p/100*per%(2*(w+h)),x,y;
    if(d<w){x=d;y=0}else if((d-=w)<h){x=w;y=d}else if((d-=h)<w){x=w-d;y=h}else{d-=w;x=0;y=h-d}
    x+=.6;y+=.6;const o=cl((t-t0)/.15);[hd,hb2].forEach(c=>{c.setAttribute('cx',x.toFixed(1));c.setAttribute('cy',y.toFixed(1));c.style.opacity=o.toFixed(3)});
    hb2.setAttribute('r',(4.2+1.2*Math.sin((t-t0)*2*Math.PI/1.3)).toFixed(2))}
  else{hd.style.opacity=0;hb2.style.opacity=0}
  N.run.style.opacity=running?1:(rm?0:(1-cl((t-td)/.15)).toFixed(3));
  if(N.hb&&running){const k=.5+.5*Math.sin((t-t0)*2*Math.PI/1.3);N.hb.style.setProperty('--hb',(rm?1:.75+.5*k).toFixed(3));N.hb.style.opacity=rm?1:(.65+.35*k).toFixed(3)}
  const st=fail?N.fail:N.ok;const oth=fail?N.ok:N.fail;if(oth)oth.style.opacity=0;
  if(done){const u=rm?1:cl((t-td)/.3);st.style.opacity=cl(u*3).toFixed(3);
    if(!fail)N.tk.style.setProperty('--dk',(1-eo(u)).toFixed(3));
    else{N.x.style.setProperty('--dk',(1-eo(u*1.8)).toFixed(3));N.x.style.setProperty('--dk2',(1-eo(u*1.8-.8)).toFixed(3))}}
  else st.style.opacity=0;
  return true};
const flip=(W,Hn,u,pin)=>{const rm=RM.matches,pf=W.firstElementChild,sh=pf.querySelector('.prf-sh');
  if(u<=0.0005){W.style.height='0px';W.style.visibility='hidden';W.classList.remove('on');if(pin)pin.style.opacity=0;return}
  W.style.visibility='';W.classList.add('on');
  if(rm){W.style.height=(u>.5?Hn:0)+'px';pf.style.transform='none';pf.style.opacity=u>.5?1:0;sh.style.opacity=0;if(pin)pin.style.opacity=u>.5?1:0;return}
  const a=-82*(1-eo(u));W.style.height=(Hn*Math.cos(a*Math.PI/180)*cl(u*4)).toFixed(2)+'px';pf.style.transform=`rotateX(${a.toFixed(2)}deg) translateY(${(-6*(1-u)).toFixed(2)}px)`;pf.style.opacity=cl(u*4).toFixed(3);
  sh.style.opacity=(.9*(1-sm(u))).toFixed(3);
  if(pin){const pu=cl((u-.55)/.45);pin.style.opacity=cl(pu*3).toFixed(3);pin.style.transform=`translate(${(6*(1-eo(pu))).toFixed(2)}px,${(-9*(1-eo(pu))).toFixed(2)}px) rotate(${(14*(1-eo(pu))).toFixed(2)}deg)`}};
const shellOut=(S,t,lt,fold)=>{let h=0;const ls=S.so.firstElementChild.children;
  [0,...lt].forEach((a,k)=>{const el=ls[k];if(!el)return;const u=k===0?1:(RM.matches?(t>=a?1:0):eo((t-a)/.2));
    el.style.opacity=(k===0?1:cl(u*1.6)).toFixed(3);el.style.transform=`translateX(${(-4*(1-u)).toFixed(2)}px)`;h+=19*(k===0?1:u)});
  return (S._pad+h)*(1-fold)};
const foldP=(paper,full,rec,t,c0,c1,Hf)=>{
  const u=RM.matches?(t>=(c0+c1)/2?1:0):eio((t-c0)/(c1-c0));
  if(!(u>0)){paper.style.setProperty('--rule',1);paper.style.height='';full.style.opacity='';full.style.transform='';rec.style.opacity=0;rec.style.pointerEvents='none';return 0}
  paper.style.height=(Hf+(36-Hf)*u).toFixed(2)+'px';
  full.style.opacity=(1-cl((u-.22)/.42)).toFixed(3);full.style.transform=`translateY(${(-14*u).toFixed(2)}px) scaleY(${(1-.04*u).toFixed(4)})`;
  rec.style.opacity=cl((u-.5)/.45).toFixed(3);paper.style.setProperty('--rule',(1-cl(u/.6)).toFixed(3));rec.style.pointerEvents=u>=1?'auto':'none';return u};
/* question card: confirmed choice (approval v2) */
const qConfirm=(t,rm)=>{const ch=choice>=0&&choice<=2?choice:-1;
  const dimU=t>=T.sel?(rm?1:eo((t-T.sel-.05)/.5)):0, gU=t>=T.g0?(rm?(t>=T.qc0?1:0):eio((t-T.g0)/(T.g1-T.g0))):0;
  const liftU=t>=T.sel?(rm?0:eo((t-T.sel)/.4)):0;
  opts.forEach((o,k)=>{const tag=o.querySelector('.q-tag'),stk=o.querySelector('.q-stk'),rec=o.querySelector('.q-rec');
    if(!(t>=T.sel)||ch<0){o.style.transform='';o.style.opacity='';o.style.zIndex='';o.style.boxShadow='';tag.style.opacity=0;stk.style.opacity=0;if(rec)rec.style.opacity='';return}
    if(k===ch){const y=-5*liftU+3*gU,r=-.5*liftU*(1-gU);o.style.zIndex=4;o.style.opacity='';
      o.style.transform=rm?'none':`translateY(${y.toFixed(2)}px) rotate(${r.toFixed(3)}deg)`;
      o.style.boxShadow=rm?'':`0 ${(6+8*liftU*(1-gU)).toFixed(1)}px ${(10+8*liftU*(1-gU)).toFixed(1)}px -${(8+2*liftU).toFixed(1)}px rgba(40,52,95,.45),0 1px 2px rgba(40,52,95,.12),inset 0 1px 2px rgba(40,52,95,.10),inset 0 0 0 1px rgba(124,143,184,.55)`;
      const su=t>=T.stk?(rm?1:cl((t-T.stk)/.32)):0;stk.style.opacity=cl(su*2.2).toFixed(3);
      stk.style.transform=`rotate(${(-14+6*eo(su)).toFixed(2)}deg) scale(${(rm?1:1.35-.35*eo(su)).toFixed(3)})`;
      stk.style.filter=`drop-shadow(0 ${(1+3*(1-eo(su))).toFixed(2)}px ${(1+3*(1-eo(su))).toFixed(2)}px rgba(56,68,108,${(.25+.1*(1-su)).toFixed(3)}))`;
      const au=t>=T.tag?(rm?1:cl((t-T.tag)/.42)):0;tag.style.opacity=cl(au*3).toFixed(3);
      tag.style.clipPath=rm?'none':`inset(-4px ${(100-100*eio(au)).toFixed(2)}% -4px -4px)`;
      tag.style.transform=`rotate(${(3.2-1.2*eo(au)).toFixed(2)}deg) translateY(${(rm?0:-2*(1-eo(au))).toFixed(2)}px)`;
      if(rec)rec.style.opacity=(1-cl(au*2.5)).toFixed(3)}
    else{const sd=k<ch?-1:1,d=Math.abs(k-ch);
      const fx=sd*(7+3*d)*dimU,fy=4*dimU,fr=sd*1.5*dimU,fs=1-.03*dimU;
      const gx=(H.op[ch].x-H.op[k].x)+sd*(5+2*d),gy=(H.op[ch].y-H.op[k].y)+4+2*d,gr=k<ch?-(2.1+.7*(d-1)):(1.7+.7*(d-1)),gs=.985;
      const x=fx+(gx-fx)*gU,y=fy+(gy-fy)*gU,r=fr+(gr-fr)*gU,sc2=fs+(gs-fs)*gU;
      o.style.zIndex=3-d;o.style.opacity=(rm?(1-.45*dimU)*(1-gU):1-.45*dimU+.2*gU).toFixed(3);
      o.style.transform=rm?'none':`translate(${x.toFixed(2)}px,${y.toFixed(2)}px) rotate(${r.toFixed(3)}deg) scale(${sc2.toFixed(4)})`;o.style.boxShadow='';
      tag.style.opacity=0;stk.style.opacity=0;if(rec)rec.style.opacity=(1-dimU*.6).toFixed(3)}});
  const hq=t>=T.sel?.15*dimU+.25*gU:0;qHead.forEach(e=>e.style.opacity=(1-hq).toFixed(3));
  return gU};
const qTickPos=(t,rm)=>{const ch=choice>=0&&choice<=2?choice:-1;qRec.classList.toggle('inkrk',ch>=0);
  if(ch<0||!(t>=T.tk0-(rm?.1:0))){qTick.style.opacity=0;return}
  const c=H.op[ch],liftU=rm?0:eo((t-T.sel)/.4),gU=t>=T.g0&&!rm?eio((t-T.g0)/(T.g1-T.g0)):0;
  const x0=c.x+c.w-46,y0=c.y+10-5*liftU+3*gU;
  const fu=rm?(t>=(T.qc0+T.qc1)/2?1:0):eio((t-T.qc0)/(T.qc1-T.qc0));
  const ff=qFull.style.transform?-14*fu:0;
  const s1=.52,x1=H.rk.x-18*s1+.8,y1=H.rk.y-17*s1-.6;
  const x=x0+(x1-x0)*fu,y=(y0+ff)+(y1-(y0+ff))*fu,sc2=1+(s1-1)*fu;
  qTick.style.opacity=1;qTick.style.transform=`translate(${x.toFixed(2)}px,${(y-(fu>0&&fu<1?10*Math.sin(Math.PI*fu):0)).toFixed(2)}px) scale(${sc2.toFixed(4)})`;
  const L=H.tl||60,du=rm?1:eio((t-T.tk0)/(T.tk1-T.tk0));
  tkPen.style.strokeDasharray=`${L+2} ${L+2}`;tkPen.style.strokeDashoffset=((L+2)*(1-du)).toFixed(2);
  const settle=rm?1:cl((t-T.tk0-.25)/.7);
  tkPen.setAttribute('stroke-width',(2.5+.5*(1-settle)*cl(du*3)+1.6*fu).toFixed(2));
  tkBl.style.strokeDasharray=`${L+2} ${L+2}`;tkBl.style.strokeDashoffset=((L+2)*(1-cl(du*1.02-.02))).toFixed(2);
  tkBl.style.opacity=(rm?.12:(.3*(1-settle)+.13)*cl(du*2)*(1-.6*fu)).toFixed(3);
  tkBl.setAttribute('stroke-width',(5.2+1.8*settle).toFixed(2))};

/* ================================ frame(t) ================================ */
let sc=-1,lastT=-1,manual=0,lastTg=0,cvBusy=0,cvWait=0;
const target=()=>{const ch=[...col.children].filter(e=>e.style.display!=='none'&&e!==who);let lastEl=ch[ch.length-1];
  if(!lastEl)lastEl=uRow.style.display==='none'?null:uRow;if(!lastEl)return 0;
  const bot=lastEl.getBoundingClientRect().bottom+Math.max(0,sc-manual);const vb=scrollEl.getBoundingClientRect().bottom-66;return Math.max(0,bot-vb)};
const roman=['i','ii','iii','iv'];
const frame=t=>{if(!M.p1)measure();const rm=RM.matches;
  if(t<lastT-.001){sc=-1;manual=0}
  /* user bubble */
  arrive(uRow,t,T.u,.45,16);
  /* Kimi row */
  arrive(who,t,T.b1-.1,.4,10);
  arrive(BB[0],t,T.b1,.4);const l1=charFrame(C[0],t);
  arrive(G,t,T.r1,.42,14);
  noteFrame(R1,t,T.r1,T.r1d);noteFrame(R2,t,T.r2,T.r2d);noteFrame(R3,t,T.r3,T.r3d);
  const g=open('grp',t>=T.gf0?(rm?(t>=T.gf1?1:0):eio((t-T.gf0)/(T.gf1-T.gf0))):0);
  const ns=[R1,R2,R3],step=M.nt+8;
  if(g<=0.0005){GB.style.height='';GL.style.opacity=0;GL.style.pointerEvents='none';ns.forEach(N=>{N.el.style.zIndex=''});GL.setAttribute('aria-expanded','true');GL.querySelector('.tv-cv').style.setProperty('--cv','180deg')}
  else{GB.style.height=(M.gb+(38-M.gb)*g).toFixed(2)+'px';
    ns.forEach((N,k)=>{if(N.el.style.display==='none')return;const y=-k*step*g,r=rm?0:(k===1?-1.1:k===2?1.4:0)*Math.sin(Math.PI*cl(g*1.15));
      N.el.style.transform=`translateY(${y.toFixed(2)}px) rotate(${r.toFixed(3)}deg) scale(${(1-.015*k*g).toFixed(4)})`;N.el.style.opacity=(1-cl((g-.45)/.4)).toFixed(3);N.el.style.zIndex=3-k});
    GL.style.opacity=cl((g-.55)/.4).toFixed(3);GL.style.pointerEvents=g>.9?'auto':'none';GL.setAttribute('aria-expanded',g>.5?'false':'true');
    GL.querySelector('.tv-cv').style.setProperty('--cv',`${(180*(1-g)).toFixed(1)}deg`)}
  arrive(BB[1],t,T.b2,.4);const l2=charFrame(C[1],t);
  /* ---- permission slip ---- */
  arrive(slip,t,T.sl,.5,22);
  const pend=t>=T.sl&&t<T.pr+.12;
  const breath=rm?.5:.5+.5*Math.sin((t-T.sl)*2*Math.PI/2.6-Math.PI/2);
  slHair.style.opacity=pend?(cl((t-T.sl-.35)/.4)*(.18+.42*breath)).toFixed(3):(t<T.cp0&&t>=T.pr?(.6*(1-cl((t-T.pr)/.4))*.5).toFixed(3):0);
  const pb=verdict==='all'?allB:verdict==='no'?noB:okB;
  const pu=t>=T.pr&&t<T.pr+.25?Math.sin(Math.PI*cl((t-T.pr)/.25)):0;
  okB.style.setProperty('--oky',(pb===okB?1.2*pu:0).toFixed(2)+'px');okB.style.setProperty('--oks',(pb===okB?1-.025*pu:1).toFixed(4));
  let sx=0,sy=0,ss=1,sr=0,so=1,shd=.22;
  if(!rm){
    if(t>=T.lift&&t<T.trav){const u=eo((t-T.lift)/(T.trav-T.lift));sy=-10*u;ss=1+.08*u;sr=-8*u;shd=.22+.12*u}
    else if(t>=T.trav&&t<T.press){const u=eio((t-T.trav)/(T.press-T.trav));sx=H.dx*u;sy=-10+(H.dy+10-16)*u-14*Math.sin(Math.PI*u);ss=1.08+.12*u;sr=-8+2*u;shd=.34+.06*u}
    else if(t>=T.press&&t<T.back){const u=(t-T.press)/(T.back-T.press);sx=H.dx;sy=H.dy-16+16*Math.sin(Math.PI*Math.min(1,u*1.6));ss=1.2-.26*Math.sin(Math.PI*Math.min(1,u*1.6));sr=-6;shd=.1}
    else if(t>=T.back&&t<T.cp0){const u=eio((t-T.back)/(T.rest-T.back-.05));sx=H.dx*(1-u);sy=(H.dy-16)*(1-u)-12*Math.sin(Math.PI*u);ss=1.2-.2*u;sr=-6+6*u;shd=.3-.08*u}}
  if(t>=T.cp0){so=1-cl((t-T.cp0)/(rm?.05:.3));ss*=1-.3*cl((t-T.cp0)/.3)}
  seal.style.transform=`translate(${sx.toFixed(2)}px,${sy.toFixed(2)}px) rotate(${sr.toFixed(2)}deg) scale(${ss.toFixed(3)})`;
  seal.style.opacity=so.toFixed(3);seal.style.filter=`drop-shadow(0 ${(3+10*(shd-.22)/.18).toFixed(1)}px ${(3+8*(shd-.22)/.18).toFixed(1)}px rgba(40,52,95,${shd.toFixed(3)}))`;
  const st=verdict==='no'?stNo:stOk,stO=verdict==='no'?stOk:stNo;stO.style.opacity=0;
  const ti=rm?T.pr+.2:T.ink;
  if(t>=ti){const u=cl((t-ti)/(rm?.25:.18));st.style.opacity=(.88*u).toFixed(3);
    st.style.transform=`rotate(-8deg) scale(${(1.05-.05*eo(u)).toFixed(3)})`;st.style.filter=`blur(${(1.2*(1-u)).toFixed(2)}px)`}else st.style.opacity=0;
  if(!rm&&t>=T.press&&t<T.press+.2){slPaper.style.transform=`translateY(${(1.2*Math.sin(Math.PI*(t-T.press)/.2)).toFixed(2)}px)`}else slPaper.style.transform='';
  foldP(slPaper,slFull,slRec,t,T.cp0,T.cp1,H.sl);
  /* the allowed edit runs as a paper note */
  if(verdict!=='no')noteFrame(A1,t,T.a1,T.a1d);else A1.el.style.display='none';
  arrive(BB[2],t,T.b3,.4);const l3=charFrame(C[2],t);
  /* ---- question card ---- */
  arrive(qc,t,T.q,.5,22);
  const qPend=t>=T.q&&t<T.sel+.1;
  qHair.style.opacity=qPend?(cl((t-T.q-.35)/.4)*(.18+.42*(rm?.5:.5+.5*Math.sin((t-T.q)*2*Math.PI/2.6-Math.PI/2)))).toFixed(3):0;
  const selU=t>=T.sel?eo((t-T.sel)/.3):0;
  opts.forEach((o,k)=>{const on=k===choice&&t>=T.sel;o.classList.toggle('sel',on);o.setAttribute('aria-checked',on);o.style.setProperty('--rs',on?(rm?1:back(selU)).toFixed(3):0)});
  qConfirm(t,rm);
  foldP(qPaper,qFull,qRec,t,T.qc0,T.qc1,H.q);qTickPos(t,rm);
  arrive(BB[3],t,T.b4,.4);const l4=charFrame(C[3],t);
  /* ---- edits, proof sheets, shell receipts ---- */
  noteFrame(E1,t,T.e1,T.e1d);
  const p1=open('p1',t<T.p1o0?0:t<T.p1c0?(rm?1:eo((t-T.p1o0)/(T.p1o1-T.p1o0))):(rm?(t>=T.p1c1?0:1):1-eio((t-T.p1c0)/(T.p1c1-T.p1c0))));
  flip(E1.pf,M.p1,p1,E1.pf.querySelector('.tv-pin'));E1.cv.style.setProperty('--cv',`${(180*p1).toFixed(1)}deg`);
  noteFrame(E2,t,T.e2,T.e2d);const p2=open('p2',0);flip(E2.pf,M.p2,p2,E2.pf.querySelector('.tv-pin'));E2.cv.style.setProperty('--cv',`${(180*p2).toFixed(1)}deg`);
  const s1l=[T.s1l0,T.s1l1,T.s1l2],s2l=[T.s2l0,T.s2l1,T.s2l2,T.s2l3],s3l=[T.s3l0,T.s3l1,T.s3l2];
  if(noteFrame(S1,t,T.s1,T.s1d)){const f=open('o1',1-(t>=T.s1f0?(rm?1:eio((t-T.s1f0)/(T.s1f1-T.s1f0))):0));S1.so.style.height=shellOut(S1,t,s1l,1-f).toFixed(2)+'px';S1.cv.style.setProperty('--cv',`${(180*f).toFixed(1)}deg`)}
  if(noteFrame(S2,t,T.s2,T.s2d,true)){const f=open('o2',1);S2.so.style.height=shellOut(S2,t,s2l,1-f).toFixed(2)+'px';S2.cv.style.setProperty('--cv',`${(180*f).toFixed(1)}deg`);
    const au=t>=T.s2d+.12?(rm?1:cl((t-T.s2d-.12)/.4)):0;S2.tag.style.opacity=cl(au*3).toFixed(3);
    S2.tag.style.clipPath=rm?'none':`inset(-4px -4px ${(100-100*eio(au)).toFixed(2)}% -4px)`;S2.tag.style.transform=`rotate(${(2.2-1*eo(au)).toFixed(2)}deg)`}
  arrive(BB[4],t,T.b5,.4);const l5=charFrame(C[4],t);
  noteFrame(E3,t,T.e3,T.e3d);const p3=open('p3',0);flip(E3.pf,M.p3,p3,E3.pf.querySelector('.tv-pin'));E3.cv.style.setProperty('--cv',`${(180*p3).toFixed(1)}deg`);
  if(noteFrame(S3,t,T.s3,T.s3d)){const f=open('o3',1);S3.so.style.height=shellOut(S3,t,s3l,1-f).toFixed(2)+'px';S3.cv.style.setProperty('--cv',`${(180*f).toFixed(1)}deg`)}
  arrive(BB[5],t,T.b6,.4);const l6=charFrame(C[5],t);
  if(arrive(SUM,t,T.sum,.45,14)){const so2=open('sl',t>=T.so0?(rm?1:eio((t-T.so0)/(T.so1-T.so0))):0);
    SW.style.height=(M.sl*so2).toFixed(2)+'px';SW.firstElementChild.style.opacity=cl(so2*1.6).toFixed(3);
    SW.firstElementChild.style.transform=rm?'none':`perspective(800px) rotateX(${(-40*(1-eo(so2))).toFixed(2)}deg)`;SW.firstElementChild.style.transformOrigin='50% 0';
    scv.style.setProperty('--cv',`${(180*so2).toFixed(1)}deg`);SH.setAttribute('aria-expanded',so2>.5)}
  /* re-guard a bubble whose words changed with the user's answer, the first time it shows */
  BB.forEach(e=>{if(e._guard&&e.style.display!=='none'){e._guard=0;guard(e)}});
  /* ---- dossier ---- */
  const started=t>=T.b1-.1;
  planNone.style.display=started?'none':'';
  const ph=[T.r3d,verdict==='no'?T.cp1:T.a1d,T.e2d,T.s3d];let k=0;while(k<4&&t>=ph[k])k++;
  tds.forEach((e,i)=>{const a=T.b1+.08*i;e.classList.toggle('rk-on',t>=a);if(t>=a){const u=rm?1:eo((t-a)/.45);e.style.opacity=u.toFixed(3);e.style.transform=u>=1?'':`translateY(${(6*(1-u)).toFixed(2)}px)`}
    const s3=i<k?'ok':i===k?'now':'todo';if(e._st!==s3){e._st=s3;e.classList.remove('ok','now','todo');e.classList.add(s3);
    e.querySelector('.mk').innerHTML=s3==='ok'?window.__rkCheck:s3==='now'?'✦':'◇'}});
  planH.textContent=started?(k>=4?'iv':roman[k])+' of iv':'—';
  const waitA=t>=T.sl+.3&&t<T.pr,waitQ=t>=T.q+.3&&t<T.sel;
  tds[1].classList.toggle('ap-hold',waitA);tds[2].classList.toggle('ap-hold',waitQ);
  const w1=waitA?cl((t-T.sl-.3)/.35)*(1-cl((t-T.pr+.15)/.15)):0,w2=waitQ?cl((t-T.q-.3)/.35)*(1-cl((t-T.sel+.15)/.15)):0;
  wts[1].style.opacity=w1.toFixed(3);wts[2].style.opacity=w2.toFixed(3);
  /* the waiting tag hangs under its plan line: make room so it never sits on the next line */
  const mb=(w,t1,t2)=>16*(rm?(w>0?1:0):Math.min(eo((t-t1)/.35),1-eo((t-t2)/.35)));
  tds[1].style.marginBottom=(waitA||(t>=T.pr&&t<T.pr+.4)?mb(w1,T.sl+.3,T.pr):0).toFixed(2)+'px';
  tds[2].style.marginBottom=(waitQ||(t>=T.sel&&t<T.sel+.4)?mb(w2,T.q+.3,T.sel):0).toFixed(2)+'px';
  const adp=verdict!=='no';
  const fc=adp&&t>=T.a1d?(rm?1:eo((t-T.a1d)/.5)):0,fa=t>=T.e1d?(rm?1:eo((t-T.e1d)/.5)):0,fb=t>=T.e2d?(rm?1:eo((t-T.e2d)/.5)):0;
  [[fxC,fc],[fxA,fa],[fxB,fb]].forEach(([e,u])=>{e.style.maxHeight=(u*30).toFixed(1)+'px';e.style.opacity=u.toFixed(3);e.style.padding=`${(4*u).toFixed(2)}px 0`});
  const any=Math.max(fc,fa,fb);none.style.maxHeight=((1-any)*26).toFixed(1)+'px';none.style.opacity=(1-any).toFixed(3);
  tot.style.maxHeight=(any*24).toFixed(1)+'px';tot.style.opacity=(any*.95).toFixed(3);
  const fixU=t>=T.e3d?1:0;
  const flipN=(el,txt,t0)=>{if(el.textContent!==txt)el.textContent=txt;if(rm||!(t>=t0)||t>t0+.45){el.style.transform='';el.style.filter='';return}
    const u=(t-t0)/.45;el.style.transform=`translateY(${(-3*Math.sin(Math.PI*u)).toFixed(2)}px) scale(${(1+.12*Math.sin(Math.PI*u)).toFixed(3)})`;el.style.filter=`drop-shadow(0 0 ${(4*Math.sin(Math.PI*u)).toFixed(2)}px rgba(232,214,160,.9))`};
  flipN(fxAa,fixU?'+13':'+12',T.e3d);flipN(fxAd,fixU?'−6':'−4',T.e3d);
  const hA=fc>0,hE1=t>=T.e1d,hE2=t>=T.e2d;
  const ta=(hA?3:0)+(hE1?12:0)+(hE2?5:0)+fixU,tdv=(hA?1:0)+(hE1?4:0)+(hE2?3:0)+(fixU?2:0);
  const lastCh=fixU?T.e3d:hE2?T.e2d:hE1?T.e1d:T.a1d;
  flipN(tA,'+'+ta,lastCh);flipN(tD,'−'+tdv,lastCh);
  const nl=(hA?1:0)+(hE1?1:0)+(hE2?1:0);leaves.textContent=['no leaves','one leaf','two leaves','three leaves'][nl];
  const ctx=6+2*cl((t-T.r1)/2)+1*cl((t-T.a1)/2)+3*cl((t-T.e1)/4)+2*cl((t-T.s2)/4)+1*cl((t-T.b6)/1.5);
  pcEl.textContent=Math.round(ctx)+'%';ofEl.textContent=Math.round(262*ctx/100)+'k of 262k';grI.style.width=ctx.toFixed(2)+'%';grB.style.left=ctx.toFixed(2)+'%';
  /* ---- composer clock: stop ring while Kimi writes, hourglass while it waits for you (approval v2) ---- */
  const streaming=(t>=T.u&&t<T.sl+.2)||(t>=T.cp1&&t<T.q+.2)||(t>=T.qc1-.05&&t<T.c6z+.3);
  const waiting=(t>=T.sl+.25&&t<T.pr+.1)||(t>=T.q+.25&&t<T.sel+.1);
  const dtc=Math.max(0,Math.min(.1,t-lastT)),kk=rm||lastT<0||t<lastT?1:1-Math.exp(-dtc/.12);
  cvBusy+=((streaming?1:0)-cvBusy)*kk;cvWait+=((waiting?1:0)-cvWait)*kk;
  setClock(cvBusy,cvWait,t);
  pen.style.setProperty('--pen',cvBusy.toFixed(3));
  if(!rm)penDots.forEach((d,k2)=>{const ph2=((t*1.25-k2*.22)%1+1)%1;d.style.opacity=(.25+.75*Math.max(0,Math.sin(ph2*Math.PI))).toFixed(2)});
  /* ---- blossom on the writing tip ---- */
  const tips=[[l1,T.c1a,T.c1z],[l2,T.c2a,T.c2z],[l3,T.c3a,T.c3z],[l4,T.c4a,T.c4z],[l5,T.c5a,T.c5z],[l6,T.c6a,T.c6z]];let tip=null;
  for(const [l,a,z] of tips)if(l&&t<z+.9){tip={l,a,z};break}
  if(tip&&!rm&&view==='live'){const r=tip.l.el.getBoundingClientRect();const after=t-tip.z;
    const o=after<0?cl((t-tip.a+.1)/.3):1-cl((after-.35)/.5);const bl=after>0?Math.sin(Math.PI*cl(after/.7)):0;
    flw.style.opacity=o.toFixed(3);flw.style.transform=`translate(${(r.right+8+5*cl(after/.3)).toFixed(2)}px,${((r.top+r.bottom)/2-1).toFixed(2)}px) scale(${(1+.18*bl-.2*cl(after/.8)).toFixed(3)})`;
    flRot.setAttribute('transform',`rotate(${(Math.min(t,tip.z)*34+7*Math.sin(t*2*Math.PI/1.8)).toFixed(2)})`);
    pos.forEach((g2,k2)=>g2.setAttribute('transform',`translate(0 ${(-1.4*bl).toFixed(2)}) rotate(${(bl*(k2%2?3:-3)).toFixed(2)})`))}
  else flw.style.opacity=0;
  /* ---- thread follower (the wheel can read back; new paper brings the view down again) ---- */
  const tg=target();if(tg>lastTg+2)manual=0;lastTg=tg;
  if(sc<0||rm)sc=tg;else{const dt=Math.max(0,Math.min(.1,t-lastT));sc+=(tg-sc)*(1-Math.exp(-dt/.2))}
  manual=Math.min(manual,sc);
  thread.style.transform=`translateY(${(-(sc-manual)).toFixed(2)}px)`;
  lastT=t};
const setClock=(bv,wv,t)=>{const rm=RM.matches;
  stopI.style.opacity=bv.toFixed(3);stopI.style.transform=`scale(${(.86+.14*bv).toFixed(3)})`;
  waitI.style.opacity=wv.toFixed(3);waitI.style.transform=`scale(${(.86+.14*wv).toFixed(3)})`;
  sl0.style.opacity=(1-Math.max(bv,wv)).toFixed(3);sl1.style.opacity=bv.toFixed(3);sl2.style.opacity=wv.toFixed(3);
  if(!rm){stArc.setAttribute('transform',`rotate(${((t*150)%360).toFixed(1)})`);
    const hp=((t%3.2)+3.2)%3.2,flow=cl(hp/2.6),fl=cl((hp-2.7)/.5);
    sandT.setAttribute('y',(-6+6*flow).toFixed(2));sandT.setAttribute('height',(6-6*flow).toFixed(2));
    sandB.setAttribute('y',(6-6*flow).toFixed(2));sandB.setAttribute('height',(6*flow).toFixed(2));
    hgG.setAttribute('transform',`rotate(${(180*eio(fl)).toFixed(1)})`);
    wRing.setAttribute('opacity',(.35+.5*(.5+.5*Math.sin(t*2*Math.PI/2.6))).toFixed(2))}};
V.live.addEventListener('wheel',e=>{e.preventDefault();manual=Math.max(0,Math.min(sc,manual-e.deltaY))},{passive:false});

/* ================================ turn controller ================================ */
let running=false,t0=0,tt=0,frozen=null;
const REC0={sl:[slRec.querySelector('.rk').innerHTML,'已允许','Accordé · 16:42'],q:'按帧批处理'};
const reset=()=>{running=false;frozen=null;AUTO=false;DEC.verdict=DEC.choice=null;verdict='ok';choice=1;
  [2,3].forEach(k=>{if(BB[k].textContent!==TXT0[k])reTxt(k,TXT0[k])});
  slRec.classList.remove('deny');slRec.querySelector('.rk').innerHTML=REC0.sl[0];slRec.querySelector('.rw').textContent=REC0.sl[1];slRec.querySelector('.rr').textContent=REC0.sl[2];
  qAns.textContent=REC0.q;qRec.querySelector('.rw').textContent='已回答';qIn.value='';
  sumR.style.display='';sumH.textContent='改动了 3 个文件';sumA.textContent='+21';sumD.textContent='−10';
  Object.keys(TG).forEach(k=>delete TG[k]);sc=-1;lastT=-1;manual=0;lastTg=0;cvBusy=cvWait=0;
  rebuild();frame(0);setClock(0,0,0);pen.style.setProperty('--pen',0)};
const start=(txt,o={})=>{reset();setTxt(uB,txt);AUTO=!!o.auto;rebuild();running=true;t0=now();tt=0;
  if(o.at!=null){frozen=o.at;for(let x=0;x<o.at;x+=1/30)frame(x);frame(o.at)}};
const decideA=v=>{if(!running||DEC.verdict||!(tt>=T.sl+.25))return;
  verdict=v;DEC.verdict={v,t:tt};
  slRec.classList.toggle('deny',v==='no');slRec.querySelector('.rk').innerHTML=v==='no'?window.__rkX:window.__rkCk;
  slRec.querySelector('.rw').textContent=v==='no'?'已拒绝':v==='all'?'本会话都允许':'已允许';
  slRec.querySelector('.rr').textContent=v==='no'?'Refusé · 16:42':'Accordé · 16:42';
  if(v==='no'){reTxt(2,'好，先不动 adapter。动手合批之前，有个取舍想听你的：');sumR.style.display='none';sumH.textContent='改动了 2 个文件';sumA.textContent='+18';sumD.textContent='−9'}
  rebuild()};
const B4T=k=>k===0?'好，定时批处理。间隔我对齐到帧：先攒着，下一帧一次提交：':k===2?'好，按句批处理。句子里面仍按帧合批，长句也不卡：先攒着，下一帧一次提交：':
  k<0?'那我先按帧批处理，之后随时可以改。先攒着，下一帧一次提交：':k>2?`好，按「${qIn.value.trim()||'其他'}」来。底层先按帧合批：先攒着，下一帧一次提交：`:TXT0[3];
const decideQ=k=>{if(!running||!DEC.verdict||DEC.choice||!(tt>=T.q+.25))return;
  choice=k;DEC.choice={v:k,t:tt};
  qAns.textContent=k<0?'已跳过':(k>2?qIn.value.trim()||'其他':opts[k].querySelector('b').textContent);
  qRec.querySelector('.rw').textContent=k<0?'已跳过':'已回答';
  const nt=B4T(k);if(BB[3].textContent!==nt)reTxt(3,nt);rebuild()};
okB.addEventListener('click',()=>decideA('ok'));allB.addEventListener('click',()=>decideA('all'));noB.addEventListener('click',()=>decideA('no'));
opts.forEach((o,k)=>o.addEventListener('click',()=>decideQ(k)));qSkip.addEventListener('click',()=>decideQ(-1));
qIn.addEventListener('keydown',e=>{if(e.key==='Enter'&&qIn.value.trim()){e.preventDefault();e.stopPropagation();decideQ(9)}});
const overlay=()=>b.classList.contains('drw-open')||b.classList.contains('pop-open')||b.classList.contains('mdl-open');
addEventListener('keydown',e=>{if(!running||view!=='live'||overlay())return;const ae=document.activeElement;if(ae&&(ae.tagName==='INPUT'||ae.tagName==='TEXTAREA'))return;
  if(!DEC.verdict&&tt>=T.sl+.25){if(e.key==='Enter'){e.preventDefault();decideA('ok')}else if(e.key==='Escape'){e.preventDefault();e.stopImmediatePropagation();decideA('no')}}
  else if(DEC.verdict&&!DEC.choice&&tt>=T.q+.25){if('123'.includes(e.key)&&e.key.length===1)decideQ(+e.key-1);else if(e.key==='Escape'){e.preventDefault();e.stopImmediatePropagation();decideQ(-1)}}},true);
/* clicks on a note / gathered line / summary bar fold them open and shut (tools v2) */
const bind=(el,key)=>{el.addEventListener('click',()=>toggle(key));el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();e.stopPropagation();toggle(key)}})};
bind(GL,'grp');bind(E1.h,'p1');bind(E2.h,'p2');bind(E3.h,'p3');bind(S1.h,'o1');bind(S2.h,'o2');bind(S3.h,'o3');bind(SH,'sl');
const loop=()=>{NOW=now();if(running){tt=frozen!=null?frozen:NOW-t0;frame(Math.min(tt,T.END))}requestAnimationFrame(loop)};

/* ================================ composer, presets, rail, drawer, model ================================ */
const ci=$('ci'),field=document.querySelector('.field');
const busy=()=>running&&view==='live'&&!(tt>=T.END);
const sendNow=txt=>{txt=(txt||ci.value||'').trim()||window.__rkPrompt;if(busy())return;
  if(localStorage.getItem('trianon_mode')==='real'){
    ci.value='';field.classList.remove('has');ci.blur();
    const fromEmpty=view==='empty';
    if(window.__real)window.__real.chat(txt);
    showView('live',{exitEmpty:fromEmpty});
    return;
  }
  ci.value='';field.classList.remove('has');ci.blur();
  const fromEmpty=view==='empty';start(txt);
  const cs=curSlip();if(cs)cs.textContent=LIVE_TITLE;railOn(-1);
  showView('live',{exitEmpty:fromEmpty})};
ci.addEventListener('input',()=>field.classList.toggle('has',!!ci.value));
ci.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing){e.preventDefault();sendNow()}});
field.addEventListener('click',e=>{if(!e.target.closest('.mchip,.pill'))ci.focus({preventScroll:true})});
send.addEventListener('click',()=>sendNow());
send.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();sendNow()}});
const PRE=['帮我整理一下这个仓库：目录、脚本和没用的依赖。',window.__rkPrompt,'随便聊聊：流式渲染最容易在哪儿卡住？'];
V.empty.querySelectorAll('.tag').forEach((t,k)=>t.addEventListener('click',()=>sendNow(PRE[k])));
let resetT=0;
const newChat=()=>{ci.value='';field.classList.remove('has');const cs=curSlip();if(cs)cs.textContent='新的对话';railOn(0);
  const wasLive=view==='live';showView('empty');clearTimeout(resetT);
  if(wasLive&&!RM.matches)resetT=setTimeout(()=>{if(view!=='live')reset()},320);else reset()};
railIts[0].addEventListener('click',newChat);
$('drw').addEventListener('click',e=>{
  const ses=e.target.closest('.dw-ses');
  if(ses&&!e.target.closest('.dw-more')){
    if(ses.classList.contains('cur'))showView(running?'live':'empty');
    else{histTitle=ses.querySelector('.dw-t').textContent;showView('hist')}
    window.__v13toggle&&window.__v13toggle(false);return}
  const nw=e.target.closest('.dw-new');if(nw&&!nw.classList.contains('ws-add')){newChat();window.__v13toggle&&window.__v13toggle(false)}});
const mcM=$('mcM');new MutationObserver(()=>{const m=mcM.textContent;$('rkCtxM').textContent=m;$('rkTopM').textContent=m}).observe(mcM,{childList:true,characterData:true,subtree:true});

/* ================================ #play: the self-running demo ================================ */
const D={x:1010,y:640,vis:0,press:-9,on:false};
window.__demoXY=()=>[D.x,D.y,now()-D.press<.12?1:0];
const cur=document.createElement('div');cur.id='rkCur';
cur.innerHTML='<svg width="22" height="26" viewBox="0 0 22 26"><path d="M3 2 L3 20.5 L7.6 16.3 L10.9 23.6 L14 22.2 L10.8 15.1 L17 14.6 Z" fill="#FBFAF6" stroke="#3E4C76" stroke-width="1.25" stroke-linejoin="round" style="filter:drop-shadow(0 1.5px 1.5px rgba(30,40,70,.35))"/></svg>';
b.appendChild(cur);
const P=(el,fx=.5,fy=.5)=>{if(!el)return [D.x,D.y];const r=el.getBoundingClientRect();return [r.left+r.width*fx,r.top+r.height*fy]};
const off=(p,dx,dy)=>[p[0]+dx,p[1]+dy];
const hgPt=()=>{const e=railIts[1];let x=0,y=0,n=e;while(n){x+=n.offsetLeft;y+=n.offsetTop;n=n.offsetParent}return [x+e.offsetWidth/2+3,y+e.offsetHeight/2+5]};
const abs=k=>t0+T[k];
const press=el=>{D.press=now();if(el)el.click()};
window.__playT0=null;
const typeTo=u=>{const s=window.__rkPrompt,n=Math.round(s.length*cl(u));if(ci.value.length!==n){ci.value=s.slice(0,n);field.classList.toggle('has',n>0)}};
const SEL=q=>()=>document.querySelector(q);
const STEPS=[
 {d:4.6},
 {to:()=>P(field,.42,.36),d:.9,show:1},
 {d:.22,act:()=>ci.focus({preventScroll:true})},
 {d:1.9,tick:typeTo},
 {d:.32},
 {to:()=>P(send,.5,.55),d:.55},
 {d:.15,act:()=>press(send)},
 {to:()=>[1010,640],d:.8},
 {until:()=>abs('sl')+1.3},
 {to:()=>off(P(okB),6,4),d:.75},
 {d:.42,act:()=>press(okB)},
 {to:()=>off(P(okB),150,74),d:.6},
 {until:()=>abs('q')+1.15},
 {to:()=>off(P(opts[0]),10,8),d:.55},{d:.35},
 {to:()=>off(P(opts[1]),-22,6),d:.42},{d:.38,act:()=>press(opts[1])},
 {to:()=>off(P(opts[1]),60,112),d:.6},
 {until:()=>abs('p1o0')-.75},
 {to:()=>P(E1.h,.42,.55),d:.6},
 {until:()=>abs('p1c0')},
 {to:()=>[1010,560],d:.7},
 {until:()=>abs('so0')-.6},
 {to:()=>P(SH,.32,.55),d:.5},
 {until:()=>abs('END')+.5},
 {to:()=>off(P(SH,.32,.55),70,60),d:.5},{d:.3},
 {to:()=>{const p=hgPt();return [7,p[1]+6]},d:.8},{d:.45},
 {to:hgPt,d:.45},{d:.32,act:()=>press(railIts[1])},{d:1.25},
 {to:()=>P(document.querySelector('#dwTabs .ptab[data-t="1"]'),.45),d:.6},{d:.28,act:()=>press(document.querySelector('#dwTabs .ptab[data-t="1"]'))},{d:.95},
 {to:()=>P([...document.querySelectorAll('.dw-pane.on .dw-ses')].find(e=>e.textContent.includes('重构聊天工作台')),.42),d:.6},
 {d:.5,act:()=>press([...document.querySelectorAll('.dw-pane.on .dw-ses')].find(e=>e.textContent.includes('重构聊天工作台')))},
 {d:1.7},
 {to:()=>P($('mchip'),.42),d:.8},{d:.3,act:()=>press($('mchip'))},{d:.95},
 {to:()=>P(document.querySelector('.mp-row[data-m="K3.1 Pro Highspeed"]'),.35),d:.5},{d:.55},
 {to:()=>P(document.querySelector('.mp-row[data-m="K3"]'),.35),d:.45},{d:.5},
 {to:()=>P(document.querySelector('.mp-row.on'),.3),d:.45},{d:1.6,end:1}];
const HOV='.sl-ok,.sl-all,.sl-no,.q-opt,.tn-h,.ts-h,.tg-l';
let hovSet=[],railHov=null;
const synth=()=>{const el=document.elementFromPoint(D.x,D.y);const nh=[];if(el){const h=el.closest(HOV);if(h)nh.push(h)}
  hovSet.forEach(e=>{if(!nh.includes(e))e.classList.remove('hov')});nh.forEach(e=>e.classList.add('hov'));hovSet=nh;
  if(window.__realMouse)return;
  window.dispatchEvent(new PointerEvent('pointermove',{clientX:D.x,clientY:D.y,bubbles:true}));
  const ri=railIts.find(e=>{const r=e.getBoundingClientRect();return b.classList.contains('rail-open')&&D.x>=r.left&&D.x<=r.right&&D.y>=r.top&&D.y<=r.bottom})||null;
  if(ri!==railHov){if(railHov)railHov.dispatchEvent(new PointerEvent('pointerleave'));if(ri)ri.dispatchEvent(new PointerEvent('pointerenter'));railHov=ri}};
let si=-1,sT=0,sEnd=0,from=[0,0],playing=false;
const begin=(i,n)=>{si=i;const s=STEPS[i];if(!s)return;sT=n;from=[D.x,D.y];if(s.show)D.vis=1;sEnd=s.until?Math.max(n,s.until()):n+(s.d||0)};
const playTick=()=>{if(!playing)return;const n=now();if(si<0)begin(0,n);
  while(si<STEPS.length&&n>=sEnd){const s=STEPS[si];if(s.to){const p=s.to();D.x=p[0];D.y=p[1]}if(s.tick)s.tick(1);if(s.act)s.act();if(s.end){playing=false;break}begin(si+1,n)}
  const s=STEPS[si];
  if(s&&playing){const u=sEnd>sT?(n-sT)/(sEnd-sT):1;if(s.to){const p=s.to(),e=sm(u);D.x=from[0]+(p[0]-from[0])*e;D.y=from[1]+(p[1]-from[1])*e}if(s.tick)s.tick(u);
    if(s.until&&!(isFinite(sEnd)))sEnd=s.until()}
  const pr=now()-D.press<.12;
  cur.style.opacity=D.vis?'1':'0';cur.style.transform=`translate(${(D.x-3).toFixed(2)}px,${(D.y-2).toFixed(2)}px) scale(${pr?.88:1})`;
  synth();requestAnimationFrame(playTick)};
const play=()=>{if(playing)return;playing=true;si=-1;window.__playT0=now();D.x=1010;D.y=640;D.vis=0;
  if(window.__v11restart)window.__v11restart();requestAnimationFrame(playTick)};
window.__playGo=play;

/* ================================ boot + scene hashes ================================ */
rebuild();frame(0);setClock(0,0,0);
const FZ={stream:()=>T.c2a+.62*(T.c2z-T.c2a),tools:()=>(T.r2+T.r2d)/2,approval:()=>T.sl+1.6,pend:()=>T.sl+1.6,q:()=>T.q+1.8,qok:()=>T.sel+.95,
  diff:()=>T.p1o1+.75,fail:()=>T.s2d+.45,end:()=>T.END,sessions:()=>T.END,model:()=>T.END,cat:()=>T.END};
const boot=()=>{setCH();measure();
  Promise.all([...document.querySelectorAll('.thread .rnd')].map(i=>i.decode?i.decode().catch(()=>0):0)).then(()=>{showAll(()=>guard())});
  const tm=HASH.map(h=>h.match(/^t=([\d.]+)$/)).find(Boolean);
  const fz=HASH.find(h=>FZ[h]);
  if(tm||fz){AUTO=true;rebuild();const at=tm?+tm[1]:FZ[fz]();start(window.__rkPrompt,{auto:true,at});
    const cs=curSlip();if(cs)cs.textContent=LIVE_TITLE;railOn(-1);showView('live',{instant:true});
    if(has('sessions'))setTimeout(()=>window.__v13toggle&&window.__v13toggle(true),150);
    if(has('model'))setTimeout(()=>window.__s2pop&&window.__s2pop(true),150)}
  else if(has('chat')||has('hist')){railOn(-1);showView('hist',{instant:true})}
  else{if(has('play'))setTimeout(play,500)}
  requestAnimationFrame(loop)};
(document.fonts&&document.fonts.ready?document.fonts.ready:Promise.resolve()).then(()=>requestAnimationFrame(boot));

window.__rk={get T(){return T},SCRIPT,DEC,frame,start,reset,decideA,decideQ,showView,newChat,sendNow,play,
  get t(){return tt},get t0(){return t0},get view(){return view},
  events:()=>SCRIPT.filter(e=>e[3]).map(([k,,,ev,p])=>({at:T[k],ev,...(p||{})}))};
})();


/* ================================ REAL MODE (Pure & Minimal Edition) ================================ */
(() => {
  let abortController = null;
  let scrollScheduled = false;
  let initialized = false;
  
  let settingsObserver = null;
  let mdlObserver = null;
  let modalAbort = null;
  let mdlAbort = null;
  let renderCatalogueFn = null;
  let currentTabId = 'all';
  let conversationHistory = [];

  const initDOM = () => {
    const thread = document.getElementById('thLive');
    const scrollBox = document.getElementById('vLive');
    return { thread, scrollBox };
  };

  // ================= 数据结构与存储 =================
  const getData = () => {
    const str = localStorage.getItem('trianon_workbench_data');
    if (!str) return { providers: [], activeModel: null };
    try { return JSON.parse(str); } catch(e) { return { providers: [], activeModel: null }; }
  };

  const saveData = (data) => {
    localStorage.setItem('trianon_workbench_data', JSON.stringify(data));
    updateMainModelText();
  };

  const getActiveConfig = () => {
    const data = getData();
    if (data.providers.length === 0) return null;
    
    let provider = data.providers.find(p => p.id === data.activeModel?.providerId);
    if (!provider || !provider.models.length) {
      provider = data.providers[0];
    }
    if (!provider || !provider.models.length) return null;

    let model = provider.models.find(m => m.id === data.activeModel?.modelId) || provider.models[0];
    
    if (!data.activeModel || data.activeModel.providerId !== provider.id || data.activeModel.modelId !== model.id) {
      data.activeModel = { providerId: provider.id, modelId: model.id };
      saveData(data);
    }
    
    return { provider, model };
  };

  const updateMainModelText = () => {
    const config = getActiveConfig();
    const mcM = document.getElementById('mcM');
    if (mcM) {
      mcM.textContent = config ? config.model.name : '未选择模型';
    }
  };

  // ================= UI 接管：全屏页面 (#mdl) =================
  const setupCataloguePage = () => {
    if (mdlObserver) return;
    const mdl = document.getElementById('mdl');
    if (!mdl) return;

    if (mdlAbort) mdlAbort.abort();
    mdlAbort = new AbortController();

    const mdIn = document.getElementById('mdIn');
    if (mdIn) {
      mdIn.addEventListener('input', () => {
        if (renderCatalogueFn) renderCatalogueFn();
      }, { signal: mdlAbort.signal });
    }

    renderCatalogueFn = () => {
      const currentMdl = document.getElementById('mdl');
      if (!currentMdl) return;
      
      const currentMdIn = document.getElementById('mdIn');
      const keyword = (currentMdIn?.value || '').toLowerCase().trim();
      
      const data = getData();
      if (currentTabId !== 'all' && !data.providers.some(p => p.id === currentTabId)) {
        currentTabId = 'all';
      }
      
      const mdTabs = document.getElementById('mdTabs');
      const mdList = document.getElementById('mdList');
      if (!mdTabs || !mdList) return;

      // 1. Tabs
      mdTabs.innerHTML = '';
      const createTab = (id, label) => {
        const tab = document.createElement('div');
        tab.className = 'ptab' + (currentTabId === id ? ' on' : '');
        tab.textContent = label;
        tab.onclick = () => { currentTabId = id; renderCatalogueFn(); };
        mdTabs.appendChild(tab);
      };

      createTab('all', '全部');
      data.providers.forEach(p => createTab(p.id, p.name));

      const addBtn = document.createElement('div');
      addBtn.className = 'ptab';
      addBtn.textContent = '+';
      addBtn.title = '添加新 API';
      addBtn.style.fontSize = '18px';
      addBtn.style.fontWeight = 'bold';
      addBtn.onclick = () => openConfigModal();
      mdTabs.appendChild(addBtn);

      // 2. List
      mdList.innerHTML = '';
      if (data.providers.length === 0) {
        const empty = document.createElement('div');
        empty.style.cssText = 'padding: 20px; color: #7C8DB5; text-align: center;';
        empty.textContent = '暂无模型，请点击 + 号添加 API';
        mdList.appendChild(empty);
      } else {
        let hasVisible = false;
        data.providers.forEach(p => {
          if (currentTabId !== 'all' && p.id !== currentTabId) return;

          p.models.forEach(m => {
            if (keyword && !m.id.toLowerCase().includes(keyword) && !m.name.toLowerCase().includes(keyword) && !p.name.toLowerCase().includes(keyword)) return;
            hasVisible = true;

            const row = document.createElement('div');
            row.className = 'md-row';
            const isActive = data.activeModel && data.activeModel.providerId === p.id && data.activeModel.modelId === m.id;
            if (isActive) {
              row.classList.add('on');
              row.setAttribute('aria-selected', 'true');
            } else {
              row.setAttribute('aria-selected', 'false');
            }

            const txDiv = document.createElement('div');
            txDiv.className = 'md-tx';
            const b = document.createElement('b');
            b.textContent = m.name;
            const metaDiv = document.createElement('div');
            metaDiv.className = 'md-meta';
            const spanP = document.createElement('span');
            spanP.textContent = p.name;
            const sep1 = document.createElement('i');
            sep1.className = 'sep';
            const spanM = document.createElement('span');
            spanM.textContent = m.id;
            metaDiv.appendChild(spanP);
            metaDiv.appendChild(sep1);
            metaDiv.appendChild(spanM);
            txDiv.appendChild(b);
            txDiv.appendChild(metaDiv);
            row.appendChild(txDiv);

            // 右侧操作区：只有选中时才显示对勾，其余什么都不显示
            const actionDiv = document.createElement('div');
            actionDiv.style.cssText = 'display: flex; align-items: center; margin-left: auto; margin-right: 12px; width: 20px; height: 20px;';
            
            if (isActive) {
              const checkSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
              checkSvg.setAttribute('width', '20');
              checkSvg.setAttribute('height', '20');
              checkSvg.setAttribute('viewBox', '0 0 24 24');
              checkSvg.setAttribute('fill', 'none');
              checkSvg.setAttribute('stroke', '#2E3B68');
              checkSvg.setAttribute('stroke-width', '2.5');
              checkSvg.setAttribute('stroke-linecap', 'round');
              checkSvg.setAttribute('stroke-linejoin', 'round');
              checkSvg.innerHTML = '<polyline points="20 6 9 17 4 12"></polyline>';
              actionDiv.appendChild(checkSvg);
            }
            row.appendChild(actionDiv);

            row.onclick = () => {
              const newData = getData();
              newData.activeModel = { providerId: p.id, modelId: m.id };
              saveData(newData);
              renderCatalogueFn();
              document.getElementById('mdl')?.setAttribute('aria-hidden', 'true');
            };
            mdList.appendChild(row);
          });
        });

        if (!hasVisible) {
          const empty = document.createElement('div');
          empty.style.cssText = 'padding: 20px; color: #7C8DB5; text-align: center;';
          empty.textContent = keyword ? '没有找到匹配的模型' : '该分组暂无模型';
          mdList.appendChild(empty);
        }
      }
    };

    mdlObserver = new MutationObserver((mutations) => {
      for (let m of mutations) {
        if (m.attributeName === 'aria-hidden' && mdl.getAttribute('aria-hidden') === 'false') {
          renderCatalogueFn();
        }
      }
    });
    mdlObserver.observe(mdl, { attributes: true });
  };

  // ================= UI 接管：小弹窗 (#mpop) =================
  const setupSmallPopup = () => {
    if (settingsObserver) return;
    const mpop = document.getElementById('mpop');
    if (!mpop) return;

    const injectRows = () => {
      const mv = document.getElementById('mpMv');
      if (!mv) return;
      
      mv.querySelectorAll('.mp-row, .tri-preset-row').forEach(el => el.remove());
      const data = getData();
      const active = data.activeModel;
      const header = mv.querySelector('.mp-hd');
      const targetNode = header ? header.nextSibling : mv.firstChild;

      if (data.providers.length === 0) {
        const emptyDiv = document.createElement('div');
        emptyDiv.className = 'mp-c tri-preset-row';
        emptyDiv.style = "color: #7C8DB5; font-size: 13px; padding: 12px 16px; text-align: center;";
        emptyDiv.textContent = "暂无模型，请在“更多模型”中配置";
        mv.insertBefore(emptyDiv, targetNode);
      } else {
        // 把保存的模型全列出来，方便快速切
        data.providers.forEach(p => {
          p.models.forEach(m => {
            const row = document.createElement('div');
            row.className = 'mp-c mp-row tri-preset-row';
            row.setAttribute('role', 'menuitemradio');
            const isActive = active && active.providerId === p.id && active.modelId === m.id;
            row.setAttribute('aria-checked', isActive ? 'true' : 'false');
            if (isActive) row.classList.add('on');
            row.style.cursor = 'pointer';

            const b = document.createElement('b');
            b.textContent = m.name;
            row.appendChild(b);

            row.onclick = () => {
              const newData = getData();
              newData.activeModel = { providerId: p.id, modelId: m.id };
              saveData(newData);
              mpop.setAttribute('aria-hidden', 'true');
              mpop.classList.remove('on');
            };
            mv.insertBefore(row, targetNode);
          });
        });
      }
    };

    settingsObserver = new MutationObserver((mutations) => {
      for (let m of mutations) {
        if (m.attributeName === 'aria-hidden' && mpop.getAttribute('aria-hidden') === 'false') {
          injectRows();
        }
      }
    });
    settingsObserver.observe(mpop, { attributes: true });
  };

  // ================= UI：API 配置弹窗 =================
  const openConfigModal = () => {
    if (document.getElementById('tri-config-modal')) return;
    if (modalAbort) modalAbort.abort();
    modalAbort = new AbortController();

    let isManualMode = false;
    let fetching = false;

    const modal = document.createElement('div');
    modal.id = 'tri-config-modal';
    modal.style.cssText = `
      position: fixed; inset: 0; background: rgba(40, 50, 79, 0.6); backdrop-filter: blur(8px);
      z-index: 2147483647; display: flex; justify-content: center; align-items: center;
    `;

    const inner = document.createElement('div');
    inner.style.cssText = "background: linear-gradient(rgb(240, 244, 250), rgb(227, 233, 243)); width: 90%; max-width: 600px; border-radius: 20px; padding: 24px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); border: 1.2px solid #fff; max-height: 90vh; overflow-y: auto;";
    
    inner.innerHTML = `
      <h3 style="margin: 0 0 16px 0; color: #2E3B68; font-family: serif; display:flex; justify-content:space-between;">
        <span>添加 API 分组</span><span id="tri-modal-close" style="cursor:pointer; font-size:16px; color:#7C8DB5;">✕</span>
      </h3>
      
      <div id="tri-config-error" style="color: #D32F2F; font-size: 12px; margin-bottom: 10px; display: none;"></div>

      <div style="background: rgba(255,255,255,0.5); padding: 16px; border-radius: 12px; border: 1px solid rgba(124,147,186,.2); margin-bottom: 16px;">
        <div style="display:flex; gap:10px; margin-bottom:10px;">
          <input type="text" id="tri-add-name" placeholder="分组名称 (如: 中转站A)" style="flex:1; padding:8px; border-radius:6px; border:1px solid #ccc; font-size:13px;">
          <input type="text" id="tri-add-baseurl" placeholder="Base URL (https://...)" style="flex:1; padding:8px; border-radius:6px; border:1px solid #ccc; font-size:13px;">
        </div>
        <input type="password" id="tri-add-apikey" placeholder="API Key" style="width:100%; margin-bottom:10px; padding:8px; border-radius:6px; border:1px solid #ccc; font-size:13px; box-sizing:border-box;">
        <button type="button" id="tri-btn-fetch" style="width:100%; padding:10px; background:#E8EEF5; color:#2E3B68; border:none; border-radius:8px; cursor:pointer; font-size:14px;">拉取模型列表</button>
      </div>

      <div id="tri-model-checkboxes" style="display: none; background: rgba(255,255,255,0.5); padding: 16px; border-radius: 12px; border: 1px solid rgba(124,147,186,.2); margin-bottom: 16px; max-height: 200px; overflow-y: auto;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
          <h4 style="margin: 0; font-size: 14px; color:#2E3B68;">勾选需要的模型：</h4>
          <span id="tri-toggle-all" style="cursor:pointer; color:#7F93BC; font-size:13px; font-weight:bold; user-select:none;">全选</span>
        </div>
        <div id="tri-model-list-container" style="display: flex; flex-direction: column; gap: 8px;"></div>
      </div>

      <div id="tri-manual-add" style="display: none; background: rgba(255,255,255,0.5); padding: 16px; border-radius: 12px; border: 1px solid rgba(124,147,186,.2); margin-bottom: 16px;">
        <h4 style="margin: 0 0 10px 0; font-size: 14px; color:#2E3B68;">手动添加模型 ID (每行一个)：</h4>
        <textarea id="tri-manual-models" style="width:100%; height:80px; padding:8px; border-radius:6px; border:1px solid #ccc; font-size:13px; box-sizing:border-box; resize:vertical;"></textarea>
      </div>

      <div style="display:flex; gap:10px;">
        <button type="button" id="tri-btn-manual" style="flex:1; padding:10px; background:#E8EEF5; color:#2E3B68; border:none; border-radius:8px; cursor:pointer; font-size:14px;">无法拉取？手动填写</button>
        <button type="button" id="tri-btn-save" style="flex:1; padding:10px; background:#7F93BC; color:#fff; border:none; border-radius:8px; cursor:pointer; font-size:14px;">保存分组</button>
      </div>
    `;

    modal.appendChild(inner);
    document.body.appendChild(modal);

    const errEl = document.getElementById('tri-config-error');
    const showError = (msg) => { errEl.textContent = msg; errEl.style.display = 'block'; };
    const clearError = () => { errEl.style.display = 'none'; };

    const isFormDirty = () => {
      return ['tri-add-name', 'tri-add-baseurl', 'tri-add-apikey', 'tri-manual-models']
        .some(id => (document.getElementById(id)?.value || '').trim() !== '');
    };

    const closeModal = (force = false) => {
      const isForce = force === true;
      if (!isForce && isFormDirty()) {
        if (!confirm('表单有未保存的内容，确定关闭吗？')) return;
      }
      if (modalAbort) { modalAbort.abort(); modalAbort = null; }
      modal.remove();
    };

    document.getElementById('tri-modal-close').onclick = () => closeModal();

    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal();
    }, { signal: modalAbort.signal });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && document.getElementById('tri-config-modal')) closeModal();
    }, { signal: modalAbort.signal });

    document.getElementById('tri-btn-fetch').onclick = async () => {
      if (fetching) return;
      clearError();
      
      const baseURL = document.getElementById('tri-add-baseurl').value.trim();
      const apiKey = document.getElementById('tri-add-apikey').value.trim();
      if (!baseURL || !apiKey) return showError("请先填写 Base URL 和 API Key");

      try {
        fetching = true;
        const btn = document.getElementById('tri-btn-fetch');
        btn.textContent = '拉取中...';
        btn.disabled = true;

        const url = baseURL.replace(/\/+$/, '') + '/models';
        const res = await fetch(url, { 
          headers: { 'Authorization': `Bearer ${apiKey}` },
          signal: modalAbort.signal
        });
        if (!res.ok) throw new Error("HTTP " + res.status);
        const data = await res.json();
        
        const fetchedModels = data.data || [];
        const container = document.getElementById('tri-model-list-container');
        container.innerHTML = '';
        const toggleBtn = document.getElementById('tri-toggle-all');

        if (fetchedModels.length === 0) {
          toggleBtn.style.display = 'none';
          container.innerHTML = '<div style="color:#7C8DB5; font-size:12px; text-align:center;">该接口未返回任何模型，请使用手动填写</div>';
        } else {
          toggleBtn.style.display = '';
          fetchedModels.forEach(m => {
            const label = document.createElement('label');
            label.style.cssText = 'display: flex; align-items: center; gap: 8px; font-size: 13px; color: #2E3B68; cursor: pointer;';
            
            const cb = document.createElement('input');
            cb.type = 'checkbox';
            cb.value = m.id;
            cb.checked = false;
            
            label.appendChild(cb);
            label.appendChild(document.createTextNode(' ' + m.id));
            container.appendChild(label);
          });

          const checkboxes = container.querySelectorAll('input[type="checkbox"]');
          
          const updateToggleText = () => {
            const total = checkboxes.length;
            const checkedCount = Array.from(checkboxes).filter(cb => cb.checked).length;
            toggleBtn.textContent = (total > 0 && checkedCount === total) ? '全不选' : '全选';
          };

          toggleBtn.onclick = () => {
            const total = checkboxes.length;
            const checkedCount = Array.from(checkboxes).filter(cb => cb.checked).length;
            const targetState = !(total > 0 && checkedCount === total);
            checkboxes.forEach(cb => cb.checked = targetState);
            updateToggleText();
          };

          checkboxes.forEach(cb => cb.addEventListener('change', updateToggleText));
          updateToggleText();
        }

        document.getElementById('tri-model-checkboxes').style.display = 'block';
        document.getElementById('tri-manual-add').style.display = 'none';
        isManualMode = false; 
      } catch (e) {
        if (e.name !== 'AbortError') {
          showError("拉取失败，请检查网络或手动填写");
          document.getElementById('tri-btn-manual').click();
        }
      } finally {
        fetching = false;
        const btn = document.getElementById('tri-btn-fetch');
        if (btn) {
          btn.textContent = '拉取模型列表';
          btn.disabled = false;
        }
      }
    };

    document.getElementById('tri-btn-manual').onclick = () => {
      isManualMode = true; 
      document.getElementById('tri-model-checkboxes').style.display = 'none';
      document.getElementById('tri-manual-add').style.display = 'block';
    };

    document.getElementById('tri-btn-save').onclick = () => {
      clearError();
      const name = document.getElementById('tri-add-name').value.trim();
      const baseURL = document.getElementById('tri-add-baseurl').value.trim();
      const apiKey = document.getElementById('tri-add-apikey').value.trim();

      if (!name || !baseURL || !apiKey) return showError("名称、URL 和 Key 必须填写！");

      let selectedModels = [];
      if (isManualMode) {
        const lines = document.getElementById('tri-manual-models').value.split('\n');
        selectedModels = lines.map(l => l.trim()).filter(Boolean).map(id => ({ id, name: id }));
      } else {
        const checkedBoxes = document.querySelectorAll('#tri-model-list-container input:checked');
        selectedModels = Array.from(checkedBoxes).map(cb => ({ id: cb.value, name: cb.value }));
      }

      if (selectedModels.length === 0) return showError("请至少选择一个模型");

      const data = getData();
      const newProvider = {
        id: 'p_' + Date.now(),
        name, baseURL, apiKey,
        models: selectedModels
      };
      
      data.providers.push(newProvider);
      if (!data.activeModel) {
        data.activeModel = { providerId: newProvider.id, modelId: selectedModels[0].id };
      }
      saveData(data);
      
      closeModal(true);
      if (renderCatalogueFn) renderCatalogueFn();
    };
  };

  const injectStyle = () => {
    if (document.getElementById('real-mode-style')) return;
    const style = document.createElement('style');
    style.id = 'real-mode-style';
    style.textContent = `
      @keyframes realFadeIn {
        from { opacity: 0; transform: translateY(6px); filter: blur(2px); }
        to { opacity: 1; transform: translateY(0); filter: blur(0); }
      }
      #thLive { display: flex; flex-direction: column; padding: 20px 24px; }
      .real-row { display: flex; width: 100%; margin-bottom: 24px; animation: realFadeIn 0.4s ease forwards; }
      .real-row.u { justify-content: flex-end; }
      .real-row.a { flex-direction: column; align-items: flex-start; }
      
      .real-bubble.u {
        background: linear-gradient(rgb(253, 249, 251), rgb(244, 234, 238));
        color: rgb(40, 50, 79); padding: 13px 24px;
        border-radius: 30px 30px 4px 30px; font-size: 16px;
        max-width: 75%; border: 1.2px solid rgba(220, 205, 210, 0.8);
        box-shadow: rgb(255, 255, 255) 0px 0px 0px 4px inset, rgba(60, 72, 110, 0.2) 0px 14px 30px -20px;
        position: relative; line-height: 1.6; word-break: break-word;
      }
      .real-bubble.u::after {
        content: ""; position: absolute; right: -6px; bottom: 0;
        width: 0; height: 0; border-bottom: 12px solid rgb(244, 234, 238); border-right: 12px solid transparent;
      }
      
      .real-who {
        color: #5B6C92; font-family: serif; letter-spacing: 3px;
        font-size: 13px; margin-bottom: 8px; margin-left: 14px;
      }
      .real-bubble.a {
        background: linear-gradient(rgb(227, 233, 243), rgb(216, 224, 236));
        box-shadow: rgb(248, 250, 253) 0px 0px 0px 4px inset, rgba(60, 72, 110, 0.38) 0px 14px 30px -20px;
        border: 1.21273px solid rgb(135, 150, 180); border-radius: 30px;
        color: rgb(40, 50, 79); padding: 16px 28px 36px 28px;
        font-size: 16px; width: 100%;
        position: relative; line-height: 1.7; word-break: break-word;
      }
      .real-bubble.a::after {
        content: "for 妁妁 only"; position: absolute; right: 24px; bottom: 12px;
        font-family: serif; font-style: italic; color: rgba(120, 140, 180, 0.5); font-size: 13px;
      }
      .real-abort-hint { color: #889; font-size: 13px; margin-left: 8px; font-style: italic; }
    `;
    document.head.appendChild(style);
  };

  const scrollToBottom = (scrollBox, force = false) => {
    if (!scrollBox) return;
    if (force) { scrollBox.scrollTop = scrollBox.scrollHeight; return; }
    if (scrollScheduled) return;
    const isNearBottom = scrollBox.scrollHeight - scrollBox.scrollTop - scrollBox.clientHeight < 80;
    if (!isNearBottom) return;
    scrollScheduled = true;
    requestAnimationFrame(() => {
      scrollBox.scrollTop = scrollBox.scrollHeight;
      scrollScheduled = false;
    });
  };

  const appendText = (bubble, text, scrollBox) => {
    if (text === undefined || text === null) return;
    bubble.appendChild(document.createTextNode(text));
    scrollToBottom(scrollBox);
  };

  const chat = async (userText) => {
    if (!userText || !userText.trim()) return;
    const { thread, scrollBox } = initDOM();
    if (!thread) return;
    
    injectStyle();
    setupCataloguePage();
    setupSmallPopup();

    const config = getActiveConfig();
    if (!config) {
      openConfigModal();
      return;
    }

    if (abortController) abortController.abort();
    const myCtrl = new AbortController();
    abortController = myCtrl;

    let uRow = null, aRow = null, myBubble = null, statusEl = null, aWho = null;
    let history = conversationHistory;

    try {
      if (!initialized) {
        thread.querySelectorAll('.row, .real-row').forEach(el => el.remove());
        initialized = true;
      }

      uRow = document.createElement('div');
      uRow.className = 'real-row u';
      const uB = document.createElement('div');
      uB.className = 'real-bubble u';
      uRow.appendChild(uB);
      thread.appendChild(uRow);
      appendText(uB, userText, scrollBox);
      scrollToBottom(scrollBox, true);

      aRow = document.createElement('div');
      aRow.className = 'real-row a';
      aWho = document.createElement('div');
      aWho.className = 'real-who';
      
      aWho.textContent = (config.model.name || 'K I M I').toUpperCase();

      myBubble = document.createElement('div');
      myBubble.className = 'real-bubble a';
      aRow.appendChild(aWho);
      aRow.appendChild(myBubble);
      thread.appendChild(aRow);

      statusEl = document.createElement('span');
      statusEl.textContent = '思考中...';
      statusEl.style.opacity = '0.5';
      myBubble.appendChild(statusEl);

      const workerURL = 'https://trianon-workbench.morning-mouse-3ac4.workers.dev/api/chat';

      const nextMessages = [...history, { role: 'user', content: userText }];

      const res = await fetch(workerURL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ messages: nextMessages, baseURL: config.provider.baseURL, apiKey: config.provider.apiKey, model: config.model.id }),
          signal: myCtrl.signal
      });

      if (!res.ok) {
          const errText = await res.text();
          const raw = errText || `HTTP ${res.status}`;
          throw new Error(raw.length > 200 ? raw.slice(0, 200) + '…' : raw);
      }

      let fullReply = '';
      let hasContent = false;

      const handleLine = (line) => {
          if (!line.startsWith('data:')) return;
          const jsonStr = line.replace(/^data:\s*/, '').trim();
          if (!jsonStr || jsonStr === '[DONE]') return;
          try {
              const data = JSON.parse(jsonStr);
              const delta = data.choices?.[0]?.delta;
              if (delta?.content) {
                  if (!hasContent) {
                      statusEl.remove();
                      hasContent = true;
                  }
                  fullReply += delta.content;
                  appendText(myBubble, delta.content, scrollBox);
              }
          } catch (e) {}
      };

      if (!res.body) {
          let data;
          try { data = await res.json(); }
          catch { throw new Error('响应格式异常'); }
          const text = data.choices?.[0]?.message?.content;
          if (text) {
              statusEl.remove();
              appendText(myBubble, text, scrollBox);
              conversationHistory = [...nextMessages, { role: 'assistant', content: text }];
              if (conversationHistory.length > 40) conversationHistory = conversationHistory.slice(-40);
          } else {
              throw new Error('无法解析响应内容');
          }
          return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';
          for (const line of lines) handleLine(line);
      }

      buffer += decoder.decode();
      for (const line of buffer.split('\n')) handleLine(line);

      if (fullReply) {
          conversationHistory = [...nextMessages, { role: 'assistant', content: fullReply }];
          if (conversationHistory.length > 40) conversationHistory = conversationHistory.slice(-40);
      } else if (!hasContent && statusEl.parentNode) {
          statusEl.textContent = '（未返回内容）';
      }

    } catch (err) {
      if (err.name === 'AbortError') {
        if (aWho && aWho.isConnected) {
            const hint = document.createElement('span');
            hint.className = 'real-abort-hint';
            hint.textContent = '· 已中断';
            aWho.appendChild(hint);
        }
        if (statusEl && statusEl.parentNode) {
            statusEl.textContent = '（已中断）';
        }
      } else {
          console.error("Chat Error:", err);
          if (statusEl && statusEl.parentNode) statusEl.remove();
          if (myBubble) {
              if (myBubble.childNodes.length > 0) {
                  myBubble.appendChild(document.createElement('br'));
              }
              const errorSpan = document.createElement('div');
              errorSpan.style.color = 'red';
              errorSpan.style.fontSize = '14px';
              errorSpan.style.marginTop = '6px';
              errorSpan.style.paddingBottom = '10px';
              errorSpan.textContent = '❌ 请求失败: ' + err.message;
              myBubble.appendChild(errorSpan);
          }
      }
    } finally {
      if (abortController === myCtrl) {
          abortController = null;
      }
    }
  };

  const destroy = () => {
    if (abortController) {
        abortController.abort();
        abortController = null;
    }
    if (settingsObserver) {
        settingsObserver.disconnect();
        settingsObserver = null;
    }
    if (mdlObserver) {
        mdlObserver.disconnect();
        mdlObserver = null;
    }
    if (modalAbort) {
        modalAbort.abort();
        modalAbort = null;
    }
    if (mdlAbort) {
        mdlAbort.abort();
        mdlAbort = null;
    }
    const style = document.getElementById('real-mode-style');
    if (style) style.remove();
    const modal = document.getElementById('tri-config-modal');
    if (modal) modal.remove();
    const thread = document.getElementById('thLive');
    if (thread) thread.querySelectorAll('.row, .real-row').forEach(el => el.remove());
    
    const mpopMv = document.getElementById('mpMv');
    if (mpopMv) mpopMv.querySelectorAll('.tri-preset-row').forEach(el => el.remove());
    
    const mdTabs = document.getElementById('mdTabs');
    const mdList = document.getElementById('mdList');
    if (mdTabs) mdTabs.innerHTML = '';
    if (mdList) mdList.innerHTML = '';
    
    renderCatalogueFn = null;
    currentTabId = 'all';
    
    conversationHistory = [];
    initialized = false;
    scrollScheduled = false;
  };

  window.__real = { chat, destroy };
  
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => { 
      injectStyle(); 
      setupCataloguePage(); 
      setupSmallPopup(); 
      updateMainModelText(); 
    });
  } else {
    injectStyle(); 
    setupCataloguePage(); 
    setupSmallPopup(); 
    updateMainModelText();
  }
})();
