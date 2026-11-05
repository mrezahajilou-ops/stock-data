/* Home page: search any US stock, today's market, top-30 teaser, all tools, Stock Pro, then book/contest/portfolio. */
var ACC=!!window.RZS_ACCESS;
function go(t){location.href='/pages/stock#'+encodeURIComponent(t)}
function chg(v){return v==null||!isFinite(v)?'—':'<span class="num '+(v>=0?'up':'dn')+'">'+(v>=0?'+':'')+v.toFixed(2)+'%</span>'}
function market(){var q=RZQ&&RZQ.q;if(!q)return;var L=[['SPY','S&P 500'],['QQQ','Nasdaq 100'],['DIA','Dow Jones']].filter(function(x){return q[x[0]]});
  if(!L.length)return;$('rzh-mkt').innerHTML=L.map(function(x){return '<span><span class="num">'+x[1]+'</span> '+chg(q[x[0]][1])+'</span>'}).join('')+'<span>'+esc(RZQ_ST[RZQ.status]||'')+'</span>'}
function top3(){fetch(RAW+'/top30/top30.json?v='+Math.floor(Date.now()/1800000)).then(function(r){if(!r.ok)throw 0;return r.json()}).then(function(D){
  var L=D.rows.map(function(r){var q=RZQ&&RZQ.q&&RZQ.q[r.t],px=q&&q[0]>0?q[0]:r.px;return {t:r.t,up:r.tgt/px-1,na:r.na}}).sort(function(a,b){return b.up-a.up}).slice(0,3);
  $('rzh-t30').innerHTML=L.map(function(r,i){return '<a href="/pages/top-30"><span><span class="r">#'+(i+1)+'</span> '+(ACC?'<span class="tk">'+esc(r.t)+'</span>':'🔒 <span class="k">مخصوص مشترکین</span>')+'<br><span class="k"><span class="num">'+r.na+'</span> تحلیلگر</span></span><span class="u">+'+(r.up*100).toFixed(0)+'%</span></a>'}).join('')}).catch(function(){var s=$('rzh-t30s');if(s)s.style.display='none'})}
liveQuotes().then(market);
liveQuotes().then(top3);
loadAll().then(function(){picker($('rzh-q'),$('rzh-sg'),go)});
$('rzh-go').addEventListener('click',function(){var t=$('rzh-q').value.trim().toUpperCase();if(t)go(t)});
