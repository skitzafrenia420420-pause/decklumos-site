#!/usr/bin/env python3
"""Refresh real sailings + homepage deals for decklumos.com/test-redesign/ (test link only).
Source: carnival.com public cruise-search JSON (robots.txt allows /cruisesearch/api). 1 request per port, 2 s apart.
Never invents data. Promo tags, "limited time" labels and countdowns are emitted ONLY when the source
returns them (merchBannerOffer / extraSavingsType / specialScoops / an end date). Carnival currently returns none.
Run: python3 test-redesign/data/refresh.py   (writes sailings.json next to this file)"""
import json, time, urllib.request, datetime, sys, os
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(HERE,'sailings.json')
PORTS=json.load(open(os.path.join(HERE,'ports.json')))
UA='Mozilla/5.0 (compatible; DecklumosBot/1.0; +https://decklumos.com/support/)'
CODES={'cozumel':'CZM','george-town-cayman':'CAY','roatan':'RTB','philipsburg':'SXM','charlotte-amalie':'STT','san-juan':'SJU','ocho-rios':'OCJ','oranjestad':'ARB',
'nassau':'NAS','bimini-bs':'BIM','celebration-key-bs':'CBK','half-moon-cay-bs':'HMD',
'juneau-us':'JNU','ketchikan-us':'KTN','skagway-us':'SKY','sitka-us':'SIT','icy-strait-point-us':'PSO','victoria-ca':'YYJ',
'barcelona':'BCN','civitavecchia':'CIV','naples':'NAP','santorini':'JTR','mykonos':'MYK','dubrovnik':'DBV','valletta':'VLT','palma':'PMI',
'cabo-san-lucas-mx':'CSL','puerto-vallarta-mx':'PVR','ensenada-mx':'ENS','mazatl-n-mx':'MZT','progreso-mx':'PGR','belize-city-bz':'BZE','costa-maya':'CMZ','puerto-lim-n-cr':'LMO',
'amsterdam-nl':'AMS','copenhagen-dk':'CPH','stockholm-se':'NYN','tallinn-ee':'TLL','helsinki-fi':'HEL'}
today=datetime.date.today()
def easter(y):
    a=y%19;b=y//100;c=y%100;d=b//4;e=b%4;f=(b+8)//25;g=(b-f+1)//3;h=(19*a+b-d-g+15)%30;i=c//4;k=c%4;l=(32+2*e+2*i-h-k)%7;m=(a+11*h+22*l)//451
    return datetime.date(y,(h+l-7*m+114)//31,(h+l-7*m+114)%31+1)
def nth(y,m,wd,n):
    d=datetime.date(y,m,1);d+=datetime.timedelta((wd-d.weekday())%7);return d+datetime.timedelta(7*(n-1))
HOL=[]
for y in (today.year,today.year+1):
    HOL+= [('Thanksgiving',nth(y,11,3,4)),('Christmas',datetime.date(y,12,25)),("New Year's",datetime.date(y+1,1,1)),('Easter',easter(y)),('Fourth of July',datetime.date(y,7,4))]
HOL=sorted({(n,d) for n,d in HOL if d>=today},key=lambda x:x[1])
def promos(it,s):
    """Only source-stated promo text. Returns list of {'text','limited','ends'}."""
    out=[]
    for o in [it.get('specialScoops'),s.get('extraSavingsType')]+[r.get('extraSavingsType') for r in (s.get('rooms') or {}).values() if isinstance(r,dict)]:
        if not o: continue
        for x in (o if isinstance(o,list) else [o]):
            t=x if isinstance(x,str) else (x.get('title') or x.get('text') or x.get('name') if isinstance(x,dict) else None)
            if not t: continue
            ends=x.get('endDate') or x.get('expirationDate') if isinstance(x,dict) else None
            out.append({'text':str(t)[:60],'limited':'limited time' in str(t).lower(),'ends':ends})
    return out
out={'checked':datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='minutes'),'sources':[
 {'site':'carnival.com','status':'used','note':'Prices per person in USD for 2 guests, cheapest room, taxes and fees not included, as shown on carnival.com when checked. Prices change; confirm on the booking site.'},
 {'site':'cruisecritic.com','status':'skipped','note':'robots.txt blocks automated agents'},
 {'site':'msccruises.com','status':'skipped','note':'blocked automated browsers; nothing taken from MSC'}],
 'ports':{}}
allrows=[]
for pid,code in CODES.items():
    url=f'https://www.carnival.com/cruisesearch/api/search?pageNumber=1&pageSize=50&ptPort={code}&sort=fromprice&showBest=true&async=true&currency=USD&locality=1'
    rows=[]
    try:
        d=json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/json'}),timeout=30))
        for it in d['results']['itineraries']:
            for s in it.get('sailings',[]):
                dep=datetime.date.fromisoformat(s['departureDate'][:10]);arr=datetime.date.fromisoformat(s['arrivalDate'][:10])
                if dep<today or not s.get('lowestPrice'):continue
                n=(arr-dep).days
                rows.append({'ship':it['shipName'],'line':'Carnival Cruise Line','title':it['itineraryTitle'],'from':it['departurePortName'],'date':dep.isoformat(),'end':arr.isoformat(),'nights':n,'price':s['lowestPrice'],'perNight':round(s['lowestPrice']/max(n,1)),'currency':'USD','source':'carnival.com','promos':promos(it,s),
                 'url':'https://www.carnival.com'+(s['sailingURL'] if s.get('sailingURL','').startswith('/') else it['itineraryURL'])})
    except Exception as e:
        print('fail',pid,e,file=sys.stderr)
    rows.sort(key=lambda r:r['date'])
    for r in rows: r['port']=pid
    allrows+=rows
    out['ports'][pid]={'carnivalCode':code,'sailings':rows[:8],'cheapest':min(rows,key=lambda r:r['price']) if rows else None,'total':len(rows)}
    print(pid,len(rows))
    time.sleep(2)
if not allrows:
    sys.exit('no sailings fetched; keeping previous sailings.json')
# ---- homepage deals: rank every region by its live best price per night; drop regions with none
regions=[]
for R in PORTS['regions']:
    rr=[r for r in allrows if r['port'] in R['ports']]
    if not rr: continue
    best=min(rr,key=lambda r:(r['perNight'],r['price']))
    regions.append({'id':R['id'],'name':R['name'],'img':R['img'],'best':best,'portName':PORTS['ports'][best['port']]['name'],'count':len(rr),
        'promo':next((p for r in rr for p in r['promos']),None)})
regions.sort(key=lambda g:g['best']['perNight'])
out['deals']={'regions':regions,'dropped':[R['name'] for R in PORTS['regions'] if R['id'] not in {g['id'] for g in regions}]}
if allrows:
    lo=min(allrows,key=lambda r:r['perNight']); out['deals']['fromPerNight']={'value':lo['perNight'],'sailing':lo}
seen=set();uniq=[]
for r in sorted(allrows,key=lambda r:r['price']):
    k=r['url']
    if k not in seen: seen.add(k);uniq.append(r)
ny=str(today.year+1)
out['deals']['nextYear']={'year':ny,'picks':[r for r in uniq if r['date'][:4]==ny][:6]}
hol=[]
for name,day in HOL:
    m=[r for r in uniq if r['date']<=day.isoformat()<r['end']]
    if m: hol.append({'holiday':name,'day':day.isoformat(),'count':len(m),'best':m[0]})
out['deals']['holidays']=hol[:6]
json.dump(out,open(OUT,'w'),indent=1)
print('regions',[(g['name'],g['best']['perNight']) for g in regions],'dropped',out['deals']['dropped'],'hol',[(h['holiday'],h['day'],h['best']['price']) for h in hol])
