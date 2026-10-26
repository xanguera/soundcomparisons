#!/usr/bin/env python3
"""Fetch Sound Comparisons study data and build index.html (mobile front-end).
Usage: python3 build.py            -> fetches live data, writes index.html
"""
import json,os,gzip,re,csv,math,colorsys,urllib.request
API='https://soundcomparisons.com/query/data'
def get(q):
  with urllib.request.urlopen(API+q, timeout=180) as r: return json.loads(r.read().decode('utf-8'))
WS=lambda x:' '.join((x or '').split())
HERE=os.path.dirname(os.path.abspath(__file__))
DUMMY={'--','..','...','…'}  # the original site's marker for "no such word in this variety" (Transcription.js); skip it
def lab(h,s,l):  # HSL -> CIELAB, to measure how different two colours look
  f=lambda c:((c+.055)/1.055)**2.4 if c>.04045 else c/12.92
  r,g,b=map(f,colorsys.hls_to_rgb(h/360,l,s))
  t=lambda x:x**(1/3) if x>.008856 else 7.787*x+16/116
  X,Y,Z=t((r*.4124+g*.3576+b*.1805)/.95047),t(r*.2126+g*.7152+b*.0722),t((r*.0193+g*.1192+b*.9505)/1.08883)
  return 116*Y-16,500*(X-Y),200*(Y-Z)
PALETTE=[(h,.7,l) for l in (.45,.62) for h in range(0,360,30)]
def region_colors(langs,n):
  # Greedy: each region takes the palette colour that differs most from regions within 300 km, so map neighbours never look alike
  pts={}
  for l in langs:
    if l[2] is not None and l[4]>=0: pts.setdefault(l[4],[]).append((l[2],l[3]))
  km=lambda a,b:min(math.hypot(p[0]-q[0],(p[1]-q[1])*math.cos(math.radians(p[0])))*111 for p in pts[a] for q in pts[b])
  col={}
  for a in range(n):
    near=[b for b in col if a in pts and b in pts and km(a,b)<300]
    gap=lambda c,bs:min([math.dist(lab(*c),lab(*col[b])) for b in bs] or [999])
    # a gap of 50 already reads as clearly different; past that, prefer a colour no other region uses
    col[a]=max(PALETTE,key=lambda c:(min(gap(c,near),50),c not in col.values(),gap(c,near),gap(c,col)))
  return ['hsl(%d %d%% %d%%)'%(h,s*100,l*100) for h,s,l in (col[a] for a in range(n))]
out={};missing=[]
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
  spell={l['LanguageIx']:l.get('IsOrthographyHasNoTranscriptions') for l in d['languages']}  # spelling-only rows never have recordings
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
  hasSound={l['LanguageIx']:False for l in d['languages']};miss=[]
  for t in d['transcriptions'].values():
    wk=t['IxElicitation']+'_'+t['IxMorphologicalInstance']
    if wk not in widx or t['LanguageIx'] not in lidx: continue
    ph=t.get('Phonetic') or ''
    ph=ph if isinstance(ph,list) else [ph]
    sps=t.get('soundPaths') or []
    if sps and not isinstance(sps[0],list): sps=[sps]
    fp=fps[t['LanguageIx']];ex=t.get('path') or [];ex=ex if isinstance(ex,list) else [ex]
    vs=[]
    for i in range(max(len(ph),len(sps))):
      if i<len(ph) and ph[i] in DUMMY: continue
      if any(sps[i] if i<len(sps) else []): hasSound[t['LanguageIx']]=True
      elif i<len(ph) and ph[i] and i<len(ex) and spell.get(t['LanguageIx'])!='1':
        miss.append([t['LanguageIx'],words[widx[wk]][0],ph[i],fp+'/'+ex[i]+'.mp3'])
      mp=[x for x in (sps[i] if i<len(sps) else []) if x.endswith('.mp3')]
      path=mp[0][len('/sound/'):-4] if mp else ''
      pre=fp+'/'+fp
      if path.startswith(pre): path='~'+path[len(pre):]
      vs.append([ph[i] if i<len(ph) else '', path])
    if any(v[0] or v[1] for v in vs): cells[widx[wk]].append([lidx[t['LanguageIx']]]+[x for v in vs for x in v])
  nmiss={}
  for li,w,p,f in miss:
    if hasSound[li]: missing.append([name,langs[lidx[li]][0],w,p,'https://soundcomparisons.com/sound/'+f])
    else: nmiss[li]=nmiss.get(li,0)+1
  for li,c in nmiss.items():  # one row per variety with no recordings at all: a wrong folder name, or none recorded by design
    missing.append([name,langs[lidx[li]][0],'(all %d words)'%c,'','https://soundcomparisons.com/sound/'+fps[li]+'/'])
  out[name]={'regions':[WS(regs[k]) for k in regList],'colors':region_colors(langs,len(regList)),'langs':langs,'words':words,'cells':cells,
    'bounds':[[float(d['study']['DefaultBottomRightLat']),float(d['study']['DefaultTopLeftLon'])],[float(d['study']['DefaultTopLeftLat']),float(d['study']['DefaultBottomRightLon'])]]}
  s=json.dumps(out[name],ensure_ascii=False,separators=(',',':'))
  print(name, len(langs),'langs',len(words),'words', len(s)//1024,'KB raw', len(gzip.compress(s.encode()))//1024,'KB gz')
out={k:out[k] for k in studies if k in out}
blob=json.dumps(out,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
tpl=open(os.path.join(HERE,'template.html'),encoding='utf-8').read()
open(os.path.join(HERE,'index.html'),'w',encoding='utf-8').write(tpl.replace('__DATA__',blob))
print('wrote index.html', len(blob)//1024,'KB')
# Recordings the Sound Comparisons server could not find on its disk (it returns no sound file for them), for its maintainers
with open(os.path.join(HERE,'missing-recordings.csv'),'w',encoding='utf-8',newline='') as f:
  w=csv.writer(f); w.writerow(['study','variety','word','transcription','expected file'])
  w.writerows(sorted(missing,key=lambda r:(studies.index(r[0]) if r[0] in studies else 99,r[2].startswith('(all'),r[1])))
print('wrote missing-recordings.csv', len(missing),'rows')
