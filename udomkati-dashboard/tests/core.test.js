const {JSDOM,VirtualConsole}=require('jsdom');const fs=require('fs');
const html=fs.readFileSync(require('path').join(__dirname,'..','index.html'),'utf8').replace(/<link[^>]*>/g,'');
const errs=[],res=[];const ok=(n,c,x)=>res.push((c?'PASS ':'FAIL ')+n+(c?'':' -> '+x));
const store=new Map(),ls=[];
const notify=()=>{const docs=[...store].map(([id,v])=>({id,data:()=>v}));ls.forEach(f=>f({docs,empty:!docs.length}))};
const db={collection:()=>({onSnapshot:(f,e)=>{ls.push(f);setTimeout(()=>f({docs:[...store].map(([id,v])=>({id,data:()=>v})),empty:!store.size}),0);return()=>{}}}),
 doc:p=>({set:async d=>{store.set(p.split('/')[1],d);setTimeout(notify,0)},delete:async()=>{store.delete(p.split('/')[1]);setTimeout(notify,0)}})};
const user={id:async()=>'u1',me:async()=>({id:'u1',name:'Math',canEdit:true,isOwner:true}),can:async()=>true,profiles:async()=>({})};
let sampleOut={scores:{A:80,B:20,C:10},primary:'A',why:'x',funnel:'aw',platform:'TikTok',hooks:['h'],risks:[]};
const saved=[];const dls={save:async o=>{saved.push(o.filename)}};
const vc=new VirtualConsole();vc.on('jsdomError',e=>errs.push('jsdomError '+e.message));vc.on('error',e=>errs.push('console.error '+e));
const dom=new JSDOM(html,{runScripts:'dangerously',pretendToBeVisual:true,virtualConsole:vc,url:'https://x.test/',beforeParse(w){
 w.claude={use:async n=>({db,user,sample:{json:async()=>sampleOut},downloads:dls}[n]||null)};
 w.addEventListener('error',e=>errs.push('window.error '+e.message));w.addEventListener('unhandledrejection',e=>errs.push('rej '+(e.reason&&e.reason.message||e.reason)));
 w.HTMLCanvasElement.prototype.getContext=()=>new Proxy({},{get:(t,k)=>k==='measureText'?()=>({width:10}):()=>{},set:()=>true});
 w.HTMLCanvasElement.prototype.toBlob=function(cb){cb(new w.Blob(['x']))};
 w.document.fonts={load:async()=>{}};w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=()=>{};}});
const w=dom.window,ev=c=>w.eval(c),sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{await sleep(300);
 ok('init no errors',!errs.length,errs.join(' | '));
 ok('host role',ev('ME.host&&ME.role')==='host'||ev('ME.role')==='host',ev('ME.role'));
 ok('self added to team',ev('C.tm.some(m=>m.u==="u1")'),'');
 ev(`C.sel={k:'day',d:'2026-10-20'};ca();$('aT').value='p';$('aN').value='<img src=x onerror=alert(1)> Post A';$('aA').checked=false;$('aB').click()`);await sleep(50);
 ok('post added',ev('P.length')===1,ev('P.length'));
 ok('xss escaped in list',!ev("$('list').innerHTML").includes('<img'),'');
 ok('plan doc saved',store.has('plan')&&JSON.parse(store.get('plan').j).posts.length===1,'');
 ev(`C.sel={k:'day',d:'2026-10-21'};ca();$('aT').value='t';$('aN').value='Task 1';$('aB').click()`);await sleep(30);
 ev(`C.sel={k:'day',d:'2026-10-22'};ca();$('aT').value='e';$('aN').value='Event 1';$('aB').click()`);await sleep(30);
 ok('task+event',ev('TK.length')===1&&ev('EV.length')===1,ev('TK.length+","+EV.length'));
 ev(`$('pjN').value='Course';$('pjB').click()`);await sleep(30);
 ok('project added',ev('C.pj.length')===1,'');
 ev(`P[0].pj=C.pj[0].id;TK[0][4]=C.pj[0].id;EV[0][2]=C.pj[0].id;ch()`);
 ok('pill colored',ev("$('cg').innerHTML").includes('color-mix'),'');
 ok('csv',ev('csvM()').includes('Course')&&ev('csvM()').includes('Task 1'),'');
 ok('draw',!!ev('drawM()'),'');
 await ev(`document.getElementById('xP').onclick()`);await sleep(30);ev(`document.getElementById('xC').onclick()`);await sleep(30);
 ok('downloads called',saved.length===2,saved.join());
 // owner/status change through UI
 const sel=w.document.querySelector('select[data-ps]');sel.value='2';sel.dispatchEvent(new w.Event('change',{bubbles:true}));await sleep(20);
 ok('status change',ev('P[0].s')===2,ev('P[0].s'));
 // viewer denied
 ev("ME.host=false;ME.role='viewer'");
 const s2=w.document.querySelector('select[data-ps]');s2.value='3';s2.dispatchEvent(new w.Event('change',{bubbles:true}));await sleep(20);
 ok('viewer denied',ev('P[0].s')===2,ev('P[0].s'));
 ev("ME.role='own';ME.name='Z'");ev("P[0].o='Z';ch()");
 const s3=w.document.querySelector('select[data-ps]');s3.value='3';s3.dispatchEvent(new w.Event('change',{bubbles:true}));await sleep(20);
 ok('own can status own',ev('P[0].s')===3,ev('P[0].s'));
 ev("P[0].o='Q';ch()");
 const s4=w.document.querySelector('select[data-ps]');s4.value='1';s4.dispatchEvent(new w.Event('change',{bubbles:true}));await sleep(20);
 ok('own denied other',ev('P[0].s')===3,ev('P[0].s'));
 ev("ME.host=true;ME.role='host'");
 // approvals
 ev("C.rq=[{u:'u9',name:'Pure',at:1}];ch()");
 w.document.querySelector('[data-ok]').click();await sleep(30);
 ok('approve',ev('C.tm.some(m=>m.u==="u9")'),'');
 // AI persona + planner
 ev("aiPost(1)");await sleep(30);ok('aiPost',ev('P[0].p.includes("A")'),'');
 ev(`$('plB').value='brief';$('plS').value='2026-11-01';$('plE').value='2026-11-14'`);
 sampleOut={project_name:'Camp',ideas:[{title:'I1',hook:'h',media:'m',goal:'g',funnel:'co',persona:'B',date:'2026-11-03'},{title:'bad',date:'2027-01-01'}],tasks:[{title:'T1',date:'2026-11-02',owner_role:'คอนเทนต์',approval:true}],notes:'n'};
 w.document.getElementById('plP').value='__new';
 w.document.getElementById('plG').click();await sleep(50);
 w.document.getElementById('plI').click();await sleep(30);
 ok('planner import',ev('P.length')===2&&ev('TK.length')===2&&ev('C.pj.length')===2,ev('P.length+","+TK.length+","+C.pj.length'));
 ev('refresh()');
 ok('alerts render',ev("$('alL').innerHTML.length")>0,'');
 ok('no errors after flows',!errs.length,errs.join(' | '));
 // second client load from db
 const html2=html;const d2=new JSDOM(html2,{runScripts:'dangerously',pretendToBeVisual:true,virtualConsole:vc,url:'https://x.test/',beforeParse(w2){
  w2.claude={use:async n=>({db,user:{...user,id:async()=>'u9',me:async()=>({id:'u9',name:'Pure',canEdit:false,isOwner:false})},sample:{json:async()=>sampleOut},downloads:dls}[n]||null)};
  w2.HTMLCanvasElement.prototype.getContext=()=>({});w2.document.fonts={load:async()=>{}};}});
 await sleep(300);const w2=d2.window;
 ok('client2 loaded state',w2.eval('P.length')===2&&w2.eval('C.pj.length')===2,w2.eval('P.length+","+C.pj.length'));
 ok('client2 role from team',w2.eval('ME.role')==='editor',w2.eval('ME.role'));
 console.log(res.join('\n'));process.exit(0)})().catch(e=>{console.log(res.join('\n'));console.log('TEST CRASH',e.stack);process.exit(1)});
