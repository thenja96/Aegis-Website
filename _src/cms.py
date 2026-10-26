"""Content backend support for the build.

mark()  tags every editable text block in a built page with data-e="<key>" and every
        <img> with data-i="<key>", and returns the page's manifest entries.
apply() writes the backend's saved edits (aegis/data/content.php) back into a page.

The PHP backend (aegis/lib.php) applies the same edits with the same rules, so a page
rebuilt here and a page saved from the backend come out identical.
Keys are a hash of the original text, so an edit stays attached to its block across rebuilds
and is simply dropped if that text is later changed in _src/pages.
"""
import hashlib, html, json, os, re
from html.parser import HTMLParser

EDITABLE = {"h1", "h2", "h3", "h4", "h5", "p", "li", "figcaption", "td", "th", "small", "b", "strong",
            "span", "a", "button", "label", "option", "dt", "dd", "blockquote", "em", "div"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
SKIP_TAGS = {"script", "style", "svg", "noscript", "template", "head", "title"}
SKIP_CLASSES = {"subnav", "crumbs", "skip", "film-ctl"}
GUARD = "<?php exit; ?>\n"


SKIP_URL = r"(?!https?:|mailto:|tel:|#|/|data:|javascript:)"


def norm(s, path=""):
    """Site-root-relative links, single spaces: the form used for keys and storage."""
    d = path.rsplit("/", 1)[0] + "/" if "/" in path else ""
    def fix(m):
        u = m.group(2)
        ups = 0
        while u.startswith("../"):
            u, ups = u[3:], ups + 1
        base = d.split("/")[:-1]
        base = base[:max(0, len(base) - ups)]
        return m.group(1) + ("/".join(base) + "/" if base else "") + u
    s = re.sub(r'((?:href|src)=")' + SKIP_URL + r'([^"]*)', fix, s)
    return re.sub(r"\s+", " ", s).strip()


def denorm(s, path=""):
    """Back to links relative to the page at `path`."""
    d = path.rsplit("/", 1)[0] + "/" if "/" in path else ""
    if not d:
        return s
    depth = d.count("/")
    def fix(m):
        u = m.group(2)
        return m.group(1) + (u[len(d):] if u.startswith(d) else "../" * depth + u)
    return re.sub(r'((?:href|src)=")' + SKIP_URL + r'([^"]*)', fix, s)


def key(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]


def text_of(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


class _Scan(HTMLParser):
    def __init__(self, src):
        super().__init__(convert_charrefs=False)
        self.src = src
        self.lines = [0]
        for m in re.finditer("\n", src):
            self.lines.append(m.end())
        self.stack = []      # [tag, start, start_end, has_text, skip, region, section]
        self.found = []      # (tag, start, start_end, end_start, region, section, cls)
        self.imgs = []       # (start, start_end, attrs)
        self.sec = 0
        self.sec_tag = {}

    def off(self):
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def handle_starttag(self, tag, attrs):
        start = self.off()
        raw = self.get_starttag_text()
        a = dict(attrs)
        if tag == "img":
            self.imgs.append((start, start + len(raw), a))
        if tag in VOID:
            return
        parent_skip = self.stack[-1][4] if self.stack else False
        cls = set((a.get("class") or "").split())
        skip = parent_skip or tag in SKIP_TAGS or bool(cls & SKIP_CLASSES)
        region = self.stack[-1][5] if self.stack else None
        sec = self.stack[-1][6] if self.stack else 0
        if tag == "main" or (tag == "aside" and "nextlink" in cls):
            region = "page"
        elif tag in ("header", "footer", "aside") and region != "page":
            region = "site"
        if tag in ("section", "aside", "main", "header", "footer"):
            self.sec += 1
            sec = self.sec
            self.sec_tag[sec] = tag
        self.stack.append([tag, start, start + len(raw), False, skip, region, sec, " ".join(sorted(cls))])

    def handle_startendtag(self, tag, attrs):
        start = self.off()
        if tag == "img":
            raw = self.get_starttag_text()
            self.imgs.append((start, start + len(raw), dict(attrs)))

    def handle_data(self, data):
        if self.stack and data.strip():
            self.stack[-1][3] = True

    def handle_entityref(self, name):
        if self.stack:
            self.stack[-1][3] = True

    handle_charref = handle_entityref

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        end_start = self.off()
        # tolerate stray tags: pop back to the matching open tag
        idx = next((i for i in range(len(self.stack) - 1, -1, -1) if self.stack[i][0] == tag), None)
        if idx is None:
            return
        while len(self.stack) > idx:
            t, s, se, has_text, skip, region, section, cls = self.stack.pop()
            if t == tag and has_text and not skip and t in EDITABLE and region:
                self.found.append((t, s, se, end_start, region, section, cls))


def mark(page_html, path):
    """Tag editable blocks and images. Returns (html, items, images)."""
    scan = _Scan(page_html)
    scan.feed(page_html)
    scan.close()
    found = sorted(scan.found, key=lambda f: f[1])
    # keep only top-most blocks: drop any block inside another editable block
    top, last_end = [], -1
    for f in found:
        if f[1] >= last_end:
            top.append(f)
            last_end = f[3]
    # name each section after its first heading (or its label when it has none)
    names = {}
    for tag, s, se, es, region, sec, cls in top:
        if region != "page":
            continue
        t = text_of(page_html[se:es])
        if tag in ("h1", "h2") and not names.get(sec, ("", 0))[1]:
            names[sec] = (t, 1)
        elif "eyebrow" in cls and sec not in names:
            names[sec] = (t, 0)
    site_names = {"header": "Top menu", "footer": "Footer", "aside": "Side contact button"}
    items, seen, edits = [], {}, []
    for tag, s, se, es, region, sec, cls in top:
        section = names.get(sec, ("", 0))[0] if region == "page" else site_names.get(scan.sec_tag.get(sec), "")
        inner = page_html[se:es]
        n = norm(inner, path)
        if not re.search(r"[A-Za-z0-9]", text_of(n)):
            continue
        k = key(n)
        scope = "*" if region == "site" else path
        edits.append((s, se, k, "data-e"))
        if (scope, k) in seen:
            seen[(scope, k)]["count"] += 1
            continue
        item = {"k": k, "scope": scope, "tag": tag, "cls": cls, "html": n, "section": section, "count": 1}
        seen[(scope, k)] = item
        items.append(item)
    images, iseen = [], set()
    for s, se, a in scan.imgs:
        src = re.sub(r"^(?:\.\./)+", "", (a.get("src") or "").split("?")[0])
        if not src.startswith("assets/"):
            continue
        k = key(src)
        edits.append((s, se, k, "data-i"))
        if k not in iseen:
            iseen.add(k)
            images.append({"k": k, "src": src, "alt": a.get("alt") or ""})
    out = page_html
    for s, se, k, attr in sorted(edits, key=lambda e: -e[0]):
        start_tag = out[s:se]
        if attr + '="' in start_tag:
            continue
        cut = se - (2 if start_tag.endswith("/>") else 1)
        out = out[:cut] + f' {attr}="{k}"' + out[cut:]
    return out, items, images


# ---------- applying saved edits (mirrors aegis/lib.php) ----------

def load_store(root):
    p = os.path.join(root, "aegis", "data", "content.php")
    if not os.path.exists(p):
        return {}
    raw = open(p, encoding="utf-8").read()
    if raw.startswith("<?php"):
        raw = raw.split("\n", 1)[1]   # skip the exit line
    return json.loads(raw) or {}


def apply(page_html, path, rel, items, store):
    """items: this page's items plus the site-wide ones, as produced by mark()."""
    texts = store.get("texts", {})
    doc = page_html
    for it in items:
        ov = texts.get(it["scope"], {}).get(it["k"])
        if not ov:
            continue
        pos = 0
        while True:
            span = _find_from(doc, it["k"], pos)
            if not span:
                break
            s, se, es, tag = span
            start_tag = re.sub(r"\shidden(?=[\s>])", "", doc[s:se])
            if ov.get("hidden"):
                start_tag = start_tag[:-1] + " hidden>"
            inner = denorm(ov["html"], path) if "html" in ov else doc[se:es]
            doc = doc[:s] + start_tag + inner + doc[es:]
            pos = s + len(start_tag) + len(inner)
    meta = store.get("meta", {}).get(path, {})
    if meta.get("title"):
        t = meta["title"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        doc = re.sub(r"<title>.*?</title>", f"<title>{t}</title>", doc, count=1, flags=re.S)
        doc = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + t, doc, count=1)
    if meta.get("description"):
        d = meta["description"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        doc = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + d, doc, count=1)
        doc = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + d, doc, count=1)
    for ik, alt in store.get("alts", {}).items():
        a = html.escape(alt, quote=True)
        doc = re.sub(r'(<img\b[^>]*\sdata-i="' + ik + r'"[^>]*>)',
                     lambda m: re.sub(r'\salt="[^"]*"', f' alt="{a}"', m.group(1)) if " alt=" in m.group(1)
                     else m.group(1).replace("<img", f'<img alt="{a}"', 1), doc)
    for src, ver in store.get("imgver", {}).items():
        doc = re.sub(r"((?:\.\./)*" + re.escape(src) + r")(?:\?v=\d+)?(?=[\"')\s,])", r"\1?v=" + str(ver), doc)
    return doc


def _find_from(doc, k, pos):
    m = re.compile(r'<([a-zA-Z0-9]+)\b[^>]*\sdata-e="' + k + r'"[^>]*>').search(doc, pos)
    if not m:
        return None
    tag = m.group(1).lower()
    depth, p = 1, m.end()
    pat = re.compile(r"<(/?)" + tag + r"\b[^>]*>", re.I)
    t = None
    while depth:
        t = pat.search(doc, p)
        if not t:
            return None
        depth += -1 if t.group(1) else 1
        p = t.end()
    return m.start(), m.end(), t.start(), tag


def write_manifest(root, pages, site_items):
    d = os.path.join(root, "aegis", "data")
    os.makedirs(d, exist_ok=True)
    data = {"pages": pages, "site": site_items}
    open(os.path.join(d, "manifest.php"), "w", encoding="utf-8", newline="\n").write(GUARD + json.dumps(data, ensure_ascii=False))
