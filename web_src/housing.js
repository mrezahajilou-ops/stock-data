
(function(){
var D=JSON.parse(document.getElementById('hs-data').textContent);
var $=function(i){return document.getElementById(i)};
var NS='http://www.w3.org/2000/svg';
var LOC=D.loc||'en-US',TX=D.tx||{};
function nf(v,d){return v.toLocaleString(LOC,{minimumFractionDigits:d,maximumFractionDigits:d})}
function fm(v,f){if(v==null||!isFinite(v))return '—';
  var Y=D.sym||'$';
  if(f==='$'){if(D.cur)return new Intl.NumberFormat(LOC,{style:'currency',currency:D.cur,currencyDisplay:D.narrow?'narrowSymbol':'symbol',maximumFractionDigits:0}).format(v);return (v<0?'-':'')+Y+Math.round(Math.abs(v)).toLocaleString('en-US')}
  if(f==='$k'){if(D.cur&&D.narrow)return new Intl.NumberFormat(LOC,{style:'currency',currency:D.cur,currencyDisplay:'narrowSymbol',maximumFractionDigits:0}).format(v);if(D.cur)return new Intl.NumberFormat(LOC,{style:'currency',currency:D.cur,currencyDisplay:D.narrow?'narrowSymbol':'symbol',notation:'compact',maximumFractionDigits:Math.abs(v)>=1e6?2:0}).format(v);return Math.abs(v)>=1e6?Y+(v/1e6).toFixed(2)+'M':Y+Math.round(v/1e3)+'K'}
  if(f==='%')return nf(v,1)+'%';
  if(f==='%2')return nf(v,2)+'%';
  if(f==='+%')return (v>0?'+':v<0?'−':'')+nf(Math.abs(v),1)+'%';
  if(f==='k')return D.loc?new Intl.NumberFormat(LOC,{notation:'compact',maximumFractionDigits:2}).format(v*1000):(Math.abs(v)>=1000?(v/1000).toFixed(2).replace(/0$/,'')+'M':Math.round(v)+'K');
  if(f==='x')return nf(v,1)+'×';
  if(f==='i')return nf(v,1);
  if(f==='n')return Math.round(v).toLocaleString(LOC);
  if(f==='m')return nf(v,1)+(TX.mo||' mo');
  return String(Math.round(v*100)/100)}
var MN=D.loc?Array.apply(null,Array(12)).map(function(_,i){return new Intl.DateTimeFormat(LOC,{month:'short'}).format(new Date(2020,i,15))}):['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
function tx(k){return +k.slice(0,4)+(+k.slice(5,7)-1)/12}
function lab(k,q){var m=+k.slice(5,7);return q?(TX.q||'Q')+(Math.floor((m-1)/3)+1)+' '+k.slice(0,4):MN[m-1]+' '+k.slice(0,4)}
function nice(lo,hi,n){var sp=(hi-lo)||Math.abs(hi)||1,st=Math.pow(10,Math.floor(Math.log10(sp/n))),e=sp/n/st;st*=e>5?10:e>2?5:e>1?2:1;var a=Math.floor(lo/st+1e-9)*st,b=Math.ceil(hi/st-1e-9)*st,o=[];for(var v=a;v<=b+st*.001;v+=st)o.push(+v.toFixed(10));return o}
/* line chart: S=[{n,c,d:[[ym,v]],ax,f,q,dash}], o={yrs, zero, h} */
function chart(el,S,o){o=o||{};var W=Math.max(300,Math.round(el.clientWidth||760)),H=o.h||(W<560?230:300),L=8,R=8,T=14,B=26,cut=o.yrs?tx(D.maxk)-o.yrs:-1e9;
  var ser=S.map(function(s){return {s:s,d:s.d.filter(function(p){return p[1]!=null&&tx(p[0])>=cut})}}).filter(function(x){return x.d.length>1});
  if(o.norm){ser.forEach(function(x){var b=x.d[0][1];x.d=x.d.map(function(p){return [p[0],p[1]/b*100]})})}
  el.innerHTML='';if(!ser.length){el.innerHTML='<p class="mut">'+(TX.nodata||'No data.')+'</p>';return}
  var xs=[].concat.apply([],ser.map(function(x){return x.d.map(function(p){return tx(p[0])})})),x0=Math.min.apply(0,xs),x1=Math.max.apply(0,xs);
  var ax={};ser.forEach(function(x){var a=x.s.ax||0,v=x.d.map(function(p){return p[1]});ax[a]=ax[a]||{lo:1e18,hi:-1e18,f:x.s.f};ax[a].lo=Math.min(ax[a].lo,Math.min.apply(0,v));ax[a].hi=Math.max(ax[a].hi,Math.max.apply(0,v))});
  Object.keys(ax).forEach(function(a){var A=ax[a],pos=A.lo>=0;if(o.zero&&A.lo>0)A.lo=0;var pad=(A.hi-A.lo)*.05||1,lo=A.lo-(o.zero&&A.lo===0?0:pad);if(pos&&lo<0)lo=0;A.t=nice(lo,A.hi+pad,W<560?4:5);A.lo=A.t[0];A.hi=A.t[A.t.length-1]});
  var dual=ax[1]!=null;L=W<560?44:56;if(D.narrow&&ax[0].f==='$')L=W<560?62:74;R=dual?(W<560?40:52):10;
  var X=function(t){return L+(t-x0)/(x1-x0||1)*(W-L-R)},Y=function(v,a){var A=ax[a||0];return T+(1-(v-A.lo)/(A.hi-A.lo||1))*(H-T-B)};
  var cid='c'+Math.random().toString(36).slice(2,8),svg='<svg viewBox="0 0 '+W+' '+H+'" width="'+W+'" height="'+H+'" role="img"><defs><clipPath id="'+cid+'"><rect x="'+L+'" y="0" width="'+(W-L-R)+'" height="'+(H-B)+'"/></clipPath></defs>';
  var tf=function(A){var f=A.f==='%2'?'%':A.f==='$'?'$k':A.f;if((f==='i'||f==='%')&&A.t.every(function(v){return Math.abs(v-Math.round(v))<1e-9}))return function(v){return f==='%'?nf(v,0)+'%':nf(v,0)};return function(v){return fm(v,f)}},tf0=tf(ax[0]),tf1=dual?tf(ax[1]):null;
  ax[0].t.forEach(function(v){var y=Y(v,0);svg+='<line x1="'+L+'" x2="'+(W-R)+'" y1="'+y+'" y2="'+y+'" stroke="#1F242E"/><text x="'+(L-6)+'" y="'+(y+4)+'" fill="#8A8F99" font-size="11.5" text-anchor="end">'+tf0(v)+'</text>'});
  if(dual)ax[1].t.forEach(function(v){var y=Y(v,1);svg+='<text x="'+(W-R+6)+'" y="'+(y+4)+'" fill="#8A8F99" font-size="11.5">'+tf1(v)+'</text>'});
  if(o.zero0&&ax[0].lo<0&&ax[0].hi>0){var yz=Y(0,0);svg+='<line x1="'+L+'" x2="'+(W-R)+'" y1="'+yz+'" y2="'+yz+'" stroke="#4A505C"/>'}
  var span=x1-x0,stp=span>40?10:span>20?5:span>8?2:1;while((W-L-R)/(span/stp)<40)stp=stp===1?2:stp===2?5:stp*2;for(var yr=Math.ceil(x0/stp)*stp;yr<=x1;yr+=stp){var xx=X(yr);svg+='<line x1="'+xx+'" x2="'+xx+'" y1="'+(H-B)+'" y2="'+(H-B+4)+'" stroke="#4A505C"/><text x="'+xx+'" y="'+(H-6)+'" fill="#8A8F99" font-size="11.5" text-anchor="middle">'+yr+'</text>'}
  if(o.bands)o.bands.forEach(function(b){var a=X(tx(b[0])),z=X(tx(b[1]));if(z>L&&a<W-R)svg+='<rect x="'+Math.max(a,L)+'" y="'+T+'" width="'+(Math.min(z,W-R)-Math.max(a,L))+'" height="'+(H-T-B)+'" fill="rgba(200,83,79,.08)"/>'});
  ser.forEach(function(x){var p=x.d.map(function(q,i){return (i?'L':'M')+X(tx(q[0])).toFixed(1)+','+Y(q[1],x.s.ax).toFixed(1)}).join('');svg+='<path d="'+p+'" fill="none" stroke="'+x.s.c+'" stroke-width="'+(x.s.w||2)+'"'+' clip-path="url(#'+cid+')"'+(x.s.dash?' stroke-dasharray="5 4"':'')+' stroke-linejoin="round"/>'});
  svg+='<line class="cx" x1="0" x2="0" y1="'+T+'" y2="'+(H-B)+'" stroke="#8A8F99" stroke-dasharray="3 3" style="display:none"/><rect x="'+L+'" y="0" width="'+(W-L-R)+'" height="'+H+'" fill="transparent"/></svg><div class="tip"></div>';
  el.innerHTML=svg;var sv=el.querySelector('svg'),cx=sv.querySelector('.cx'),tip=el.querySelector('.tip');
  function mv(e){var b=sv.getBoundingClientRect(),px=((e.touches?e.touches[0].clientX:e.clientX)-b.left)/b.width*W;if(px<L||px>W-R){tip.style.display='none';cx.style.display='none';return}
    var t=x0+(px-L)/(W-L-R)*(x1-x0),h='',k0=null;ser.forEach(function(x){var best=null,bd=1e9;x.d.forEach(function(q){var dd=Math.abs(tx(q[0])-t);if(dd<bd){bd=dd;best=q}});if(best&&bd<.6){if(!k0)k0=best[0];h+='<div><i style="display:inline-block;width:9px;height:9px;border-radius:2px;background:'+x.s.c+';margin-right:6px"></i>'+x.s.n+': <b>'+(o.norm?fm(best[1],'i'):fm(best[1],x.s.f))+'</b></div>'}});
    if(!h){tip.style.display='none';return}var lx=X(tx(k0));cx.setAttribute('x1',lx);cx.setAttribute('x2',lx);cx.style.display='';
    tip.innerHTML='<div style="color:#8A8F99">'+lab(k0,ser[0].s.q)+'</div>'+h;tip.style.display='block';var w=tip.offsetWidth,pxl=lx/W*b.width;tip.style.left=Math.max(0,Math.min(b.width-w,pxl+(pxl>b.width/2?-w-12:12)))+'px'}
  sv.addEventListener('mousemove',mv);sv.addEventListener('touchmove',mv,{passive:true});sv.addEventListener('touchstart',mv,{passive:true});
  sv.addEventListener('mouseleave',function(){tip.style.display='none';cx.style.display='none'});
  var lg=el.parentNode.querySelector('.lg');if(lg)lg.innerHTML=ser.map(function(x){return '<span><i style="background:'+x.s.c+'"></i>'+x.s.n+'</span>'}).join('')}
/* chart cards: data-c = config key; tabs (data-t) and ranges (data-y) */
var CFG=window.HS_CFG;
document.querySelectorAll('#hs [data-chart]').forEach(function(card){var key=card.getAttribute('data-chart'),C=CFG[key],box=card.querySelector('.ch'),st={t:0,y:C.y||0};
  function draw(){var v=C.v[st.t];chart(box,v.s(D),{yrs:st.y,zero:v.zero,zero0:v.zero0,norm:v.norm,bands:D.rec});var n=card.querySelector('.cn');if(n)n.innerHTML=v.note||''}
  var rw=0;window.addEventListener('resize',function(){clearTimeout(rw);rw=setTimeout(function(){if(Math.abs(box.clientWidth-(box.__w||0))>20){box.__w=box.clientWidth;draw()}},150)});box.__w=box.clientWidth;
  card.querySelectorAll('[data-t]').forEach(function(b){b.addEventListener('click',function(){st.t=+b.getAttribute('data-t');card.querySelectorAll('[data-t]').forEach(function(x){x.classList.toggle('on',x===b)});draw()})});
  card.querySelectorAll('[data-y]').forEach(function(b){b.addEventListener('click',function(){st.y=+b.getAttribute('data-y');card.querySelectorAll('[data-y]').forEach(function(x){x.classList.toggle('on',x===b)});draw()})});
  draw()});
/* sparklines in the driver tiles */
document.querySelectorAll('#hs svg[data-sp]').forEach(function(s){var d=D.sp[s.getAttribute('data-sp')]||[];if(d.length<2)return;var v=d.map(function(p){return p[1]}),lo=Math.min.apply(0,v),hi=Math.max.apply(0,v),W=200,H=34;
  s.setAttribute('viewBox','0 0 '+W+' '+H);s.setAttribute('preserveAspectRatio','none');s.innerHTML='<path d="'+v.map(function(y,i){return (i?'L':'M')+(i/(v.length-1)*W).toFixed(1)+','+(H-2-(y-lo)/((hi-lo)||1)*(H-4)).toFixed(1)}).join('')+'" fill="none" stroke="#C9A961" stroke-width="1.6" vector-effect="non-scaling-stroke"/>'});
/* sortable tables with "show more" and a year-by-year detail row */
function yearly(yr,rentLab){var h='<div class="tw"><table class="yt"><thead><tr><th>Year</th><th>Typical home</th><th>Change</th><th>House</th><th>Change</th><th class="hm">Apartment / condo</th><th class="hm">Change</th><th>'+rentLab+'</th><th>Change</th></tr></thead><tbody>';
  var rows=[];for(var i=yr.length-1;i>=1;i--){var a=yr[i],p=yr[i-1];if(a[1]==null)continue;
    function c(j){return a[j]&&p[j]?(a[j]/p[j]-1)*100:null}
    function cc(v){return '<td class="'+(v==null?'':v>0?'up':'dn')+'">'+fm(v,'+%')+'</td>'}
    rows.push('<tr><td>'+a[0]+(i===yr.length-1?' <small class="mut">(latest)</small>':'')+'</td><td>'+fm(a[1],'$')+'</td>'+cc(c(1))+'<td>'+fm(a[2],'$')+'</td>'+cc(c(2))+'<td class="hm">'+fm(a[3],'$')+'</td>'+cc(c(3)).replace('<td','<td class="hm"')+'<td>'+fm(a[4],'$')+'</td>'+cc(c(4))+'</tr>')}
  return h+rows.join('')+'</tbody></table></div>'}
function table(id,rows,opt){var tb=$(id);if(!tb)return;var tbl=tb.closest('table'),body=tbl.tBodies[0],btn=$(id+'-more'),sel=$(id+'-sort'),shown=opt.n,all=false;
  var trs={};Array.prototype.forEach.call(body.querySelectorAll('tr.rw'),function(tr){trs[tr.getAttribute('data-k')]=tr});
  var map={};rows.forEach(function(r){map[r.k]=r});
  function render(){var key=sel?sel.value:opt.def,sp=key.split(':'),f=sp[0],dir=sp[1]==='d'?-1:1;
    var list=rows.slice();if(f==='def'){list.sort(function(a,b){return a.o-b.o})}else list.sort(function(a,b){var x=a[f],y=b[f];if(x==null&&y==null)return 0;if(x==null)return 1;if(y==null)return -1;return typeof x==='string'?dir*x.localeCompare(y):dir*(x-y)});
    body.querySelectorAll('tr.det').forEach(function(d){d.remove()});
    list.forEach(function(r,i){var tr=trs[r.k];tr.classList.remove('open');tr.classList.toggle('hid',!all&&i>=shown);body.appendChild(tr)});
    if(btn)btn.textContent=all?opt.less:opt.more}
  if(sel)sel.addEventListener('change',render);
  if(btn)btn.addEventListener('click',function(){all=!all;render();if(!all)tbl.scrollIntoView({block:'nearest'})});
  body.addEventListener('click',function(e){var tr=e.target.closest('tr.rw');if(!tr||e.target.closest('a'))return;open(tr)});
  function open(tr,force){var nx=tr.nextElementSibling;if(nx&&nx.classList.contains('det')){if(force)return;nx.remove();tr.classList.remove('open');return}
    var r=map[tr.getAttribute('data-k')],d=document.createElement('tr');d.className='det';d.innerHTML='<td colspan="'+tr.children.length+'">'+opt.detail(r)+'</td>';tr.after(d);tr.classList.add('open')}
  render();return {open:function(k){var tr=trs[k];if(!tr)return;if(tr.classList.contains('hid')){all=true;render()}open(tr,true);tr.scrollIntoView({behavior:'smooth',block:'center'})}}}
function stDetail(r){var g=function(lbl,v,s){return '<div><small>'+lbl+'</small><b>'+v+'</b>'+(s?'<small>'+s+'</small>':'')+'</div>'};
  return '<div class="dg">'+g('Price-to-income',fm(r.pir,'x'),'home value ÷ household income')+g('Gross rent yield',fm(r.yld,'%2'),'yearly rent ÷ home value')+g('Property tax',fm(r.tax,'%2'),'taxes paid ÷ home value')+g('Homeownership',fm(r.own,'%'),'owner households')+
  g('Rental vacancy',fm(r.rv,'%'),'empty rentals for rent')+g('Median household income',fm(r.inc,'$'),'Census '+(r.ry||''))+g('Rent by size',(r.r1?fm(r.r1,'$')+' / '+fm(r.r2,'$')+' / '+fm(r.r3,'$'):'—'),'1 / 2 / 3 bedrooms')+
  (r.lst_n?g('Homes for sale',fm(r.lst_n,'n'),(r.lst!=null?fm(r.lst,'+%')+' vs a year ago':'')):'')+(r.dom?g('Days on market',fm(r.dom,'n'),'median, listings'):'')+(r.lp?g('Median listing price',fm(r.lp,'$'),'asking price'):'')+'</div>'+
  '<b style="font-weight:600">'+r.n+': year by year</b><p class="mut" style="margin:2px 0 6px;font-size:12.5px">End-of-year values (December); the last row is the latest month. House = single-family home, apartment / condo = condos and co-ops. Rent = median gross rent from the Census survey of that year.</p>'+yearly(r.yr,'Median rent')}
function mtDetail(r){return '<b style="font-weight:600">'+r.n+': year by year</b><p class="mut" style="margin:2px 0 6px;font-size:12.5px">December of each year and the latest month. Rent = typical asking rent for a new lease (all rentals), available from 2015.</p>'+yearly(r.yr,'Typical rent')}
D.states.forEach(function(r,i){r.k=r.ab;r.o=i});D.metros.forEach(function(r,i){r.k='m'+i;r.o=i});
var ST=table('hs-st',D.states,{n:D.nshow||5,def:'def',more:D.moreS||'Show all '+D.states.length+' states',less:D.lessS||'Show the 5 largest states only',detail:window.HS_STDETAIL||stDetail});
if(D.metros.length)table('hs-mt',D.metros,{n:5,def:'def',more:'Show all '+D.metros.length+' metro areas',less:'Show the 5 largest only',detail:mtDetail});
document.querySelectorAll('#hs table.stk').forEach(function(t){var b=t.parentNode.parentNode.querySelector('.more');if(!b)return;b.addEventListener('click',function(){var on=b.getAttribute('data-on')!=='1';b.setAttribute('data-on',on?'1':'0');t.querySelectorAll('tr.xr').forEach(function(r){r.classList.toggle('hid',!on)});b.textContent=on?'Show fewer':b.getAttribute('data-l')})});
document.querySelectorAll('#hs .stabs [data-g]').forEach(function(b){b.addEventListener('click',function(){var g=b.getAttribute('data-g');document.querySelectorAll('#hs .stabs [data-g]').forEach(function(x){x.classList.toggle('on',x===b)});document.querySelectorAll('#hs .sgrp').forEach(function(x){x.style.display=x.getAttribute('data-g')===g?'':'none'})})});
/* map */
var MAP=$('hs-map');if(MAP){var G=D.geo,svg=MAP.querySelector('svg'),tip=MAP.querySelector('.tip'),by={};D.states.forEach(function(r){by[r.ab]=r});
  var M=D.mapm||{v:['Typical home value','$',0],y1:['1-year change','+%',1],y10:['10-year change','+%',0],rent:['Median rent','$',0],yld:['Gross rent yield','%2',0],pir:['Price-to-income','x',0],tax:['Property tax rate','%2',0],lst:['Homes for sale, 1-year change','+%',1]};
  var cur=D.map0||'v',small=D.small||{RI:1,DE:1,CT:1,NJ:1,MD:1,MA:1,NH:1,VT:1,DC:1,HI:0};
  var ps='',ts='';Object.keys(G.s).forEach(function(ab){ps+='<path data-s="'+ab+'" d="'+G.s[ab].d+'"/>';if(!small[ab])ts+='<text x="'+G.s[ab].c[0]+'" y="'+G.s[ab].c[1]+'" data-s="'+ab+'">'+ab+'</text>'});
  svg.innerHTML=ps+ts;
  function col(t,div){if(div){var a=[200,83,79],m=[58,62,72],b=[79,163,122],c=t<.5?a:b,k=t<.5?(.5-t)*2:(t-.5)*2;return 'rgb('+Math.round(m[0]+(c[0]-m[0])*k)+','+Math.round(m[1]+(c[1]-m[1])*k)+','+Math.round(m[2]+(c[2]-m[2])*k)+')'}
    var lo=[36,40,50],hi=[232,200,120];return 'rgb('+Math.round(lo[0]+(hi[0]-lo[0])*t)+','+Math.round(lo[1]+(hi[1]-lo[1])*t)+','+Math.round(lo[2]+(hi[2]-lo[2])*t)+')'}
  function paint(){var m=M[cur],div=m[2],vals=D.states.map(function(r){return r[cur]}).filter(function(v){return v!=null}).sort(function(a,b){return a-b}),mx=Math.max(Math.abs(vals[0]),Math.abs(vals[vals.length-1]))||1;
    svg.querySelectorAll('path').forEach(function(p){var r=by[p.getAttribute('data-s')],v=r?r[cur]:null,t;
      if(v==null){p.setAttribute('fill','#1C2029');return}
      if(div)t=.5+v/mx/2;else{var i=0;while(i<vals.length&&vals[i]<v)i++;t=vals.length>1?i/(vals.length-1):.5}
      p.setAttribute('fill',col(t,div));if(G.merged){p.setAttribute('stroke',col(t,div));p.style.strokeWidth='1.4'}p.__t=t});
    svg.querySelectorAll('text').forEach(function(x){var p=svg.querySelector('path[data-s="'+x.getAttribute('data-s')+'"]');x.classList.toggle('lt',!div&&p&&p.__t<.45||div&&p&&Math.abs(p.__t-.5)<.22)});
    var sc=MAP.parentNode.querySelector('.scale');sc.innerHTML='<span>'+(div?fm(-mx,m[1]):fm(vals[0],m[1]))+'</span><i style="background:linear-gradient(90deg,'+(div?col(0,1)+','+col(.5,1)+','+col(1,1):col(0)+','+col(1))+')"></i><span>'+(div?fm(mx,m[1]):fm(vals[vals.length-1],m[1]))+'</span><span>'+m[0]+'</span>'}
  function show(e,ab){var r=by[ab];if(!r)return;var b=MAP.getBoundingClientRect(),x=(e.touches?e.touches[0].clientX:e.clientX)-b.left,y=(e.touches?e.touches[0].clientY:e.clientY)-b.top;
    if(D.tip){tip.innerHTML='<b style="font-weight:600">'+r.n+'</b>'+D.tip.map(function(x){return '<br>'+x[0]+': <b>'+fm(r[x[1]],x[2])+'</b>'}).join('')}else
    tip.innerHTML='<b style="font-weight:600">'+r.n+'</b><br>Typical home: <b>'+fm(r.v,'$')+'</b> <span class="'+(r.y1>0?'up':'dn')+'">'+fm(r.y1,'+%')+'</span><br>Median rent: <b>'+fm(r.rent,'$')+'</b> · yield '+fm(r.yld,'%2')+(cur!=='v'&&cur!=='rent'&&cur!=='yld'&&cur!=='y1'?'<br>'+M[cur][0]+': <b>'+fm(r[cur],M[cur][1])+'</b>':'');
    tip.style.display='block';var w=tip.offsetWidth;tip.style.left=Math.max(0,Math.min(b.width-w,x+(x>b.width/2?-w-14:14)))+'px';tip.style.top=Math.max(0,y-70)+'px'}
  svg.addEventListener('mousemove',function(e){var p=e.target.closest('path');if(p)show(e,p.getAttribute('data-s'));else tip.style.display='none'});
  svg.addEventListener('mouseleave',function(){tip.style.display='none'});
  svg.addEventListener('click',function(e){var p=e.target.closest('path');if(!p)return;var ab=p.getAttribute('data-s');if(e.pointerType==='touch'||('ontouchstart' in window&&!tip.__s)){show(e,ab)}if(ST)ST.open(ab)});
  document.querySelectorAll('#hs [data-m]').forEach(function(b){b.addEventListener('click',function(){cur=b.getAttribute('data-m');document.querySelectorAll('#hs [data-m]').forEach(function(x){x.classList.toggle('on',x===b)});paint()})});
  paint()}
})();
