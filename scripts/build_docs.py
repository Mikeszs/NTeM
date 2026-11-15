"""Gera docs/index.html (site público) a partir dos .md de docs/.

Uso: python scripts/build_docs.py   (requer: pip install markdown)
O HTML é derivado; edite sempre os .md e rode o script de novo.
"""
import re
from datetime import date
from pathlib import Path

import markdown

DOCS = Path(__file__).resolve().parent.parent / "docs"
PAGINAS = [  # (arquivo, rótulo no menu)
    ("manual-do-usuario.md", "Manual do usuário"),
    ("guia-do-desenvolvedor.md", "Guia do desenvolvedor"),
    ("api.md", "API"),
    ("arquitetura.md", "Arquitetura"),
    ("antropometria-formulas.md", "Fórmulas"),
    ("qualidade-de-software.md", "Qualidade"),
]
MD2ID = {a: a[:-3] for a, _ in PAGINAS}

CSS = """
:root{--bg:#f4f7f5;--paper:#fff;--ink:#20312c;--muted:#62736c;--green:#16745b;--line:#dce7e1;--code:#edf3ef;--th:#eaf3ee;--h:#174d3d}
@media(prefers-color-scheme:dark){:root{--bg:#12181b;--paper:#1a2226;--ink:#e3ece8;--muted:#9fb0a9;--green:#4fd1a5;--line:#2c3a3f;--code:#243137;--th:#223036;--h:#7fe0bd}}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.72 system-ui,-apple-system,"Segoe UI",sans-serif}
header{background:linear-gradient(135deg,#123b32,#16745b);color:#fff;padding:36px 22px 28px}
.w{max-width:960px;margin:auto}header h1{margin:6px 0;font-size:clamp(1.8rem,5vw,2.8rem);line-height:1.15}
header h1{color:#fff}header p{margin:6px 0 0;opacity:.9;max-width:720px}header code{background:rgba(255,255,255,.18);color:#fff}
nav{position:sticky;top:0;background:var(--paper);border-bottom:1px solid var(--line);z-index:5}
nav .w{display:flex;gap:4px;overflow-x:auto;padding:0 12px}
nav a{padding:12px 12px;white-space:nowrap;text-decoration:none;color:var(--muted);font-size:.92rem;border-bottom:3px solid transparent}
nav a:hover,nav a.on{color:var(--green);border-color:var(--green)}
main{max-width:960px;margin:24px auto 50px;padding:34px clamp(18px,5vw,56px);background:var(--paper);border:1px solid var(--line);border-radius:16px}
section.pg{display:none}section.pg.on{display:block}
h1,h2,h3{color:var(--h);line-height:1.3}h1{margin-top:0}h2{margin-top:2em;padding-bottom:.4em;border-bottom:1px solid var(--line)}
a{color:var(--green)}p,li{overflow-wrap:anywhere}
table{width:100%;border-collapse:collapse;display:block;overflow-x:auto;margin:1.1em 0;font-size:.94rem}
th,td{border:1px solid var(--line);padding:8px 11px;text-align:left;vertical-align:top;min-width:110px}th{background:var(--th);color:var(--h)}
pre{overflow-x:auto;padding:16px;border-radius:10px;background:#17251f;color:#e8f3ed;line-height:1.5}
code{background:var(--code);padding:.1em .35em;border-radius:4px;font-size:.9em}pre code{background:none;padding:0}
footer{text-align:center;color:var(--muted);font-size:.85rem;padding:0 20px 32px}
@media print{nav{display:none}section.pg{display:block!important;page-break-before:always}header{background:none;color:#000}main{border:0;padding:0}}
"""

JS = """
(function(){var ps=[].slice.call(document.querySelectorAll('section.pg')),ls=[].slice.call(document.querySelectorAll('nav a'));
function show(){var id=(location.hash||'').slice(1).split('/')[0];if(!ps.some(function(p){return p.id===id}))id=ps[0].id;
ps.forEach(function(p){p.classList.toggle('on',p.id===id)});ls.forEach(function(a){a.classList.toggle('on',a.hash==='#'+id)});window.scrollTo(0,0)}
window.addEventListener('hashchange',show);show()})();
"""


def converter(md_texto):
    html = markdown.markdown(md_texto, extensions=["tables", "fenced_code"])
    # links entre documentos (api.md#x ou api.md) viram navegação interna
    def troca(m):
        arq = m.group(1)
        return f'href="#{MD2ID[arq]}"' if arq in MD2ID else m.group(0)
    return re.sub(r'href="([\w-]+\.md)(?:#[\w-]+)?"', troca, html)


def main():
    nav, secoes = [], []
    for arq, rotulo in PAGINAS:
        nav.append(f'<a href="#{MD2ID[arq]}">{rotulo}</a>')
        corpo = converter((DOCS / arq).read_text(encoding="utf-8"))
        secoes.append(f'<section class="pg" id="{MD2ID[arq]}">{corpo}</section>')
    html = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Manual do usuário, guia do desenvolvedor, API, arquitetura e qualidade de software do NTeM (NutriSocial).">
<title>NTeM — Documentação</title><style>{CSS}</style></head>
<body><header><div class="w"><div style="text-transform:uppercase;letter-spacing:.14em;font-size:.75rem;opacity:.8">NutriSocial · NTeM</div>
<h1>Documentação da plataforma</h1><p>Gerada a partir dos arquivos Markdown de <code>docs/</code> do repositório, que são a fonte oficial.</p></div></header>
<nav><div class="w">{''.join(nav)}</div></nav>
<main>{''.join(secoes)}</main>
<footer>NTeM — NutriSocial · gerado em {date.today():%d/%m/%Y} · <a href="https://github.com/Mikeszs/NTeM">código-fonte</a></footer>
<script>{JS}</script></body></html>"""
    (DOCS / "index.html").write_text(html, encoding="utf-8")
    print("docs/index.html gerado")


if __name__ == "__main__":
    main()
