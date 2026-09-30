"""Build the public guide with Python's standard library."""
from pathlib import Path
import base64
import html
import re

ROOT = Path(__file__).resolve().parent

def anchor(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def inline(text):
    safe = html.escape(text)
    def link(match):
        url = match[0].rstrip('.,:!?)')
        suffix = match[0][len(url):]
        return f'<a href="{url}">{url}</a>{suffix}'
    return re.sub(r'https://[^\s<>]+', link, safe)

def build():
    blocks = ROOT.joinpath('GUIDE.md').read_text(encoding='utf-8').strip().split('\n\n')
    content, navigation = ['<div class="cover">'], []
    cover_open = True
    for block in blocks:
        match = re.match(r'^(#{1,3}) (.+)$', block)
        if match:
            level, title = len(match[1]), match[2]
            if level == 2 and cover_open:
                content.append('</div>')
                cover_open = False
            key = anchor(title)
            content.append(f'<h{level} id="{key}">{html.escape(title)}</h{level}>')
            if level > 1:
                navigation.append(f'<li class="level-{level}"><a href="#{key}">{html.escape(title)}</a></li>')
        elif block.startswith('> '):
            content.append(f'<aside>{inline(block[2:])}</aside>')
        elif block.startswith('![Webex lab environment'):
            content.append('<figure>' + ROOT.joinpath('lab-topology.svg').read_text(encoding='utf-8') + '<figcaption>Figure 1. Logical Webex lab environment</figcaption></figure>')
        elif block.startswith('- '):
            content.append('<ul class="objectives">' + ''.join(f'<li>{inline(line[2:])}</li>' for line in block.splitlines()) + '</ul>')
        elif block.startswith('| '):
            rows = [[cell.strip() for cell in line.strip('|').split('|')] for line in block.splitlines()]
            content.append('<div class="table-wrap"><table><thead><tr>' + ''.join(f'<th scope="col">{inline(c)}</th>' for c in rows[0]) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in row) + '</tr>' for row in rows[2:]) + '</tbody></table></div>')
        else:
            content.append(f'<p>{inline(block)}</p>')
    banner = base64.b64encode(ROOT.joinpath('template-banner.jpg').read_bytes()).decode('ascii')
    logo = base64.b64encode(ROOT.joinpath('template-logo.png').read_bytes()).decode('ascii')
    page = '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LABCOL-1709 | AI by Design for Collaboration</title>
<style>
:root{color-scheme:light;--navy:#0d274d}*{box-sizing:border-box}body{margin:0;color:#17243a;background:#f4f5f7;font:16px/1.6 "Inter Medium",Inter,Arial,sans-serif}a{color:var(--navy)}header{background:#06182a}header img{width:100%;height:auto;max-width:1600px;display:block;margin:auto}nav{position:sticky;top:24px;align-self:start;background:white;padding:24px;max-height:90vh;overflow:auto;font-size:14px}nav ul{list-style:none;margin:0;padding:0}nav li{margin:10px 0}nav .level-3{padding-left:14px;font-size:13px}main{background:white;padding:44px 54px;min-width:0;border-top:4px solid var(--navy)}section{display:grid;grid-template-columns:285px minmax(0,1fr);gap:24px;max-width:1350px;margin:28px auto;padding:0 24px}h1{line-height:1.15;color:var(--navy);font-size:40px;margin-top:0;max-width:650px}h2{color:var(--navy);font-size:25px;margin-top:44px}h3{color:var(--navy);font-size:20px;margin-top:28px}h1,h2,h3{scroll-margin-top:24px}p{overflow-wrap:anywhere;margin:14px 0}li{margin:8px 0}figure{margin:24px 0}figure svg{width:100%;height:auto;display:block}figcaption{font-size:13px;color:#526076;margin-top:8px;text-align:center}.table-wrap{overflow:auto}table{border-collapse:collapse;width:100%;font-size:16px}th,td{border-bottom:1px solid #0877ad;padding:12px 14px;text-align:center;vertical-align:top}th{color:var(--navy);font-size:20px}.cover{text-align:center;padding:28px 0 34px}.cover h1{margin-left:auto;margin-right:auto}footer{padding:26px;text-align:center;font-size:13px}.brand-logo{width:160px;display:block;margin:0 auto 14px}nav a{text-decoration:none}nav a:hover{text-decoration:underline}.skip{position:absolute;left:-9999px}.skip:focus{left:10px;top:10px;background:white;padding:10px;z-index:9}@media(max-width:850px){section{display:block;padding:0 12px}nav{position:static;max-height:none;margin-bottom:20px}main{padding:26px 22px}h1{font-size:32px}h2{font-size:24px}}@media print{@page{size:A4;margin:20mm 20mm 22mm}body{background:white;font-size:10pt}header{background:white}nav,footer{display:none}section{display:block;margin:0;padding:0}main{padding:8mm 0;border:0}h1{font-size:24pt}h2{font-size:14pt;break-after:avoid}h3{font-size:14pt;break-after:avoid}h2[id^="task-"]{break-before:page}figure,table{break-inside:avoid}a{text-decoration:none}header img{max-height:20mm;width:100%;object-fit:cover}}
</style></head><body><a class="skip" href="#guide">Skip to lab guide</a>
<header><img alt="Cisco Live Melbourne November 9â€“12, 2026" src="data:image/jpeg;base64,''' + banner + '''"></header>
<section><nav aria-label="Lab contents"><strong>Lab contents</strong><ul>''' + ''.join(navigation) + '</ul></nav><main id="guide">' + '\n'.join(content) + '''</main></section>
<footer><img class="brand-logo" alt="Cisco Live" src="data:image/png;base64,''' + logo + '''"><a href="LABCOL-1709-AI-by-Design-Lab-Guide.docx">Download Word guide</a> · <a href="GUIDE.md">Markdown source</a> Â· <a href="https://github.com/Joshua-Tan-Wai-Kiat/labcol-1709-ai-by-design-collaboration-lab-guide">GitHub repository</a></footer></body></html>'''
    ROOT.joinpath('index.html').write_text(page, encoding='utf-8')
    print(f'Built {len(blocks)} content blocks and {len(navigation)} navigation links.')

if __name__ == '__main__':
    build()
