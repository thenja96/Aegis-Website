"""Generates the inline SVG diagrams and (re)inserts them into the page fragments.
Labels are taken from existing page copy only. Run after editing: python _src/tools/diagrams.py && python _src/build.py"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "_src", "pages")

DEFS = ('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0 0 L10 5 L0 10 z" fill="#1AB191"/></marker><marker id="arr-blue" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#0E6BB4"/></marker></defs>')

def text(x, y, s, size=12, cls="d-small", anchor="middle", fill=None, weight=None, ls=None):
    style = ""
    if fill: style += f"fill:{fill};"
    if weight: style += f"font-weight:{weight};"
    if ls: style += f"letter-spacing:{ls}px;"
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}" font-size="{size}"{" style=" + chr(34) + style + chr(34) if style else ""}>{s}</text>'

def box(x, y, w, h, title, lines, accent=False):
    out = [f'<rect class="{"d-box-accent" if accent else "d-box"}" x="{x}" y="{y}" width="{w}" height="{h}" rx="4"/>']
    ty = y + 26
    long = len(title) > 13
    out.append(text(x + w / 2, ty, title.upper(), 10.5 if long else 12.5, "d-label", fill="#FFFFFF" if accent else None, weight=600, ls=0.6 if long else 1.5))
    for ln in lines:
        ty += 20
        out.append(text(x + w / 2, ty, ln, 12, "d-small", fill="#C6D6E0" if accent else None))
    return "".join(out)

def arrow(x1, y1, x2, y2):
    return f'<path class="d-arrow" pathLength="1" d="M{x1} {y1} L{x2} {y2}"/>'

def loop_diagram(company, company_lines, stages, outcomes, feedback, foundation, caption):
    W, bw, bh, gap, y, x = 1000, 140, 108, 18, 60, 20
    p = [f'<svg viewBox="0 0 {W} 320" role="img" aria-label="{caption}">', DEFS, box(x, y, bw, bh, company, company_lines, True)]
    for t, lines in stages:
        nx = x + bw + gap
        p.append(arrow(x + bw + 2, y + bh / 2, nx - 2, y + bh / 2)); p.append(box(nx, y, bw, bh, t, lines)); x = nx
    p.append(arrow(x + bw + 2, y + bh / 2, x + bw + gap - 2, y + bh / 2))
    ox = x + bw + gap; ow = W - ox - 20; oh = 24
    for i, o in enumerate(outcomes):
        oy = y + i * (oh + 4)
        p.append(f'<rect class="d-pill" x="{ox}" y="{oy}" width="{ow}" height="{oh}" rx="3"/>' + text(ox + ow / 2, oy + 16, o, 12, "d-label", weight=600))
    p.append(f'<path class="d-loop" pathLength="1" d="M{ox + 40} {y + bh + 14} L{ox + 40} {y + bh + 50} L{20 + bw / 2} {y + bh + 50} L{20 + bw / 2} {y + bh + 8}"/>')
    p.append(text(W / 2, y + bh + 44, feedback, 12))
    p.append(f'<rect x="20" y="{y + bh + 76}" width="{W - 40}" height="40" rx="8" fill="#0F172A"/>')
    p.append(text(W / 2, y + bh + 101, foundation, 11.5, "d-small", fill="#DCE7EE", ls=1))
    p.append("</svg>")
    return f'<figure class="diagram reveal">{"".join(p)}<figcaption>{caption}</figcaption></figure>'

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

def spine():
    p = ['<svg viewBox="0 0 1000 340" role="img" aria-label="Integrated IR and PR engagement model">', DEFS]
    p.append(box(20, 106, 170, 108, "Company / client", ["Priorities", "Initiatives", "Milestones"], True))
    p.append(arrow(192, 160, 228, 160))
    p.append(box(230, 106, 170, 108, "Narrative spine", ["One approved story", "Meets disclosure rules"]))
    p.append(arrow(402, 140, 438, 80)); p.append(arrow(402, 180, 438, 240))
    p.append(box(440, 20, 200, 100, "IR lane", ["The investment case", "Institutions · Analysts · Retail"]))
    p.append(box(440, 200, 200, 100, "PR lane", ["The corporate narrative", "Media · Regulators · Partners"]))
    p.append(arrow(642, 80, 678, 140)); p.append(arrow(642, 240, 678, 180))
    p.append(box(680, 106, 150, 108, "Disclosure gate", ["Client approval", "by risk tier"], True))
    p.append(arrow(832, 160, 868, 160))
    p.append('<rect class="d-pill" x="870" y="122" width="110" height="76" rx="3"/>' + text(925, 152, "Analysts", 12, "d-label", weight=600) + text(925, 172, "and media", 12, "d-label", weight=600))
    p.append('<path class="d-loop" pathLength="1" d="M925 200 L925 318 L105 318 L105 216"/>')
    p.append(text(500, 334, "one story · one approval gate · one timed calendar · one feedback loop", 12))
    p.append("</svg>")
    return f'<figure class="diagram reveal">{"".join(p)}<figcaption>Integrated IR + PR engagement model: one narrative, two audiences, one disclosure gate.</figcaption></figure>'

def timeline():
    steps = [("01", "Approval"), ("02", "Underwriting agreement"), ("03", "Prospectus launch"), ("04", "Balloting"), ("05", "Listing ceremony")]
    p = ['<svg viewBox="0 0 1000 200" role="img" aria-label="IPO communications roadmap">', DEFS,
         '<path class="d-line" pathLength="1" d="M40 110 L760 110" stroke="#1AB191" stroke-width="3"/>', '<path d="M760 110 L800 110" stroke="#0E6BB4" stroke-width="3" stroke-dasharray="8 6"/>']
    for i, (n, t) in enumerate(steps):
        x = 60 + i * 170
        p.append(f'<circle cx="{x}" cy="110" r="15" fill="#0F172A"/>' + text(x, 115, n, 11, "d-small", fill="#FFFFFF", weight=600))
        w = t.split(" ")
        if len(w) > 1 and len(t) > 12:
            p.append(text(x, 62, w[0], 14, "d-label", weight=600) + text(x, 82, " ".join(w[1:]), 14, "d-label", weight=600))
        else:
            p.append(text(x, 82, t, 14, "d-label", weight=600))
    p.append('<rect x="796" y="82" width="190" height="56" rx="28" fill="#0E6BB4"/>' + text(891, 104, "06 · RETAINER PROGRAMME", 10, "d-small", fill="#FFFFFF", weight=600, ls=0.4) + text(891, 122, "Continuous market communications", 9.5, "d-small", fill="#DCE7EE"))
    p.append(text(420, 165, "3 months to listing · 2 months to listing · 1 month to listing · post-listing visibility", 12))
    p.append("</svg>")
    return f'<figure class="diagram reveal">{"".join(p)}<figcaption>Aegis roadmap: five coordinated milestones, then the retainer programme.</figcaption></figure>'

def put(name, anchor_regex, fig):
    path = os.path.join(P, name); s = open(path, encoding="utf-8").read()
    s = re.sub(r'\s*<figure class="diagram reveal">.*?</figure>\n?', "\n", s, flags=re.S)
    s2 = re.sub(anchor_regex, lambda m: m.group(1) + "    " + fig + "\n", s, count=1, flags=re.S)
    assert s2 != s, name
    open(path, "w", encoding="utf-8").write(s2)

put("services-investor-relations.html", r'(<span class="eyebrow">IR framework</span>.*?</div>\n)', IR)
put("services-public-relations.html", r'(<span class="eyebrow">PR framework</span>.*?</div>\n)', PR)
put("approach.html", r'(<span class="eyebrow">Integrated IR \+ PR engagement model</span>.*?</div>\n)', spine())
print("diagrams ok")
