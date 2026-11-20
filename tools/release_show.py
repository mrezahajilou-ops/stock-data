import json,re,sys
def show(t,n=4200,keys=()):
    d=json.load(open('/tmp/epr/pr/%s.json'%t)); x=d['text']
    q=json.load(open('/tmp/earn/e/%s.json'%t))['q'][:3]
    print('=====',t,d['d'],[(a.get('q'),a.get('act'),a.get('f'),a.get('ly'),a.get('rev'),a.get('revly'),a.get('rx')) for a in q])
    x=re.sub(r'[ \t]*\n[ \t]*',' / ',x); x=re.sub(r' {2,}',' ',x)
    print(x[:n])
    for k in keys:
        for m in list(re.finditer(k,x))[:1]: print('  >>',x[max(0,m.start()-60):m.start()+900])
for a in sys.argv[1:]:
    p=a.split(':'); show(p[0],int(p[1]) if len(p)>1 else 4200,tuple(p[2:]))
