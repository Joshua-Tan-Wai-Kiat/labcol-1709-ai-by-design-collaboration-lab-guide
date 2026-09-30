"""Build the public guide with Python's standard library."""
from pathlib import Path
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
    content, navigation = [], []
    for block in blocks:
        match = re.match(r'^(#{1,3}) (.+)$', block)
        if match:
            level, title = len(match[1]), match[2]
            key = anchor(title)
            content.append(f'<h{level} id="{key}">{html.escape(title)}</h{level}>')
            if level > 1:
                navigation.append(f'<li class="level-{level}"><a href="#{key}">{html.escape(title)}</a></li>')
        elif block.startswith('> '):
            content.append(f'<aside>{inline(block[2:])}</aside>')
        else:
            content.append(f'<p>{inline(block)}</p>')
    page = '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LABCOL-1709 | AI by Design for Collaboration</title>
<style>
:root{color-scheme:light;--blue:#005c9e}*{box-sizing:border-box}body{margin:0;color:#203346;background:#f5f8fb;font:17px/1.65 system-ui,sans-serif}a{color:var(--blue)}header{background:#083b60;color:white;padding:22px 5vw}header a{color:white}header strong{display:block;font-size:24px}header p{margin:0}nav{position:sticky;top:24px;align-self:start;background:white;padding:22px;border-radius:12px;max-height:90vh;overflow:auto;font-size:14px}nav ul{list-style:none;margin:0;padding:0}nav li{margin:10px 0}nav .level-3{padding-left:14px}main{background:white;border-radius:12px;padding:32px 42px;min-width:0}section{display:grid;grid-template-columns:290px minmax(0,1fr);gap:28px;max-width:1320px;margin:28px auto;padding:0 24px}h1{line-height:1.2;font-size:36px;margin-top:0}h2{font-size:28px;margin-top:50px;padding-top:14px;border-top:1px solid #dce5ec}h3{font-size:23px;margin-top:32px}h1,h2,h3{scroll-margin-top:24px}p{overflow-wrap:anywhere}aside{padding:20px;border-left:4px solid #009bcc;background:#eef7fc;border-radius:4px}footer{padding:24px;text-align:center;font-size:14px}nav a{text-decoration:none}nav a:hover{text-decoration:underline}.skip{position:absolute;left:-9999px}.skip:focus{left:10px;top:10px;background:white;padding:10px;z-index:9}@media(max-width:850px){section{display:block;padding:0 16px}nav{position:static;max-height:none;margin-bottom:20px}main{padding:24px}h1{font-size:30px}}@media print{header,nav,footer{display:none}section{display:block;margin:0;padding:0}main{padding:0}body{background:white}}
</style></head><body><a class="skip" href="#guide">Skip to lab guide</a>
<header><strong>Cisco Live Melbourne 2026</strong><p>LABCOL-1709 · AI by Design for Collaboration</p></header>
<section><nav aria-label="Lab contents"><strong>Lab contents</strong><ul>''' + ''.join(navigation) + '</ul></nav><main id="guide">' + '\n'.join(content) + '''</main></section>
<footer><a href="GUIDE.md">Markdown source</a> · <a href="https://github.com/Joshua-Tan-Wai-Kiat/labcol-1709-ai-by-design-collaboration-lab-guide">GitHub repository</a></footer></body></html>'''
    ROOT.joinpath('index.html').write_text(page, encoding='utf-8')
    print(f'Built {len(blocks)} content blocks and {len(navigation)} navigation links.')

if __name__ == '__main__':
    build()
