"""Conservative crawler: unstructured dates are review candidates, never confirmed events."""
import os, re, datetime as dt, io, time, urllib.parse as u, urllib.request as req
from bs4 import BeautifulSoup
from pypdf import PdfReader
from collect import load,save,extract,merge,key
from deep44 import labelled
from multi45 import cards
TERMS=r'교육|수강|강좌|특강|초청강연|기술교류|설명회|교육신청|training|course|lecture|conference|symposium|workshop|seminar|webinar|call.for.papers|deadline|submission|학회|학술|세미나|워크숍|연구회|초록|마감|講演|学会|研究会|会议|研讨|征稿|tagung|colloque|congreso'
DATE=r'20\d{2}\s*[./년年-]\s*\d{1,2}\s*[./월月-]\s*\d{1,2}|(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+20\d{2}|\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+20\d{2}'
def candidates(text,url):
 out=[]
 for m in re.finditer(DATE,text,re.I):
  snippet=text[max(0,m.start()-180):m.end()+180].strip()
  if re.search(TERMS,snippet,re.I):out.append(dict(url=url,date_text=m.group(),evidence=snippet,status='review required'))
 return out[:40]
def fetch(url):
 with req.urlopen(req.Request(url,headers={'User-Agent':'ResearchPortal/4.1 public metadata crawler'}),timeout=12) as r:
  return r.read(8_000_001),r.headers.get('Content-Type',''),r.geturl()
def run():
 import urllib.robotparser as rp
 old=load('events.json'); found=[]; logs=[]; review=[]; changes=load('changes.json'); sources=load('sources.json'); today=dt.date.today(); limit=today+dt.timedelta(days=1096)
 # rotate candidate sources weekly; priority sources daily
 for i,s in enumerate(sources):
  if os.getenv('DOMESTIC_ONLY')=='1' and not s.get('domestic'):continue
  if not s.get('domestic') and not s.get('priority') and i%7!=today.weekday():continue
  root=s['url']; queue=[root]; seen=set(); log=dict(url=root,checked=dt.datetime.now(dt.timezone.utc).isoformat(),count=0,status='no dates',errors=[])
  robots=rp.RobotFileParser(); robots.set_url(u.urljoin(root,'/robots.txt'))
  try:
   raw,_,_=fetch(robots.url); robots.parse(raw.decode('utf8','replace').splitlines())
  except Exception as e:
   if getattr(e,'code',None)==404:robots.parse([])
   else:log['status']='robots unavailable';logs.append(log);continue
  while queue and len(seen)<12:
   url=queue.pop(0)
   if url in seen or not robots.can_fetch('ResearchPortal',url):continue
   seen.add(url)
   try:
    raw,typ,final=fetch(url)
    if len(raw)>8_000_000 or u.urlsplit(final).netloc!=u.urlsplit(root).netloc:raise ValueError('size or external redirect')
    if 'pdf' in typ or raw.startswith(b'%PDF'):
     text=' '.join(p.extract_text() or '' for p in PdfReader(io.BytesIO(raw)).pages[:20])
    else:
     html=raw.decode('utf8','replace'); soup=BeautifulSoup(raw,'html.parser'); text=soup.get_text(' ',strip=True)
     for a in soup.select('a[href]'):
      href=u.urljoin(final,a['href']).split('#')[0]
      if u.urlsplit(href).netloc==u.urlsplit(root).netloc and u.urlsplit(href).scheme in ('http','https') and re.search(TERMS+r'|cfp|important.dates|events?|notice|board|공지|일정|행사|2027|2028|2029',a.get_text(' ',strip=True)+' '+href,re.I) and href not in seen and href not in queue:queue.append(href)
     queue.sort(key=lambda x: not bool(re.search(r'202[789]|cfp|deadline|important.date|schedule|calendar|일정|공지',x,re.I)))
     for e in extract(html,final,s['fields'],s['kind']):
      if s.get('aggregator'): e['origin']='labelled aggregator structured candidate — review source'
      if today.isoformat()<=e['end'] and e['start']<=limit.isoformat():found.append(e);log['count']+=1
    if 'pdf' not in typ and not raw.startswith(b'%PDF'):
     heading=soup.find('h1') or soup.title
     if heading:
      for e in cards(soup,final,s['fields'],s['kind'],today,limit)+labelled(text,heading.get_text(' ',strip=True),final,s['fields'],s['kind'],today,limit):
       review.append(dict(url=final,date_text=e['start'],evidence=e['title']+' | '+e['evidence'],status='labelled candidate',event=e))
       found.append(e);log['count']+=1
    review.extend(candidates(text,final));log['status']='fetched'
   except Exception as e:log['errors'].append(str(e)[:180])
   time.sleep(1)
  logs.append(log)
  print(f"{i+1}/{len(sources)} {root} {log['status']} events={log['count']} pages={len(seen)}",flush=True)
 prior={key(e):e for e in old}
 for e in found:
  p=prior.get(key(e))
  if p and any(p.get(k)!=e.get(k) for k in ('start','end','location')):changes.append(dict(title=e['title'],before=p,after=e,checked=today.isoformat()))
 save('events.json',merge(old,[e for e in found if key(e) not in prior or e['origin']=='structured feed']));save('logs.json',logs);save('changes.json',changes[-1000:]); previous=load('review.json');save('review.json',list({(x['url'],x['evidence']):x for x in previous+review}.values())[-5000:])
if __name__=='__main__':run()
