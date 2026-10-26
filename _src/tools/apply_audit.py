"""One-off: audit items 1,3,4,5,6,8,12,13,14. Layout and system only; page copy unchanged."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
def rw(p, fn):
    s = open(p, encoding="utf-8").read(); n = fn(s); assert n != s, p; open(p, "w", encoding="utf-8").write(n)

# 3. short sub-nav labels: build.py maps long eyebrow text to a short nav label
SHORT = {
 "Why IPO communications discipline matters": "Why it matters", "When to bring Aegis in": "Timing",
 "For principal advisers and underwriters": "Advisers", "Aegis roadmap": "Roadmap", "IPO countdown": "Countdown",
 "Commercial scope": "Scope", "Investment community strategy": "Investors", "Digital amplification": "Digital",
 "Why Aegis for your IPO": "Why Aegis", "Established PLC": "Established PLC", "Integrated IR + PR engagement model": "The model",
 "Risk-tier disclosure gate": "Disclosure gate", "Disclosure and information control": "Information control",
 "Corporate exercise communications": "Corporate exercises", "When something goes wrong": "Crisis", "Annual obligations": "Annual cycle",
 "Client-Aegis closeness": "Working together", "Newly listed": "Newly listed", "The quarterly rhythm": "Quarterly rhythm",
 "The first twelve months": "First 12 months", "What the IR mandate covers": "What we do", "IR framework": "Framework",
 "IR process": "Process", "For investors, analysts and media": "Investor access", "Core functions": "What we do",
 "PR framework": "Framework", "PR process": "Process", "Media monitoring and sentiment analysis": "Monitoring", "For media": "Media desk",
}
# 1. sections that collapse into accordions (secondary detail), by eyebrow text
COLLAPSE = {"Commercial scope", "Investment community strategy", "Digital amplification", "Disclosure and information control",
            "Annual obligations", "Client-Aegis closeness", "IR framework", "IR process", "PR framework", "PR process",
            "Media monitoring and sentiment analysis", "The first twelve months"}

def bld(s):
    s = s.replace('import os, re, datetime, html, json, time', 'import os, re, datetime, html, json, time\nSHORT = ' + repr(SHORT) + '\nCOLLAPSE = ' + repr(COLLAPSE))
    # short labels in subnav
    s = s.replace('''    links = "".join(f'<a href="#{sid}">{html.escape(label)}</a>' for label, sid in entries)''',
                  '''    links = "".join(f'<a href="#{sid}">{html.escape(SHORT.get(label, label))}</a>' for label, sid in entries)''')
    # accordion: wrap body of collapsible sections (everything after the section-head) in <details>
    s = s.replace('''        entries.append((label, sid))
        return tag + inner + "</section>"''',
'''        entries.append((label, sid))
        if label in COLLAPSE and len(entries) >= 1:
            # keep the section head visible; fold the rest behind a toggle
            m2 = re.search(r'(<div class="section-head reveal">.*?</div>\\n)', inner, flags=re.S)
            if m2:
                head_end = m2.end()
                inner = inner[:head_end] + '<details class="fold"><summary><span>Show details</span></summary><div class="fold-body">' + inner[head_end:]
                inner = re.sub(r'(\\s*</div>\\s*)$', r'</div></details>\\1', inner, count=1)
                tag = tag[:-1] + ' data-fold>'
        return tag + inner + "</section>"''')
    # 4. desktop side CTA on long pages (where subnav exists)
    s = s.replace('''{header(rel)}
{subnav}''', '''{header(rel)}
{subnav}
{'<aside class="side-cta" aria-label="Contact"><a class="btn btn-primary sm" href="' + rel + 'contact.html">Contact us</a><a class="side-tel" href="tel:+60350231848">+603 5023 1848</a></aside>' if subnav else ''}''')
    return s
rw("_src/build.py", bld)

# 8. one generic button label: "Talk to Aegis", "Get in touch", "Start a conversation" -> "Contact us"; specific labels stay
def unify(s):
    for old in ["Talk to Aegis", "Get in touch", "Start a conversation"]:
        s = s.replace(f'>{old}</a>', '>Contact us</a>')
    return s
for f in os.listdir("_src/pages"):
    p = os.path.join("_src/pages", f); t = open(p, encoding="utf-8").read(); n = unify(t)
    if n != t: open(p, "w", encoding="utf-8").write(n)

# 14. neutral first option on the contact form
rw("_src/pages/contact.html", lambda s: s.replace('<select id="status" name="status">\n            <option>Pre-IPO / planning to list</option>',
   '<select id="status" name="status">\n            <option value="" selected disabled>Please select</option>\n            <option>Pre-IPO / planning to list</option>'))

CSS = r'''
/* ---- Audit: folds, side CTA, tablet fixes ---- */
.fold{margin-top:calc(var(--s6) * -1 + var(--s3))}
.fold>summary{list-style:none;cursor:pointer;display:inline-flex;align-items:center;gap:10px;font-weight:600;font-size:.92rem;color:var(--blue-deep);padding:10px 0;user-select:none}
.fold>summary::-webkit-details-marker{display:none}
.fold>summary::after{content:"";width:8px;height:8px;border-right:2px solid currentColor;border-bottom:2px solid currentColor;transform:rotate(45deg) translateY(-2px);transition:transform .2s}
.fold[open]>summary::after{transform:rotate(-135deg) translateY(-2px)}
.fold[open]>summary span::before{content:"Hide details";}
.fold[open]>summary span{font-size:0}
.fold[open]>summary span::before{font-size:.92rem}
.fold-body{padding-top:var(--s4)}
.dark .fold>summary{color:var(--teal-bright)}
.side-cta{display:none}
@media (min-width:1280px){
  .side-cta{display:flex;flex-direction:column;gap:8px;position:fixed;right:20px;top:50%;transform:translateY(-50%);z-index:45;background:var(--white);border:1px solid var(--line-soft);border-radius:var(--radius-lg);padding:12px;box-shadow:var(--shadow)}
  .side-cta .btn{justify-content:center}
  .side-tel{font-size:.8rem;color:var(--slate);text-align:center}
}
@media (max-width:1024px){
  .stats .container{grid-template-columns:1fr 1fr}
  .stat{padding:var(--s4) var(--s3)}
  .stat:nth-child(odd){border-left:0;padding-left:0}
  .hero .container{padding-top:var(--s7);padding-bottom:var(--s7);gap:var(--s5)}
  .hero-panel{padding:var(--s4)}
}
'''
open("assets/style.css", "a", encoding="utf-8").write(CSS)

JS = r'''
// ---- Audit: Escape closes the mobile menu; open a fold when its sub-nav link is used ----
(function () {
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var nav = document.querySelector('.nav.open'), t = document.querySelector('.nav-toggle');
    if (nav && t) { t.click(); t.focus(); }
  });
  function openFoldFor(hash) {
    if (!hash) return;
    var sec = document.getElementById(hash.slice(1)); if (!sec) return;
    var d = sec.querySelector('details.fold'); if (d) d.open = true;
  }
  document.querySelectorAll('.subnav a[href^="#"]').forEach(function (a) { a.addEventListener('click', function () { openFoldFor(a.getAttribute('href')); }); });
  openFoldFor(location.hash);
  window.addEventListener('hashchange', function () { openFoldFor(location.hash); });
  window.addEventListener('beforeprint', function () { document.querySelectorAll('details.fold').forEach(function (d) { d.open = true; }); });
})();
'''
open("assets/site.js", "a", encoding="utf-8").write(JS)
print("audit edits ok")
