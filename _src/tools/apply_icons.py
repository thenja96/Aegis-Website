"""One-off: icon markup (no copy changes) and About submenu."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
def rw(p, fn):
    s = open(p, encoding="utf-8").read(); n = fn(s); assert n != s, p; open(p, "w", encoding="utf-8").write(n)
def ico(name, cls="ico"):
    return f'<svg class="{cls}" aria-hidden="true"><use href="#i-{name}"/></svg>'

SECTORS = [("Technology, Software &amp; Cybersecurity", "tech"), ("Property, Construction &amp; Building Materials", "property"),
           ("Energy, Oil &amp; Gas &amp; Marine", "energy"), ("Consumer, Retail &amp; Appliances", "consumer"),
           ("Fintech &amp; Business Services", "fintech"), ("Engineering, Industrial &amp; Renewable Energy", "engineering")]

# home: sector tags -> icon tiles; service cards, why-Aegis steps and stats get icons
def home(s):
    tiles = "".join(f'<div class="sector">{ico(i)}<span>{t}</span></div>' for t, i in SECTORS)
    s = re.sub(r'<div class="tags">.*?</div>', f'<div class="sectors">{tiles}</div>', s, count=1, flags=re.S)
    for href, i in [("services/investor-relations.html", "ir"), ("services/public-relations.html", "pr"), ("services/ipo-communications.html", "ipo"),
                    ("services/events.html", "events"), ("services/creative-digital.html", "creative"), ("services/creative-digital.html#digital", "digital")]:
        s = re.sub(rf'(<a class="card link reveal"[^>]*href="{re.escape(href)}">)<span class="num">', rf'\1{ico(i, "ico ico-card")}<span class="num">', s, count=1)
    for n, i in [("01", "experience"), ("02", "direct"), ("03", "integrated"), ("04", "outreach"), ("05", "timing")]:
        s = s.replace(f'<div class="step"><span class="n">{n}</span>', f'<div class="step">{ico(i, "ico ico-step")}<span class="n">{n}</span>', 1)
    for key, i in [("<b>17+</b>", "years"), ("<b>30+</b>", "companies"), ("<b>RM100m to RM5bn</b>", "marketcap"), ("<b>Local + regional</b>", "regional")]:
        s = s.replace(f'<div class="stat">{key}', f'<div class="stat">{ico(i, "ico ico-stat")}{key}', 1)
    # hero panel stage icons
    s = s.replace('<li><a href="services/ipo-communications.html">Preparing to list</a>', f'<li>{ico("ipo", "ico ico-panel")}<a href="services/ipo-communications.html">Preparing to list</a>', 1)
    s = s.replace('<li><a href="services/investor-relations.html">Newly listed</a>', f'<li>{ico("ir", "ico ico-panel")}<a href="services/investor-relations.html">Newly listed</a>', 1)
    s = s.replace('<li><a href="approach.html">Established PLC</a>', f'<li>{ico("credible", "ico ico-panel")}<a href="approach.html">Established PLC</a>', 1)
    return s
rw("_src/pages/index.html", home)

# about: dark sector cards -> icon tiles
def about(s):
    for t, i in SECTORS:
        s = s.replace(f'<div class="card on-dark"><h3>{t}</h3></div>', f'<div class="card on-dark sector">{ico(i)}<h3>{t}</h3></div>', 1)
    return s
rw("_src/pages/about.html", about)

# ipo: what companies need
def ipo(s):
    for t, i in [("Be understood", "understood"), ("Be visible", "visible"), ("Be credible", "credible"), ("Be ready", "ready")]:
        s = s.replace(f'<div class="card"><h4>{t}</h4>', f'<div class="card has-ico">{ico(i, "ico ico-card")}<h4>{t}</h4>', 1)
    return s
rw("_src/pages/services-ipo-communications.html", ipo)

# build: About submenu, sprite injection
def bld(s):
    s = s.replace('''    ("Our Approach", "approach.html", None),
    ("Track Record", "track-record.html", None),
    ("About", "about.html", None),
]''', '''    ("About", None, ABOUT),
]''')
    s = s.replace('NAV = [', '''ABOUT = [
    ("About Aegis", "about.html"),
    ("Our People", "about.html#our-people"),
    ("Our Approach", "approach.html"),
    ("Track Record", "track-record.html"),
]
NAV = [''')
    s = s.replace('''        if sub:
            links = "".join(f'<li><a href="{rel}{h}">{l}</a></li>' for l, h in sub)
            items.append(f'<li class="has-sub"><a href="{rel}services/investor-relations.html" aria-haspopup="true">{label}</a>'
                         f'<ul class="sub"><li class="sub-label">What we do</li>{links}</ul></li>')''',
'''        if sub:
            links = "".join(f'<li><a href="{rel}{h}">{l}</a></li>' for l, h in sub)
            top = "services/investor-relations.html" if label == "Services" else "about.html"
            heading = "What we do" if label == "Services" else "Who we are"
            items.append(f'<li class="has-sub"><a href="{rel}{top}" aria-haspopup="true">{label}</a>'
                         f'<ul class="sub"><li class="sub-label">{heading}</li>{links}</ul></li>')''')
    s = s.replace('SPRITE_PLACEHOLDER', '')
    s = s.replace('def wrap(meta, body, rel):', 'SPRITE = open(os.path.join(ROOT, "_src", "icons.svg"), encoding="utf-8").read()\n\ndef wrap(meta, body, rel):')
    s = s.replace('{header(rel)}\n{subnav}', '{SPRITE}\n{header(rel)}\n{subnav}')
    return s
rw("_src/build.py", bld)

CSS = r'''
/* ---- Icons ---- */
.ico{width:24px;height:24px;stroke:currentColor;fill:none;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round;flex:none}
.sectors{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--s3);margin-top:var(--s4)}
.sector{display:flex;align-items:center;gap:14px;padding:18px 20px;border:1px solid var(--line-soft);border-radius:var(--radius-lg);background:var(--white);color:var(--navy);font-weight:500;font-size:.95rem;line-height:1.3;transition:border-color .2s,transform .2s}
.sector:hover{border-color:rgba(37,119,188,.35);transform:translateY(-2px)}
.sector .ico{width:34px;height:34px;color:var(--teal-text);padding:6px;border-radius:10px;background:var(--tint)}
.card.on-dark.sector{display:flex;align-items:center;gap:14px;padding:22px}
.card.on-dark.sector .ico{color:var(--teal-bright);background:rgba(255,255,255,.08)}
.card.on-dark.sector h3{margin:0;font-size:1.15rem}
.ico-card{width:40px;height:40px;color:var(--teal-text);background:var(--tint);padding:9px;border-radius:12px;margin-bottom:var(--s3)}
.card.link .ico-card{transition:background .2s,color .2s}
.card.link:hover .ico-card{background:var(--navy);color:var(--white)}
.ico-step{position:absolute;right:var(--s4);top:var(--s4);width:28px;height:28px;color:var(--blue);opacity:.75}
.ico-stat{width:26px;height:26px;color:var(--teal-text);margin-bottom:10px}
.ico-panel{width:20px;height:20px;color:var(--teal-bright);float:left;margin:2px 10px 0 0}
.hero-panel li a::before{display:none}
.hero-panel li small{padding-left:30px}
@media (max-width:768px){.sectors{grid-template-columns:1fr 1fr}.sector{padding:14px;font-size:.88rem;flex-direction:column;align-items:flex-start;gap:10px}.ico-step{right:0;top:var(--s4)}}
@media (max-width:480px){.sectors{grid-template-columns:1fr}.sector{flex-direction:row}}
'''
open("assets/style.css", "a", encoding="utf-8").write(CSS)
print("icons applied")
