"""One-off: plain-language pass on copy that was written for the site (not taken from the decks).
Deck-approved lines are left untouched."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "_src", "pages")

R = {
"index.html": [
("Investor relations and public relations run as one programme, so your story stays consistent across every announcement.",
 "We run investor relations and public relations as one programme, so your company tells the same story in every announcement."),
("Best started when your principal adviser is appointed, not at approval", "Best to start when you appoint your principal adviser, not after approval"),
("Perception audit, corporate exercises, crisis readiness, annual obligations", "How the market sees you, corporate exercises, crisis plans, annual report and AGM"),
("Management and the board bring strategy, results and corporate developments. The market decides what it believes. Aegis sits between the two: translating corporate priorities into a coherent market narrative, and bringing perception and feedback back inward.",
 "Management and the board set the strategy and deliver the results. The market decides what it believes. Aegis sits between the two. We turn your priorities into a clear story for the market, and bring back what the market thinks."),
("Whether you are preparing to list or already public, the first conversation is the fastest way to see how we would work with you.",
 "Preparing to list or already listed, a first conversation is the quickest way to see how we would work together."),
],
"about.html": [
("Aegis Communication is a Kuala Lumpur-based firm working with public listed companies and pre-IPO companies in Malaysia. Over 17 years and more than 30 public listed companies, our work has spanned the Main Market and the ACE Market, companies from RM100 million to RM5 billion in market capitalisation, and the local and regional investment community.",
 "Aegis Communication is a Kuala Lumpur firm. We work with public listed companies and pre-IPO companies in Malaysia. Over 17 years we have served more than 30 public listed companies on the Main Market and the ACE Market, from RM100 million to RM5 billion in market value, reaching investors in Malaysia and across the region."),
("Aegis pairs senior advisory with a focused execution team across strategy and IR content, client and media engagement, and operations. The people who set your strategy are the people in the room.",
 "Senior advisers lead every mandate, backed by a team that handles IR content, media and client engagement, and operations. The people who set your strategy are the people in the room."),
],
"approach.html": [
("Results are sound, but the multiple lags the sector. The investment case has not been retold since the business changed.",
 "Results are sound, but the share price trails the sector. The company has changed and the market has not been told the new story."),
("Analysts who initiated at listing have moved on. No independent view of value is reaching fund managers.",
 "The analysts who covered you at listing have moved on. Fund managers no longer get an independent view of what the company is worth."),
("Few institutional holders, no foreign funds, liquidity thin. Non-deal roadshows to domestic anchors and regional funds have not been run in years.",
 "Few institutional holders, no foreign funds, and shares that trade thinly. Nobody has taken the company to local and regional funds in years."),
("Acquisition, placement, diversification, Main Market transfer or rebrand. Each needs messaging that clears counsel and lands with the market.",
 "An acquisition, a placement, a new business line, a Main Market transfer or a rebrand. Each needs a message that lawyers will clear and the market will understand."),
("A query, a headline, a forum thread. Nobody owns the response plan, and the first 24 hours set the story.",
 "A Bursa query, a bad headline, a forum thread. Nobody owns the response, and the first 24 hours decide the story."),
("Before any programme, Aegis interviews investors, analysts, media and staff, scores the company's risk profile and maps the shareholder and stakeholder base. You see how the market reads you today, then decide the programme. For companies with advisers already in place, this is the lowest-commitment way to start.",
 "Before any programme, Aegis talks to your investors, analysts, media and staff, scores your risk profile and maps who holds your shares and who else matters. You see how the market reads you today, then decide what to do next. If you already have advisers, this is the simplest way to start."),
("Where a corporate communications or IR function exists, Aegis works inside it: shared playbook, message bank and approval matrix, one counterpart on each side. Where there is none, Aegis acts as the function, reporting to the CEO and CFO. Either way, experienced advice is delivered directly, with no layers and no handoffs.",
 "If you have a corporate communications or IR team, Aegis works inside it: one shared playbook, message bank and approval matrix, and one contact on each side. If you have none, Aegis acts as that team and reports to the CEO and CFO. Either way, you get experienced advice directly, with no layers and no handoffs."),
("Bursa announcement support: Aegis supports the narrative and the communications that follow an announcement. The company secretary remains the announcing party. Counterparts, sync cadence and escalation are set out under client-Aegis closeness below.",
 "Bursa announcement support means Aegis helps with the story and the communications that follow an announcement. The company secretary remains the announcing party. Who you deal with, how often you meet and how issues are escalated are set out under client-Aegis closeness below."),
("Under NDA and the insider list: rationale, key messages, investor and media Q&amp;A bank and holding statements prepared with counsel and the adviser. Nothing moves outside the information-control circle.",
 "Under NDA and on the insider list, Aegis prepares the reasons for the deal, the key messages, the investor and media Q&amp;A and the holding statements, with your lawyers and adviser. Nothing leaves the circle of people allowed to know."),
("Exchange announcement first. Press release, analyst note and media follow-up released together, timed for exposure and impact. Spokespeople briefed on what can and cannot be said.",
 "The Bursa announcement goes out first. The press release, analyst note and media follow-up go out together, timed for the most attention. Spokespeople are briefed on what they can and cannot say."),
("Analyst and fund manager briefing, media interviews, coverage tracking, shareholder update ahead of any EGM. Perception checked and the narrative adjusted before the next milestone.",
 "Analyst and fund manager briefing, media interviews, tracking of coverage, and a shareholder update before any EGM. We check how it landed and adjust the story before the next step."),
("a thread on an investor forum. Tier 3 readiness is built before it is needed.", "a thread on an investor forum. The plan for these is built before it is needed."),
("Tracking whether the correction has landed, in coverage and on forums", "Checking that the correct story has landed, in the press and on forums"),
("Re-tier, review and fold the lesson into the playbook", "Review, reset the risk tier and add the lesson to the playbook"),
("The fixed points of a listed company's year, treated as communications rather than compliance filings.",
 "The fixed dates in a listed company's year, treated as chances to tell your story rather than filings to get done."),
("Chairman's and CEO's statements, management discussion and analysis, and the investment case told consistently with the IR deck and results releases. Design and production through the creative team.",
 "Chairman's and CEO's statements, the management discussion and analysis, and the investment case, all told the same way as your IR deck and results releases. Design and production by the creative team."),
("Sustainability statement narrative aligned to Bursa reporting requirements and the Malaysian Code on Corporate Governance. Engagement with ESG raters and proxy advisers as part of the IR constituencies.",
 "Sustainability statement written to Bursa reporting requirements and the Malaysian Code on Corporate Governance. We also engage ESG raters and proxy advisers as part of your investor audience."),
("Shareholder Q&amp;A preparation, including anticipated questions from minority shareholder groups, board briefing, event management and media communication on the day.",
 "Shareholder Q&amp;A preparation, including the questions minority shareholder groups are likely to ask, a board briefing, event management and media communication on the day."),
],
"services-investor-relations.html": [
("For newly listed and established public companies: structured, well-prepared engagement with the investors, analysts and fund managers who set your valuation, run on a monthly retainer scoped to your results calendar.",
 "For newly listed and established public companies. Well-prepared meetings and briefings with the investors, analysts and fund managers who set your share price, run on a monthly retainer built around your results calendar."),
("The first year as a public company is where the equity story is either confirmed or forgotten. Five things go wrong most often.",
 "In the first year as a public company, the market either confirms your story or forgets it. Five things go wrong most often."),
("Balloting brings retail shareholders. Without institutional engagement, liquidity and valuation rest on sentiment.",
 "Balloting brings retail shareholders. Without institutional investors, trading and share price rest on sentiment."),
("A first quarterly announcement with no narrative around it is read by the market, not explained to it.",
 "A first quarterly result with no explanation around it is read by the market, not explained to it."),
("Continuous disclosure, quiet periods and selective-disclosure discipline arrive on day one, with no rehearsal.",
 "Disclosure rules, quiet periods and limits on what can be said in private all apply from day one, with no rehearsal."),
("A monthly retainer programme, scoped to your results calendar and corporate pipeline, with one accountable team across IR, media and events. Project work such as an investor day or a corporate exercise is scoped separately.",
 "A monthly retainer built around your results calendar and upcoming corporate events, with one accountable team across IR, media and events. Projects such as an investor day or a corporate exercise are quoted separately."),
("Information requests from analysts and investors coordinated and answered within disclosure rules.",
 "Questions from analysts and investors answered within disclosure rules."),
("Perception and coverage reviewed with management. Findings feed the next quarter's messages.",
 "Coverage and investor feedback reviewed with management. What we learn shapes the next quarter's messages."),
("Post-listing coverage round-up, investor update, research engagement opened with research houses.",
 "Round-up of listing coverage, an investor update, and first contact with research houses."),
("The quarterly rhythm above, each time with a sharper narrative and a wider audience.",
 "The quarterly rhythm above, each time with a sharper story and a wider audience."),
("AGM communications and event support, annual report narrative, shareholder Q&amp;A preparation.",
 "AGM communications and event support, the annual report story, and shareholder Q&amp;A preparation."),
("Register mix, analyst coverage, liquidity and valuation versus peers reviewed. Programme reset for year two.",
 "We review who holds your shares, analyst coverage, trading volume and valuation against peers, then reset the programme for year two."),
("Briefings and one-to-one meetings follow the Bursa announcement. Aegis works to continuous disclosure, selective-disclosure discipline and quiet periods, so no price-sensitive information is given in private that has not been announced.",
 "Briefings and one-to-one meetings happen after the Bursa announcement. Aegis follows the disclosure rules and quiet periods, so nothing price-sensitive is shared in private before it is announced."),
],
"services-ipo-communications.html": [
("The campaign itself runs from approval to listing day. The equity story, the spokespeople and the message bank are built in the quiet months before that, so nothing is improvised once the timetable is public.",
 "The campaign runs from approval to listing day. The story, the spokespeople and the approved messages are built in the quiet months before that, so nothing is made up on the spot once the timetable is public."),
("Adviser appointed, submission being prepared. Aegis learns the business, drafts the equity story and key messages, maps investors and media, and sets the information protocol with the company secretary.",
 "Your adviser is appointed and the submission is being prepared. Aegis learns the business, drafts the story and key messages, maps the investors and media that matter, and agrees with the company secretary who may know what, and when."),
("Then the retainer carries the story into the aftermarket.", "Then the retainer carries the story into life as a listed company."),
("Aegis runs the communications workstream beside them: one point of contact, one approval route agreed with the adviser and counsel, and releases timed to Bursa announcements rather than ahead of them.",
 "Aegis runs communications beside them: one point of contact, one approval route agreed with the adviser and lawyers, and releases that follow Bursa announcements, never ahead of them."),
("Publicity before prospectus registration is restricted under Securities Commission and Bursa Malaysia requirements. Aegis plans every release, interview and digital post around the adviser's guidance on what can be said, and when, so that visibility never puts the timetable at risk.",
 "Before the prospectus is registered, what a company may say in public is limited by Securities Commission and Bursa Malaysia rules. Aegis plans every release, interview and social post around the adviser's guidance on what can be said and when, so publicity never puts the timetable at risk."),
("Disclosure rules, insider list and sign-off. Aegis drafts inside that protocol and clears releases through it.",
 "Disclosure rules, the insider list and sign-off. Aegis drafts within those rules and clears every release through them."),
("Introduce a listing candidate early, before submission, and the communications plan is built to your timetable rather than retrofitted to it.",
 "Introduce a listing candidate early, before submission, and the communications plan is built around your timetable from the start."),
("Every release, interview brief and digital post stays within the registered prospectus and the Bursa announcements. Publicity before registration follows Securities Commission and Bursa Malaysia requirements and the adviser's guidance. The media Q&amp;A bank is pre-cleared through the adviser and counsel before any spokesperson uses it.",
 "Every release, interview brief and social post stays within the registered prospectus and the Bursa announcements. Publicity before registration follows Securities Commission and Bursa Malaysia rules and the adviser's guidance. The media Q&amp;A is cleared by the adviser and lawyers before any spokesperson uses it."),
],
"services-public-relations.html": [
("Bursa announcement support covers the narrative and the press release, briefing and Q&amp;A that follow an announcement. The company secretary remains the announcing party.",
 "Bursa announcement support means Aegis helps with the story, the press release, the briefing and the Q&amp;A that follow an announcement. The company secretary remains the announcing party."),
("Working relationships span English, Bahasa Malaysia and Chinese-language media, so that one announcement lands consistently across every title.",
 "We work with English, Bahasa Malaysia and Chinese-language media, so one announcement reads the same in every title."),
],
"services-creative-digital.html": [
("Most clients engage creative and digital as part of an IR or IPO programme. Each can also be mandated on its own.",
 "Most clients take creative and digital as part of an IR or IPO programme. Each can also be engaged on its own."),
],
}

n = 0
for f, pairs in R.items():
    p = os.path.join(P, f); s = open(p, encoding="utf-8").read()
    for old, new in pairs:
        assert old in s, (f, old[:60])
        s = s.replace(old, new); n += 1
    open(p, "w", encoding="utf-8").write(s)
print("replacements:", n)
