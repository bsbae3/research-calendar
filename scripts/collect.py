import argparse,csv,json,re,datetime as dt, pathlib, urllib.parse, urllib.request, time
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parents[1]; DATA=ROOT/'docs/data'
def load(n): return json.loads((DATA/n).read_text(encoding='utf8'))
def save(n,v):
 p=DATA/n; tmp=p.with_suffix('.tmp'); tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8'); tmp.replace(p)
def day(s): return dt.date.fromisoformat(str(s)[:10]).isoformat()
def valid(e):
 title=str(e['title']).strip(); url=str(e['source_url']); start=day(e['start']); end=day(e.get('end') or start)
 if not title or urllib.parse.urlsplit(url).scheme not in ('http','https') or end<start: raise ValueError('invalid event')
 f=e.get('fields',[]); f=f if isinstance(f,list) else re.split('[;|]',f)
 return dict(e,title=title,source_url=url,start=start,end=end,location=str(e.get('location') or ''),kind=str(e.get('kind') or '학회'),fields=f,origin=e.get('origin','manual import'))
def key(e):
 y=re.search(r'20\d\d',e['title']); return (e['title'].casefold().strip(),e['kind'],y.group() if y else e['start'][:4])
def merge(old,new):
 out={key(e):e for e in old}
 for e in new: out[key(e)]=e
 return sorted(out.values(),key=lambda e:(e['start'],e['title']))
class Parser(HTMLParser):
 def __init__(self): super().__init__(); self.active=False; self.buf=[]; self.objects=[]
 def handle_starttag(self,t,a):
  if t=='script' and dict(a).get('type','').lower()=='application/ld+json': self.active=True; self.buf=[]
 def handle_data(self,d):
  if self.active:self.buf.append(d)
 def handle_endtag(self,t):
  if t=='script' and self.active:
   self.active=False
   try:self.objects.append(json.loads(''.join(self.buf)))
   except ValueError:pass
def walk(x):
 if isinstance(x,list):
  for v in x:yield from walk(v)
 elif isinstance(x,dict):
  t=x.get('@type',[]); t=[t] if isinstance(t,str) else t
  if any(str(v).split('/')[-1] in ('Event','BusinessEvent','EducationEvent','ExhibitionEvent','ConferenceEvent') for v in t):yield x
  for v in x.values():
   if isinstance(v,(list,dict)):yield from walk(v)
def location(x):
 if isinstance(x,str):return x
 if isinstance(x,list):return '; '.join(map(location,x))
 if not isinstance(x,dict):return ''
 a=x.get('address',{}); a=a if isinstance(a,dict) else {'streetAddress':a}; return ', '.join(str(v) for v in [x.get('name'),a.get('streetAddress'),a.get('addressLocality'),a.get('addressRegion'),a.get('addressCountry')] if v)
def extract(html,url,fields,kind):
 p=Parser();p.feed(html); out=[]
 for x in walk(p.objects):
  try:
   if any(s in str(x.get('eventStatus','')) for s in ('Cancelled','Postponed')):continue
   out.append(valid(dict(title=x['name'],source_url=url,start=x['startDate'],end=x.get('endDate'),location=location(x.get('location')),kind=kind,fields=fields,origin='structured feed')))
  except (ValueError,KeyError,TypeError):continue
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--import-file');ap.add_argument('--collect',action='store_true');args=ap.parse_args();old=load('events.json');new=[]
 if args.import_file:
  p=pathlib.Path(args.import_file)
  with p.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f)) if p.suffix.lower()=='.csv' else json.load(f)
  for e in rows:new.append(valid(e))
 if args.collect:
  logs=[]; today=dt.date.today(); limit=today+dt.timedelta(days=1096)
  for s in load('sources.json'):
   url=s['url']; log=dict(url=url,checked=dt.datetime.now(dt.timezone.utc).isoformat(),count=0)
   try:
    req=urllib.request.Request(url,headers={'User-Agent':'ResearchPortal/4.0 (public event metadata; low frequency)'})
    with urllib.request.urlopen(req,timeout=15) as r: html=r.read(3_000_000).decode('utf8','replace')
    found=[e for e in extract(html,url,s['fields'],s['kind']) if today<=dt.date.fromisoformat(e['end']) and dt.date.fromisoformat(e['start'])<=limit];new.extend(found);log.update(status='ok' if found else 'no structured events',count=len(found))
   except Exception as e:log['status']=f'{type(e).__name__}: {e}'[:250]
   logs.append(log);time.sleep(1)
  save('logs.json',logs)
 save('events.json',merge(old,new));print(f'{len(new)} incoming; {len(merge(old,new))} total')
if __name__=='__main__':main()
