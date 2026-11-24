"""Extract explicit dates from event cards and labelled date rows. Never infer years."""
import re, datetime as dt, calendar
from collect import valid
M={x.lower():i for i in range(1,13) for x in (calendar.month_name[i],calendar.month_abbr[i])}; M['sept']=9
MON='(?:'+'|'.join(sorted(M,key=len,reverse=True))+')'
SEP=r'\s*(?:[-–—~〜～]|to|至|부터)\s*'
PATTERNS=[(rf'(?P<y>20\d{{2}})\s*[-./년年]\s*(?P<m>\d{{1,2}})\s*[-./월月]\s*(?P<d>\d{{1,2}})(?:일|日)?(?:{SEP}(?:(?P<ey>20\d{{2}})\s*[-./년年]\s*)?(?:(?P<em>\d{{1,2}})\s*[-./월月]\s*)?(?P<ed>\d{{1,2}})(?:일|日)?)?',False),(rf'(?P<m>{MON})\.?\s+(?P<d>\d{{1,2}})(?:{SEP}(?:(?P<em>{MON})\.?\s+)?(?P<ed>\d{{1,2}}))?\s*,?\s*(?P<y>20\d{{2}})',True),(rf'(?P<d>\d{{1,2}})(?:{SEP}(?P<ed>\d{{1,2}}))?\s+(?P<m>{MON})\.?\s*,?\s*(?P<y>20\d{{2}})',True)]
EVENT=r'conference|symposium|workshop|seminar|congress|summit|meeting|exhibition|forum|training|course|학회|학술|세미나|워크숍|교육|포럼|전시|강연|学会|講演|会议|研讨|展览|\b(?:ISSCC|IEDM|IMID|IDW|DAC|ISCA|ITC|SID|ICCAD|CVPR|ICML|NeurIPS|ICLR|AAAI|ICCV|ECCV)\b'
LABEL=r'(?:conference dates?|event dates?|meeting dates?|開催日程|開催期間|会议时间|会议日期|개최\s*(?:일정|기간|일시)|행사\s*일시|교육\s*기간|(?:paper|abstract|full paper|manuscript)\s+(?:submission\s+)?(?:deadline|due)|submission deadline|registration deadline|early registration|논문\s*(?:제출|접수)\s*마감|초록\s*(?:제출|접수)\s*마감|신청\s*마감|投稿締切|截稿日期)'
def dates(text):
 for pat,english in PATTERNS:
  for m in re.finditer(pat,text,re.I):
   g=m.groupdict(); month=lambda x:M[x.lower()] if english else int(x)
   try:
    a=dt.date(int(g['y']),month(g['m']),int(g['d'])); b=dt.date(int(g.get('ey') or g['y']),month(g.get('em') or g['m']),int(g.get('ed') or g['d']))
    if a<=b and (b-a).days<=45:yield a,b,m.group()
   except (ValueError,KeyError):pass

def cards(soup,url,fields,kind,today,limit):
 out=[]; heading=soup.find('h1') or soup.title
 def add(title,text,k,source):
  if not title or len(title)>200 or not re.search(EVENT,title,re.I):return
  for a,b,evidence in dates(text):
   if today<=b and a<=limit:
    out.append(valid(dict(title=title,source_url=source,start=str(a),end=str(b),location='',kind=k,fields=fields,origin='labelled multi-source candidate — review source',evidence=evidence+' | '+text[:350])))
 for node in soup.select('article, tr, li, .event, .conference, .event-card, .conference-card')[:1500]:
  text=node.get_text(' ',strip=True)
  if len(text)>650 or not text:continue
  h=node.select_one('h2,h3,h4,a[href]'); title=h.get_text(' ',strip=True) if h else ''
  if not title or re.search(LABEL,text,re.I):continue
  # A single explicit date/range in a compact event card is a candidate only.
  if len(list(dates(text)))==1:add(title,text,kind,url)
 if heading:
  title=heading.get_text(' ',strip=True)
  for node in soup.select('tr, li, p, dt, div')[:2500]:
   text=node.get_text(' ',strip=True)
   if len(text)>240:continue
   m=re.search(LABEL,text,re.I)
   if not m:continue
   label=m.group(); k='등록 마감' if re.search('registration|신청',label,re.I) else '논문 마감' if re.search('deadline|due|마감|締切|截稿',label,re.I) else kind
   add(title+(' — '+label if k!=kind else ''),text[m.end():],k,url)
 return list({(e['title'],e['start'],e['kind']):e for e in out}.values())
