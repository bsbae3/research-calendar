"""Month-only planning hints; never inserted into dated events."""
import datetime as dt, re
from collect import load,save
SERIES=[('IMID',8,'https://www.imid.or.kr/','LCD / OLED / Display'),('SID Display Week',5,'https://www.displayweek.org/','LCD / OLED / Display'),('IDW',12,'https://www.idw.or.jp/','LCD / OLED / Display'),('IEDM',12,'https://ieee-iedm.org/','반도체 소자 및 공정'),('ISSCC',2,'https://www.isscc.org/','TFT 집적회로'),('VLSI Symposium',6,'https://www.vlsisymposium.org/','반도체 소자 및 공정'),('IEEE SENSORS',10,'https://ieee-sensors.org/','센서'),('CVPR',6,'https://cvpr.thecvf.com/','컴퓨터 사이언스'),('NeurIPS',12,'https://neurips.cc/','AI 반도체'),('ICML',7,'https://icml.cc/','컴퓨터 사이언스')]
def run(today=None):
 today=today or dt.date.today(); events=load('events.json'); out=[]
 for offset in range(37):
  y,m=divmod(today.year*12+today.month-1+offset,12);m+=1
  for name,month,url,field in SERIES:
   if month!=m:continue
   alias='Display Week' if name=='SID Display Week' else name
   if any(re.search(r'\b'+re.escape(alias)+r'\b',e['title'],re.I) and e['start'][:4]==str(y) and e['kind']=='학회' and not e.get('origin','').startswith('labelled') for e in events):continue
   out.append(dict(title=f'{name} {y}',month=f'{y}-{m:02}',source_url=url,field=field,status='예상 개최 월 · 공식 날짜 미확정',location=''))
 save('recurring.json',out)
if __name__=='__main__':run()
