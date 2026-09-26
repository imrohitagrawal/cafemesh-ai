from pathlib import Path
from html import escape
import json, math, textwrap
from PIL import ImageFont

OUT=Path(__file__).parent
SHA='76134e6099c4abd0c04de06227b91e7944cc0a6e'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
C={'ink':'#202B41','muted':'#626D7E','line':'#506882','blue':'#285DA0','bluefill':'#EDF4FC','purple':'#7953AF','purplefill':'#F5F0FC','orange':'#B86023','orangefill':'#FFF3E6','gray':'#788494','grayfill':'#F3F5F8','border':'#D8DFE8','bg':'#FFFFFF','sage':'#477453'}
class Diagram:
 def __init__(self,slug,num,title,subtitle,h=1100,planned=False,badge=None):
  self.slug,self.num,self.h=slug,num,h
  self.svg=[];self.elements=[];self.seq=0;self.boxes=[]
  self.rect(0,0,1600,h,'#FFFFFF','transparent',0)
  self.text(60,49,'CAFÉMESH AI  /  ARCHITECTURE',16,C['sage'],True)
  self.text(60,103,title,36,C['ink'],True)
  self.text(60,141,subtitle,18,C['muted'])
  self.rect(1320,31,220,34,C['orangefill'] if planned else C['bluefill'],'transparent',8)
  self.text(1430,54,badge or ('PLANNED' if planned else 'CURRENT CODE'),14,C['orange'] if planned else C['blue'],True,'middle')
  self.line([(60,h-79),(1540,h-79)],C['border'],1,arrow=False)
  self.text(60,h-33,f'CODE-REVIEWED  •  26 SEP 2026  •  SOURCE {SHA[:7]}',14,C['muted'])
  self.text(1540,h-33,f'{num:02d} / 09',16,C['ink'],True,'end')
 def base(self,typ,x,y,w,h,stroke,fill,sw=1,roundness=None):
  self.seq+=1
  e={'id':f'{self.slug}-{self.seq}','type':typ,'x':x,'y':y,'width':w,'height':h,'angle':0,'strokeColor':stroke,'backgroundColor':fill,'fillStyle':'solid','strokeWidth':sw,'strokeStyle':'solid','roughness':0,'opacity':100,'groupIds':[],'frameId':None,'roundness':roundness,'seed':self.seq*719,'version':1,'versionNonce':self.seq*317,'isDeleted':False,'boundElements':None,'updated':1,'link':None,'locked':False}
  self.elements.append(e);return e
 def rect(self,x,y,w,h,fill,stroke,rx=14,sw=1.5,dashed=False):
  self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"'+(' stroke-dasharray="8 7"' if dashed else '')+'/>')
  e=self.base('rectangle',x,y,w,h,stroke,fill,sw,{'type':3} if rx else None)
  if dashed:e['strokeStyle']='dashed'
 def text(self,x,y,s,size=18,color=None,bold=False,anchor='start'):
  color=color or C['ink']; font=ImageFont.truetype(BOLD if bold else FONT,size);width=font.getlength(s)
  xx=x if anchor=='start' else x-width if anchor=='end' else x-width/2
  assert xx>=-1 and xx+width<=1601,(self.slug,s,xx,width)
  self.svg.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}" text-anchor="{anchor}">{escape(s)}</text>')
  e=self.base('text',xx,y-size,width,size*1.25,color,'transparent',1,None)
  e.update({'fontSize':size,'fontFamily':2,'text':s,'originalText':s,'textAlign':'left','verticalAlign':'top','containerId':None,'autoResize':True,'lineHeight':1.25})
 def box(self,x,y,w,h,title,body=(),kind='blue',tag=None,size=23):
  start=len(self.elements)
  color=C[kind];fill=C[kind+'fill']
  self.rect(x,y,w,h,fill,C['border'])
  self.rect(x,y+15,4,h-30,color,'transparent',2)
  yy=y+30
  if tag:self.text(x+23,yy,tag.upper(),12,color,True);yy+=33
  size=min(size, (w-46)/max(ImageFont.truetype(BOLD,size).getlength(title),1)*size)
  self.text(x+23,yy,title,int(size),C['ink'],True);yy+=31
  for row in body:
   ss=min(17,int((w-46)/max(ImageFont.truetype(FONT,17).getlength(row),1)*17))
   assert ss>=14,(title,row,'body too small')
   self.text(x+23,yy,row,ss,C['muted']);yy+=25
  assert yy-25<=y+h-10,(self.slug,title,'height overflow',yy,y+h)
  group=f'group-{self.slug}-{start}'
  for e in self.elements[start:]:e['groupIds']=[group]
  self.boxes.append((x,y,w,h,title))
 def line(self,pts,color=None,width=2.3,dash=False,arrow=True):
  color=color or C['line']; p=' '.join(f'{x},{y}' for x,y in pts)
  marker=f' marker-end="url(#{color[1:]})"' if arrow else ''
  self.svg.append(f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"'+(' stroke-dasharray="8 7"' if dash else '')+marker+'/>')
  x,y=pts[0]; rel=[[xx-x,yy-y] for xx,yy in pts]
  e=self.base('arrow' if arrow else 'line',x,y,max(xx for xx,yy in pts)-min(xx for xx,yy in pts),max(yy for xx,yy in pts)-min(yy for xx,yy in pts),color,'transparent',width,None)
  e.update({'points':rel,'lastCommittedPoint':None,'startBinding':None,'endBinding':None,'startArrowhead':None,'endArrowhead':'arrow' if arrow else None})
  if dash:e['strokeStyle']='dashed'
 def label(self,x,y,s,color=None):
  width=ImageFont.truetype(FONT,15).getlength(s)
  self.rect(x-width/2-7,y-17,width+14,24,'#FFFFFF','transparent',5)
  self.text(x,y,s,15,color or C['muted'],False,'middle')
 def note(self,x,y,s,size=17):self.text(x,y,s,size,C['muted'])
 def boundary(self,x,y,w,h,s):
  self.rect(x,y,w,h,'#FBFCFE',C['border'],18,1.5,True);self.text(x+20,y+29,s,14,C['muted'],True)
 def legend(self,y):
  self.line([(60,y),(103,y)],C['line']);self.text(116,y+6,'Application / data flow',15,C['muted'])
  self.line([(410,y),(453,y)],C['purple'],dash=True);self.text(466,y+6,'AI / advisory exchange',15,C['muted'])
  self.rect(790,y-9,20,20,C['orangefill'],C['orange'],5);self.text(822,y+6,'Human decision',15,C['muted'])
  self.rect(1090,y-9,20,20,C['grayfill'],C['border'],5);self.text(1122,y+6,'External system / local mode',15,C['muted'])
 def save(self,mermaid):
  defs='<defs>'+''.join(f'<marker id="{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 1 L 9 5 L 0 9" fill="none" stroke="{c}" stroke-width="1.5"/></marker>' for c in set(C.values()))+'</defs>'
  (OUT/(self.slug+'.svg')).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="{self.h}" viewBox="0 0 1600 {self.h}" role="img"><title>CaféMesh AI — {escape(self.slug)}</title>{defs}'+''.join(self.svg)+'</svg>')
  (OUT/(self.slug+'.excalidraw')).write_text(json.dumps({'type':'excalidraw','version':2,'source':'cafemesh-architecture','elements':self.elements,'appState':{'viewBackgroundColor':'#FFFFFF','gridSize':None},'files':{}},ensure_ascii=False,indent=2))
  (OUT/(self.slug+'.mmd')).write_text(mermaid.strip()+'\n')

d=Diagram('01-c4-system-context',1,'C4 · System context','People and managed-service dependencies, including the hosted Cloud Firestore state.',1280)
d.box(60,240,310,155,'Customer',['Discover and plan a café visit.','Confirm demo orders; give feedback.'],tag='Person')
d.box(60,480,310,180,'Café manager',['Review queue and service signals.','Transition simulated orders.','Record accept / reject decisions.'],tag='Person')
d.box(60,745,310,155,'Café owner',['Inspect windowed demo metrics.','Read a grounded owner brief.'],tag='Person')
d.box(565,400,420,330,'CaféMesh AI',['Discovery and menu guidance.','Synthetic orders and operations.','Shared owner insight and learning.','Hosted state in Cloud Firestore.','Four browser workspaces;','one backend application.'],tag='Software system',size=32)
d.box(1220,190,320,155,'Google Identity',['Sign-in and reviewer ID tokens.','No staff / tenant RBAC yet.'],kind='gray',tag='External identity service')
d.box(1220,410,320,155,'Google Maps',['Places directory search.','Walking Routes to first result.'],kind='gray',tag='External data service')
d.box(1220,630,320,155,'Vertex AI / Gemini',['Optional advisory inference.','ADK runs inside the application.'],kind='purple',tag='External model service')
d.box(1220,850,320,155,'Cloud Firestore',['Read / persist synthetic records.','One bounded snapshot document.'],tag='Managed persistence service')
for y,port,label in [(318,455,'Customer actions'),(570,555,'Review / transition'),(823,665,'Metrics / brief')]:
 d.line([(370,y),(465,y),(465,port),(565,port)]);d.label(465,y-13,label)
for y,port,bend,label,ai in [(268,440,1105,'Verify ID tokens',False),(488,515,1140,'Search / route',False),(708,610,1120,'Bounded inference',True),(928,700,1050,'Read / persist state',False)]:
 d.line([(985,port),(bend,port),(bend,y),(1220,y)],C['purple'] if ai else C['line'],dash=ai)
 d.label(1105,y-13,label,C['purple'] if ai else None)
d.note(60,1075,'Cloud Firestore is an explicit managed dependency here; L2 and view 06 explain the internal snapshot adapter and record model.')
d.note(60,1105,'Cloud Run, Cloudflare and Secret Manager: view 02. Build-time Google TTS, media and release tooling: view 08.')
d.note(60,1135,'Maps listings are live directory data. Menu, allergen, inventory, occupancy, orders and manager decisions remain synthetic.')
d.legend(1165)
d.save("""flowchart LR
  Customer["Customer"] -->|"Discover, preview, confirm, feedback"| App["CaféMesh AI"]
  Manager["Café manager"] -->|"Review operations, transition orders, record decisions"| App
  Owner["Café owner"] -->|"Windowed metrics and owner brief"| App
  App -->|"Verify ID tokens"| Identity["Google Identity"]
  App -->|"Search and walking route"| Maps["Google Maps: Places and Routes"]
  App -.->|"Optional advisory inference via in-process ADK"| Vertex["Vertex AI / Gemini"]
  App -->|"Read and persist synthetic state"| Firestore[("Cloud Firestore: bounded single snapshot")]
""")

d=Diagram('02-c4-containers-deployment',2,'C4 · Containers & deployment','Packaged application plus the documented hosted deployment; live infrastructure was not queried.',1370,badge='CODE + DEPLOY DOCS')
d.boundary(510,385,510,605,'DOCUMENTED HOSTING  /  asia-south1')
d.box(60,210,330,150,'Browser application',['React · Vite · TypeScript','Customer / reviewer experience'],tag='Browser container')
d.box(560,210,410,130,'Cloudflare Worker',['Custom hostname → origin proxy'],kind='gray',tag='Edge routing')
d.box(560,455,410,210,'FastAPI on Cloud Run',['Serves built SPA + JSON API.','Contracts, policy and coordination.','Verifies reviewer ID tokens.','ADK executes in this process.'],tag='Single application container')
d.box(560,805,410,155,'Firestore snapshot',['One serialized SQLite snapshot.','Compare-and-set · 700 KB ceiling.'],tag='Hosted synthetic state')
d.box(1180,210,360,155,'Google Identity',['Browser sign-in → ID token.','OAuth Testing: documented setting.'],kind='gray',tag='Identity provider')
d.box(1180,455,360,155,'Places + Routes',['Server-side API-key requests.','Directory data + walking routes.'],kind='gray',tag='Google Maps Platform')
d.box(1180,700,360,155,'Vertex AI / Gemini',['Optional bounded inference.','Runtime identity / ADC.'],kind='purple',tag='Managed model provider')
d.box(60,805,330,155,'SQLite file',['Local development mode only.','Alternative to hosted snapshot.'],kind='gray',tag='Local data container')
d.line([(390,285),(560,285)]);d.label(475,272,'HTTPS')
d.line([(225,210),(225,176),(1360,176),(1360,210)]);d.label(790,178,'Google Identity Services sign-in')
d.line([(765,340),(765,455)]);d.label(765,369,'HTTPS · app + API')
d.line([(970,475),(1080,475),(1080,287),(1180,287)]);d.label(1070,275,'Token verification')
d.line([(970,555),(1180,555)]);d.label(1075,542,'HTTPS / JSON')
d.line([(970,635),(1080,635),(1080,777),(1180,777)],C['purple'],dash=True);d.label(1080,757,'Optional',C['purple'])
d.line([(765,665),(765,805)]);d.label(765,742,'Snapshot read / commit')
d.line([(560,625),(450,625),(450,882),(390,882)]);d.label(450,767,'Local mode')
d.box(60,445,330,155,'Secret Manager',['Supplies the server-side Maps key.','Access per deployment documentation.'],kind='gray',tag='Deployment config (docs)')
d.line([(390,520),(560,520)]);d.label(475,507,'Inject Maps key')
d.note(60,670,'Public customer endpoints.',17)
d.note(60,700,'Cloud Run origin is also public.',17)
d.note(60,730,'Reviewer token checks are in-app.',17)
d.note(1180,916,'Model access: ADC / runtime identity.',16)
d.note(1180,945,'API-key mode is also supported.',16)
d.note(60,1050,'Documented settings: max instances = 1; concurrency = 1; runtime identity with Firestore / Vertex / secret access. Not re-queried here.')
d.note(60,1080,'The SPA, saved MP3s, MP4s and poster assets are bundled in the image. Playback makes no runtime TTS request (see view 08).')
d.note(60,1110,'Local development uses Vite :5173 → FastAPI :8000; the packaged app serves both UI and API from one origin.')
d.note(60,1140,'No tenant isolation or café staff roles. Provider status combines configuration and last observations; it is not a fresh health probe.')
d.note(60,1170,'Code confirms provider adapters and env-based configuration. Region, deployed settings, OAuth audience and IAM grants are documentary evidence.')
d.legend(1240)
d.save('''flowchart TB
  Browser["React SPA · browser"] -->|"HTTPS"| Edge["Cloudflare Worker · custom-domain proxy"]
  Browser -->|"Sign-in / ID token"| Identity["Google Identity · OAuth Testing"]
  subgraph Hosted["Hosted service and state · asia-south1"]
    API["FastAPI on Cloud Run · serves SPA and JSON API · in-process ADK"]
    Snapshot[("Firestore · single SQLite snapshot · synthetic state")]
    API -->|"Read / commit with compare-and-set"| Snapshot
  end
  Secrets["Secret Manager: Maps key"] -->|"Runtime injection"| API
  Edge -->|"Forward requests"| API
  API -->|"Verify reviewer ID tokens"| Identity
  API -->|"Server-side requests"| Maps["Places + Routes"]
  API -.->|"Optional inference"| Vertex["Vertex AI / Gemini"]
  API -->|"Local mode instead of Firestore"| Local[("SQLite file")]
''')

d=Diagram('03-c4-runtime-components',3,'C4 · Runtime components','Logical code boundaries inside the current application; these boxes are not separate services.',1320)
d.box(60,190,1480,110,'React experiences',['Customer / Ops / Owner / Vision · regex constraint extraction · opt-in geolocation · saved walkthrough playback'],tag=None)
d.boundary(60,350,1480,800,'FASTAPI APPLICATION  /  backend/cafemesh')
d.box(100,405,900,180,'HTTP routes, contracts & coordination',['main.py · schemas + handler checks · Google reviewer ID tokens','Maps · feedback · transitions · manager decision · reset · provider status','Optional ADK execution · narrative guards · static UI / media delivery'],tag='Application boundary')
d.box(100,690,620,160,'Deterministic domain policy',['service.py · recommendations, preview, confirmation, owner metrics','Request constraints, lexical matching, ranking and time estimates'],tag='Authoritative')
d.box(820,690,280,145,'Ops metrics',['observability.py','Shared event derivation'],tag='Read model',size=22)
d.box(1150,665,350,290,'ADK agents',['ConciergeAgent','TasteSafetyAgent','VisitOrderAgent · OpsOwnerAgent','agents.py · optional Gemini','Read-only fact / metrics tools.','No order-write tool.'],kind='purple',tag='Advisory',size=26)
d.box(100,950,310,120,'Structured facts',['data.py · menu, café, queue, zones'],size=22)
d.box(480,950,620,135,'Shared records & persistence',['orders · proposals · preferences · feedback · prep_observations','events · decisions · activity · db.py selects SQLite / Firestore'],size=23)
d.line([(550,300),(550,405)]);d.label(550,328,'HTTPS / JSON')
d.line([(410,585),(410,690)]);d.label(410,625,'Domain calls')
d.line([(960,585),(960,690)]);d.label(960,625,'Read metrics')
d.line([(1000,480),(1325,480),(1325,665)],C['purple'],dash=True);d.label(1180,467,'Optional model path',C['purple'])
d.line([(240,850),(240,950)]);d.label(240,913,'Read facts')
d.line([(600,850),(600,950)]);d.label(600,913,'Read / write')
d.line([(960,835),(960,950)]);d.label(960,913,'Read records')
d.line([(1150,890),(760,890),(760,825),(720,825)],C['purple'],dash=True);d.label(957,877,'owner_facts → metrics()',C['purple'])
d.line([(1325,955),(1325,1110),(255,1110),(255,1070)],C['purple'],dash=True);d.label(800,1110,'menu_facts / visit_facts → structured data (read only)',C['purple'])
d.note(60,1190,'Scope: main.py also writes events and activity directly. See views 06–07 for record and agent detail; these are logical modules.')
d.legend(1211)
d.save('''flowchart TB
  UI["React experiences · Customer / Operations / Owner / Vision"] -->|"HTTPS / JSON"| API
  subgraph Application["FastAPI application · backend/cafemesh"]
    API["main.py · routes, schemas and handler checks, reviewer auth, Maps, feedback, transitions, decisions, reset, provider status, ADK and guards"]
    Domain["service.py · deterministic recommendation, preview, confirmation and metrics"]
    Ops["observability.py · operational metrics"]
    Agents["agents.py · Concierge, TasteSafety, VisitOrder, OpsOwner · read-only tools"]
    Facts["data.py · structured synthetic menu, café, queue, zones"]
    Store["db.py · SQLite / Firestore snapshot · events, activity, proposals and orders"]
    API -->|"Direct feedback, transition, decision and activity writes"| Store
    API --> Domain
    API --> Ops
    API -.->|"Optional execution"| Agents
    Domain --> Facts
    Domain --> Store
    Ops --> Store
    Agents -.->|"owner_facts calls metrics"| Domain
    Agents -.->|"menu_facts / visit_facts"| Facts
  end
''')

d=Diagram('04-trusted-ai-request-flow',4,'Trusted AI · From request to simulated order','Implemented request controls and explicit limits, checked against main.py and service.py.',1530)
d.box(80,195,740,110,'1   Validate customer input',['POST /api/recommend · structured schema and explicit constraints'])
d.box(80,385,740,155,'2   Retrieve facts & apply deterministic policy',['Lexical menu matching · budget / diet / allergy / time constraints','Evidence IDs + eligibility + staff-review status','Record recommendation and safety events.'])
d.box(1000,385,500,195,'Optional ADK + Gemini',['Only when configured and candidates exist.','Read-only menu, visit and owner fact tools.','Interprets and explains supplied facts.','No order-write authority.'],kind='purple',tag='Advisory branch',size=24)
d.box(80,685,740,130,'3   Return structured result',['Candidates · evidence · eligibility · provider status','Unknown / stale allergy evidence requires staff review.'])
d.box(1000,685,500,155,'Model summary guard',['Withhold narrative for declared allergies OR','matched allergy-safety wording.','Keep structured candidates authoritative.'],kind='purple',size=24)
d.box(80,900,740,110,'4   Validate and persist exact preview',['POST /api/preview · bound item, quantity, price and constraints'])
d.box(1000,900,500,110,'5   Customer explicitly confirms',['The displayed proposal + an idempotency key.'],kind='orange',size=24)
d.box(1000,1110,500,135,'6   Backend action gate',['Unused, unchanged snapshot + current constraints.','Prior key returns prior order before payload checks.','No safety-age recheck or proposal TTL.'],size=24)
d.box(80,1110,740,135,'7   Commit simulated order & event',['Mark proposal confirmed and return the synthetic order ID.','No payment, POS or fulfillment integration.'])
d.line([(450,305),(450,385)]);d.label(450,350,'Validated constraints')
d.line([(450,540),(450,685)]);d.label(450,596,'No candidates → no generation');d.label(450,630,'AI unconfigured → deterministic response')
d.line([(820,460),(1000,460)],C['purple'],dash=True);d.label(910,445,'Facts + request',C['purple'])
d.line([(1250,580),(1250,685)],C['purple'],dash=True);d.label(1250,637,'Untrusted model text',C['purple'])
d.line([(1000,750),(820,750)],C['purple'],dash=True);d.label(910,735,'Guarded text',C['purple'])
d.line([(450,815),(450,900)]);d.label(450,858,'Select eligible candidate')
d.line([(820,955),(1000,955)],C['orange']);d.label(910,939,'Show proposal',C['orange'])
d.line([(1250,1010),(1250,1110)],C['orange']);d.label(1250,1060,'Explicit confirm',C['orange'])
d.line([(1000,1175),(820,1175)]);d.label(910,1160,'Checks pass')
d.note(80,1290,'Configured provider failures return explicit errors (502 / 503 / 504); they are not silently reported as successful demo responses.',17)
d.note(80,1330,'Review gap: recommendation checks safety-record age, but preview / confirm do not repeat that check. Staff review is a status, not a resolver.')
d.note(80,1360,'Availability is checked, but inventory units are not reserved or decremented. Confirmation remains a synthetic write only.')
d.legend(1411)
d.save('''flowchart TB
  Input["Validate POST /api/recommend and explicit constraints"] --> Policy["Structured lexical retrieval and deterministic policy · record evidence/events"]
  Policy -->|"Deterministic result; skip generation if no candidates"| Response["Candidates, evidence, eligibility, staff-review and provider status"]
  Policy -.->|"Configured and candidates exist"| AI["Optional ADK / Gemini · read-only tools"]
  AI -.-> Guard["Model summary guard · withhold declared allergy context or matched safety wording"]
  Guard -.-> Response
  AI -->|"Configured failure"| Error["Explicit 502 / 503 / 504 · no silent demo fallback"]
  Response -->|"Select eligible candidate"| Preview["Validate and persist exact preview"]
  Preview --> Human["Customer explicitly confirms proposal"]
  Human --> Gate["Backend action gate · prior idempotency key replays first · unchanged unused proposal · implemented checks only; no age/TTL recheck"]
  Gate -->|"Checks pass"| Commit["Commit synthetic order and event"]
  Gate -->|"Rejected"| Reject["No new order · return error"]
''')

d=Diagram('05-target-production-architecture',5,'Target · Production reference architecture','Proposed evolution only. Logical capability boundaries do not require a microservice per box.',1730,True)
d.box(80,180,1440,85,'Companion     •     Connect     •     Operations     •     Owner     •     Administration',[],size=25)
d.box(400,330,800,115,'Edge, identity & tenant authorization',['Load balancing / WAF / rate limits · identity · tenant isolation · RBAC'],tag='Proposed perimeter')
d.box(400,505,800,110,'Versioned API & workflow coordination',['Cloud Run · controlled tools · request identity and audit context'])
d.box(80,700,420,195,'Agent / AI plane',['ADK + Gemini · bounded tools','Model Armor + input / output controls','Versioned harness, budgets and replay','Advisory output only'],kind='purple',tag='Planned',size=25)
d.box(590,700,420,195,'Policy / action plane',['Deterministic authorization','Human approval where required','Idempotency and state transitions','Separate approval / action / outcome'],tag='Planned',size=25)
d.box(1100,700,420,195,'Governed retrieval',['Versioned café documents','Citation and access controls','Maps provider adapters'],kind='purple',tag='Planned',size=25)
d.box(590,950,420,115,'Domain capabilities',['Catalog · inventory reservation','Order lifecycle + transactional outbox'],size=24)
d.box(590,1155,420,120,'Tenant-scoped data',['Firestore or fit-for-purpose SQL','Transactional records; replace snapshot'],size=25)
d.box(1100,1125,420,150,'Events & analytics',['Reliable event delivery / export','BigQuery · governed analytics'],tag='Planned',size=25)
d.box(1100,1350,420,140,'Quality evaluation',['Goldens · adversarial tests · replay','Optional calibrated judge; human labels','Hard policy gates remain absolute.'],size=24)
d.box(80,1350,420,140,'Human release gate',['Review results; approve agent changes.','Shadow / canary / monitored rollout','Tested rollback and bounded recovery.'],kind='orange',size=24)
d.box(80,1010,420,205,'Operational telemetry',['Cloud Logging / Monitoring / traces','Latency, errors, quality and cost','SLOs · alerting · incident response','API, tool and domain instrumentation'],kind='gray',tag='Planned',size=23)
d.line([(800,265),(800,330)])
d.line([(800,445),(800,505)])
d.line([(600,615),(600,655),(290,655),(290,700)],C['purple'],dash=True)
d.line([(800,615),(800,700)]);d.label(800,664,'Authorize requests')
d.line([(1000,615),(1000,655),(1310,655),(1310,700)],C['purple'],dash=True)
d.line([(500,791),(590,791)],C['purple'],dash=True)
d.line([(1100,791),(1010,791)],C['purple'],dash=True)
d.line([(800,895),(800,950)]);d.label(800,915,'Authorized operations')
d.line([(800,1065),(800,1155)]);d.label(800,1114,'Transactional writes')
d.line([(1010,1220),(1100,1220)]);d.label(1055,1198,'Outbox')
d.line([(1310,1275),(1310,1350)])
d.line([(1100,1405),(500,1405)],C['orange']);d.label(800,1387,'Reviewed evidence and quality gates',C['orange'])
d.line([(80,1405),(40,1405),(40,785),(80,785)],C['orange']);
d.line([(400,560),(20,560),(20,1108),(80,1108)],C['gray']);d.label(210,543,'Instrumentation')
d.box(1100,945,420,135,'Integration adapters',['POS / payments / loyalty / notifications','Voice and consented arrival workflows','Only after pilot and partner gates.'],kind='gray',size=24)
d.line([(1010,1008),(1100,1008)])
d.note(60,1540,'Cross-cutting: onboarding and trusted data ownership · consent / export / deletion · security / privacy · backups / restore · SLOs.')
d.note(60,1570,'Detailed reservations, community, service recovery, forecasts and administration scope is mapped in ARCHITECTURE-AUDIT.md.')
d.legend(1610)
d.save('''flowchart TB
  Clients["Companion · Connect · Operations · Owner · Administration"] --> Edge["Edge + WAF + rate limits + identity + tenant RBAC"]
  Edge --> API["Versioned API on Cloud Run · workflow coordination"]
  API -.-> AI["ADK / Gemini · bounded tools · Model Armor and input/output controls"]
  API --> Policy["Deterministic authorization · human approval · idempotency"]
  API -.-> Retrieval["Governed document retrieval / citations · Maps adapters"]
  AI -.->|"Proposals only"| Policy
  Retrieval -.->|"Access-controlled evidence"| Policy
  Policy --> Domain["Catalog · inventory reservation · orders / transactional outbox"]
  Domain --> Integrations["Planned POS, payments, loyalty, notifications, voice and arrival adapters"]
  Domain --> Data[("Tenant-scoped Firestore or suitable SQL")]
  Data -->|"Reliable outbox / export"| Events["Event pipeline · BigQuery analytics"]
  Events --> Evals["Versioned evaluations · replay · experiments"]
  Evals --> Human["Human review / release gate"]
  Human -->|"Approved changes"| AI
  API --> Telemetry["Cloud Logging / Monitoring / traces · SLOs · cost and quality alerts"]
''')


d=Diagram('06-state-and-learning',6,'State · Persistence & controlled learning','All eight stored record types, their persistence boundary, and the implemented learning loops.',1620)
d.box(60,185,460,180,'Synthetic business fixtures',['data.py · CAFE / MENU / QUEUE / ZONES','Prices, allergens, stock and occupancy','These are code fixtures, not Firestore tables.'],kind='gray',tag='Reference facts',size=25)
d.box(650,185,890,180,'Application commands & read models',['main.py + service.py + observability.py','Recommendation / preview / confirm / transition / feedback / decision / reset','Ops and Owner read the same records; recommendations are events.'],tag='Shared synthetic workflow',size=26)
d.line([(520,270),(650,270)]);d.label(585,256,'Read fixtures')
d.boundary(60,455,1480,365,'LOGICAL TABLES  /  IDs AND JSON PAYLOAD LINKS; NO DECLARED FOREIGN-KEY RELATIONSHIPS')
records=[('orders',['Order ID · unique idempotency key']),('proposals',['Proposal ID · snapshot · confirmed']),('preferences',['Customer ID · bounded profile']),('feedback',['Customer ID · feedback payload']),('prep_observations',['Predicted / actual · source tag']),('events',['Kind · JSON data · created_at']),('decisions',['Recommendation · accept / reject']),('activity',['Agent / tool · evidence · latency'])]
for i,(title,body) in enumerate(records):
 d.box(90+(i%4)*360,520+(i//4)*160,330,110,title,body,size=23)
d.line([(1095,365),(1095,455)]);d.label(1095,414,'Read / write / audit')
d.box(590,900,420,110,'db.py · backend selector',['CAFEMESH_STORAGE_BACKEND'],size=26)
d.line([(800,820),(800,900)])
d.box(60,1090,590,170,'Hosted: Cloud Firestore',['cafemesh_state/demo · sqlite_snapshot payload','Deserialize into in-memory SQLite; serialize on commit.','Compare-and-set; 700,000-byte decoded payload cap.','One instance / concurrency one remains a demo constraint.'],size=25)
d.box(950,1090,590,170,'Local: SQLite file',['Default: data/cafemesh.db','Same logical schema and SQL service boundary.','Local development alternative, not a second hosted store.'],kind='gray',size=25)
d.line([(700,1010),(700,1050),(355,1050),(355,1090)]);d.label(510,1040,'firestore')
d.line([(900,1010),(900,1050),(1245,1050),(1245,1090)]);d.label(1100,1040,'sqlite')
d.text(60,1320,'LEARNING AND REVIEW OVER THE SAME SHARED RECORDS',16,C['muted'],True)
d.box(60,1360,460,140,'Taste preferences',['Feedback adjusts four bounded taste weights.','Ranking uses these weights; safety is excluded.','No separate customer profiles or consent API.'],size=23)
d.box(560,1360,460,140,'Measured timing',['Latest 20 measured samples; default minimum 3.','Seeded samples never calibrate estimates.','Total-time / prep-time mismatch: see audit.'],size=23)
d.box(1060,1360,480,140,'AI review signals',['Error / review activity becomes a visible signal.','No automatic golden-case or prompt promotion.','Human review workflow remains planned.'],kind='purple',size=23)
d.note(60,1530,'Orders, profiles and decisions are synthetic. Reset clears all eight tables and rebuilds the seeded demo baseline.')
d.save('''flowchart TB
  Fixtures["data.py: CAFE, MENU, QUEUE, ZONES · code fixtures"] --> App["main.py / service.py / observability.py"]
  App --> Records["Eight tables: orders, proposals, preferences, feedback, prep_observations, events, decisions, activity"]
  Records --> Selector["db.py selects storage backend"]
  Selector -->|"Hosted"| Firestore[("Cloud Firestore: single serialized SQLite snapshot; CAS; 700000-byte decoded limit")]
  Selector -->|"Local"| SQLite[("SQLite file")]
  Records --> Taste["Bounded preference weights; safety excluded"]
  Records --> Timing["Measured-only timing calibration; latest 20; default minimum 3"]
  Records --> Review["Error/review activity signals; no automatic promotion"]
''')

d=Diagram('07-agent-execution',7,'Agents · Actual execution paths','Four ADK definitions, parallel recommendation helpers, and the separate owner-brief path.',1530)
d.box(60,185,940,120,'POST /api/recommend',['Run deterministic recommendation first. Skip generation when no candidates exist.','Use live ADK only when an API key or Vertex AI mode is configured.'],size=26)
d.box(1080,185,460,120,'GET /api/owner',['Reviewer auth · window 1–365 days','Compute shared-record metrics first.'],size=25)
d.box(60,420,430,160,'TasteSafetyAgent',['Fixed menu/safety helper prompt.','Instructed to call menu_facts().','No eligibility or order-write authority.'],kind='purple',size=25)
d.box(570,420,430,160,'VisitOrderAgent',['Fixed queue/seating helper prompt.','Instructed to call visit_facts().','No preview or confirmation tool.'],kind='purple',size=25)
d.line([(330,305),(330,365),(275,365),(275,420)],C['purple'],dash=True)
d.line([(730,305),(730,365),(785,365),(785,420)],C['purple'],dash=True)
d.label(530,365,'Parallel invocation: asyncio.gather',C['purple'])
d.box(60,660,430,105,'menu_facts()',['Reads fields from data.MENU.'],kind='gray',size=25)
d.box(570,660,430,105,'visit_facts()',['Reads data.QUEUE and data.ZONES.'],kind='gray',size=25)
d.line([(275,580),(275,660)],C['purple'],dash=True);d.line([(785,580),(785,660)],C['purple'],dash=True)
d.box(260,910,540,190,'ConciergeAgent',['Receives user text, authoritative candidates,','queue facts and both helper outputs.','Root definition registers all three sub-agents.','Runs through a fresh InMemoryRunner session.'],kind='purple',tag='Fourth ADK definition',size=26)
d.line([(275,765),(275,835),(385,835),(385,910)],C['purple'],dash=True)
d.line([(785,765),(785,835),(675,835),(675,910)],C['purple'],dash=True)
d.label(530,838,'Helper text + authoritative request context',C['purple'])
d.box(1080,420,460,160,'OpsOwnerAgent',['Invoked directly for the owner brief.','Must call owner_facts(days).','Read-only; no operational write tools.'],kind='purple',size=25)
d.line([(1310,305),(1310,420)],C['purple'],dash=True)
d.box(1080,660,460,125,'owner_facts(days)',['Validates 1–365 day window.','Calls service.metrics(days) over shared state.'],kind='gray',size=24)
d.line([(1310,580),(1310,660)],C['purple'],dash=True)
d.box(1080,910,460,190,'Owner completion gate',['main.py requires completed owner_facts','and non-empty generated text.','Failure returns an explicit error.','This is not numeric fact-checking of prose.'],size=25)
d.line([(1310,785),(1310,910)],C['purple'],dash=True)
d.box(260,1200,540,130,'Recommendation response guard',['Withhold declared allergy / safety-language prose.','Structured candidates remain authoritative.','Record outcomes, latency, evidence and guard activity.'],size=24)
d.box(1080,1200,460,130,'Owner response',['Computed metrics + optional generated brief.','No credentials: deterministic demo brief.','Recorded owner tool outcome is separate.'],size=24)
d.line([(530,1100),(530,1200)],C['purple'],dash=True)
d.line([(1310,1100),(1310,1200)])
d.note(60,1400,'ADK session state is in memory; selected activity is persisted separately. No durable workflow engine or generalized agent harness exists.')
d.note(60,1430,'Recommendation helpers are prompted to use tools, but tool completion is not enforced there; the owner path enforces it. See audit.')
d.save('''flowchart TB
  Recommend["POST /api/recommend: deterministic facts first"] -.-> Taste["TasteSafetyAgent · fixed helper prompt"]
  Recommend -.-> Visit["VisitOrderAgent · fixed helper prompt"]
  Taste -.-> Menu["menu_facts: data.MENU"]
  Visit -.-> Facts["visit_facts: QUEUE / ZONES"]
  Menu -.-> Concierge["Concierge: helper outputs + request + authoritative candidates; root registers three sub-agents"]
  Facts -.-> Concierge
  Concierge -.-> Guard["Summary guard; record activity; return structured result"]
  Owner["GET /api/owner: auth and deterministic metrics"] -.-> Ops["OpsOwnerAgent"]
  Ops -.-> Tool["owner_facts(days): service.metrics"]
  Tool --> Check["Require completed tool and nonempty text"]
  Check --> Brief["Computed metrics + brief or explicit error"]
''')

d=Diagram('08-delivery-and-media',8,'Delivery · CI, deployment & saved media','Build-time service use is separated from customer-request runtime behavior.',1560,badge='CODE + DEPLOY DOCS')
d.box(60,185,700,115,'GitHub source + locked dependencies',['quality.yml · push / PR / manual / weekly triggers','uv.lock + package-lock.json · Dockerfile'],size=26)
d.box(60,410,700,215,'CI verification and supply-chain checks',['make verify: pytest + TypeScript + Vite build','make demo-smoke: two synthetic connected journeys','npm audit + pip-audit · deployment-container build','Parallel job: Gitleaks over repository and history','These checks do not deploy to Cloud Run.'],tag='GitHub Actions',size=26)
d.line([(410,300),(410,410)])
d.box(60,775,700,150,'Manual release / source deployment',['Documented gcloud run deploy --source . command','Cloud Build builds the source-deploy image.','Post-deploy health, auth and media checks are documented.'],kind='orange',size=26)
d.line([(410,625),(410,775)],C['orange']);d.label(410,705,'Operator initiates deployment',C['orange'])
d.box(60,1080,700,180,'Cloud Run runtime',['FastAPI + SPA + saved audio / video / poster assets','Deployment docs specify ADC and scoped runtime roles.','Firestore and Vertex access; Maps key via Secret Manager.','Cloudflare Worker routes the public custom hostname.'],size=26)
d.line([(410,925),(410,1080)]);d.label(410,1005,'Built image + runtime configuration')
d.box(900,185,640,115,'Narration source + media scripts',['Product / engineering narration and sanitized screenshot scenes','Prepared outside the customer request path.'],kind='gray',size=25)
d.box(900,410,640,160,'Google Cloud Text-to-Speech',['generate_voiceover.py · Gemini-TTS · en-IN / Despina','ADC-authenticated build-time synthesis','Paragraph segments + timing manifest; no runtime voice chat.'],kind='purple',tag='Build-time provider',size=25)
d.line([(1220,300),(1220,410)],C['purple'],dash=True)
d.box(900,675,640,110,'Saved narration assets',['MP3 audio + scene timing JSON'],kind='gray',size=25)
d.line([(1220,570),(1220,675)],C['purple'],dash=True)
d.box(900,885,640,150,'Screenshot + narration rendering',['Sanitized captures; Chromium for engineering slide renders.','FFmpeg / ffprobe compose and check H.264 + AAC MP4s.','Paragraph-synchronized stills, not continuous recordings.'],kind='gray',size=25)
d.line([(1220,785),(1220,885)])
d.box(900,1130,640,110,'Bundled static media',['frontend/public/audio, videos and images → Vite build'],kind='gray',size=25)
d.line([(1220,1035),(1220,1130)])
d.line([(900,1185),(760,1185)]);d.label(829,1169,'Bundle')
d.line([(1540,730),(1570,730),(1570,1185),(1540,1185)],C['gray'])
d.note(60,1370,'Google TTS is used to create assets. Browser playback reads bundled MP3 / MP4 files and makes no synthesis call.')
d.note(60,1400,'Existing CI is verification-only. Protected deployment promotion, image attestations, canary gates and rollback drills are target work.')
d.note(60,1430,'Recorded release evidence is historical; this architecture audit did not rerun live provider, deployment or browser-permission tests.')
d.legend(1450)
d.save('''flowchart TB
  Source["GitHub source and locked dependencies"] --> CI["Actions: verify, smoke, npm/pip audits, Docker build, parallel history secret scan"]
  CI -->|"Operator-controlled; no CI deployment step"| Deploy["Manual gcloud source deployment · Cloud Build"]
  Deploy --> Run["Cloud Run: FastAPI + SPA + saved assets"]
  Narration["Narration scripts and sanitized scenes"] -.-> TTS["Google Cloud TTS · build time only"]
  TTS --> Audio["MP3 + paragraph timing JSON"]
  Audio --> Render["Screenshot/slide composition · Chromium + FFmpeg/ffprobe"]
  Render --> Bundle["frontend/public media bundled by Vite"]
  Audio --> Bundle
  Bundle --> Run
''')


# Product capability map complements the technical production reference.
d=Diagram('09-end-to-end-capabilities',9,'End-to-end product capabilities','The complete visit, café operation and improvement loop; current coverage is explicitly limited.',1800,planned=True,badge='TARGET + COVERAGE')
d.note(60,185,'MIXED = demo path plus substantial missing work. PLANNED = no complete implemented workflow. Full criteria: docs/14-END-TO-END-CAPABILITIES.md',15)
d.box(60,235,460,210,'1  Onboard & govern',['Administrator: locations, staff and integrations.','Reviewed menu / safety / price / hours / spaces.','Today: code fixtures; no administration workflow.'],kind='gray',tag='Planned',size=27)
d.box(570,235,460,210,'2  Discover & plan',['Customer: participating café, intent and route.','Amenities, demand, halfway and group planning.','Today: Places / Routes; synthetic café context.'],tag='Mixed',size=27)
d.box(1080,235,460,210,'3  Personalize & choose',['Customer: explicit constraints and preferences.','Evidence-backed choice; optional explanation.','Today: lexical rules / feedback; safety gaps.'],tag='Mixed · F01 / F02 / F15',size=27)
d.line([(520,335),(570,335)]);d.line([(1030,335),(1080,335)])
d.box(1080,525,460,235,'4  Preview & commit',['Customer: current quote and explicit consent.','Reserve stock / capacity; payment when enabled.','Today: synthetic preview and order only.','Missing TTL, transactions and retry binding.'],tag='Mixed · F01–F05',size=27)
d.line([(1310,445),(1310,525)])
d.box(570,525,460,235,'5  Prepare & arrive',['Team: station, queue, inventory and arrival.','Customer: tracking, collection and seating.','Today: synthetic lifecycle and timing samples.','Reservations / arrival / stations remain planned.'],tag='Mixed · F06',size=27)
d.box(60,525,460,235,'6  Serve & recover',['Customer: assistance, cancellation and refund.','Team: owned recovery and shift handover.','Today: limited simulated cancellation.','Help / payments / recovery workflows planned.'],tag='Mixed',size=27)
d.line([(1080,640),(1030,640)]);d.line([(570,640),(520,640)])
d.box(60,850,460,210,'7  Feedback & return',['Customer: correct preferences and control data.','Opt-in loyalty; inspect / export / delete profile.','Today: four bounded weights; shared demo user.'],tag='Mixed · F02 / F13',size=27)
d.box(570,850,460,210,'8  Operate & analyze',['Manager: decision, execution and outcome.','Owner: service / business / multi-location KPIs.','Today: decision audit and limited demo metrics.'],tag='Mixed · F09 / F13',size=27)
d.box(1080,850,460,210,'9  Review & improve',['Human review of facts, cases and interventions.','Versioned experiments; controlled rollout.','Today: review signals; no automatic promotion.'],tag='Mixed',size=27)
d.line([(290,760),(290,850)]);d.line([(520,955),(570,955)]);d.line([(1030,955),(1080,955)])
d.line([(1540,955),(1570,955),(1570,210),(290,210),(290,235)],C['sage'],dash=True)
d.label(825,213,'Approved improvements return to governed facts',C['sage'])
d.box(60,1140,710,190,'Optional CaféMesh Connect',['Events / moderated interest tables → consented joins → group visits.','Meet-halfway planning; leave / hide / block / report controls.','Direct person matching only after identity, consent and moderation.'],kind='purple',tag='Planned · connects to planning and experience',size=28)
d.box(830,1140,710,190,'Pilot prerequisites across the journey',['Tenant roles · governed records · transactional stock / orders.','Privacy lifecycle · approved adapters · accessibility / localization.','Backups / recovery · support ownership · monitoring and budgets.'],kind='orange',tag='Release gate · not implemented as a complete platform',size=28)
d.box(60,1410,1480,205,'Shared trust, intelligence and delivery',['Structured facts remain authoritative; model output cannot authorize safety or a real-world action.','Versioned agent tools, prompts and evaluations; governed RAG / voice only after specific acceptance gates.','Reliable events and metric definitions; SLOs, privacy, cost limits, human releases, canary and rollback.','Maps listing ≠ participating café. Demo confirmation ≠ fulfillment. Manager acceptance ≠ execution.'],kind='gray',size=29)
d.note(60,1662,'Delivery slices: close demo gaps → controlled café pilot → complete visit / recovery → community & multi-location → evaluated optimization.',16)
d.save('''flowchart TB
  Govern["Admin: onboard and govern facts · planned"] --> Plan["Customer: discover and plan · mixed"]
  Plan --> Choose["Constrain, choose, preview and confirm · mixed"]
  Choose --> Fulfill["Team: transact stock, prepare, arrive and serve · mixed"]
  Fulfill --> Recover["Help, cancellation, refund and recovery · mostly planned"]
  Recover --> Return["Customer: feedback, data control and return · mixed"]
  Return --> Analyze["Manager / owner: outcomes and metrics · mixed"]
  Analyze --> Improve["Human review and controlled improvement · mostly planned"]
  Improve --> Govern
  Connect["Optional Connect: events, tables, groups and consent · planned"] --> Plan
  Connect --> Return
  Gate["Pilot gates: tenancy, governed safety, transactions, privacy and recovery · planned"] --> Govern
  Gate --> Fulfill
  AI["Shared: bounded AI, evaluations, telemetry and release gates · mixed"] --> Choose
  AI --> Improve
''')
print('Generated nine SVG, Excalidraw and Mermaid diagrams.')
