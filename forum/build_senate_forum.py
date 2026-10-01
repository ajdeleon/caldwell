"""Build docs/senate_candidate_forum_2026.html from the Whisper transcript.

Usage (from the repo root):
    python forum/build_senate_forum.py [--transcript PATH]   # write the page
    python forum/build_senate_forum.py --list                # print numbered, timestamped segments

The transcript is Whisper's JSON output (whisper ... --output_format json), which lives
in the git-ignored videos/ directory. Answer boundaries below are 1-based Whisper segment
numbers, as shown by --list. Summaries and question text are maintained here by hand;
answer text is pulled from the transcript and lightly cleaned. Times are converted to
YouTube time: the local recording has 520s of extra pre-roll before the YouTube upload.
"""
import argparse, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / 'forum' / 'senate_forum_template.html'
OUTPUT = ROOT / 'docs' / 'senate_candidate_forum_2026.html'

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--transcript', type=Path, default=ROOT / 'videos' / 'transcript' / 'audio.json')
parser.add_argument('--list', action='store_true', help='print numbered segments in YouTube time and exit')
args = parser.parse_args()

OFFSET = 520
segs = json.load(open(args.transcript))['segments']

if args.list:
    for i, seg in enumerate(segs, 1):
        t = int(seg['start']) - OFFSET
        print(f"{i:5} [{'-' if t < 0 else ''}{abs(t) // 60}:{abs(t) % 60:02d}] {seg['text'].strip()}")
    raise SystemExit

# Segments dropped from answer text: moderator interjections inside an answer (172-173, 377, 966)
# and Whisper repetition artifacts confirmed by re-transcribing those passages (417-418, 768-770)
EXCLUDE = {377, 417, 418, 768, 769, 770, 966, 172, 173}

FIXES = [
    (r'\bJim (Rich|Ursch|Morris)\b', 'Jim Risch'),
    (r'\bPete Hexeth\b', 'Pete Hegseth'),
    (r'\bEd Galerain\b', 'Ed Gallrein'),
    (r'\bOverturning Citizens United\b', 'overturning Citizens United'),
    (r'\bemergency better tariff\b', 'emergency butter tariff'),
    (r'\b287G\b', '287(g)'),
    (r'\bA\.I\.', 'AI'),
    (r'\bDOBS\b', 'Dobbs'),
    (r'\bagency, you that mean ICE\b', 'agency, that means ICE'),
    (r'\bNextdoor\b', 'next door'),
]

def clean(t):
    t = re.sub(r'\b([Uu]m|[Uu]h),?\s+', '', t)
    # collapse stutters: "the the", "their their their", "to to"
    t = re.sub(r"\b(?!(?:that|had)\b)([\w']+)(\s+\1\b)+", r'\1', t, flags=re.I)
    for pat, rep in FIXES:
        t = re.sub(pat, rep, t)
    return re.sub(r'\s+', ' ', t).strip()

def yt(line):
    return max(0, int(segs[line - 1]['start']) - OFFSET)

def text(a, b, drop_trailing_thanks=True):
    lines = [segs[i - 1]['text'].strip() for i in range(a, b + 1) if i not in EXCLUDE]
    while drop_trailing_thanks and lines and re.fullmatch(r'(So )?[Tt]hank you\.?', lines[-1]):
        lines.pop()
    return clean(' '.join(lines))

A, F, L = 'achilles', 'fleming', 'loesby'

def ans(c, a, b, summary, start=None):
    return {'candidate': c, 'start': start if start is not None else yt(a), 'summary': summary, 'text': text(a, b)}

questions = [
  dict(id='tariffs', topic='Cost of living & tariffs', qline=56,
    context="Canada is Idaho's biggest customer, buying about $1.8 billion in Idaho goods in 2025 — roughly two-thirds of the state's exports. After U.S. tariffs of up to 50% on some Canadian goods took effect in August, Canada announced counter-tariffs.",
    question="What specific step would you take in the Senate to lower everyday costs for Idaho families, and should today's tariffs be kept, expanded, or rolled back?",
    answers=[
      ans(A, 59, 63, "Calls tariffs a tax paid by buyers that should be used only strategically (e.g., steel, cars, semiconductors). Says the trade war with Canada erased Idaho's trade surplus; would roll tariffs back and have Congress reclaim tariff authority from the White House."),
      ans(L, 65, 75, "Says fuel costs from the Iran war and other foreign-policy decisions raise living costs more than tariffs do; calls for ending foreign wars and deporting millions of people to ease competition for housing. Sees tariffs as a tool to bring back manufacturing, but says the current ones should be rolled back for a better strategy."),
      ans(F, 77, 98, "Criticizes the current tariffs and the conflict with Canada, calling Canada an ally. Names housing as her top affordability priority, citing large corporations buying mobile-home parks and raising lot rents, and calls for streamlining immigration for the workers who build homes and grow food."),
    ]),
  dict(id='money-in-politics', topic='Money in politics', qline=99,
    context="In this year's May primaries, political action committees spent more than $4.2 million backing Republican candidates. This spring the Idaho Legislature, with bipartisan support, asked Congress to propose a constitutional amendment restoring the power of Congress and the states to set rules on election spending.",
    question="What would you do in the Senate about outside and undisclosed money in our elections, and would you vote for the kind of constitutional amendment Idaho's Legislature has asked for?",
    answers=[
      ans(L, 104, 118, "Opposes campaign finance laws generally, saying they burden low-budget campaigns without showing who influences politicians. Calls Citizens United correctly decided on free-speech grounds; says the fix is shrinking federal power — including overturning Wickard v. Filburn — not a constitutional amendment."),
      ans(F, 120, 131, "Says her own analysis of FEC data as a data scientist showed money being funneled through county and state parties on both sides. Supports stronger laws against dark money and limits on campaign spending by individuals."),
      ans(A, 133, 151, "Supports the intent of the amendment (would need to see its text) and overturning Citizens United, focusing on dark-money groups. Says he is the only candidate in the race who has filed FEC reports and Senate financial disclosures; points to Montana and Hawaii redefining corporations' election powers as a model for Idaho."),
    ]),
  dict(id='public-financing', topic='Publicly funded campaigns', follow_up=True, qline=152,
    question="Are you in support of publicly funded campaigns? (One minute each.)",
    answers=[
      ans(L, 155, 159, "Opposes. Says it shouldn't be easy to file paperwork and receive tens of thousands of public dollars to campaign."),
      ans(F, 161, 170, "Undecided. Says events like this forum and new technology can help level the field without public money."),
      ans(A, 174, 186, "Sees merit in narrowing the gap between candidates. Says the absent incumbent has raised over $4 million, mostly from outside Idaho, while his own campaign has raised about $1.7 million without party funding."),
    ]),
  dict(id='national-security', topic='National security & war powers', qline=187,
    context="The Constitution gives Congress the power to declare war, but presidents of both parties have sent U.S. forces into combat without a declaration. In January a U.S. operation captured Venezuela's president; on February 28 the U.S. and Israel began striking Iran. In June both chambers of Congress passed a resolution directing the president to end hostilities with Iran — the first time since the War Powers Act became law in 1973.",
    question="What do you see as the greatest threat to America's security, and when should the United States use military force — including what role the Senate should play in that decision?",
    answers=[
      ans(F, 197, 213, "Sees internal division, fueled by foreign propaganda, as the greatest threat. Supports the Defend the Guard bill (no overseas Guard deployments without a declaration of war), calls the Iran war unnecessary, criticizes Defense Secretary Hegseth, and says Congress must reassert its role. Describes what is happening in Israel's conflict as genocide."),
      ans(A, 215, 234, "Agrees the biggest threat is internal: corruption, partisanship and senators not doing their constitutional duty. Drawing on two Persian Gulf deployments, faults Sen. Risch as Foreign Relations chair for holding no hearings on Venezuela, Caribbean boat strikes or the Iran war."),
      ans(L, 236, 246, "Says the greatest threat is tens of millions of people in the U.S. whose primary loyalty is to another country, and calls for sending them home. Would defund foreign bases to bring troops home, and says the president should be impeached for sending troops to fight for other countries."),
    ]),
  dict(id='ukraine', topic='Ukraine', follow_up=True, qline=247,
    context="More than four years into Russia's full-scale invasion of Ukraine, U.S.-mediated talks still haven't produced a ceasefire.",
    question="What should U.S. policy toward Ukraine be — continued military aid, pressure on Kyiv to accept a deal, tougher sanctions on Russia, or something else?",
    answers=[
      ans(F, 254, 275, "Supports Ukraine and sanctions on Russia, noting Ukraine gave up its nuclear weapons in exchange for security commitments. Raises concerns about depleted-uranium munitions and warns against entering the AI era with a \"war mindset.\""),
      ans(A, 277, 281, "Calls Ukrainians freedom fighters; would continue support and increase economic pressure on Russia. Says the war ends when Russia stops fighting."),
      ans(L, 283, 307, "Says Ukraine cannot win and that the U.S. and NATO discouraged an early deal; would stop sending weapons and push Ukraine to negotiate with Moscow. Calls for the U.S. to leave NATO."),
    ]),
  dict(id='immigration', topic='Immigration & the workforce', audience=True, qline=308,
    context="Last October, more than 200 officers converged on a horse-racing event in Wilder attended by about 400 people. The FBI said it was investigating illegal gambling; 105 people were detained on immigration violations. A federal lawsuit over the raid is pending in Boise.",
    question="What should immigration policy look like for a community like Canyon County, and what are your views on legal pathways for the workers Idaho farms and dairies rely on?",
    answers=[
      ans(A, 318, 337, "Says immigration is a federal issue and he voted against a state immigration bill as a legislator. Proposes four steps — a secure border (credits the Trump administration), a working visa system, a compassionate asylum system, and citizenship for long-time residents — passed on a bipartisan basis."),
      ans(L, 339, 350, "Argues immigrant labor undercuts wages and opportunities for young Americans. Calls for enforcing borders and returning people to their home countries, while keeping immigration easy for cases like marrying an American."),
      ans(F, 352, 371, "Calls America a nation of immigrants and cites the Bible's protection of immigrants. Says the current system is backlogged and cruel by design, cites lower crime rates among immigrants, and calls for streamlining the process."),
    ]),
  dict(id='local-enforcement', topic='Local police & ICE (287(g))', follow_up=True, qline=373,
    question="Should local police and sheriffs help carry out federal immigration enforcement, or should that be left to federal agents?",
    answers=[
      ans(A, 376, 390, "Prefers leaving it to local governments; has argued Idaho police shouldn't partner with ICE until ICE follows the law (judicial warrants, body cameras). Sees a narrow role in removing undocumented people convicted of crimes."),
      ans(L, 393, 405, "Says people who entered without permission are invaders; local police should work with federal agents to remove them with as little violence as possible — not only those charged with crimes."),
      ans(F, 408, 430, "Opposes federal agencies having power over local ones and calls sanctuary cities \"constitutional cities.\" Says each community should decide whether to turn someone over, citing a case she sees as an overly broad definition of \"criminal.\""),
    ]),
  dict(id='health-care', topic='Health care', qline=431,
    context="Enhanced premium tax credits for marketplace insurance expired at the end of 2025; Idaho's exchange estimates about 30,000 more Idahoans will go uninsured. Starting in January, Idahoans on Medicaid expansion must document at least 80 hours a month of work, school or volunteering — affecting roughly 85,000 people.",
    question="What would you do to make health coverage affordable for working Idahoans and keep rural hospitals and clinics open?",
    answers=[
      ans(L, 441, 456, "Would repeal medical licensing laws, which he says created today's insurance system, and end Medicaid, Medicare and Social Security as wealth transfers. Says care gets cheaper when government stops paying for it and lobbies stop restricting access."),
      ans(F, 458, 485, "Says a healthy population works better and calls for compassion. Highlights direct primary care paired with catastrophic insurance, criticizes prescription-drug price manipulation, and rejects describing basic care as a wealth transfer."),
      ans(A, 489, 521, "Opposes unlicensed medicine and says the ACA isn't working. Backs a bipartisan bill to break up large health-care companies, most-favored-nation drug pricing, requiring large employers to cover part-time workers, and a public option."),
    ]),
  dict(id='abortion', topic='Abortion & Proposition 1', follow_up=True, qline=522,
    context="On November 3, Idaho voters will decide Proposition 1, a citizen initiative on abortion access and protections for contraception and IVF.",
    question="After Dobbs, should there be a national abortion law — either setting national limits or protecting access nationwide — or should this stay with the states? (One minute each.)",
    answers=[
      ans(L, 534, 552, "Considers abortion homicide, permissible only in cases of self-defense. Agrees with Dobbs that it is a state issue, not a federal one."),
      ans(F, 555, 576, "Torn between state and federal roles; cites her niece's delayed emergency care and her own experience as a rape survivor. Leans toward federal protections for the health and life of the mother."),
      ans(A, 580, 588, "Supports Proposition 1; says government shouldn't come between a woman, her doctor and her family. Expects the issue to remain at the state level."),
    ]),
  dict(id='budget', topic='Budget & national debt', qline=590,
    context="The Congressional Budget Office projects interest on the national debt will reach about $1 trillion this year — more than the government spends on defense or Medicaid — and federal agencies have been through three funding lapses totaling 123 days over the past year.",
    question="Name one specific spending cut and one revenue change you would support to bring deficits down.",
    answers=[
      ans(F, 603, 630, "Revenue: streamline immigration so more people work and pay taxes legally, citing a Cato study. Cut: offensive military spending such as the Iran war. Adds that Medicaid spending helps keep people healthy enough to work."),
      ans(A, 633, 658, "Notes the debt grew from $10 trillion to $40 trillion during Sen. Risch's tenure. Cut: reject the proposed defense increase from $1 trillion to $1.5 trillion. Revenue: close corporate loopholes (about $300 billion) and tax-avoidance strategies used by high earners."),
      ans(L, 660, 681, "Says the problem is spending, not revenue. Would end Medicare, Medicaid and Social Security, end foreign wars, bring troops home, and cut regulations and taxes."),
    ]),
  dict(id='social-security', topic='Social Security', follow_up=True, qline=682,
    context="Social Security's retirement trust fund is projected to run short in the early 2030s, which would trigger automatic benefit cuts.",
    question="Would you raise or lift the cap on payroll taxes, raise the retirement age, trim benefits for higher earners, or do something else?",
    answers=[
      ans(F, 690, 718, "Would grow revenue by removing barriers for small businesses and improving health so more people can work. Calls for investing in families, children and education, using the LDS Church's welfare model as an example."),
      ans(A, 722, 741, "Would lift the payroll-tax cap (currently $184,500) entirely, which he says covers about 73% of the gap, and tax investment income like wages for the rest. Opposes trimming benefits."),
      ans(L, 744, 773, "Calls Social Security a Ponzi scheme; would cut benefits and raise the retirement age over time toward abolishing the system, relying on families and voluntary generosity instead."),
    ]),
  dict(id='path-to-victory', topic='Path to winning', audience=True, qline=775,
    context="Republicans have not lost a U.S. Senate race in Idaho since 1974. The Democratic nominee ended his campaign this summer, so every candidate on stage is running outside the two major parties.",
    question="What is your realistic path to winning, and which voters do you still need to persuade?",
    answers=[
      ans(A, 790, 823, "Cites 16 months and 300+ events around the state, and says about 65% of Idahoans identify as or lean independent. Says his polling shows him ahead of Sen. Risch and calls this the best chance in 50 years to defeat him."),
      ans(L, 825, 843, "Says he expects Sen. Risch to win and is running for other goals: sending national Republicans a message about Israel, Ukraine and federal spending."),
      ans(F, 846, 874, "Points to talking with thousands of voters while gathering signatures for the medical cannabis initiative, and says she trusts Idahoans to research the candidates. Criticizes the pressure on Democrat David Roth to leave the race."),
    ]),
  dict(id='vacancy-law', topic='Senate vacancy law (Idaho Code 59-910)', qline=876,
    context="Under Idaho Code § 59-910, if a U.S. Senate vacancy occurs within 30 days of an election, no election for that seat is held in the general election — arguably letting the governor appoint the next senator if the incumbent retired in that window.",
    question="Is this a conspiracy theory or hardball politics? How likely is something like this?",
    answers=[
      ans(L, 894, 907, "Would want to read the precedents first; expects a court challenge if it were tried. Thinks it more likely Sen. Risch wins, retires in a year or two, and Gov. Little appoints a successor."),
      ans(F, 909, 930, "Says the idea is new to her and alarming; doubts Idahoans would accept it and expects public outrage, though she isn't predicting it will happen."),
      ans(A, 932, 946, "Calls the 1917 statute unconstitutional under the 17th Amendment, notes roughly 100,000 ballots have already been mailed, and warns the maneuver could be repeated indefinitely."),
    ]),
]

lightning = dict(id='lightning-round', topic='Lightning round', qline=947, items=[
  dict(question="Should members of Congress be barred from trading individual stocks?", qline=952, answers=[
    ans(F, 953, 953, "Yes"), ans(A, 955, 955, "Yes"), ans(L, 957, 957, "No")]),
  dict(question="Do you support term limits for members of Congress?", qline=958, answers=[
    ans(A, 960, 961, "Yes — including for the Supreme Court; pledges to serve at most two terms"),
    ans(L, 963, 963, "No"),
    ans(F, 965, 971, "Undecided; would step down after accomplishing specific goals")]),
  dict(question="Should marijuana be legalized at the federal level?", qline=974, answers=[
    ans(L, 975, 978, "Torn — yes philosophically, but cites Colorado's experience"),
    ans(F, 980, 983, "Undecided federally; supports medical cannabis in Idaho"),
    ans(A, 985, 985, "Medical cannabis only")]),
  dict(question="Do you support background checks on all gun sales, including private sales?", qline=987, answers=[
    ans(F, 989, 989, "Not for private sales"),
    ans(A, 991, 991, "Yes", start=yt(990)),
    ans(L, 993, 993, "Would repeal the National Firearms Act of 1934")]),
])
for it in lightning['items']:
    it['start'] = yt(it.pop('qline'))

closing = dict(id='closing', topic='Closing statements', qline=996,
  question="Give us your final argument for your campaign. (Two minutes each.)",
  answers=[
    ans(A, 1000, 1030, "Says Idahoans want someone who will work across the aisle. Criticizes Sen. Risch for voting with party leadership 99.7% of the time and holding no public town halls; cites his own farm upbringing, Army service, tech career, teaching and legislative experience, and says an independent vote would carry extra weight in a closely divided Senate."),
    ans(L, 1032, 1052, "Says the key question is whom the government serves. Argues Democrats serve minority \"client groups\" and Republicans serve the \"Zionist lobby,\" H-1B employers and corporate donors; asks voters to punish both parties and reclaim \"our homeland.\""),
    ans(F, 1054, 1084, "Describes her background: raised on an Oregon farm, a single mother of four in Idaho, and a degree in IT management. Priorities include limits on AI, data centers and mass surveillance, opposition to authoritarianism in both parties, women's issues including the SAVE Act, and forest management."),
  ])

for q in questions + [lightning, closing]:
    q['start'] = yt(q.pop('qline'))

data = {
  'event': {
    'title': 'U.S. Senate Candidate Forum',
    'race': 'Idaho — U.S. Senate, 2026',
    'date': '2026-09-30',
    'date_label': 'September 30, 2026',
    'location': 'Caldwell City Hall, Caldwell, Idaho',
    'youtube_id': '12DyOv_H4ns',
    'election_label': 'Election Day: November 3, 2026',
    'moderators': [
      {'name': 'McKay Cunningham', 'role': 'Director, Master of Applied Public Policy, College of Idaho'},
      {'name': 'Latonia Haney Keith', 'role': 'Dean of Graduate Studies & Chief Strategy Officer, College of Idaho'},
    ],
    'sponsors': [
      {'name': 'League of Women Voters of Idaho', 'url': 'https://www.lwvid.org/'},
      {'name': 'Caldwell Chamber of Commerce', 'url': 'https://www.caldwellchamber.org/'},
      {'name': 'College of Idaho', 'url': 'https://www.collegeofidaho.edu/'},
      {'name': 'AAUW Idaho', 'url': 'https://aauw-id.aauw.net/', 'role': 'co-sponsor'},
    ],
    'segments': [
      {'label': 'Welcome & sponsors', 'start': yt(28)},
      {'label': 'Forum rules', 'start': yt(34)},
      {'label': 'Moderator introductions', 'start': yt(50)},
    ],
  },
  'candidates': [
    {'id': A, 'name': 'Todd Achilles', 'party': 'Independent', 'url': 'https://www.achillesforidaho.com/'},
    {'id': F, 'name': 'Natalie Fleming', 'party': 'Independent', 'url': 'https://nataliefleming.info/'},
    {'id': L, 'name': 'Matt Loesby', 'party': 'Libertarian', 'url': 'https://www.loesby.us/'},
  ],
  'absent': [
    {'name': 'Jim Risch', 'party': 'Republican (incumbent)', 'url': 'https://senatorrisch.com/', 'note': 'Invited; declined to participate.', 'start': yt(32)},
  ],
  'questions': questions,
  'lightning': lightning,
  'closing': closing,
}

js = json.dumps(data, indent=1, ensure_ascii=False).replace('</', '<\/')
OUTPUT.write_text(TEMPLATE.read_text().replace('/*FORUM_DATA*/', js))
print(f"wrote {OUTPUT.relative_to(ROOT)} ({sum(len(q['answers']) for q in questions + [closing])} answers)")
