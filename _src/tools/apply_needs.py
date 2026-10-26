"""One-off: IPO 'What companies need / What can go wrong' as a split panel (option C). Copy unchanged."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
p = "_src/pages/services-ipo-communications.html"
s = open(p, encoding="utf-8").read()
a = s.index('Why IPO communications discipline matters'); a = s.rfind('<section', 0, a); b = s.index('</section>', a) + 10
sec = s[a:b]
need = re.findall(r'<div class="card has-ico">(?:<svg.*?</svg>)?<h4>([^<]+)</h4><p>([^<]+)</p></div>', sec, flags=re.S)
w0 = sec.index("What can go wrong")
wrong = re.findall(r'<div class="card"><h4>([^<]+)</h4><p>([^<]+)</p></div>', sec[w0:])
assert len(need) == 4 and len(wrong) == 4
L = "".join(f'<li><b>{t}</b><p>{d}</p></li>' for t, d in need)
R = "".join(f'<li><b>{t}</b><p>{d}</p></li>' for t, d in wrong)
new = f'''<div class="needs-risks reveal">
      <div class="nr-need"><h3 class="nr-tag">What companies need</h3><ul>{L}</ul></div>
      <div class="nr-risk"><h3 class="nr-tag">What can go wrong</h3><ul>{R}</ul></div>
    </div>'''
s0 = sec.index('<div class="split">'); s1 = sec.rindex('</div>\n  </div>\n</section>')
sec = sec[:s0] + new + "\n  " + sec[s1 + len('</div>\n'):]
s = s[:a] + sec + s[b:]
open(p, "w", encoding="utf-8").write(s)

CSS = r'''
/* ---- IPO needs / risks split panel ---- */
.needs-risks{display:grid;grid-template-columns:1fr 1fr;border:1px solid var(--line);border-radius:var(--radius-lg);overflow:hidden}
.nr-need,.nr-risk{padding:var(--s5) var(--s6) var(--s5)}
.nr-risk{background:var(--navy)}
.nr-tag{font:600 .72rem var(--font-body);letter-spacing:.18em;text-transform:uppercase;color:var(--teal-text);margin:0 0 var(--s3)}
.nr-risk .nr-tag{color:#F2A08B}
.needs-risks ul{list-style:none;margin:0;padding:0}
.needs-risks li{padding:var(--s3) 0;border-top:1px solid var(--line)}
.needs-risks li::before{display:none}
.needs-risks b{display:block;font-weight:600;color:var(--navy);font-size:1rem}
.needs-risks p{margin:4px 0 0;color:var(--slate);font-size:.95rem;line-height:1.55}
.nr-risk li{border-top-color:rgba(255,255,255,.12)}
.nr-risk b{color:var(--white)}
.nr-risk p{color:#A9B6C6}
@media (max-width:900px){
  .needs-risks{grid-template-columns:1fr}
  .nr-need,.nr-risk{padding:var(--s4) var(--s4) var(--s3)}
}
@media (max-width:768px){
  .needs-risks{margin:0 calc(var(--s4) * -1);border-left:0;border-right:0;border-radius:0}
  .nr-need,.nr-risk{padding:var(--s4) var(--s4) var(--s2)}
  .needs-risks li{padding:14px 0}
  .needs-risks b{font-size:.98rem}
  .needs-risks p{font-size:.93rem}
}
'''
open("assets/style.css", "a", encoding="utf-8").write(CSS)
print("needs/risks applied")
