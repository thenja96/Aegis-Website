"""One-off: applies the CEO-review changes (nav, headline, IPO timing + adviser fit, approach lede, team cards)."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)

def rw(p, fn):
    s = open(p, encoding="utf-8").read(); n = fn(s); assert n != s, p
    open(p, "w", encoding="utf-8").write(n)

# 9. nav: IPO stays top-level, dropdown keeps the other four
rw("_src/build.py", lambda s: s.replace('        ("IPO Communications", "services/ipo-communications.html"),\n', ''))

# 7. shorter hero headline + 1. timing hint in hero panel
def home(s):
    s = s.replace('<h1>Your capital market communications partner for public listed companies and pre-IPO companies.</h1>\n      <p>Aegis brings investor relations and public relations together as one programme, so that listed and IPO-bound companies are understood by investors, visible in the media and consistent across every announcement.</p>',
                  '<h1>Get your company understood by investors, analysts and the media.</h1>\n      <p>Aegis Communication is the capital market communications partner for public listed companies and pre-IPO companies in Malaysia. Investor relations and public relations run as one programme, so your story stays consistent across every announcement.</p>')
    s = s.replace('<li><a href="services/ipo-communications.html">Preparing to list</a><small>IPO communications, from approval to listing day</small></li>',
                  '<li><a href="services/ipo-communications.html">Preparing to list</a><small>Best started when your principal adviser is appointed, not at approval</small></li>')
    return s
rw("_src/pages/index.html", home)

# 3. plain-language lede on Approach
rw("_src/pages/approach.html", lambda s: s.replace('<p>IR and PR run as a single engine: one story, one approval gate, one timed calendar, one feedback loop.</p>',
    '<p>In practice: one approved company story, one sign-off route your board controls, one calendar for investor and media releases, and a quarterly check on what the market actually heard. IR and PR run as a single engine.</p>'))

# 1 + 2. IPO page: when to engage, and how Aegis fits with the other advisers
block = '''<section class="section">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">When to bring Aegis in</span>
      <hr class="rule">
      <h2>Earlier than the prospectus. Ideally when the principal adviser is appointed.</h2>
      <p class="lede">The campaign itself runs from approval to listing day. The equity story, the spokespeople and the message bank are built in the quiet months before that, so nothing is improvised once the timetable is public.</p>
    </div>
    <div class="steps reveal">
      <div class="step"><span class="n">A</span><h3>Pre-submission</h3><p>Adviser appointed, submission being prepared. Aegis learns the business, drafts the equity story and key messages, maps investors and media, and sets the information protocol with the company secretary.</p></div>
      <div class="step"><span class="n">B</span><h3>Submission to approval</h3><p>Materials built and rehearsed in private: IR deck, fact sheet, Q&amp;A bank, holding statements. Management coached. No public activity until the approval is announced.</p></div>
      <div class="step"><span class="n">C</span><h3>Approval to listing</h3><p>The five-milestone campaign below: approval release, underwriting, prospectus launch, balloting, listing ceremony. Then the retainer carries the story into the aftermarket.</p></div>
    </div>
    <div class="split" style="margin-top:56px">
      <div class="reveal">
        <span class="eyebrow">Working alongside your advisers</span>
        <hr class="rule">
        <h2>One communications workstream inside the listing team.</h2>
        <p>Your principal adviser, underwriter, lawyers, company secretary and auditors own the listing process. Aegis runs the communications workstream beside them: one point of contact, one approval route agreed with the adviser and counsel, and releases timed to Bursa announcements rather than ahead of them.</p>
        <p>Publicity before prospectus registration is restricted under Securities Commission and Bursa Malaysia requirements. Aegis plans every release, interview and digital post around the adviser's guidance on what can be said, and when, so that visibility never puts the timetable at risk.</p>
      </div>
      <div class="grid reveal">
        <div class="card"><h4>Principal adviser and underwriter</h4><p>Timetable, approvals and the sequence of announcements. Aegis aligns the communications calendar to theirs.</p></div>
        <div class="card"><h4>Lawyers and company secretary</h4><p>Disclosure rules, insider list and sign-off. Aegis drafts inside that protocol and clears releases through it.</p></div>
        <div class="card"><h4>Management</h4><p>The story and the decisions. Aegis prepares spokespeople, materials and the rooms where they will be tested.</p></div>
      </div>
    </div>
  </div>
</section>

<section class="section light">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Aegis roadmap</span>'''
rw("_src/pages/services-ipo-communications.html", lambda s: s.replace('<section class="section light">\n  <div class="container">\n    <div class="section-head reveal">\n      <span class="eyebrow">Aegis roadmap</span>', block, 1))

# 4. team cards: photo slot per person (drop a file at assets/team/<slug>.jpg), one factual line each
ONERR = '''onerror="this.style.display='none';this.nextElementSibling.style.display='flex'"'''
people = [
    ("jason-fong", "JF", "Jason Fong Jian Sheng", "Founder and Executive Director", "Founded Aegis and leads every mandate. 17+ years in corporate investor relations and public relations across Bursa Malaysia listed and pre-IPO companies."),
    ("reiko-lai", "RL", "Reiko Lai", "Executive Director", "Co-leads client mandates with Jason and is a direct contact for IR, PR and IPO engagements."),
    ("aden-then", "AT", "Aden Then Jian An", "Senior Executive", "Strategy and IR content: investor materials, results communication and research."),
    ("ryan-low", "RL", "Ryan Low Sze Quan", "Senior Executive", "Client and media engagement: press releases, media liaison and briefings."),
    ("cherise-lai", "CL", "Cherise Yenyen Lai", "Operations and Strategic Coordination Lead", "Operations, event coordination and the engagement timeline."),
    ("wong-seng-chun", "WS", "Wong Seng Chun", "Senior Marketing Strategist", "Digital amplification, campaigns and creative content."),
]
cards = "\n".join(
    f'      <div class="person"><img class="headshot" src="assets/team/{slug}.jpg" alt="{name}" {ONERR}><div class="avatar" aria-hidden="true" style="display:none">{ini}</div><div><b>{name}</b><span>{title}</span><small>{bio}</small></div></div>'
    for slug, ini, name, title, bio in people)
team = f'''    <div class="team reveal">
{cards}
    </div>
    <p class="disclaimer" style="margin-top:22px">Aegis pairs senior advisory with a focused execution team across strategy and IR content, client and media engagement, and operations. The people who set your strategy are the people in the room.</p>
'''
def about(s):
    a = s.index('    <div class="team reveal">'); b = s.index('    </div>\n  </div>\n</section>', a) + len('    </div>\n')
    return s[:a] + team + s[b:]
rw("_src/pages/about.html", about)

# css for headshots and bio line
rw("assets/style.css", lambda s: s.replace('.person b{display:block;color:var(--navy);font-size:1.02rem}',
    '.person{align-items:flex-start}\n.headshot{width:72px;height:72px;border-radius:50%;object-fit:cover;flex:none}\n.person small{display:block;color:var(--slate);font-size:.88rem;margin-top:8px;line-height:1.5}\n.person b{display:block;color:var(--navy);font-size:1.02rem}'))
print("edits ok")
