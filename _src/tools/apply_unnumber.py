"""One-off: drop numbering from unordered lists (service cards, Why Aegis reasons, service eyebrows). Sequences keep numbers."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "_src", "pages")
def rw(name, fn):
    p = os.path.join(P, name); s = open(p, encoding="utf-8").read(); n = fn(s)
    assert n != s, name; open(p, "w", encoding="utf-8").write(n)
def section(s, eyebrow):
    a = s.rfind("<section", 0, s.index(eyebrow)); b = s.index("</section>", a) + 10
    return a, b
def strip_in(s, eyebrow, pattern):
    a, b = section(s, eyebrow)
    return s[:a] + re.sub(pattern, "", s[a:b]) + s[b:]
# home: service cards and Why Aegis reasons
rw("index.html", lambda s: strip_in(strip_in(s, '<span class="eyebrow">Our services</span>', r'<span class="num">0\d</span>'),
                                    '<span class="eyebrow">Why Aegis</span>', r'<span class="n">0\d</span>'))
# IPO: Why Aegis for your IPO reasons
rw("services-ipo-communications.html", lambda s: strip_in(s, 'Why Aegis for your IPO</span>', r'<span class="n">0\d</span>'))
# service eyebrows: drop "Service · NN · " prefixes
for f in ["services-investor-relations.html", "services-public-relations.html", "services-ipo-communications.html", "services-events.html", "services-creative-digital.html"]:
    rw(f, lambda s: re.sub(r'Service · \d\d(?: and \d\d)? · ', '', s))
print("unnumbered")
