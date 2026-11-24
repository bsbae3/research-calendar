from multi45 import *
from bs4 import BeautifulSoup
for text in ['August 12–15, 2027','12–15 August 2027','2027년 8월 12일~15일','2027年8月12日～15日']:
 assert [(str(a),str(b)) for a,b,_ in dates(text)]==[('2027-08-12','2027-08-15')],text
s=BeautifulSoup('<article><h2>Sensor Conference 2027</h2><p>August 12–15, 2027</p></article>','html.parser')
a=cards(s,'https://example.org', ['센서'],'학회',dt.date(2026,11,24),dt.date(2029,11,24));assert len(a)==1 and a[0]['origin'].startswith('labelled')
assert not list(dates('August 12–15'))
print('PASS multi-source date and card fixtures')
