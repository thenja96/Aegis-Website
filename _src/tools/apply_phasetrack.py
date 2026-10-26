"""One-off: 'When to bring Aegis in' A/B/C as a phase track (option 1, no label). Copy unchanged."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
p = "_src/pages/services-ipo-communications.html"
s = open(p, encoding="utf-8").read()
a = s.rfind('<section', 0, s.index('When to bring Aegis in'))
i = s.index('<div class="steps reveal">', a)
j = s.index('</div>\n', s.index('<span class="n">C</span>', i)) + len('</div>\n')
j = s.index('</div>', j) + len('</div>')  # closing of .steps
block = s[i:j]
steps = re.findall(r'<div class="step"><span class="n">([ABC])</span><h3>([^<]+)</h3><p>([^<]+)</p></div>', block)
assert len(steps) == 3
segs = "".join(f'<div class="pt-step pt-{l.lower()}"><span class="pt-l">{l}</span><h3>{t}</h3><p>{d}</p></div>' for l, t, d in steps)
new = f'<div class="phase-track reveal"><div class="pt-line" aria-hidden="true"></div><div class="pt-steps">{segs}</div></div>'
s = s[:i] + new + s[j:]
open(p, "w", encoding="utf-8").write(s)
CSS = r'''
/* ---- IPO 'When to bring Aegis in' phase track: grey through A and B (private), gradient for C (public) ---- */
.phase-track{margin-top:var(--s2)}
.pt-line{position:relative;height:16px;margin-bottom:var(--s4)}
.pt-line::before{content:"";position:absolute;left:0;right:0;top:6px;height:3px;border-radius:2px;background:linear-gradient(90deg,var(--line) 0,var(--line) 66.66%,var(--teal) 66.66%,var(--blue) 100%)}
.pt-line::after{content:"";position:absolute;left:0;top:0;width:15px;height:15px;border-radius:50%;background:var(--teal);box-shadow:0 0 0 5px rgba(26,177,145,.18)}
.pt-steps{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--s6)}
.pt-step{border-left:1px solid var(--line);padding-left:var(--s4)}
.pt-step.pt-a{border-left:2px solid var(--teal)}
.pt-l{display:block;font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;font-size:.76rem;letter-spacing:.08em;color:var(--teal-text);margin-bottom:10px}
.pt-step h3{font-size:1.2rem;font-weight:400;margin:0 0 8px}
.pt-step p{margin:0;color:var(--slate);font-size:.95rem;line-height:1.6}
@media (max-width:1024px){.pt-steps{gap:var(--s4)}.pt-step{padding-left:var(--s3)}}
@media (max-width:768px){
  .pt-line{display:none}
  .pt-steps{grid-template-columns:1fr;gap:var(--s4)}
  .pt-step{border-left:2px solid var(--line);padding-left:18px}
  .pt-step.pt-a{border-left-color:var(--teal)}
  .pt-step.pt-c{border-image:linear-gradient(var(--teal),var(--blue)) 1}
}
'''
open("assets/style.css", "a", encoding="utf-8").write(CSS)
print("phase track applied")
