from collect import *
html='''<script type="application/ld+json">{"@graph":[{"@type":"Event","name":"Test 2027","startDate":"2027-03-01","endDate":"2027-03-02","location":{"name":"Hall","address":{"addressCountry":"Korea"}}}]}</script>'''
a=extract(html,'https://example.org',['TFT'],'학회');assert len(a)==1 and a[0]['location']=='Hall, Korea';assert len(merge(a,a))==1;assert len(load('watchlist.json'))>=200;assert len(load('events.json'))>=43
for e in load('events.json'):valid(e)
print('PASS: extraction, deduplication, seed validation')
