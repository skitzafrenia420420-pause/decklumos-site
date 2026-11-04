"""Builds data/all-sailings.json (unique sailings across data/sailings/*.json) for the
Trending deals tiles and the /sailings/ list. Run after refresh.py. No new facts: copies fields."""
import json, glob, os
H = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(H, 'sailings.json')))
U = {}
for f in sorted(glob.glob(os.path.join(H, 'sailings', '*.json'))):
    for r in json.load(open(f))['sailings']:
        U.setdefault(r['url'], r)
rows = sorted(U.values(), key=lambda r: (r['date'], r['price']))
froms = sorted({r['from'] for r in rows})
out = {'checked': S['checked'], 'source': 'carnival.com', 'froms': froms,
       'cols': ['date', 'nights', 'price', 'perNight', 'from', 'title', 'ship', 'url'],
       'rows': [[r['date'], r['nights'], r['price'], r['perNight'], froms.index(r['from']), r['title'], r['ship'], r['url']] for r in rows]}
json.dump(out, open(os.path.join(H, 'all-sailings.json'), 'w'), separators=(',', ':'))
print(len(rows), 'sailings')
