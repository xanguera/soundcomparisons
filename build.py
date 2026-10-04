#!/usr/bin/env python3
"""Fetch Sound Comparisons study data and build index.html (mobile front-end).
Usage: python3 build.py            -> fetches live data, writes index.html
"""
import json,os,gzip,re,urllib.request
API='https://soundcomparisons.com/query/data'
def get(q):
  with urllib.request.urlopen(API+q, timeout=180) as r: return json.loads(r.read().decode('utf-8'))
WS=lambda x:' '.join((x or '').split())
HERE=os.path.dirname(os.path.abspath(__file__))
out={}
studies=[x for x in get('?global')['studies'] if x!='--']
for sname in studies:
  print('fetching',sname,flush=True)
  d=get('?study='+sname); name=d['study']['Name']
  RK=lambda r:(r['FamilyIx'],r.get('SubFamilyIx') or '0',r['RegionGpIx'])
  regs={RK(r):r['RegionGpNameLong'] for r in d['regions']}
  rorder={RK(r):(int(r['FamilyIx']),int(r.get('SubFamilyIx') or 0),int(r['RegionGpSortIx'] or 0)) for r in d['regions']}
  lreg={}
  for rl in d['regionLanguages']:
    lreg.setdefault(rl['LanguageIx'],(RK(rl), rl['RegionGpMemberLgNameLongInThisSubFamilyWebsite'] or ''))
  regList=sorted(regs, key=lambda k:rorder[k]); rid={k:i for i,k in enumerate(regList)}
  langs=[];lidx={};fps={l['LanguageIx']:l['FilePathPart'] for l in d['languages']}
  for l in d['languages']:
    try: lat=float(l['Latitude']); lon=float(l.get('Longitude') or l['Longtitude'])
    except: lat=lon=None
    rg,ln=lreg.get(l['LanguageIx'],(None,''))
    lidx[l['LanguageIx']]=len(langs)
    langs.append([WS(ln or l['ShortName']), l['FilePathPart'], round(lat,3) if lat is not None else None, round(lon,3) if lon is not None else None, rid.get(rg,-1)])
  words=[];widx={}
  for w in d['words']:
    k=w['IxElicitation']+'_'+w['IxMorphologicalInstance']
    widx[k]=len(words)
    g=w['FullRfcModernLg01']; 
    if w.get('LongerRfcModernLg01'): g+=' ('+w['LongerRfcModernLg01']+')'
    words.append([g, w['FullRfcProtoLg01']])
  # cells: per word: list of [langIdx, ipa, path]
  cells=[[] for _ in words]
  for t in d['transcriptions'].values():
    wk=t['IxElicitation']+'_'+t['IxMorphologicalInstance']
    if wk not in widx or t['LanguageIx'] not in lidx: continue
    ph=t.get('Phonetic') or ''
    ph=ph if isinstance(ph,list) else [ph]
    sps=t.get('soundPaths') or []
    if sps and not isinstance(sps[0],list): sps=[sps]
    fp=fps[t['LanguageIx']]
    vs=[]
    for i in range(max(len(ph),len(sps))):
      mp=[x for x in (sps[i] if i<len(sps) else []) if x.endswith('.mp3')]
      path=mp[0][len('/sound/'):-4] if mp else ''
      pre=fp+'/'+fp
      if path.startswith(pre): path='~'+path[len(pre):]
      vs.append([ph[i] if i<len(ph) else '', path])
    if any(v[0] or v[1] for v in vs): cells[widx[wk]].append([lidx[t['LanguageIx']]]+[x for v in vs for x in v])
  out[name]={'regions':[WS(regs[k]) for k in regList],'langs':langs,'words':words,'cells':cells,
    'bounds':[[float(d['study']['DefaultBottomRightLat']),float(d['study']['DefaultTopLeftLon'])],[float(d['study']['DefaultTopLeftLat']),float(d['study']['DefaultBottomRightLon'])]]}
  s=json.dumps(out[name],ensure_ascii=False,separators=(',',':'))
  print(name, len(langs),'langs',len(words),'words', len(s)//1024,'KB raw', len(gzip.compress(s.encode()))//1024,'KB gz')
out={k:out[k] for k in studies if k in out}
blob=json.dumps(out,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
tpl=open(os.path.join(HERE,'template.html'),encoding='utf-8').read()
open(os.path.join(HERE,'index.html'),'w',encoding='utf-8').write(tpl.replace('__DATA__',blob))
print('wrote index.html', len(blob)//1024,'KB')
