"""Generate source-faithful lab pages and build them with MkDocs Material."""
from pathlib import Path
import importlib.util,sys,re,json,shutil

ROOT=Path(__file__).resolve().parent
if importlib.util.find_spec('mkdocs') is None:
    for local in [ROOT.parent/'.local-deps',ROOT.parent.parent/'.local-deps']:
        if (local/'mkdocs').is_dir():
            sys.path.insert(0,str(local))
            break
from bs4 import BeautifulSoup,Tag
from mkdocs.config import load_config
from mkdocs.commands.build import build as build_mkdocs

SOURCE=json.loads((ROOT/'source-manifest.json').read_text(encoding='utf-8'))
AUDIT=json.loads((ROOT/'screenshot-audit.json').read_text(encoding='utf-8'))
MODEL=json.loads((ROOT/'page-manifest.json').read_text(encoding='utf-8'))
PAGES=MODEL['pages']
RAW=(ROOT/'content.html').read_text(encoding='utf-8')
chunks=re.split(r'(?=<h[23]\s)',RAW)
SECTIONS={re.search(r'<h[23] id="([^"]+)"',chunk)[1]:chunk for chunk in chunks[1:]}
DOCS=ROOT/'.build-docs'
STAGE=ROOT/'site'
for target in [DOCS,STAGE]:
    assert target.resolve().parent==ROOT.resolve() and target.name in ['.build-docs','site'],target
DOCS.mkdir(exist_ok=True)
FIGURES={7:'Workstation 1 desktop and lab credential files',12:'Control Hub idle timeout',13:'Open the AI Assistant customization settings',14:'Calling AI feature settings',15:'Messaging AI features',16:'Meeting AI features',17:'General AI settings and search sources',21:'Open Cisco AI Assistant from a space',22:'Ask a question about the conversation',23:'Review the AI answer and source citations',24:'Cisco AI Assistant in the messaging space',25:'Choose a summary time range',26:'Review the generated space summary',28:'Draft a message and select Rewrite',30:'Preview a rewritten message',31:'Send the updated message',33:'Choose and save a translation language',34:'Translate an individual message',35:'Translated messages in the space',36:'Start live translation',37:'Live translations in the conversation',38:'Open the Meetings tab and AI Assistant',40:'Review and confirm the AI-scheduled meeting',42:'Enable real-time translation and transcription',44:'Join from the meeting reminder',45:'Choose a caption language',46:'Spoken language and caption controls',47:'Language detection on the speaking workstation',48:'Translated captions on the receiving workstation',49:'Select Bosnian captions',50:'French captions on one workstation',51:'Bosnian captions on the other workstation',52:'Start Cisco AI Assistant for the meeting',53:'Start the meeting recording',54:'Catch me up',55:'Was my name mentioned?',56:'What are the action items?',57:'Ask about meeting highlights',58:'Ask about the customer response',60:'Post-meeting summary',61:'Post-meeting transcript'}
STEPS={
 'setup/index.html':['Open Control Hub','Sign in as Charles','Set the idle timeout','Open the AI settings','Enable the lab features'],
 'messaging/ask-assistant/index.html':['Open Webex','Open AI Assistant','Ask about the space'],
 'messaging/space-summaries/index.html':['Generate a space summary'],
 'messaging/rewrite/index.html':['Draft a message','Apply and send the rewrite'],
 'messaging/translation/index.html':['Open Webex settings','Choose your translation language','Translate messages in the space'],
 'meetings/schedule/index.html':['Open Webex','Open AI Assistant','Describe the meeting','Review the proposed meeting','Confirm the meeting'],
 'meetings/captions/index.html':['Open your meeting site','Open site options','Enable translation','Start the meeting and captions','Join as Anita','Enable captions for Anita','Set the caption language','Check the host language controls','Test another spoken language','Change Anita’s caption language','Set Charles’s language options','Compare the translated captions','Explore other languages','Keep the meeting running'],
 'meetings/assistant/index.html':['Keep the meeting running','Start AI Assistant','Confirm that AI Assistant is active','Record the meeting','Keep recording active','Discuss sample action items','Open Anita’s AI Assistant panel','Ask follow-up questions','End the meeting','View the post-meeting summary','Open the summary and transcript']}
SHORT={
 'webex-suite-ai-overview':'Lab overview',
 'accessing-your-lab':'Access your lab',
 'connect-to-the-workstations-via-remote-desktop':'Connect to the workstations',
 'login-to-the-webex-clients':'Sign in to Webex',
 'login-to-collaboration-control-hub-from-within-workstation-1':'Sign in to Control Hub',
 'alternate-instructions-for-accessing-collaboration-control-hub':'Alternative Control Hub access'}
ROUTES=dict(MODEL['legacy_routes'])
for key,value in list(ROUTES.items()):
    ROUTES[key]='overview/' if value=='index.html' else value.replace('index.html','')

def text(node):return re.sub(r'\s+',' ',node.get_text()).strip()
def module(text_value):
    match=re.match(r'(Module \d+[a-z]?)\s*:',text_value)
    return match[1] if match else ''
def md_heading(node,level,title):
    identifier=node.get('id','')
    attrs=(f'#{identifier} ' if identifier else '')+f'data-source-block="{node["data-source-block"]}"'
    return '\n'+'#'*level+' '+title+' { '+attrs+' }\n\n'

def prepare_page(page):
    soup=BeautifulSoup(''.join(SECTIONS[key] for key in page['sections']),'html.parser')
    output=[];figure_count=0;step_count=0;heading_count=0;step_page=page['path'];step_section='guide';background=False
    full=page['path']=='print/index.html'
    if full:
        output.append('# Complete printable guide\n\nAI by Design for Collaboration · LABCOL-1709\n\nHussain Ali and Omer Ilyas · Technical Marketing Engineers\n\n')
    for node in list(soup.contents):
        if not isinstance(node,Tag):continue
        source_block=node.get('data-source-block')
        if node.name in ['h2','h3']:
            original=text(node)
            if full:
                step_count=0;step_page=MODEL['legacy_routes'].get(node.get('id'),page['path']);step_section=node.get('id','guide')
                output.append(md_heading(node,2 if node.name=='h2' else 3,original));continue
            parent=page['path'] in ['setup/index.html','messaging/ask-assistant/index.html'] and heading_count==0
            if parent:
                node.name='p';node['class']=['lab-module'];node.string=module(original)
                output.append(str(node)+'\n\n');heading_count+=1;continue
            primary=heading_count==(1 if page['path'] in ['setup/index.html','messaging/ask-assistant/index.html'] else 0)
            title=page['title'] if primary else SHORT.get(node.get('id'),original)
            mod=module(original)
            if primary and mod:output.append('<p class="lab-module" data-format-generated="true">'+mod+'</p>\n\n')
            output.append(md_heading(node,1 if primary else 2,title))
            if primary and page['path']=='index.html':
                output.append('<p class="lab-byline" data-format-generated="true">LABCOL-1709 · AI by Design for Collaboration<br>Hussain Ali and Omer Ilyas, Technical Marketing Engineers</p>\n\n')
            heading_count+=1;continue
        if source_block=='24' and page['path']=='index.html':continue
        if source_block=='187' and page['path']=='meetings/index.html':
            output.append('<details class="admonition note"><summary>Background: how AI supports Webex meetings</summary>\n\n');background=True
        numeric=node.select_one('.step-number')
        numbered=numeric is not None and text(numeric)!='•'
        bullet=numeric is not None and text(numeric)=='•'
        if numeric:numeric.decompose()
        original_text=text(node)
        complete=original_text.startswith(('This completes','This task is now completed'))
        if numbered and not complete:
            step_count+=1
            names=STEPS.get(step_page,[])
            title=names[step_count-1] if step_count<=len(names) else 'Continue the exercise'
            marker=f'{step_section}-step-{step_count}' if full else f'step-{step_count}'
            output.append('\n'+('####' if full else '##')+f' Step {step_count}: {title} {{ #{marker} .lab-step-title }}\n\n')
        if not numbered:
            for strong in list(node.select('strong')):strong.unwrap()
        for mark in list(node.select('mark')):mark.unwrap()
        for link in list(node.select('a.figure-link')):
            image=link.find('img')
            if image is None:continue
            figure_count+=1;number=int(re.search(r'\d+',Path(image['src']).name)[0])
            caption=FIGURES.get(number,'Lab guide reference')
            width=int(image.get('width',760));height=int(image.get('height',460));display_width=round(min(760,width,460*width/height))
            image['style']=f'width:min(100%,{display_width}px);aspect-ratio:{width}/{height}'
            image['alt']=caption
            link['data-lab-zoom']='';link['aria-label']='Enlarge '+caption;link['class']=['lab-image-link']
            fig=soup.new_tag('figure',attrs={'class':'lab-figure'})
            link.wrap(fig)
            label=soup.new_tag('figcaption',attrs={'data-format-generated':'true'})
            label.string=f'Figure {figure_count}. {caption}. Select to enlarge.'
            fig.append(label)
        for omitted in list(node.select('.omitted-figure')):
            details=soup.new_tag('details',attrs={'class':'admonition note private-example'})
            summary=soup.new_tag('summary');summary.string='Private example screenshot omitted'
            omitted.wrap(details);details.insert(0,summary)
        if bullet:
            node.name='ul';node['class']=['lab-bullets']
            inner=node.select_one('.paragraph-content')
            if inner:inner.name='li';inner.attrs={}
        else:node['class']=['source-paragraph']+(['lab-complete'] if complete else [])
        if not complete and original_text.startswith(('Note:','NOTE:','Important!','VERY IMPORTANT NOTE:')):
            aside=soup.new_tag('div',attrs={'class':'admonition note'})
            title=soup.new_tag('p',attrs={'class':'admonition-title','data-format-generated':'true'})
            title.string='Microphone prerequisite' if source_block=='186' else 'Note'
            aside.append(title);aside.append(node.extract());node=aside
        output.append(str(node)+'\n\n')
    if background:output.append('</details>\n\n')
    markup=''.join(output)
    # Page-relative paths resolve against the generated directory URLs.
    old=page['path'];depth=len(Path(old).parent.parts)
    base='../'*depth if depth else '../'  # overview.md renders in overview/.
    markup=re.sub(r'((?:src|href)=")assets/',lambda m:m[1]+base+'assets/',markup)
    return markup,{'step_headings':step_count,'captioned_screenshots':figure_count}

def audit_page():
    lines=['# Screenshot availability','','All **41 instructional screenshots** are published. The seven control icons and two branding images are also available. Each of the 50 published assets was downloaded and matched against its Word original.','','Ten images containing private details are intentionally withheld, and one non-instructional menu icon is unused. The table accounts for all 61 Word images.','','Last image check: '+AUDIT['checked_at']+'.','','| Source image | Type | Status | Preview or reason |','| --- | --- | --- | --- |']
    for item in AUDIT['images']:
        value=('[Open original](../'+item['path']+')') if item['status']=='Published' else item['reason']
        lines.append('| '+item['file']+' | '+item['role']+' | '+item['status']+' | '+value+' |')
    return '\n'.join(lines)+'\n'

def build():
    generated=[];formatting=[]
    home='---\ntemplate: home.html\nhide:\n  - navigation\n  - toc\ntitle: Home\n---\n'
    (DOCS/'index.md').write_text(home,encoding='utf-8',newline='\n')
    for page in PAGES:
        if page['path']=='screenshots/index.html':body=audit_page();stats={}
        else:body,stats=prepare_page(page)
        target='overview.md' if page['path']=='index.html' else page['path'].replace('index.html','index.md')
        path=DOCS/target;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(body,encoding='utf-8',newline='\n')
        generated.append(target);formatting.append({'path':target,**stats})
    (DOCS/'stylesheets').mkdir(exist_ok=True);(DOCS/'javascripts').mkdir(exist_ok=True)
    shutil.copy2(ROOT/'theme/lab.css',DOCS/'stylesheets/lab.css')
    shutil.copy2(ROOT/'theme/lab.js',DOCS/'javascripts/lab.js')
    shutil.copytree(ROOT/'assets/source-guide',DOCS/'assets/source-guide',dirs_exist_ok=True)
    for name in ['source-manifest.json','screenshot-audit.json']:shutil.copy2(ROOT/name,DOCS/name)
    config=load_config(config_file=str(ROOT/'mkdocs.yml'))
    config.extra['legacy_routes']=ROUTES
    # MkDocs cleans only this validated, generated output directory.
    assert Path(config.site_dir).resolve()==STAGE.resolve() and STAGE.resolve().parent==ROOT.resolve()
    build_mkdocs(config)
    (ROOT/'formatting-manifest.json').write_text(json.dumps({'theme':'MkDocs Material 9.7.7','source':'content.html','pages':formatting,'legacy_routes':ROUTES,'preservation':'Original instructional prose and all published images are retained. Exercise headings are shortened, and descriptive step headings and figure captions are added. The printable guide retains all original source blocks and headings. The task-completed boilerplate is omitted from the overview and retained in the printable guide.'},indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Built Material site with',len(generated)+1,'pages and',len(SOURCE['included_images']),'unchanged source images.')

if __name__=='__main__':build()
