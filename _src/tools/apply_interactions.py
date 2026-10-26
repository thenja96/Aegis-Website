"""One-off: interaction options S3 S4 B2 A2 A3 A4 V4 V5. Markup hooks, CSS and JS. No copy changes."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)

def rw(p, fn):
    s = open(p, encoding="utf-8").read(); n = fn(s); assert n != s, p; open(p, "w", encoding="utf-8").write(n)

# diagrams: pathLength so stroke-dash animation works
def dg(s):
    s = s.replace("""return f'<path class="d-arrow" d="M{x1} {y1} L{x2} {y2}"/>'""", """return f'<path class="d-arrow" pathLength="1" d="M{x1} {y1} L{x2} {y2}"/>'""")
    s = s.replace("""p.append(f'<path class="d-loop" d=""", """p.append(f'<path class="d-loop" pathLength="1" d=""")
    s = s.replace("""p.append('<path class="d-loop" d="M925 200""", """p.append('<path class="d-loop" pathLength="1" d="M925 200""")
    s = s.replace("""'<path d="M40 110 L760 110" stroke="#00AE91" stroke-width="3"/>'""", """'<path class="d-line" pathLength="1" d="M40 110 L760 110" stroke="#00AE91" stroke-width="3"/>'""")
    return s
rw("_src/tools/diagrams.py", dg)

# home: audience tabs and data-aud hooks
def home(s):
    aud = {"services/investor-relations.html": "new plc", "services/public-relations.html": "new plc", "services/ipo-communications.html": "ipo",
           "services/events.html": "ipo plc", "services/creative-digital.html": "ipo new plc", "services/creative-digital.html#digital": "new plc"}
    for href, a in aud.items():
        s = s.replace(f'<a class="card link reveal" href="{href}">', f'<a class="card link reveal" data-aud="{a}" href="{href}">', 1)
    ipo_logos = {"bus-cap", "autocount", "kinergy", "northern-solar"}
    s = re.sub(r'<div><img src="assets/clients/([a-z0-9-]+)\.png"',
               lambda m: f'<div data-aud="{"ipo" if m.group(1) in ipo_logos else "new plc"}"><img src="assets/clients/{m.group(1)}.png"', s)
    tabs = '''<div class="aud-tabs" role="tablist" aria-label="Filter by company stage">
      <button type="button" role="tab" aria-selected="true" data-filter="all">All</button>
      <button type="button" role="tab" aria-selected="false" data-filter="ipo"><i class="dot aud-ipo"></i>Preparing to list</button>
      <button type="button" role="tab" aria-selected="false" data-filter="new"><i class="dot aud-new"></i>Newly listed</button>
      <button type="button" role="tab" aria-selected="false" data-filter="plc"><i class="dot aud-plc"></i>Established PLC</button>
    </div>
    <div class="grid grid-3">'''
    return s.replace('<div class="grid grid-3">', tabs, 1)
rw("_src/pages/index.html", home)

rw("_src/pages/approach.html", lambda s: s.replace('<div class="table-wrap reveal">', '<div class="table-wrap reveal tier-wrap">', 1))

def bld(s):
    s = s.replace('<body>\n{header(rel)}', '<body{" class=" + chr(34) + "home" + chr(34) if path == "index.html" else ""}>\n{header(rel)}')
    s = s.replace('    <ul class="nav" id="nav">{"".join(items)}</ul>\n  </div>\n</header>', '    <ul class="nav" id="nav">{"".join(items)}</ul>\n  </div>\n  <div class="progress" aria-hidden="true"></div>\n</header>')
    return s
rw("_src/build.py", bld)

CSS = r'''
/* ---- Interaction options S3 S4 B2 A2 A3 A4 V4 V5 ---- */
@media (min-width:1025px){
  body.home{scroll-snap-type:y proximity}
  body.home main>section{scroll-snap-align:start;scroll-margin-top:var(--header-h)}
  body.home .stats{scroll-snap-align:none}
}
.progress{position:absolute;left:0;bottom:-1px;height:3px;width:0;background:var(--grad);transition:width .1s linear}
.btn.magnet{transition:transform .25s cubic-bezier(.2,.7,.2,1),box-shadow .18s ease,background .18s ease,color .18s ease;will-change:transform}
.diagram .d-arrow,.diagram .d-loop,.diagram .d-line{stroke-dasharray:1;stroke-dashoffset:1}
.diagram .d-box,.diagram .d-box-accent,.diagram .d-pill,.diagram text,.diagram circle{opacity:0;transition:opacity .5s ease}
.diagram.in .d-box,.diagram.in .d-box-accent,.diagram.in .d-pill,.diagram.in text,.diagram.in circle{opacity:1}
.diagram.in .d-arrow,.diagram.in .d-line{animation:draw .9s cubic-bezier(.2,.7,.2,1) .45s forwards}
.diagram.in .d-loop{animation:draw 1.2s ease 1.2s forwards}
.diagram.in .d-arrow:nth-of-type(2){animation-delay:.6s}.diagram.in .d-arrow:nth-of-type(3){animation-delay:.75s}
.diagram.in .d-arrow:nth-of-type(4){animation-delay:.9s}.diagram.in .d-arrow:nth-of-type(5){animation-delay:1.05s}.diagram.in .d-arrow:nth-of-type(n+6){animation-delay:1.2s}
.diagram .d-arrow,.diagram .d-loop{marker-end:none}
.diagram .d-arrow.drawn{marker-end:url(#arr)}.diagram .d-loop.drawn{marker-end:url(#arr-blue)}
@keyframes draw{to{stroke-dashoffset:0}}
.hero h1 .w{display:inline-block;opacity:0;transform:translateY(.35em);animation:wordin .7s cubic-bezier(.2,.7,.2,1) forwards}
@keyframes wordin{to{opacity:1;transform:none}}
.step .n{color:var(--line);transition:color .6s ease}
.steps.reveal.in .step .n{color:var(--blue)}
.dark .steps.reveal.in .step .n{color:var(--teal-bright)}
.steps.reveal.in .step:nth-child(2) .n{transition-delay:.15s}.steps.reveal.in .step:nth-child(3) .n{transition-delay:.3s}
.steps.reveal.in .step:nth-child(4) .n{transition-delay:.45s}.steps.reveal.in .step:nth-child(5) .n{transition-delay:.6s}.steps.reveal.in .step:nth-child(n+6) .n{transition-delay:.75s}
.tier-tabs{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:var(--s3)}
.tier-tabs button,.aud-tabs button{font:inherit;font-size:.86rem;font-weight:600;padding:10px 16px;border-radius:999px;border:1.5px solid var(--line);background:var(--white);color:var(--slate);cursor:pointer;transition:background .15s,color .15s,border-color .15s;display:inline-flex;align-items:center;gap:8px}
.tier-tabs button:hover,.aud-tabs button:hover{border-color:var(--navy);color:var(--navy)}
.tier-tabs button[aria-selected="true"],.aud-tabs button[aria-selected="true"]{background:var(--navy);color:var(--white);border-color:var(--navy)}
.tier-wrap[data-tier="1"] .table th:nth-child(2),.tier-wrap[data-tier="1"] .table td:nth-child(2),
.tier-wrap[data-tier="2"] .table th:nth-child(3),.tier-wrap[data-tier="2"] .table td:nth-child(3),
.tier-wrap[data-tier="3"] .table th:nth-child(4),.tier-wrap[data-tier="3"] .table td:nth-child(4){background:var(--tint)}
@media (max-width:768px){
  .tier-wrap[data-tier="1"] .table td:nth-child(3),.tier-wrap[data-tier="1"] .table td:nth-child(4),
  .tier-wrap[data-tier="2"] .table td:nth-child(2),.tier-wrap[data-tier="2"] .table td:nth-child(4),
  .tier-wrap[data-tier="3"] .table td:nth-child(2),.tier-wrap[data-tier="3"] .table td:nth-child(3){display:none}
  .tier-wrap[data-tier] .table.stack td::before{content:none}
  .tier-wrap[data-tier] .table.stack td{padding:6px 0 0;border:0}
}
.aud-tabs{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 var(--s4)}
.aud-tabs .dot{width:9px;height:9px;border-radius:50%;background:var(--teal);display:inline-block}
.aud-tabs .aud-ipo{background:var(--aud-ipo)}.aud-tabs .aud-new{background:var(--aud-new)}.aud-tabs .aud-plc{background:var(--aud-plc)}
[data-aud].dim{opacity:.28;filter:grayscale(1);transform:none !important;box-shadow:none !important;transition:opacity .3s ease}
@media (prefers-reduced-motion:reduce){
  .hero h1 .w{opacity:1;transform:none;animation:none}
  .diagram .d-arrow,.diagram .d-loop,.diagram .d-line{stroke-dashoffset:0;animation:none}
  .diagram .d-box,.diagram .d-box-accent,.diagram .d-pill,.diagram text,.diagram circle{opacity:1}
  .diagram .d-arrow{marker-end:url(#arr) !important}.diagram .d-loop{marker-end:url(#arr-blue) !important}
  body.home{scroll-snap-type:none}
  .btn.magnet{transition:none}
}
'''
JS = r'''
// ---- Interaction options S4 B2 A2 A3 V4 V5 ----
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  // S4 reading progress bar
  var bar = document.querySelector('.progress');
  if (bar) {
    var upd = function () {
      var h = document.documentElement.scrollHeight - innerHeight;
      bar.style.width = (h > 0 ? Math.min(100, scrollY / h * 100) : 0) + '%';
    };
    addEventListener('scroll', upd, { passive: true }); addEventListener('resize', upd); upd();
  }

  // B2 magnetic buttons (desktop pointers only)
  if (fine && !reduce) {
    document.querySelectorAll('.btn').forEach(function (b) {
      b.classList.add('magnet');
      b.addEventListener('mousemove', function (e) {
        var r = b.getBoundingClientRect(), x = e.clientX - r.left - r.width / 2, y = e.clientY - r.top - r.height / 2;
        b.style.transform = 'translate(' + x * 0.18 + 'px,' + y * 0.28 + 'px)';
      });
      b.addEventListener('mouseleave', function () { b.style.transform = ''; });
    });
  }

  // A2 arrowheads appear once each line has drawn
  document.querySelectorAll('.diagram .d-arrow, .diagram .d-loop').forEach(function (p) {
    p.addEventListener('animationend', function () { p.classList.add('drawn'); });
  });

  // A3 hero headline word reveal (text unchanged, split into spans)
  var h1 = document.querySelector('.hero h1');
  if (h1 && !reduce && !h1.querySelector('*')) {
    var words = h1.textContent.split(/(\s+)/), i = 0;
    h1.textContent = '';
    words.forEach(function (w) {
      if (!w) return;
      if (/^\s+$/.test(w)) { h1.appendChild(document.createTextNode(' ')); return; }
      var s = document.createElement('span'); s.className = 'w'; s.textContent = w; s.style.animationDelay = (0.08 * i++) + 's'; h1.appendChild(s);
    });
  }

  // V4 risk-tier selector, labels taken from the table headings
  var tw = document.querySelector('.tier-wrap');
  if (tw) {
    var ths = Array.prototype.slice.call(tw.querySelectorAll('thead th')).slice(1);
    var tabs = document.createElement('div'); tabs.className = 'tier-tabs'; tabs.setAttribute('role', 'tablist');
    var all = document.createElement('button'); all.type = 'button'; all.textContent = 'All tiers'; all.setAttribute('role', 'tab'); all.setAttribute('aria-selected', 'true'); tabs.appendChild(all);
    ths.forEach(function (th, idx) {
      var b = document.createElement('button'); b.type = 'button'; b.textContent = th.textContent; b.setAttribute('role', 'tab'); b.setAttribute('aria-selected', 'false'); b.dataset.tier = String(idx + 1); tabs.appendChild(b);
    });
    tabs.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      tabs.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-selected', x === b ? 'true' : 'false'); });
      if (b.dataset.tier) tw.dataset.tier = b.dataset.tier; else delete tw.dataset.tier;
    });
    tw.parentNode.insertBefore(tabs, tw);
    if (window.matchMedia('(max-width: 768px)').matches) tabs.querySelector('[data-tier="1"]').click();
  }

  // V5 audience tabs on the home page
  var at = document.querySelector('.aud-tabs');
  if (at) {
    at.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      var f = b.dataset.filter;
      at.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-selected', x === b ? 'true' : 'false'); });
      document.querySelectorAll('[data-aud]').forEach(function (el) {
        el.classList.toggle('dim', f !== 'all' && el.dataset.aud.split(' ').indexOf(f) === -1);
      });
    });
  }
})();
'''
open("assets/style.css", "a", encoding="utf-8").write(CSS)
open("assets/site.js", "a", encoding="utf-8").write(JS)
print("interactions applied")
