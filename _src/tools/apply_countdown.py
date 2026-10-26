"""One-off: IPO countdown as a countdown bar (option 1). Copy reused verbatim from the three cards and the flow strip."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)

p = "_src/pages/services-ipo-communications.html"
s = open(p, encoding="utf-8").read()
a = s.index('<span class="eyebrow on-dark">IPO countdown</span>'); a = s.rfind('<section', 0, a); b = s.index('</section>', a) + 10
sec = s[a:b]

g0 = sec.index('<div class="grid grid-3 reveal">')
g1 = sec.index('<p class="disclaimer reveal"')
old_block = sec[g0:g1]

phases = re.findall(r'<span class="num">([^<]+)</span>\s*<ul>(.*?)</ul>', old_block, flags=re.S)
assert len(phases) == 3
flow = re.findall(r'<span>([^<]+)</span>', re.search(r'<div class="flow reveal">(.*?)</div>', old_block, flags=re.S).group(1))
assert len(flow) == 2

bar = "".join(f'<div class="seg"><span>{head.split("·")[0].strip()}</span></div>' for head, _ in phases)
cols = ""
for head, ul in phases:
    when, name = [x.strip() for x in head.split("·", 1)]
    items = re.findall(r'<li><strong>(\d+) ([^<]+)</strong>: ([^<]+)</li>', ul)
    lis = "".join(f'<li><span class="no">{no}</span><div><b>{t}</b><p>{d}</p></div></li>' for no, t, d in items)
    cols += f'<div class="cd-col"><span class="when">{when}</span><h3>{name}</h3><ol>{lis}</ol></div>'
no10, title10 = [x.strip() for x in flow[0].split("·", 1)]
new_block = f'''<div class="countdown reveal">
      <div class="cd-bar" aria-hidden="true">{bar}<div class="flag">Listing day</div></div>
      <div class="cd-cols">{cols}</div>
      <div class="cd-after"><span class="dash" aria-hidden="true"></span><span class="no">{no10}</span><b>{title10}</b><span class="what">{flow[1]}</span></div>
    </div>
    '''
sec = sec.replace(old_block, new_block)
s = s[:a] + sec + s[b:]
open(p, "w", encoding="utf-8").write(s)

CSS = r'''
/* ---- IPO countdown bar ---- */
.countdown{margin-top:var(--s2)}
.cd-bar{display:grid;grid-template-columns:1fr 1fr 1fr auto;align-items:end;margin-bottom:var(--s5)}
.cd-bar .seg{position:relative;padding:0 0 12px;margin-right:6px}
.cd-bar .seg::after{content:"";position:absolute;left:0;right:0;bottom:0;height:3px;border-radius:2px;background:linear-gradient(90deg,var(--teal),var(--blue))}
.cd-bar .seg:nth-child(2)::after{opacity:.85}.cd-bar .seg:nth-child(3)::after{opacity:.7}
.cd-bar .seg span,.cd-col .when{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;font-size:.76rem;letter-spacing:.08em;text-transform:uppercase;color:var(--teal-bright)}
.cd-bar .flag{position:relative;padding:0 0 10px 14px;font:600 .74rem var(--font-body);letter-spacing:.16em;text-transform:uppercase;color:var(--white);white-space:nowrap}
.cd-bar .flag::before{content:"";position:absolute;left:0;bottom:0;width:2px;height:34px;background:var(--white)}
.cd-cols{display:grid;grid-template-columns:1fr 1fr 1fr;gap:0 var(--s6);padding-right:110px}
.cd-col .when{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.cd-col h3{font-size:1.25rem;font-weight:400;color:var(--white);margin:0 0 var(--s3)}
.cd-col ol{list-style:none;margin:0;padding:0}
.cd-col li{display:grid;grid-template-columns:30px 1fr;gap:12px;padding:15px 0;border-top:1px solid rgba(255,255,255,.12)}
.cd-col li::before{display:none}
.countdown .no{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;font-size:.78rem;color:var(--teal-bright);padding-top:2px}
.cd-col b{display:block;color:var(--white);font-weight:600;font-size:.98rem}
.cd-col p{margin:4px 0 0;color:#A9B6C6;font-size:.92rem;line-height:1.5}
.cd-after{display:flex;align-items:center;flex-wrap:wrap;gap:8px 14px;margin-top:var(--s5);padding-top:var(--s4);border-top:1px solid rgba(255,255,255,.12)}
.cd-after .dash{width:72px;border-top:2px dashed var(--blue)}
.cd-after b{color:var(--white);font-weight:600}
.cd-after .what{color:#A9B6C6}
@media (max-width:1024px){
  .cd-cols{gap:0 var(--s4);padding-right:0}
  .cd-bar{grid-template-columns:1fr 1fr 1fr}
  .cd-bar .flag{display:none}
  .cd-col h3{font-size:1.1rem}
}
@media (max-width:768px){
  .cd-bar{display:none}
  .cd-cols{grid-template-columns:1fr;gap:var(--s5)}
  .cd-col .when{position:static;width:auto;height:auto;overflow:visible;clip:auto;display:block;padding-bottom:10px;margin-bottom:12px;background:linear-gradient(90deg,var(--teal),var(--blue)) left bottom/48px 3px no-repeat}
  .cd-col h3{font-size:1.15rem;margin-bottom:var(--s2)}
  .cd-after{align-items:flex-start}
  .cd-after .dash{width:100%;margin-bottom:4px}
}
'''
open("assets/style.css", "a", encoding="utf-8").write(CSS)
print("countdown applied")
