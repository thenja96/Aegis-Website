"""One-off: IR 'What the IR mandate covers' as index rows (option A). Copy unchanged."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
p = "_src/pages/services-investor-relations.html"
s = open(p, encoding="utf-8").read()
a = s.index('<span class="eyebrow">What the IR mandate covers</span>')
a = s.rindex('<div class="reveal">', 0, a)
b = s.index('<div class="photo-grid', a)
old = s[a:b]
core = re.findall(r'<li>(.*?)</li>', old[:old.index('</ul>')])
groups = re.findall(r'<h3[^>]*>(.*?)</h3>(.*?)(?=<h3|$)', old, flags=re.S)
assert len(core) == 10 and len(groups) == 3
li = lambda xs: "".join(f"<li>{x}</li>" for x in xs)
rows = ['''<div class="m-row">
        <div class="m-head"><span class="eyebrow">What the IR mandate covers</span>
        <hr class="rule">
        <h2>Core functions.</h2></div>
        <ul class="m-list two">''' + li(core) + '</ul>\n      </div>']
for h, body in groups:
    items = re.findall(r'<li>(.*?)</li>', body)
    inner = (f'<ul class="m-list">{li(items)}</ul>' if items else "")
    inner += "".join(f"<p>{x}</p>" for x in re.findall(r'<p>(.*?)</p>', body))
    inner += "".join(f'<p class="disclaimer">{x}</p>' for x in re.findall(r'<p class="disclaimer">(.*?)</p>', body))
    rows.append(f'<div class="m-row">\n        <h3>{h}</h3>\n        <div>{inner}</div>\n      </div>')
new = '<div class="mandate reveal">\n      ' + "\n      ".join(rows) + '\n    </div>\n    '
s = s[:a] + new + s[b:]
open(p, "w", encoding="utf-8").write(s)

CSS = r'''
/* ---- IR mandate index rows ---- */
.mandate .m-row{display:grid;grid-template-columns:1fr 2fr;gap:var(--s6);padding:var(--s4) 0;border-top:1px solid var(--line)}
.mandate .m-row:first-child{border-top:0;padding-top:0;align-items:end}
.mandate .m-row:last-child{border-bottom:1px solid var(--line)}
.mandate .m-head h2{margin:0}
.mandate h3{font-family:var(--font-head);font-weight:500;font-size:1.3rem;line-height:1.3;margin:0;color:var(--navy)}
.m-list{list-style:none;margin:0;padding:0}
.m-list li{padding:7px 0;color:var(--navy);font-size:1rem;line-height:1.45}
.m-list li::before{display:none}
.m-list.two{columns:2;column-gap:var(--s5)}
.m-list.two li{break-inside:avoid}
.mandate .m-row p{margin:0;color:var(--slate);line-height:1.6}
.mandate .m-row p.disclaimer{margin-top:var(--s2)}
@media (max-width:900px){ .mandate .m-row{gap:var(--s4)} }
@media (max-width:768px){
  .mandate .m-row{grid-template-columns:1fr;gap:var(--s2);padding:var(--s3) 0}
  .mandate .m-row:first-child{gap:var(--s3)}
  .m-list.two{columns:1}
  .m-list li{padding:6px 0;font-size:.98rem}
}
'''
open("assets/style.css", "a", encoding="utf-8").write(CSS)
print("mandate applied")
