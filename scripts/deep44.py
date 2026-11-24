"""Conservative labelled-date extraction, supplementing existing crawler."""
import re, datetime as dt, calendar
from collect import valid
MONTHS={m.lower():i for i,m in enumerate(calendar.month_name) if i}
MONTHS.update({m.lower():i for i,m in enumerate(calendar.month_abbr) if i})
M='(?:'+'|'.join(sorted(MONTHS,key=len,reverse=True))+')'
D=rf'(?:20\d{{2}}\s*[-./년]\s*\d{{1,2}}\s*[-./월]\s*\d{{1,2}}(?:일)?|{M}\s+\d{{1,2}},?\s+20\d{{2}}|\d{{1,2}}\s+{M}\s+20\d{{2}})'
LABEL=r'(?:conference dates?|event dates?|meeting dates?|workshop dates?|開催日程|개최\s*일정|행사\s*일시|교육\s*기간|교육\s*일정|개최\s*기간|논문\s*(?:제출|접수)\s*마감|초록\s*(?:제출|접수)\s*마감|(?:paper|abstract|full paper)\s+(?:submission\s+)?deadline|registration deadline|신청\s*마감)'
def parse(s):
 n=re.findall(r'\d+',s); m=re.search(M,s,re.I)
 if m:return dt.date(int(n[-1]),MONTHS[m.group().lower()],int(n[0]))
 return dt.date(*map(int,n))
def labelled(text,title,url,fields,kind,today,limit):
 if not title or len(title)>180 or not re.search(r'conference|symposium|workshop|seminar|meeting|training|course|학회|학술|세미나|워크숍|교육|강연|설명회|교류회',title,re.I):return []
 if not re.search(r'20\d{2}',title):return []
 out=[]
 for m in re.finditer(rf'({LABEL})\s*[:：]?\s*({D})(?:\s*(?:~|–|—|to|부터)\s*({D}))?',text,re.I):
  try:
   start=parse(m[2]); end=parse(m[3]) if m[3] else start
   # Do not truncate abbreviated ranges or accept a date followed by another range marker.
   if re.match(r'\s*(?:~|–|—|to\b|부터|\s-\s)',text[m.end():],re.I):continue
   if not today<=end<=limit or start>end:continue
   label=m[1]; deadline=bool(re.search('deadline|마감',label,re.I)); k=('등록 마감' if re.search('registration|신청',label,re.I) else '논문 마감') if deadline else kind
   if not deadline and not m[3] and not re.search('일시',label):continue
   out.append(valid(dict(title=title+(' — '+label if deadline else ''),source_url=url,start=str(start),end=str(end),location='',kind=k,fields=fields,origin='labelled official-page candidate — review source',evidence=m.group())))
  except (ValueError,KeyError):continue
 return out
