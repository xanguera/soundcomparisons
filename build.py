#!/usr/bin/env python3
"""Fetch Sound Comparisons study data and build index.html (mobile front-end).
Usage: python3 build.py            -> fetches live data, writes index.html
"""
import json,os,gzip,re,csv,urllib.request
API='https://soundcomparisons.com/query/data'
def get(q):
  with urllib.request.urlopen(API+q, timeout=180) as r: return json.loads(r.read().decode('utf-8'))
WS=lambda x:' '.join((x or '').split())
HERE=os.path.dirname(os.path.abspath(__file__))
DUMMY={'--','..','...','…'}  # the original site's marker for "no such word in this variety" (Transcription.js); skip it
# The original site's colour list (soundcomparisons.com/js/models/Colors.js, live copy; the GitHub repo is out of date)
COLORS=['#E6E6E6','#CCCCFF','#CCFFFF','#CFFF7C','#FFFACD','#FFCC99','#C59595','#E6C7DD','#FECECE','#FFFFFF']
def region_color(d,fams,r):
  # Same rule as the original site (models/Region.js, models/Family.js): in multi-family studies (ColorByFamily=1)
  # a region takes its family's colour, by the family's position in the study's list; otherwise colour by RegionGpIx
  if d['study']['ColorByFamily']=='1' and r['FamilyIx'] in fams: return COLORS[fams.index(r['FamilyIx'])%len(COLORS)]
  return COLORS[int(r['RegionGpIx'])%len(COLORS)]
out={};missing=[]
G=get('?global');studies=[x for x in G['studies'] if x!='--'];G=G['global']
PEOPLE={str(c['ContributorIx']):WS((c['Forenames'] or '')+' '+(c['Surnames'] or '')) for c in G['contributors']}
STATUS={str(t['LanguageStatusType']):t['StatusTooltip'] for t in G['languageStatusTypes']}
MGROUPS=[(str(m['MeaningGroupIx']),m['Name']) for m in G['meaningGroups']]
CREDITS=[('Spoken by','ContributorSpokenBy'),('Recorded by','ContributorRecordedBy1'),('Recorded by','ContributorRecordedBy2'),
  ('Sound editing','ContributorSoundEditingBy'),('Phonetic transcription','ContributorPhoneticTranscriptionBy'),('Reconstruction','ContributorReconstructionBy')]
def info(l):
  # Details for the variety page; only fields that have a value, credits resolved to names
  i={'key':l['FilePathPart']}
  def put(k,v):
    v=WS(v)
    if v: i[k]=v
  put('about',l.get('ToolTip')); put('variety',l.get('SpecificLanguageVarietyName'))
  put('status',STATUS.get(l.get('LanguageStatusType') or '')); put('period',l.get('HistoricalPeriod'))
  put('place',', '.join(x for x in dict.fromkeys(WS(l.get(k)) for k in ('PreciseLocality','NearestCity','StateRegion')) if x))
  put('iso',l.get('ISOCode')); put('glotto',l.get('GlottoCode')); put('wiki',(l.get('WikipediaLinkPart') or '').replace(' ','_'))
  put('speaker',(l.get('SpeakerFirstNames') or '')+' '+(l.get('SpeakerSurnames') or ''))
  cr={}
  for label,k in CREDITS:
    n=PEOPLE.get(l.get(k) or '')
    if n and n not in cr.setdefault(label,[]): cr[label].append(n)
  for a,y,pg in (('ContributorCitationAuthor1','Citation1Year','Citation1Pages'),('ContributorCitationAuthor2','Citation2Year','Citation2Pages')):
    n=PEOPLE.get(l.get(a) or '')
    if n: cr.setdefault('Source',[]).append(n+(' '+l[y] if l.get(y) else '')+(': '+l[pg] if l.get(pg) else ''))
  if cr: i['credits']=[[k,v] for k,v in cr.items() if v]
  return i
for sname in studies:
  print('fetching',sname,flush=True)
  d=get('?study='+sname); name=d['study']['Name']
  RK=lambda r:(r['FamilyIx'],r.get('SubFamilyIx') or '0',r['RegionGpIx'])
  regs={RK(r):r['RegionGpNameLong'] for r in d['regions']}
  fams=[f['FamilyIx'] for f in d['families']]
  rcol={RK(r):region_color(d,fams,r) for r in d['regions']}
  rorder={RK(r):(int(r['FamilyIx']),int(r.get('SubFamilyIx') or 0),int(r['RegionGpSortIx'] or 0)) for r in d['regions']}
  lreg={}
  for rl in d['regionLanguages']:
    if RK(rl) in regs:  # skip memberships of featured sets that are not a listed region (e.g. Europe's family-0 set)
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
    g2=WS(w.get('FullRfcModernLg02'))
    words.append([g, w['FullRfcProtoLg01'], w['FileNameRfcModernLg01'] or '', g2 if g2 and g2!=WS(w['FullRfcModernLg01']) else ''])
  # Meaning groups (Numbers, Colours...) in the original site's order; words in member order inside each
  gw={}
  for w in d['words']:
    gw.setdefault(w['MeaningGroupIx'] or '',[]).append((int(w['MeaningGroupMemberIx'] or 0),widx[w['IxElicitation']+'_'+w['IxMorphologicalInstance']]))
  groups=[[n,[i for _,i in sorted(gw.pop(k))]] for k,n in MGROUPS if k in gw]
  rest=sorted(i for v in gw.values() for _,i in v)
  if rest: groups.append(['Other',rest])
  # cells: per word: list of [langIdx, ipa, path, spelling, ipa, path, spelling...]
  cells=[[] for _ in words]
  hasSound={l['LanguageIx']:False for l in d['languages']};miss=[]
  for t in d['transcriptions'].values():
    wk=t['IxElicitation']+'_'+t['IxMorphologicalInstance']
    if wk not in widx or t['LanguageIx'] not in lidx: continue
    ph=t.get('Phonetic') or ''
    ph=ph if isinstance(ph,list) else [ph]
    sp=t.get('SpellingAltv1') or '';sp=sp if isinstance(sp,list) else [sp]
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
      vs.append([ph[i] if i<len(ph) else '', path, WS(sp[i]) if i<len(sp) and sp[i] else ''])
    if any(v[0] or v[1] for v in vs): cells[widx[wk]].append([lidx[t['LanguageIx']]]+[x for v in vs for x in v])
  nmiss={}
  for li,w,p,f in miss:
    if hasSound[li]: missing.append([name,langs[lidx[li]][0],w,p,'https://soundcomparisons.com/sound/'+f])
    else: nmiss[li]=nmiss.get(li,0)+1
  for li,c in nmiss.items():  # one row per variety with no recordings at all: a wrong folder name, or none recorded by design
    missing.append([name,langs[lidx[li]][0],'(all %d words)'%c,'','https://soundcomparisons.com/sound/'+fps[li]+'/'])
  out[name]={'regions':[WS(regs[k]) for k in regList],'colors':[rcol[k] for k in regList],'langs':langs,'words':words,'groups':groups,'cells':cells,'info':[info(l) for l in d['languages']],
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
