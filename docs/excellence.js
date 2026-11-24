let excellence=[];
const escRx=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
function matches(e,r){let t=e.title;return [r.abbr,r.name,...(r.abbr==='NIPS'?['NeurIPS']:[])].filter(Boolean).some(n=>new RegExp('(^|[^A-Za-z0-9])'+escRx(n)+'(?=$|[^A-Za-z0-9])',n.length<=4?'':'i').test(t))}
function quality(e){let b=excellence.filter(r=>r.category==='bk'&&matches(e,r)&&(!/spotlight/i.test(r.abbr+' '+r.name)||/spotlight/i.test(e.title)));let ranks=[...new Set(b.map(r=>r.rank))];if(b.length&&ranks.length===1)return b[0];if(b.length)return {category:'ambiguous',source:'복수 인정 IF 후보: 원문 확인'};return excellence.find(r=>r.category==='focus'&&matches(e,r))}
function qualityPass(e){let f=$('quality').value,r=quality(e);return !f||!!r&&(f===r.category||f===String(r.rank))}
function qualityLabel(e){let r=quality(e);return !r?'':r.category==='bk'?'★ BK21 IF '+r.rank:r.category==='focus'?'★ 연구 관심':'★ 인정 확인 필요'}
function qualityColor(e){let r=quality(e);return r?.category==='bk'?({4:'#c62828',3:'#b45309',2:'#7952b3',1:'#2475c5'})[r.rank]:r?.category==='focus'?'#008b8b':'#777'}
function catalogue(){let q=$('q').value.toLowerCase(),f=$('quality').value,rs=excellence.filter(r=>(!f||f===r.category||f===String(r.rank))&&JSON.stringify(r).toLowerCase().includes(q));$('note').textContent=rs.length+'개 항목 · 일정 확정과 별개 · BK21+ 현행 기준 재확인 필요';for(let r of rs){let n=el('article',undefined,'event');n.append(el('div',r.abbr,'date'),el('div',r.name+' · '+(r.category==='bk'?'BK21 IF '+r.rank+' · '+r.code+' · PDF '+r.page+'쪽':r.field)+' · '+r.source,'details'));$('results').append(n)}}
