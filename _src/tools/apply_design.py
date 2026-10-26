"""One-off: markup-only design changes to fragments (no copy changes).
Hero photo backgrounds, audience markers, stacked tier table, logo marquee, dark-band budget,
inline SVG diagrams built from existing page labels."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "_src", "pages")

def rw(name, fn):
    p = os.path.join(P, name); s = open(p, encoding="utf-8").read(); n = fn(s)
    assert n != s, name; open(p, "w", encoding="utf-8").write(n)

# 1. hero backgrounds (dimmed event photos) and audience markers
HERO = {
    "services-investor-relations.html": ("../assets/photos/ir-group-briefing.webp", '<span class="aud aud-new">Newly listed</span>'),
    "services-public-relations.html": ("../assets/photos/pr-brand-event.webp", None),
    "services-ipo-communications.html": ("../assets/photos/ipo-listing-ceremony.webp", '<span class="aud aud-ipo">Preparing to list</span>'),
    "services-events.html": ("../assets/photos/event-hall.webp", None),
    "services-creative-digital.html": ("../assets/photos/pr-media-briefing.webp", None),
    "approach.html": ("assets/photos/ir-boardroom-briefing.webp", '<span class="aud aud-plc">Established PLC</span>'),
    "track-record.html": ("assets/photos/ipo-prospectus-launch.webp", None),
    "about.html": ("assets/photos/event-guests.webp", None),
    "contact.html": ("assets/photos/ir-webinar.webp", None),
}
for name, (img, marker) in HERO.items():
    def f(s, img=img, marker=marker):
        s = s.replace('<section class="hero compact">', f'<section class="hero compact has-img" style="--hero-img:url({img})">', 1)
        if marker:
            s = re.sub(r'(<span class="eyebrow on-dark">[^<]*</span>)', r'\1' + marker, s, count=1)
        return s
    rw(name, f)

# 2. risk-tier table: stacked cards on phones
def table(s):
    s = s.replace('<table class="table">', '<table class="table stack">', 1)
    labels = ["", "Tier 1 · Standard", "Tier 2 · Controlled", "Tier 3 · Restricted"]
    def row(m):
        cells = re.findall(r"<td>(.*?)</td>", m.group(0), flags=re.S)
        return "<tr>" + "".join(f'<td data-label="{labels[i]}">{c}</td>' for i, c in enumerate(cells)) + "</tr>"
    return re.sub(r"<tr><td>.*?</tr>", row, s, flags=re.S)
rw("approach.html", table)

# 3. home: selected clients become a marquee (logos duplicated for the loop)
def marquee(s):
    m = re.search(r'<div class="logo-wall cols-3">(.*?)</div>\s*</div>', s, flags=re.S)
    logos = re.findall(r"<div><img[^>]+></div>", m.group(1))
    track = "".join(logos) * 2
    return s.replace(m.group(0), f'<div class="marquee" aria-label="Selected clients"><div class="marquee-track">{track}</div></div>', 1)
rw("index.html", marquee)

# 4. one dark band per page: IPO "Why Aegis" goes light
def ipo_dark(s):
    i = s.index('<span class="eyebrow on-dark">Why Aegis for your IPO</span>')
    a = s.rfind('<section class="section dark">', 0, i)
    return s[:a] + '<section class="section light">' + s[a + len('<section class="section dark">'):i] + '<span class="eyebrow">Why Aegis for your IPO</span>' + s[i + len('<span class="eyebrow on-dark">Why Aegis for your IPO</span>'):]
rw("services-ipo-communications.html", ipo_dark)

# 5. diagrams
DEFS = '''<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#00AE91"/></marker><marker id="arr-blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#2577BC"/></marker></defs>'''

def box(x, y, w, h, title, lines, accent=False, r=10):
    cls = "d-box-accent" if accent else "d-box"
    tc = "#FFFFFF" if accent else None
    out = [f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/>']
    ty = y + 26
    out.append(f'<text x="{x + w / 2}" y="{ty}" text-anchor="middle" class="d-label" font-size="13" letter-spacing="1.5"{" fill=" + chr(34) + tc + chr(34) if tc else ""}>{title.upper()}</text>')
    for ln in lines:
        ty += 20
        out.append(f'<text x="{x + w / 2}" y="{ty}" text-anchor="middle" class="d-small" font-size="12"{" fill=" + chr(34) + "#C6D6E0" + chr(34) if accent else ""}>{ln}</text>')
    return "".join(out)

def arrow(x1, y1, x2, y2, loop=False):
    return f'<path class="{"d-loop" if loop else "d-arrow"}" d="M{x1} {y1} L{x2} {y2}"/>'

def pills(x, y, items, w=150, gap=10, h=30):
    out = []
    for i, t in enumerate(items):
        px = x + i * (w + gap)
        out.append(f'<rect class="d-pill" x="{px}" y="{y}" width="{w}" height="{h}" rx="15"/><text x="{px + w / 2}" y="{y + 19}" text-anchor="middle" font-size="12" class="d-label">{t}</text>')
    return "".join(out)

def loop_diagram(company, company_lines, stages, outcomes, feedback, foundation, caption):
    W = 1000
    parts = [f'<svg viewBox="0 0 {W} 330" role="img" aria-label="{caption}">', DEFS]
    bw, bh, gap, y = 150, 108, 24, 70
    x = 20
    parts.append(box(x, y, bw, bh, company, company_lines, accent=True))
    for i, (t, lines) in enumerate(stages):
        nx = x + bw + gap
        parts.append(arrow(x + bw + 2, y + bh / 2, nx - 2, y + bh / 2))
        parts.append(box(nx, y, bw, bh, t, lines)); x = nx
    parts.append(arrow(x + bw + 2, y + bh / 2, x + bw + gap - 2, y + bh / 2))
    ox = x + bw + gap
    oh = 24
    for i, o in enumerate(outcomes):
        oy = y + i * (oh + 4)
        parts.append(f'<rect class="d-pill" x="{ox}" y="{oy}" width="{W - ox - 20}" height="{oh}" rx="12"/><text x="{ox + (W - ox - 20) / 2}" y="{oy + 16}" text-anchor="middle" font-size="12" class="d-label">{o}</text>')
    # feedback loop below
    parts.append(f'<path class="d-loop" d="M{ox + 40} {y + bh + 14} L{ox + 40} {y + bh + 50} L{20 + bw / 2} {y + bh + 50} L{20 + bw / 2} {y + bh + 8}"/>')
    parts.append(f'<text x="{W / 2}" y="{y + bh + 44}" text-anchor="middle" font-size="12" class="d-small">{feedback}</text>')
    # foundation bar
    parts.append(f'<rect x="20" y="{y + bh + 76}" width="{W - 40}" height="40" rx="8" fill="#123140"/>')
    parts.append(f'<text x="{W / 2}" y="{y + bh + 101}" text-anchor="middle" font-size="12" fill="#DCE7EE" letter-spacing="1">{foundation}</text>')
    parts.append('</svg>')
    return f'<figure class="diagram reveal">{"".join(parts)}<figcaption>{caption}</figcaption></figure>'

IR = loop_diagram("Company", ["Strategy · Financial plan", "Leadership · Milestones"],
    [("Investment messages", ["Growth thesis", "Capital allocation", "KPIs, catalysts, risks"]),
     ("IR materials", ["IR presentation", "Fact sheet · Q&amp;A bank", "Results announcements"]),
     ("IR activities", ["Results briefings", "Roadshows · 1-on-1s", "AGM · Investor day"]),
     ("IR constituencies", ["Institutions · Analysts", "Private and retail", "Credit, ESG · Media"])],
    ["Fair valuation", "Lower cost of capital", "Access to capital", "Strategy execution"],
    "feedback refines the investment case",
    "DISCLOSURE AND COMPLIANCE FOUNDATION · BURSA LISTING REQUIREMENTS · CONTINUOUS DISCLOSURE · QUIET PERIODS · MCCG",
    "IR framework: from company strategy to investor understanding, with feedback refining the investment case.")

PR = loop_diagram("Client", ["Purpose · Strategy", "Leadership · Milestones"],
    [("Core narrative", ["Brand positioning", "Corporate narrative", "Leadership voice"]),
     ("PR assets", ["Press releases", "Media kit · Fact sheet", "Spokesperson briefs"]),
     ("PR activities", ["Media relations", "Press conferences", "Op-eds · Events · Crisis"]),
     ("Stakeholders", ["Media · Regulators", "Partners · Employees", "Communities · KOLs"])],
    ["Visibility", "Credibility", "Trust", "Reputation"],
    "feedback refines the narrative",
    "GOVERNANCE FOUNDATION · APPROVALS WORKFLOW · MESSAGE DISCIPLINE · BRAND GUIDELINES · CRISIS PROTOCOLS",
    "PR framework: from client strategy to stakeholder trust, with feedback refining the narrative.")

def spine_diagram():
    W = 1000
    p = [f'<svg viewBox="0 0 {W} 300" role="img" aria-label="Integrated IR and PR engagement model">', DEFS]
    p.append(box(20, 96, 170, 108, "Company / client", ["Priorities", "Initiatives", "Milestones"], accent=True))
    p.append(arrow(192, 150, 228, 150))
    p.append(box(230, 96, 170, 108, "Narrative spine", ["One approved story", "Meets disclosure rules"]))
    p.append(arrow(402, 130, 438, 70)); p.append(arrow(402, 170, 438, 230))
    p.append(box(440, 20, 200, 100, "IR lane", ["The investment case", "Institutions · Analysts · Retail"]))
    p.append(box(440, 180, 200, 100, "PR lane", ["The corporate narrative", "Media · Regulators · Partners"]))
    p.append(arrow(642, 70, 678, 130)); p.append(arrow(642, 230, 678, 170))
    p.append(box(680, 96, 150, 108, "Disclosure gate", ["Client approval", "by risk tier"], accent=True))
    p.append(arrow(832, 150, 868, 150))
    p.append(f'<rect class="d-pill" x="870" y="112" width="110" height="76" rx="12"/><text x="925" y="142" text-anchor="middle" font-size="12" class="d-label">Analysts</text><text x="925" y="162" text-anchor="middle" font-size="12" class="d-label">and media</text>')
    p.append(f'<path class="d-loop" d="M925 190 L925 262 L105 262 L105 206"/>')
    p.append(f'<text x="500" y="256" text-anchor="middle" font-size="12" class="d-small">one story · one approval gate · one timed calendar · one feedback loop</text>')
    p.append('</svg>')
    return f'<figure class="diagram reveal">{"".join(p)}<figcaption>Integrated IR + PR engagement model: one narrative, two audiences, one disclosure gate.</figcaption></figure>'

def ipo_timeline():
    W = 1000
    steps = [("01", "Approval"), ("02", "Underwriting agreement"), ("03", "Prospectus launch"), ("04", "Balloting"), ("05", "Listing ceremony")]
    p = [f'<svg viewBox="0 0 {W} 190" role="img" aria-label="IPO communications roadmap">', DEFS]
    p.append('<path d="M40 100 L780 100" stroke="#00AE91" stroke-width="3"/>')
    p.append('<path d="M780 100 L960 100" stroke="#2577BC" stroke-width="3" stroke-dasharray="8 6"/>')
    for i, (n, t) in enumerate(steps):
        x = 60 + i * 180
        p.append(f'<circle cx="{x}" cy="100" r="14" fill="#123140"/><text x="{x}" y="105" text-anchor="middle" font-size="11" fill="#FFFFFF" font-weight="600">{n}</text>')
        words = t.split(" ")
        if len(words) > 1 and len(t) > 12:
            p.append(f'<text x="{x}" y="60" text-anchor="middle" font-size="13" class="d-label">{words[0]}</text><text x="{x}" y="78" text-anchor="middle" font-size="13" class="d-label">{" ".join(words[1:])}</text>')
        else:
            p.append(f'<text x="{x}" y="78" text-anchor="middle" font-size="13" class="d-label">{t}</text>')
    p.append('<rect x="820" y="80" width="150" height="40" rx="20" fill="#2577BC"/><text x="895" y="98" text-anchor="middle" font-size="11" fill="#FFFFFF" font-weight="600">06 · RETAINER</text><text x="895" y="112" text-anchor="middle" font-size="10" fill="#DCE7EE">Continuous market communications</text>')
    p.append('<text x="420" y="150" text-anchor="middle" font-size="12" class="d-small">3 months to listing · 2 months to listing · 1 month to listing · post-listing visibility</text>')
    p.append('</svg>')
    return f'<figure class="diagram reveal">{"".join(p)}<figcaption>Aegis roadmap: five coordinated milestones, then the retainer programme.</figcaption></figure>'

rw("services-investor-relations.html", lambda s: s.replace('    <div class="framework reveal">', "    " + IR + '\n    <div class="framework reveal">', 1))
rw("services-public-relations.html", lambda s: s.replace('    <div class="framework reveal">', "    " + PR + '\n    <div class="framework reveal">', 1))
rw("approach.html", lambda s: re.sub(r'(<span class="eyebrow">Integrated IR \+ PR engagement model</span>.*?</div>\n)', lambda m: m.group(1) + "    " + spine_diagram() + "\n", s, count=1, flags=re.S))
rw("services-ipo-communications.html", lambda s: re.sub(r'(<span class="eyebrow">Aegis roadmap</span>.*?</div>\n)', lambda m: m.group(1) + "    " + ipo_timeline() + "\n", s, count=1, flags=re.S))
print("design edits ok")
