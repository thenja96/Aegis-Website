"""One-off: replace the IPO roadmap diagram + five-step rail + retainer card with one interactive stepper.
Copy is reused verbatim from the existing rail and card."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)

p = "_src/pages/services-ipo-communications.html"
s = open(p, encoding="utf-8").read()
a = s.index('<span class="eyebrow">Aegis roadmap</span>'); a = s.rfind('<section', 0, a); b = s.index('</section>', a) + 10
sec = s[a:b]

steps = re.findall(r'<div class="step"><span class="n">(\d+)</span><h3>([^<]+)</h3><p>([^<]+)</p></div>', sec)
assert len(steps) == 5, steps
card = re.search(r'<span class="num">([^<]+)</span>\s*<h3>([^<]+)</h3>\s*<p>([^<]+)</p>', sec)
num6, h6, p6 = card.groups()
items = steps + [("06", h6, p6)]
short = [t for _, t, _ in steps] + ["Retainer programme"]

tabs = "".join(
    f'<li><button type="button" role="tab" id="ms-tab-{i}" aria-controls="ms-panel-{i}" aria-selected="{"true" if i == 1 else "false"}" tabindex="{0 if i == 1 else -1}"'
    f'{" class=" + chr(34) + "is-retainer" + chr(34) if i == 6 else ""}><span class="dot">{n}</span><span class="lbl">{short[i-1]}</span></button></li>'
    for i, (n, t, d) in enumerate(items, 1))
panels = "".join(
    f'<div class="step{" is-retainer" if i == 6 else ""}" role="tabpanel" id="ms-panel-{i}" aria-labelledby="ms-tab-{i}">'
    f'<span class="n">{num6 if i == 6 else n}</span><h3>{t}</h3><p>{d}</p></div>'
    for i, (n, t, d) in enumerate(items, 1))

head = re.search(r'(<div class="section-head reveal">.*?</div>)', sec, flags=re.S).group(1)
new = f'''<section class="section">
  <div class="container">
    {head}
    <div class="stepper reveal" data-stepper>
      <ol class="stepper-track" role="tablist" aria-label="IPO roadmap milestones">{tabs}</ol>
      <div class="steps stepper-panels">{panels}</div>
    </div>
  </div>
</section>'''
s = s[:a] + new + s[b:]
open(p, "w", encoding="utf-8").write(s)

# stop diagrams.py re-inserting the old roadmap SVG
d = "_src/tools/diagrams.py"; t = open(d, encoding="utf-8").read()
t = t.replace('put("services-ipo-communications.html", r\'(<span class="eyebrow">Aegis roadmap</span>.*?</div>\\n)\', timeline())\n', '')
open(d, "w", encoding="utf-8").write(t)

CSS = r'''
/* ---- IPO roadmap stepper: one track, one description panel ---- */
.stepper-track{list-style:none;margin:0 0 var(--s5);padding:0;display:grid;grid-template-columns:repeat(5,1fr) 1.25fr;position:relative}
.stepper-track::before{content:"";position:absolute;left:0;right:calc(100% / 6.25 * 1.25);top:19px;height:2px;background:linear-gradient(90deg,var(--teal),var(--blue))}
.stepper-track li:last-child::before{content:"";position:absolute;left:-2%;width:30%;top:19px;height:0;border-top:2px dashed var(--blue)}
.stepper-track li{position:relative}
.stepper-track button{all:unset;cursor:pointer;display:flex;flex-direction:column;align-items:flex-start;gap:12px;width:100%;box-sizing:border-box;padding-right:12px}
.stepper-track .dot{position:relative;z-index:1;width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:var(--white);border:2px solid var(--line);font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;font-size:.78rem;font-weight:500;color:var(--muted);transition:background .25s,border-color .25s,color .25s}
.stepper-track .lbl{font-family:var(--font-head);font-size:1.05rem;color:var(--muted);line-height:1.25;transition:color .25s}
.stepper-track button:hover .dot{border-color:var(--teal)}
.stepper-track button:hover .lbl{color:var(--navy)}
.stepper-track button[aria-selected="true"] .dot{background:var(--navy);border-color:var(--navy);color:var(--white)}
.stepper-track button[aria-selected="true"] .lbl{color:var(--navy)}
.stepper-track button.is-retainer[aria-selected="true"] .dot{background:var(--blue);border-color:var(--blue)}
.stepper-track button:focus-visible .dot{outline:3px solid var(--teal-bright);outline-offset:3px}
.stepper-panels{display:block;border:0 !important;padding:0 !important}
.stepper .stepper-panels .step{display:none;border:0;border-top:1px solid var(--line);padding:var(--s4) 0 0;max-width:680px}
.stepper .stepper-panels .step.is-active{display:block;animation:rise .45s cubic-bezier(.2,.7,.2,1) both}
.stepper .stepper-panels .step::before,.stepper .stepper-panels .step::after{display:none}
.stepper .stepper-panels .step .n{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;font-size:.74rem;letter-spacing:.08em;text-transform:uppercase;color:var(--teal-text);margin-bottom:10px}
.stepper .stepper-panels .step h3{font-size:1.5rem;font-weight:400;margin:0 0 8px}
.stepper .stepper-panels .step p{font-size:1.02rem;color:var(--slate)}
/* no JS: show every milestone */
.stepper:not(.js) .stepper-track{display:none}
.stepper:not(.js) .stepper-panels .step{display:block;margin-bottom:var(--s4)}
@media (max-width:768px){
  .stepper-track{display:none}
  .stepper .stepper-panels{padding-left:24px !important;position:relative}
  .stepper .stepper-panels .step{display:block !important;border:0;padding:0 0 28px !important;animation:none;max-width:none}
  .stepper .stepper-panels .step::before{display:block !important}
  .stepper .stepper-panels .step h3{font-size:1.15rem}
  .stepper .stepper-panels .step p{font-size:.95rem}
}
'''
open("assets/style.css", "a", encoding="utf-8").write(CSS)

JS = r'''
// ---- IPO roadmap stepper: hover (desktop) or click/keys select a milestone ----
(function () {
  document.querySelectorAll('[data-stepper]').forEach(function (root) {
    root.classList.add('js');
    var tabs = Array.prototype.slice.call(root.querySelectorAll('[role="tab"]'));
    var panels = Array.prototype.slice.call(root.querySelectorAll('[role="tabpanel"]'));
    var fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    function select(i, focus) {
      tabs.forEach(function (t, k) { var on = k === i; t.setAttribute('aria-selected', on ? 'true' : 'false'); t.tabIndex = on ? 0 : -1; });
      panels.forEach(function (p, k) { p.classList.toggle('is-active', k === i); });
      if (focus) tabs[i].focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(i); });
      if (fine) t.addEventListener('mouseenter', function () { select(i); });
      t.addEventListener('keydown', function (e) {
        var k = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
        if (k) { e.preventDefault(); select((i + k + tabs.length) % tabs.length, true); }
        if (e.key === 'Home') { e.preventDefault(); select(0, true); }
        if (e.key === 'End') { e.preventDefault(); select(tabs.length - 1, true); }
      });
    });
    select(0);
  });
})();
'''
open("assets/site.js", "a", encoding="utf-8").write(JS)
print("stepper applied")
