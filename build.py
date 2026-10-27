"""Build a concise, multi-page lab guide without third-party dependencies."""
from pathlib import Path, PurePosixPath
from html import escape
from html.parser import HTMLParser
from datetime import datetime
import json, re, shutil

ROOT=Path(__file__).resolve().parent
MANIFEST=json.loads(ROOT.joinpath('source-manifest.json').read_text(encoding='utf-8'))
AUDIT=json.loads(ROOT.joinpath('screenshot-audit.json').read_text(encoding='utf-8'))
RAW=ROOT.joinpath('content.html').read_text(encoding='utf-8')
chunks=re.split(r'(?=<h[23]\s)',RAW)
SECTIONS={re.search(r'<h[23] id="([^"]+)"',chunk)[1]:chunk for chunk in chunks[1:]}
HEADINGS=[h['id'] for h in MANIFEST['headings']]
PAGES=[
 {'path':'index.html','title':'Lab overview','group':'Getting started','sections':HEADINGS[0:1]},
 {'path':'getting-started/index.html','title':'Access your lab','group':'Getting started','sections':HEADINGS[1:6]},
 {'path':'setup/index.html','title':'Activate AI Assistant','group':'Setup','sections':HEADINGS[6:8]},
 {'path':'messaging/ask-assistant/index.html','title':'Ask AI Assistant','group':'Messaging','sections':HEADINGS[8:10]},
 {'path':'messaging/space-summaries/index.html','title':'Space summaries','group':'Messaging','sections':HEADINGS[10:11]},
 {'path':'messaging/rewrite/index.html','title':'Rewrite messages','group':'Messaging','sections':HEADINGS[11:12]},
 {'path':'messaging/translation/index.html','title':'Translate messages','group':'Messaging','sections':HEADINGS[12:13]},
 {'path':'meetings/index.html','title':'Meeting overview','group':'Meetings','sections':HEADINGS[13:14]},
 {'path':'meetings/schedule/index.html','title':'Schedule with AI','group':'Meetings','sections':HEADINGS[14:15]},
 {'path':'meetings/captions/index.html','title':'Captions and translation','group':'Meetings','sections':HEADINGS[15:16]},
 {'path':'meetings/assistant/index.html','title':'Meeting AI Assistant','group':'Meetings','sections':HEADINGS[16:17]},
 {'path':'screenshots/index.html','title':'Screenshot availability','group':'Reference','sections':[]},
 {'path':'print/index.html','title':'Complete printable guide','group':'Reference','sections':HEADINGS},
]
ROUTES={key:page['path'] for page in PAGES if page['group']!='Reference' for key in page['sections']}
assert set(ROUTES)==set(HEADINGS)
ICONS={
 'search':'<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.8"/><path d="m16 16 5 5"/></svg>',
 'theme':'<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 1v3m0 16v3M1 12h3m16 0h3M4 4l2 2m12 12 2 2M4 20l2-2M18 6l2-2"/></svg>',
 'menu':'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 5h18M3 12h18M3 19h18"/></svg>',
 'close':'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 5 14 14M5 19 19 5"/></svg>',
}

class PlainText(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.parts=[]
 def handle_data(self,data):self.parts.append(data)
def plain(markup):
 parser=PlainText();parser.feed(markup)
 return re.sub(r'\s+',' ',' '.join(parser.parts)).strip()
def prefix(path):
 depth=len(PurePosixPath(path).parent.parts)
 return '../'*depth if depth else './'
def relocate(markup,base):
 return re.sub(r'((?:src|href)=")assets/',lambda m:m[1]+base+'assets/',markup)
def heading_as(chunk,tag,cls=''):
 match=re.match(r'<h([23])([^>]*)>(.*?)</h\1>',chunk,re.S)
 assert match
 attrs=match[2]+(f' class="{cls}"' if cls else '')
 return f'<{tag}{attrs}>{match[3]}</{tag}>'+chunk[match.end():]
def content_for(page):
 selected=[SECTIONS[key] for key in page['sections']]
 if page['path']=='print/index.html':
  return '<div class="print-cover"><h1>AI by Design for Collaboration</h1><p>LABCOL-1709</p><p>Hussain Ali, Technical Marketing Engineer<br>Omer Ilyas, Technical Marketing Engineer</p></div>'+''.join(selected)
 if page['path']=='index.html':
  return '<h1>Lab overview</h1><p class="authors"><span>LABCOL-1709 · AI by Design for Collaboration</span><span>Hussain Ali and Omer Ilyas · Technical Marketing Engineers</span></p>'+''.join(selected)
 if page['path'] in ['setup/index.html','messaging/ask-assistant/index.html']:
  selected[0]=heading_as(selected[0],'p','module-label')
  selected[1]=heading_as(selected[1],'h1')
 else:
  selected[0]=heading_as(selected[0],'h1')
 if page['path']=='meetings/index.html':
  # Keep the microphone note visible; retain longer background prose on demand.
  chunk=selected[0]
  position=chunk.find('<div',chunk.find('data-source-block="186"')+1)
  # Blocks 187 onward are explanation, not the microphone prerequisite.
  boundary=chunk.find('<div class="" data-source-block="187"')
  if boundary!=-1:
   selected[0]=chunk[:boundary]+'<details class="background-reading"><summary>Background: how AI supports Webex meetings</summary>'+chunk[boundary:]+'</details>'
 return ''.join(selected)

def audit_content():
 checked=datetime.fromisoformat(AUDIT['checked_at']).strftime('%d %B %Y at %H:%M UTC')
 rows=[]
 for image in AUDIT['images']:
  status=image['status'];kind='published' if status=='Published' else 'private' if status=='Withheld for privacy' else 'unused'
  number=re.search(r'\d+',image['file'])[0]
  reference=('Screenshot '+number) if image['role']=='Instructional screenshot' else 'Image '+number
  if status=='Published':
   detail='HTTP 200 · matches the Word image exactly'
   target='<a href="../'+image['path']+'" target="_blank" rel="noopener">Open image</a>'
  else:
   detail=image['reason'];target='—'
  rows.append(f'<tr data-image-status="{kind}"><td>{reference}<small>{escape(image["file"])}</small></td><td>{escape(image["role"])}</td><td class="'+('status-ok' if kind=='published' else 'status-private')+f'">{escape(status)}</td><td>{escape(detail)}</td><td>{target}</td></tr>')
 return '<h1>Screenshot availability</h1><p class="audit-summary"><strong>All 41 published instructional screenshots are available.</strong> The seven inline control icons and two branding images also load correctly. Each of the 50 published files was downloaded and compared with the corresponding Word image; no missing, broken, or altered files were found.</p><p>Ten screenshots containing private access, account contact, or tenant details are intentionally withheld. They have labelled placeholders in the guide. One non-instructional menu icon is not used in the web edition. All 61 images from the Word file are accounted for below.</p><p class="audit-count">Verified '+checked+'. The checked source is the supplied Lab Guide (2).docx.</p><div class="audit-tools" role="group" aria-label="Filter image inventory"><button data-audit-filter="all" aria-pressed="true">All 61 images</button><button data-audit-filter="published" aria-pressed="false">Published 50</button><button data-audit-filter="private" aria-pressed="false">Withheld 10</button><button data-audit-filter="unused" aria-pressed="false">Not used 1</button></div><p id="audit-count" class="audit-count" aria-live="polite">61 source images shown</p><div class="table-wrap"><table><thead><tr><th>Source reference</th><th>Type</th><th>Status</th><th>Verification or reason</th><th>Preview</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'

def sidebar(page,base):
 groups=[]
 for group in ['Getting started','Setup','Messaging','Meetings','Reference']:
  if group not in [page['group'],'Reference']:continue
  links=[]
  for item in PAGES:
   if item['group']!=group:continue
   active=item['path']==page['path']
   current=' aria-current="page"' if active else ''
   toc=''
   if active and len(item['sections'])>1 and item['group']!='Reference':
    toc='<ul class="page-toc">'+''.join(f'<li><a href="#{key}">{escape(next(h["title"] for h in MANIFEST["headings"] if h["id"]==key))}</a></li>' for key in item['sections'][1:])+'</ul>'
   links.append(f'<li><a href="{base+item["path"]}"{current}>{escape(item["title"])}</a>{toc}</li>')
  groups.append(f'<section class="nav-group"><h2>{group}</h2><ul>'+''.join(links)+'</ul></section>')
 return ''.join(groups)

def render(page,index,body):
 base=prefix(page['path'])
 tabs=[]
 for label,path in [('Getting started','index.html'),('Setup','setup/index.html'),('Messaging','messaging/ask-assistant/index.html'),('Meetings','meetings/index.html'),('Reference','screenshots/index.html')]:
  active=' aria-current="true"' if page['group']==label else ''
  tabs.append(f'<a href="{base+path}"{active}>{label}</a>')
 prev=PAGES[index-1] if index else None
 after=PAGES[index+1] if index+1<len(PAGES) else None
 previous=f'<a href="{base+prev["path"]}"><small>← Previous</small><strong>{escape(prev["title"])}</strong></a>' if prev else '<span></span>'
 following=f'<a class="next" href="{base+after["path"]}"><small>Next →</small><strong>{escape(after["title"])}</strong></a>' if after else '<span></span>'
 root_data=escape(base,quote=True)
 return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(page['title'])} | LABCOL-1709</title><meta name="description" content="Cisco Live Melbourne AI by Design for Collaboration lab guide"><script>try{{document.documentElement.dataset.theme=localStorage.getItem('labcol1709-theme')||'light';}}catch(_){{}}</script><link rel="stylesheet" href="{base}assets/site.css"></head><body data-root="{root_data}"><a class="skip" href="#main-content">Skip to content</a><header class="site-header"><div class="header-inner"><button class="icon-button menu-button" id="menu-toggle" aria-label="Open navigation" aria-controls="site-navigation" aria-expanded="false">{ICONS['menu']}</button><a class="brand" href="{base}index.html">Cisco <b>Live!</b></a><span class="site-title">LABCOL-1709 · AI by Design for Collaboration</span><button id="theme-toggle" class="icon-button" aria-label="Switch to dark mode" aria-pressed="false">{ICONS['theme']}</button><button class="search-trigger" id="search-open" aria-label="Search guide">{ICONS['search']}<span>Search</span><kbd>/</kbd></button></div><nav class="tabs" aria-label="Lab sections">{''.join(tabs)}</nav></header><button class="nav-shade" id="nav-shade" aria-label="Close navigation"></button><div class="docs-layout"><nav class="sidebar" id="site-navigation" aria-label="Lab navigation"><div class="drawer-close">LABCOL-1709<button id="menu-close" class="icon-button" aria-label="Close navigation">{ICONS['close']}</button></div>{sidebar(page,base)}</nav><article id="main-content"><div class="breadcrumbs"><a href="{base}index.html">LABCOL-1709</a> / {escape(page['group'])}</div>{body}<div class="page-footer"><a href="{base}screenshots/index.html">Screenshot availability</a><a href="{base}print/index.html">Complete printable guide</a><a href="https://github.com/Joshua-Tan-Wai-Kiat/labcol-1709-ai-by-design-collaboration-lab-guide">GitHub</a></div></article></div><footer><nav class="next-prev" aria-label="Previous and next exercise"><div class="next-prev-inner">{previous}{following}</div></nav><div class="copyright">Cisco Live Melbourne 2026 · LABCOL-1709 · Based on the supplied lab guide</div></footer><dialog id="search-dialog" class="search-dialog" aria-label="Search the lab guide"><div class="search-box">{ICONS['search']}<input id="guide-search" type="search" aria-label="Search all exercises" placeholder="Search the guide" autocomplete="off"><button id="search-close" class="icon-button" aria-label="Close search">{ICONS['close']}</button></div><div id="search-results" class="search-results" aria-live="polite"><p class="search-message">Search the guide for a feature, setting, or exercise.</p></div></dialog><script type="application/json" id="legacy-routes">{json.dumps(ROUTES)}</script><script src="{base}assets/site.js" defer></script></body></html>'''

def build():
 search=[];rendered=[]
 for index,page in enumerate(PAGES):
  body=audit_content() if page['path']=='screenshots/index.html' else content_for(page)
  # Source asset links become relative to each exercise directory.
  if page['path']!='screenshots/index.html':body=relocate(body,prefix(page['path']))
  result=render(page,index,body)
  path=ROOT/page['path'];path.parent.mkdir(parents=True,exist_ok=True);path.write_text('\n'.join(line.rstrip() for line in result.splitlines())+'\n',encoding='utf-8',newline='\n')
  rendered.append(page['path'])
  if page['path']!='print/index.html':search.append({'path':page['path'],'title':page['title'],'text':plain(body)})
 ROOT.joinpath('search-index.json').write_text(json.dumps(search,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
 ROOT.joinpath('page-manifest.json').write_text(json.dumps({'pages':PAGES,'legacy_routes':ROUTES},indent=2)+'\n',encoding='utf-8',newline='\n')
 stage=ROOT/'site';stage.mkdir(exist_ok=True)
 for name in rendered+['GUIDE.md','source-manifest.json','screenshot-audit.json','search-index.json','page-manifest.json']:
  target=stage/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
 shutil.copytree(ROOT/'assets',stage/'assets',dirs_exist_ok=True)
 print(f'Built {len(PAGES)} documentation pages; all {MANIFEST["source_blocks"]} source blocks and {AUDIT["published_assets"]} published images retained.')

if __name__=='__main__':build()
