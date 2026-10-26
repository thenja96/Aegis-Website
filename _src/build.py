"""Assemble the site: wraps each fragment in _src/pages/ with the shared header and footer.

Run:  python _src/build.py
Fragments start with a small header block:
    title: ...
    description: ...
    path: services/investor-relations.html
    ---
    <body html>
Output goes to the site root. Edit fragments or this file, never the generated HTML.

Build-time additions (no copy changes): skip link, breadcrumbs, sticky sub-navigation from section
eyebrows, next-page link, image width/height, WebP <picture> for photos, JSON-LD organisation data,
back-to-top button and mobile contact bar.
"""
import os, re, datetime, html, json, time
import cms
SHORT = {'Why IPO communications discipline matters': 'Why it matters', 'When to bring Aegis in': 'Timing', 'For principal advisers and underwriters': 'Advisers', 'Aegis roadmap': 'Roadmap', 'IPO countdown': 'Countdown', 'Commercial scope': 'Scope', 'Investment community strategy': 'Investors', 'Digital amplification': 'Digital', 'Why Aegis for your IPO': 'Why Aegis', 'Established PLC': 'Established PLC', 'Integrated IR + PR engagement model': 'The model', 'Risk-tier disclosure gate': 'Disclosure gate', 'Disclosure and information control': 'Information control', 'Corporate exercise communications': 'Corporate exercises', 'When something goes wrong': 'Crisis', 'Annual obligations': 'Annual cycle', 'Client-Aegis closeness': 'Working together', 'Newly listed': 'Newly listed', 'The quarterly rhythm': 'Quarterly rhythm', 'The first twelve months': 'First 12 months', 'What the IR mandate covers': 'What we do', 'IR framework': 'Framework', 'IR process': 'Process', 'For investors, analysts and media': 'Investor access', 'Core functions': 'What we do', 'PR framework': 'Framework', 'PR process': 'Process', 'Media monitoring and sentiment analysis': 'Monitoring', 'For media': 'Media desk'}
SUBNAV_KEEP = {'PR framework', 'Risk-tier disclosure gate', 'Media monitoring and sentiment analysis', 'Aegis roadmap', 'Newly listed', 'Established PLC', 'Why Aegis for your IPO', 'When to bring Aegis in', 'When something goes wrong', 'Integrated IR + PR engagement model', 'Core functions', 'For media', 'Why IPO communications discipline matters', 'PR process', 'For investors, analysts and media', 'The quarterly rhythm', 'Corporate exercise communications', 'Commercial scope', 'What the IR mandate covers', 'IR framework'}  # max five jump links per page
COLLAPSE = {'PR framework', 'Disclosure and information control', 'IR framework', 'Digital amplification', 'IR process', 'Media monitoring and sentiment analysis', 'PR process', 'Commercial scope', 'The first twelve months', 'Client-Aegis closeness', 'Annual obligations', 'Investment community strategy', 'IPO countdown', 'Corporate exercise communications'}
try:
    from PIL import Image
except ImportError:
    Image = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "_src", "pages")
SITE_URL = "https://www.aegiscomm.com.my/"

SERVICES = [
    ("Investor Relations", "services/investor-relations.html"),
    ("Public & Media Relations", "services/public-relations.html"),
    ("Event Management", "services/events.html"),
    ("Creative, Content & Digital", "services/creative-digital.html"),
]
ABOUT = [
    ("About Aegis", "about.html"),
    ("Our People", "people.html"),
    ("Our Approach", "approach.html"),
    ("Track Record", "track-record.html"),
]
NAV = [
    ("Home", "index.html", None),
    ("Services", None, SERVICES),
    ("IPO Communications", "services/ipo-communications.html", None),
    ("About", None, ABOUT),
]
# Reading order for the "next page" link at the bottom of long pages
NEXT = {
    "services/ipo-communications.html": ("Investor Relations", "services/investor-relations.html"),
    "services/investor-relations.html": ("Public & Media Relations", "services/public-relations.html"),
    "services/public-relations.html": ("Event Management", "services/events.html"),
    "services/events.html": ("Creative, Content & Digital", "services/creative-digital.html"),
    "services/creative-digital.html": ("Our Approach", "approach.html"),
    "approach.html": ("Track Record", "track-record.html"),
    "track-record.html": ("About Aegis", "about.html"),
    "about.html": ("Our People", "people.html"),
    "people.html": ("Contact", "contact.html"),
}
TITLES = {p: t for t, p in SERVICES}
TITLES.update({"services/ipo-communications.html": "IPO Communications", "approach.html": "Our Approach",
               "track-record.html": "Track Record", "about.html": "About", "people.html": "Our People", "contact.html": "Contact", "404.html": "Page not found"})

def header(rel):
    items = []
    for label, href, sub in NAV:
        if sub:
            links = "".join(f'<li><a href="{rel}{h}">{l}</a></li>' for l, h in sub)
            top = "services/investor-relations.html" if label == "Services" else "about.html"
            heading = "What we do" if label == "Services" else "Who we are"
            items.append(f'<li class="has-sub"><a href="{rel}{top}" aria-haspopup="true">{label}</a>'
                         f'<ul class="sub"><li class="sub-label">{heading}</li>{links}</ul></li>')
        else:
            items.append(f'<li><a href="{rel}{href}">{label}</a></li>')
    items.append(f'<li><a class="btn btn-primary" href="{rel}contact.html">Contact us</a></li>')
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="header">
  <div class="container">
    <a class="brand" href="{rel}index.html" aria-label="Aegis Communication home"><img src="{rel}assets/logo.png" alt="Aegis Communication" width="190" height="72"></a>
    <button class="nav-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>
    <ul class="nav" id="nav">{"".join(items)}</ul>
  </div>
  <div class="progress" aria-hidden="true"></div>
</header>'''

def footer(rel, path, v=""):
    year = datetime.date.today().year
    nxt = NEXT.get(path)
    nextlink = (f'<aside class="nextlink"><div class="container"><div><small>Next</small><a href="{rel}{nxt[1]}">{nxt[0]}</a></div>'
                '</div></aside>') if nxt else ""
    cta_bar = "" if path == "contact.html" else f'<div class="mobile-cta"><a class="btn btn-primary" href="{rel}contact.html">Contact us</a></div>'
    return f'''{nextlink}
<footer class="footer">
  <div class="container">
    <div class="cols">
      <div>
        <img src="{rel}assets/logo-light.png" alt="Aegis Communication" width="150" height="54">
        <p>Capital market communications for public listed companies and pre-IPO companies in Malaysia. Investor relations, public relations, IPO communications and events, run as one programme.</p>
      </div>
      <div>
        <h4>Services</h4>
        <ul>
          <li><a href="{rel}services/investor-relations.html">Investor Relations</a></li>
          <li><a href="{rel}services/public-relations.html">Public &amp; Media Relations</a></li>
          <li><a href="{rel}services/ipo-communications.html">IPO Communications</a></li>
          <li><a href="{rel}services/events.html">Event Management</a></li>
          <li><a href="{rel}services/creative-digital.html">Creative, Content &amp; Digital</a></li>
        </ul>
      </div>
      <div>
        <h4>Company</h4>
        <ul>
          <li><a href="{rel}approach.html">Our Approach</a></li>
          <li><a href="{rel}track-record.html">Track Record</a></li>
          <li><a href="{rel}about.html">About Aegis</a></li>
          <li><a href="{rel}people.html">Our People</a></li>
          <li><a href="{rel}contact.html">Contact</a></li>
          <li><a href="{rel}services/public-relations.html#media">Media enquiries</a></li>
          <li><a href="{rel}services/investor-relations.html#investors">Investor and analyst access</a></li>
        </ul>
      </div>
      <div>
        <h4>Office</h4>
        <ul class="office">
          <li>B-2-5, Union Tower, Jalan Desa Bakti, Taman Desa, 58000 Kuala Lumpur</li>
          <li><a href="tel:+60350231848">+603 5023 1848</a></li>
          <li><a href="mailto:aegis@aegiscomm.com.my">aegis@aegiscomm.com.my</a></li>
        </ul>
      </div>
    </div>
    <div class="legal">
      <span>&copy; {year} Aegis Communication Sdn. Bhd. (Reg. No. 1274315-W). All rights reserved.</span>
      <span>Information on this site is general in nature and does not constitute investment advice.</span>
    </div>
  </div>
</footer>
<button class="totop" aria-label="Back to top"></button>
{cta_bar}
<script src="{rel}assets/site.js?v={v}" defer></script>'''

def jsonld():
    data = {
        "@context": "https://schema.org", "@type": "ProfessionalService",
        "name": "Aegis Communication Sdn. Bhd.", "url": SITE_URL, "logo": SITE_URL + "assets/logo.png",
        "image": SITE_URL + "assets/og-image.png", "telephone": "+60350231848", "email": "aegis@aegiscomm.com.my",
        "address": {"@type": "PostalAddress", "streetAddress": "B-2-5, Union Tower, Jalan Desa Bakti, Taman Desa",
                    "addressLocality": "Kuala Lumpur", "postalCode": "58000", "addressCountry": "MY"},
        "areaServed": "MY",
        "knowsAbout": ["Investor relations", "Public relations", "IPO communications", "Bursa Malaysia"],
    }
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'

def slug(s):
    s = html.unescape(re.sub(r"<[^>]+>", "", s)).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:40].rstrip("-")

def add_section_ids_and_subnav(body):
    """Give each top-level section with an eyebrow an id; return (body, subnav html)."""
    entries = []
    def repl(m):
        tag, inner = m.group(1), m.group(2)
        if 'class="hero' in tag or 'class="cta' in tag or 'class="stats' in tag:
            return m.group(0)
        eb = re.search(r'<span class="eyebrow[^"]*">(.*?)</span>', inner)
        if not eb:
            return m.group(0)
        label = html.unescape(re.sub(r"<[^>]+>", "", eb.group(1))).strip()
        idm = re.search(r'\bid="([^"]+)"', tag)
        sid = idm.group(1) if idm else slug(label)
        if not idm:
            tag = tag[:-1] + f' id="{sid}">'
        entries.append((label, sid))
        if label in COLLAPSE and len(entries) >= 1:
            # keep the section head visible; fold the rest behind a toggle
            m2 = re.search(r'(<div class="section-head reveal">.*?</div>\n)', inner, flags=re.S)
            if m2:
                head_end = m2.end()
                inner = inner[:head_end] + '<details class="fold"><summary><span class="when-closed">Show details</span><span class="when-open">Hide details</span></summary><div class="fold-body">' + inner[head_end:]
                inner = re.sub(r'(\s*</div>\s*)$', r'</div></details>\1', inner, count=1)
                tag = tag[:-1] + ' data-fold>'
        return tag + inner + "</section>"
    body = re.sub(r"(<section\b[^>]*>)(.*?)</section>", repl, body, flags=re.S)
    if len(entries) < 5:
        return body, ""
    shown = [e for e in entries if e[0] in SUBNAV_KEEP][:5] or entries[:5]
    links = "".join(f'<a href="#{sid}">{html.escape(SHORT.get(label, label))}</a>' for label, sid in shown)
    return body, f'<nav class="subnav" aria-label="On this page"><div class="container">{links}</div></nav>'

def breadcrumbs(body, rel, path):
    if path in ("index.html", "404.html"):
        return body
    parts = [f'<span><a href="{rel}index.html">Home</a></span>']
    # parent path only: the page name already appears in the hero label below
    if path.startswith("services/"):
        parts.append(f'<span><a href="{rel}services/investor-relations.html">Services</a></span>')
    elif path in ("people.html", "approach.html", "track-record.html"):
        parts.append(f'<span><a href="{rel}about.html">About</a></span>')
    crumbs = f'<nav class="crumbs" aria-label="Breadcrumb">{"".join(parts)}</nav>'
    return re.sub(r'(<section class="hero[^"]*"[^>]*>\s*<div class="container">\s*)', r"\1" + crumbs + "\n    ", body, count=1)

def image_sizes(body):
    """Add width/height to local images and wrap photos in <picture> with WebP."""
    if Image is None:
        return body
    def fix(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag)
        if not src or src.group(1).startswith("http"):
            return tag
        local = os.path.join(ROOT, src.group(1).replace("../", ""))
        if not os.path.exists(local):
            return tag
        if "width=" not in tag:
            try:
                w, h = Image.open(local).size
                tag = tag[:-1] + f' width="{w}" height="{h}">'
            except Exception:
                pass
        if ("/photos/" in src.group(1) or "/network/" in src.group(1)) and src.group(1)[-4:] in (".jpg", ".png") and os.path.exists(local[:-4] + ".webp"):
            webp = src.group(1)[:-4] + ".webp"
            return f'<picture><source srcset="{webp}" type="image/webp">{tag}</picture>'
        return tag
    body = re.sub(r"<img\b[^>]*>", fix, body)
    body = re.sub(r"(<figure>)(<picture>.*?</picture>|<img\b[^>]*>)", r'\1<div class="frame">\2</div>', body)
    return body

SPRITE = open(os.path.join(ROOT, "_src", "icons.svg"), encoding="utf-8").read()

def mark_label_steps(body):
    """Steps whose marker is a word label (not a 1-2 character number) get class step-label."""
    def f(m):
        txt = html.unescape(m.group(2)).strip()
        return m.group(0) if len(txt) <= 3 else f'<div class="step step-label"><span class="n">{m.group(2)}</span>'
    return re.sub(r'(<div class="step"><span class="n">)([^<]*)</span>', f, body)

def split_hero_eyebrow(body):
    """Hero eyebrows like 'Service · 03 · IPO Communications': last part drops to its own line on phones."""
    def f(m):
        txt = m.group(1)
        if " · " not in txt:
            return m.group(0)
        head, name = txt.rsplit(" · ", 1)
        return f'<span class="eyebrow on-dark"><span class="eb-text">{head}<span class="eb-sep"> · </span><span class="eb-name">{name}</span></span></span>'
    return re.sub(r'<span class="eyebrow on-dark">([^<]+)</span>', f, body, count=1)

def wrap(meta, body, rel):
    path = meta["path"]
    # cache-busting query from the asset mtimes, so browsers pick up CSS and JS changes after upload
    v = str(int(max(os.path.getmtime(os.path.join(ROOT, "assets", f)) for f in ("style.css", "site.js"))))
    canonical = SITE_URL + ("" if path == "index.html" else path)
    body, subnav = add_section_ids_and_subnav(body)
    body = breadcrumbs(body, rel, path)
    body = image_sizes(body)
    body = mark_label_steps(body)
    body = split_hero_eyebrow(body)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{meta["title"]}</title>
<meta name="description" content="{meta["description"]}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#0F172A">
<script>if("scrollRestoration" in history)history.scrollRestoration="manual";</script>
<meta property="og:type" content="website">
<meta property="og:site_name" content="Aegis Communication">
<meta property="og:title" content="{meta["title"]}">
<meta property="og:description" content="{meta["description"]}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{rel}assets/favicon.svg" type="image/svg+xml">
<link rel="alternate icon" href="{rel}assets/favicon.png" type="image/png">
<link rel="preload" href="{rel}assets/fonts/newsreader-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{rel}assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{rel}assets/style.css?v={v}">
{jsonld()}
</head>
<body{" class=" + chr(34) + "home" + chr(34) if path == "index.html" else ""}>
{SPRITE}
{header(rel)}
{subnav}
{'<aside class="side-cta" aria-label="Contact"><a class="btn btn-primary sm" href="' + rel + 'contact.html">Contact us</a><a class="side-tel" href="tel:+60350231848">+603 5023 1848</a></aside>' if subnav else ''}
<main id="main">
{body.strip()}
</main>
{footer(rel, path, v)}
</body>
</html>
'''

def build():
    pages = []
    store = cms.load_store(ROOT)
    manifest, site_items = [], {}
    for fn in sorted(os.listdir(SRC)):
        if not fn.endswith(".html"):
            continue
        raw = open(os.path.join(SRC, fn), encoding="utf-8").read()
        head, body = raw.split("\n---\n", 1)
        meta = dict(re.findall(r"^(\w+):\s*(.+)$", head, flags=re.M))
        depth = meta["path"].count("/")
        rel = "../" * depth
        out = os.path.join(ROOT, meta["path"])
        os.makedirs(os.path.dirname(out), exist_ok=True)
        page, items, images = cms.mark(wrap(meta, body, rel), meta["path"])
        # backend edits (aegis/data/content.php) are re-applied so a rebuild never loses them
        page = cms.apply(page, meta["path"], rel, items, store)
        open(out, "w", encoding="utf-8").write(page)
        manifest.append({"path": meta["path"], "title": meta["title"], "description": meta["description"],
                         "items": [i for i in items if i["scope"] != "*"], "images": images})
        for i in items:
            if i["scope"] == "*":
                site_items.setdefault(i["k"], i)
        pages.append(meta["path"])
        print("built", meta["path"])
    today = datetime.date.today().isoformat()
    urls = "".join(f"  <url><loc>{SITE_URL}{'' if p == 'index.html' else p}</loc><lastmod>{today}</lastmod></url>\n"
                   for p in pages if p != "404.html")
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    cms.write_manifest(ROOT, manifest, list(site_items.values()))
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\nDisallow: /_src/\nSitemap: {SITE_URL}sitemap.xml\n")

if __name__ == "__main__":
    build()
