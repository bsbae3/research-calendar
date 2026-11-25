let excellence=[],csRankings=[];
function csMatches(e){return csRankings.filter(r=>!/(?:oral|poster|spotlight|findings)/i.test(r.abbr)&&matches(e,r))}
function csPass(e,f){let rows=csMatches(e);return rows.some(r=>f==='kiise-top'?r.kiise==='최우수':f==='kiise-good'?r.kiise==='우수':r.score>=.75)}
function csEventSearch(e,q){return csMatches(e).some(r=>searchMatch(r,q))}
function csLabel(e){let rows=csMatches(e);if(rows.length!==1)return '';let r=rows[0];return [r.kiise?'KIISE '+r.kiise+' (2024)':'','CS '+r.score.toFixed(2)].filter(Boolean).join(' · ')}
function csCatalogue(){
 let q=$('q').value, f=$('quality').value,root=$('results');
 let rows=csRankings.filter(r=>searchMatch(r,q)&&(!f||f==='kiise-top'&&r.kiise==='최우수'||f==='kiise-good'&&r.kiise==='우수'||f==='cs-high'&&r.score>=.75||f==='bk'&&r.bk21||['1','2','3','4'].includes(f)&&r.bk21===f));
 rows.sort((a,b)=>b.score-a.score||a.abbr.localeCompare(b.abbr));
 $('note').textContent=rows.length+'개 평가 항목 · 첨부 통합 목록 기준 (현재 인정 여부는 기관별 원문 확인)';
 let info=el('article',undefined,'event');let d=el('div',undefined,'details');
 d.append(el('h3','CS 분야 우수 학술대회 통합 평가'),el('p','KIISE 2024 · BK21 2018 · KAIST 2025 · SNU 2024.4 · POSTECH 2026.1'),el('p','종합 점수는 5개 평가를 정규화하여 평균한 참고 지표이며 공식 IF가 아닙니다. 공란은 해당 목록의 표시 없음.'),link('https://yoon.ws/csconf','자료 출처 / 기준 설명'));info.append(d);root.append(info);
 for(let r of rows){let box=el('article',undefined,'event'),d=el('div',undefined,'details');d.append(el('h3',r.abbr+' — '+r.name),el('p','종합 점수 '+r.score.toFixed(2)),el('p','KIISE: '+(r.kiise||'—')+' · BK21 IF: '+(r.bk21||'—')+' · KAIST: '+(r.kaist||'—')+' · SNU: '+(r.snu||'—')+' · POSTECH: '+(r.postech||'—')),link('https://dblp.org/db/'+r.dblp+'/index.html','DBLP'));box.append(d);root.append(box)}
}
const escRx=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
function matches(e,r){let t=e.title;return [r.abbr,r.name,...(r.abbr==='NIPS'?['NeurIPS']:[])].filter(Boolean).some(n=>new RegExp('(^|[^A-Za-z0-9])'+escRx(n)+'(?=$|[^A-Za-z0-9])',n.length<=4?'':'i').test(t))}
function quality(e){let b=excellence.filter(r=>r.category==='bk'&&matches(e,r)&&(!/spotlight/i.test(r.abbr+' '+r.name)||/spotlight/i.test(e.title)));let ranks=[...new Set(b.map(r=>r.rank))];if(b.length&&ranks.length===1)return b[0];if(b.length)return {category:'ambiguous',source:'복수 인정 IF 후보: 원문 확인'};return excellence.find(r=>r.category==='focus'&&matches(e,r))}
function qualityPass(e){let f=$('quality').value,r=quality(e);return !f||(['kiise-top','kiise-good','cs-high'].includes(f)?csPass(e,f):!!r&&(f===r.category||f===String(r.rank)))}
function qualityLabel(e){let r=quality(e);return !r?csLabel(e):r.category==='bk'?'★ BK21 IF '+r.rank:r.category==='focus'?'★ 연구 관심':'★ 인정 확인 필요'}
function qualityColor(e){let r=quality(e);return r?.category==='bk'?({4:'#c62828',3:'#b45309',2:'#7952b3',1:'#2475c5'})[r.rank]:r?.category==='focus'?'#008b8b':'#777'}
function catalogue(){let q=$('q').value.toLowerCase(),f=$('quality').value,field=$('field').value,rs=excellence.filter(r=>(!field||r.field===field||!r.field&&field!=='양자컴퓨팅 / Quantum Computing')&&(!f||f===r.category||f===String(r.rank))&&searchMatch(r,q));$('note').textContent=rs.length+'개 항목 · 일정 확정과 별개 · BK21+ 현행 기준 재확인 필요';for(let r of rs){let n=el('article',undefined,'event');n.append(el('div',r.abbr,'date'),el('div',r.name+' · '+(r.category==='bk'?'BK21 IF '+r.rank+' · '+r.code+' · PDF '+r.page+'쪽':r.field)+' · '+r.source,'details'));$('results').append(n)}}
