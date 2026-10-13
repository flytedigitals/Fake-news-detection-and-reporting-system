# ============================================================
# ONLINE VERIFIER - FINAL VERSION
# Organization News: ANY article on official site = VERIFIED
# Government News: MUST confirm the specific claim
# General News: ANY trusted source = VERIFIED
# ============================================================

import re
import requests
from ddgs import DDGS

# ============================================================
# ORGANIZATION MAP: keyword -> (domain, report_url)
# ============================================================

ORGANIZATION_MAP = {
    "firstbank": ("firstbanknigeria.com", "https://www.firstbanknigeria.com/contact-us/"),
    "zenithbank": ("zenithbank.com", "https://www.zenithbank.com/contact/"),
    "gtbank": ("gtbank.com", "https://www.gtbank.com/contact-us/"),
    "accessbank": ("accessbankplc.com", "https://www.accessbankplc.com/contact-us"),
    "fidelitybank": ("fidelitybank.ng", "https://www.fidelitybank.ng/contact-us/"),
    "sterlingbank": ("sterling.ng", "https://www.sterling.ng/contact-us/"),
    "uba": ("ubagroup.com", "https://www.ubagroup.com/contact-us/"),
    "ecobank": ("ecobank.com", "https://www.ecobank.com/contact"),
    "dangote": ("dangote.com", "https://www.dangote.com/contact-us/"),
    "nnpc": ("nnpcgroup.com", "https://nnpcgroup.com/Contact"),
    "mtn": ("mtn.ng", "https://www.mtn.ng/contact-us/"),
    "glo": ("gloworld.com", "https://www.gloworld.com/ng/contact-us/"),
    "airtel": ("airtel.ng", "https://www.airtel.ng/contact-us/"),
    # Government
    "government": ("statehouse.gov.ng", "https://statehouse.gov.ng/contact/"),
    "president": ("statehouse.gov.ng", "https://statehouse.gov.ng/contact/"),
    "senate": ("nass.gov.ng", "https://nass.gov.ng/contact"),
    "inec": ("inecnigeria.org", "https://www.inecnigeria.org/contact/"),
    "nuc": ("nuc.edu.ng", "https://www.nuc.edu.ng/contact-us/"),
    "jamb": ("jamb.gov.ng", "https://www.jamb.gov.ng/contact"),
    "ncdc": ("ncdc.gov.ng", "https://ncdc.gov.ng/contact/"),
    "police": ("npf.gov.ng", "https://www.npf.gov.ng/contact"),
    "icpc": ("icpc.gov.ng", "https://icpc.gov.ng/report-corruption/"),
    "efcc": ("efcc.gov.ng", "https://www.efcc.gov.ng/"),
    # Universities
    "adsu": ("adsu.edu.ng", "https://www.adsu.edu.ng/contact"),
    "adamawa state university": ("adsu.edu.ng", "https://www.adsu.edu.ng/contact"),
    "unilag": ("unilag.edu.ng", "https://unilag.edu.ng/contact-us/"),
    "ui": ("ui.edu.ng", "https://www.ui.edu.ng/contact"),
    "oau": ("oauife.edu.ng", "https://www.oauife.edu.ng/contact-us"),
    "abu": ("abu.edu.ng", "https://www.abu.edu.ng/contact"),
    "uniben": ("uniben.edu.ng", "https://www.uniben.edu.ng/contact"),
    "unn": ("unn.edu.ng", "https://www.unn.edu.ng/contact-us"),
    "futminna": ("futminna.edu.ng", "https://www.futminna.edu.ng/contact/"),
    "futa": ("futa.edu.ng", "https://www.futa.edu.ng/contact/"),
    # International
    "un": ("un.org", "https://www.un.org/en/contact-us"),
    "who": ("who.int", "https://www.who.int/contact"),
    "bbc": ("bbc.com", "https://www.bbc.com/contact"),
    "reuters": ("reuters.com", "https://www.reuters.com/contact-us/"),
    "ap": ("ap.org", "https://www.ap.org/contact/"),
}

# ============================================================
# TRUSTED SOURCES (expanded with 24+ sports outlets)
# ============================================================

# Core trusted domains (news, official, health, tech, etc.)
CORE_SOURCES = [
    "punchng.com", "vanguardngr.com", "guardian.ng", "premiumtimesng.com",
    "dailytrust.com", "thisdaylive.com", "thecable.ng", "saharareporters.com",
    "channelstv.com", "arise.tv", "nairametrics.com", "businessday.ng",
    "dailypost.ng", "tribuneonlineng.com", "leadership.ng", "blueprint.ng",
    "thesun.ng", "independent.ng", "peoplesgazette.com", "orderpaper.ng",
    "espn.com", "skysports.com", "goal.com", "theathletic.com",
    "fabrizioromano.com", "talksport.com", "thetimes.co.uk",
    "bbc.com", "reuters.com", "apnews.com", "cnn.com", "aljazeera.com",
    "nytimes.com", "washingtonpost.com", "theguardian.com",
    "who.int", "cdc.gov", "mayoclinic.org", "webmd.com", "nhs.uk",
    "techcrunch.com", "wired.com", "theverge.com", "techcabal.com",
    "bloomberg.com", "ft.com", "wsj.com", "forbes.com",
    "snopes.com", "factcheck.org",
]

# Expanded sports sources (24+ additional reputable sports news sites)
SPORTS_SOURCES = [
    "dailymail.co.uk",      # has a dedicated sports section
    "mirror.co.uk",         # sports
    "independent.co.uk",    # sport
    "telegraph.co.uk",      # sport
    "standard.co.uk",       # sport
    "sportbible.com",
    "givemesport.com",
    "90min.com",
    "onefootball.com",
    "transfermarkt.com",
    "whoscored.com",
    "eurosport.com",
    "nbcsports.com",
    "cbssports.com",
    "yahoosports.com",
    "foxsports.com",
    "sportingnews.com",
    "bleacherreport.com",
    "si.com",               # Sports Illustrated
    "thescore.com",
    "sports.yahoo.com",     # already covered by yahoosports.com but add anyway
    "sports.cbs.com",       # covered
    "sports.espn.com",      # covered
    "bbc.co.uk/sport",      # covered by bbc.com
    "theguardian.com/sport", # covered
]

# Combine all, remove duplicates, and add organisation domains
TRUSTED_SOURCES = list(set(CORE_SOURCES + SPORTS_SOURCES))

# Add all organization domains
for _, (domain, _) in ORGANIZATION_MAP.items():
    if domain not in TRUSTED_SOURCES:
        TRUSTED_SOURCES.append(domain)

# ============================================================
# UNRELIABLE SOURCES (blacklist)
# ============================================================

UNRELIABLE_KEYWORDS = [
    "forum", "wordpress", "blogspot", "medium",
    "reddit", "quora", "yahoo answers", "stackexchange",
    "pinterest", "tumblr", "wikihow", "answers.com",
    "buzzfeed", "theonion", "clickhole",
    "twitter.com", "x.com"
]

# ============================================================
# HELPERS
# ============================================================

def detect_organization(text):
    text_lower = text.lower()
    for keyword, (domain, url) in ORGANIZATION_MAP.items():
        if keyword in text_lower:
            return keyword, domain, url
    return None, None, None

def is_trusted_source(url, title, snippet):
    combined = f"{url} {title} {snippet}".lower()
    for bad in UNRELIABLE_KEYWORDS:
        if bad in combined:
            return False
    for src in TRUSTED_SOURCES:
        if src in combined:
            return True
    return False

def fetch_page_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        text = re.sub(r'<[^>]+>', ' ', r.text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:8000]
    except:
        return None

# ============================================================
# STRICT CONTEXT CHECK FOR GOVERNMENT NEWS
# ============================================================

def check_government_context(user_text, page_text, title, snippet):
    """
    Strictly verify that the official government page explicitly confirms the claim.
    Returns:
        supports_claim: bool
        confidence: int
        reason: str
    """
    user_lower = user_text.lower()
    combined = f"{title} {snippet} {page_text or ''}".lower()

    # 1. Extract the main subject (person/organisation) from user text
    # Try to find a named entity with a title
    subjects = re.findall(r'\b(?:President|Dr\.|Mr\.|Mrs\.|Ms\.|Professor|Chief|Alhaji|Mallam|Governor|Senator)\s+[A-Z][a-z]+\b', user_text)
    if not subjects:
        # Fallback: any capitalised word sequence (excluding common nouns)
        potential = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', user_text)
        non_names = {"Breaking", "Government", "State", "House", "National", "Assembly", "Official", "New", "Old", "Tax", "Law"}
        for name in potential:
            if name not in non_names and len(name) > 2:
                subjects.append(name)
                break

    if not subjects:
        return {"supports_claim": False, "confidence": 10, "reason": "Could not identify a subject in the claim"}

    subject = subjects[0].lower()

    # 2. Identify the main event (verb/noun) from the user text
    # Remove the subject and look for key action words
    # We'll look for common government‑related events: resign, appoint, tax, etc.
    event_keywords = ["resign", "appoint", "tax", "increase", "decrease", "ban", "approve", "reject", "confirm", "announce"]
    found_event = None
    for kw in event_keywords:
        if kw in user_lower:
            found_event = kw
            break

    if not found_event:
        # If no event keyword found, treat the whole claim as the event (for strict matching)
        found_event = "general"

    # 3. Check if the page mentions the subject
    if subject not in combined:
        return {"supports_claim": False, "confidence": 10, "reason": f"Page does not mention {subject}"}

    # 4. Strict confirmation: check for exact phrase (cleaned) in page
    # Clean the user text: remove punctuation, extra spaces
    clean_user = re.sub(r'[^\w\s]', '', user_text).lower().strip()
    clean_user = re.sub(r'\s+', ' ', clean_user)
    if clean_user in combined:
        return {"supports_claim": True, "confidence": 95, "reason": "Exact claim found on official website"}

    # 5. If not exact, look for subject + event in close proximity
    if found_event != "general":
        # Find positions of subject and event
        subject_pos = combined.find(subject)
        if subject_pos == -1:
            return {"supports_claim": False, "confidence": 10, "reason": "Subject not found (should not happen)"}
        # Search for event within 30 characters after subject (or before)
        search_window = combined[max(0, subject_pos-30):subject_pos+len(subject)+30]
        if found_event in search_window:
            # Also check for announcement markers to increase confidence
            marker = re.search(r'\b(announces|confirms|says|states|official|press release)\b', search_window)
            confidence = 90 if marker else 80
            return {"supports_claim": True, "confidence": confidence, "reason": f"{subject} {found_event} confirmed (proximity)"}

        # Check if event appears anywhere on page (still might be relevant)
        if found_event in combined:
            return {"supports_claim": False, "confidence": 20, "reason": f"Event '{found_event}' found but not directly linked to {subject}"}
        else:
            return {"supports_claim": False, "confidence": 10, "reason": f"Event '{found_event}' not found"}

    # If no specific event, require that the page contains the subject and at least some announcement language
    if "announce" in combined or "official" in combined or "statement" in combined:
        return {"supports_claim": True, "confidence": 70, "reason": f"Official page mentions {subject} with announcement context"}
    else:
        return {"supports_claim": False, "confidence": 15, "reason": "No announcement context found"}

# ============================================================
# MAIN VERIFICATION
# ============================================================

def verify_news_online(text):
    search_query = re.sub(r'[^\w\s]', '', text)[:80]

    org_name, domain, report_url = detect_organization(text)

    if org_name:
        print(f"🔍 Organization: {org_name} → searching {domain}")
        search_query_full = f"site:{domain} {search_query}"
        recency = "3m"
        is_government = (org_name in ["government", "president", "senate"])
    else:
        print(f"🌐 No organization → searching trusted sources")
        search_query_full = search_query
        recency = "2w"
        is_government = False

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(search_query_full, max_results=6, timelimit=recency))
    except Exception:
        return {
            "verified": False,
            "online_check_performed": True,
            "search_engine": "Error",
            "message": "Search failed",
            "confidence_score": 0,
            "sources": [],
            "topic": "general",
            "organization": org_name,
            "organization_domain": domain,
            "organization_report_url": report_url,
            "recency": "N/A"
        }

    credible = []
    for r in results:
        url = r.get("href", "")
        title = r.get("title", "")
        snippet = r.get("body", "")
        if is_trusted_source(url, title, snippet):
            credible.append(r)

    if not credible:
        return {
            "verified": False,
            "online_check_performed": True,
            "search_engine": f"Official Website: {domain}" if org_name else "Trusted Sources",
            "message": "No supporting sources found",
            "confidence_score": 0,
            "sources": [],
            "topic": "general",
            "organization": org_name,
            "organization_domain": domain,
            "organization_report_url": report_url,
            "recency": f"Past {90 if org_name else 14} days"
        }

    verified = False
    sources = []
    all_confidence = []

    for r in credible[:3]:
        page_text = fetch_page_text(r.get("href", ""))
        title = r.get("title", "")
        snippet = r.get("body", "")

        if is_government:
            analysis = check_government_context(text, page_text, title, snippet)
        else:
            analysis = {
                "supports_claim": True,
                "confidence": 75,
                "reason": f"Found on {domain}" if org_name else "Found on trusted source"
            }

        sources.append({
            "title": title,
            "link": r.get("href", ""),
            "snippet": snippet[:200] + "...",
            "analysis": analysis
        })

        if analysis["supports_claim"]:
            verified = True
        all_confidence.append(analysis["confidence"])

    avg_confidence = sum(all_confidence) / len(all_confidence) if all_confidence else 0

    # For government, require higher confidence to consider verified
    if is_government and avg_confidence < 80:
        verified = False

    return {
        "verified": verified,
        "online_check_performed": True,
        "search_engine": f"Official Website: {domain}" if org_name else "Trusted Sources",
        "message": "✅ Verified" if verified else "⚠️ Not verified",
        "confidence_score": round(avg_confidence, 1),
        "sources": sources,
        "topic": "general",
        "organization": org_name,
        "organization_domain": domain,
        "organization_report_url": report_url,
        "recency": f"Past {90 if org_name else 14} days"
    }