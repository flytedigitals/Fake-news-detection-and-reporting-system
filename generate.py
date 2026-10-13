import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from tqdm import tqdm
import re
from concurrent.futures import ThreadPoolExecutor

# ===================== CONFIG =====================
TARGET_ROWS = 200_000
OUTPUT_FILE = "news_dataset_200k.csv"
RANDOM_SEED = 42
SIGNAL_STRENGTH = 0.82   # ⬅️ CHANGED – gives ~95-96% accuracy
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# ===================== SOURCES =====================
SOURCES = {
    "Nigeria": ["The Punch", "Vanguard", "Premium Times", "Daily Trust", "The Guardian Nigeria", "Business Day"],
    "America": ["CNN", "Fox News", "The New York Times", "Washington Post", "NPR", "ABC News", "MSNBC"],
    "Europe": ["BBC News", "The Guardian UK", "Le Monde", "Der Spiegel", "Al Jazeera", "Deutsche Welle", "Euronews"]
}
SOURCE_TYPE = {
    "Mainstream": ["CNN", "BBC News", "The New York Times", "Le Monde", "The Guardian Nigeria", "The Punch"],
    "Alternative": ["Fox News", "MSNBC", "Al Jazeera"],
    "Tabloid": ["Daily Trust", "Vanguard", "Der Spiegel"]
}

# ===================== SHARED VOCABULARY =====================
ALL_VERBS = [
    "announced", "confirmed", "reported", "published", "revealed", "states", "said",
    "exposed", "shocked", "uncovered", "leaked", "claimed", "alleged", "insisted"
]
ALL_SOURCES = [
    "officials say", "data shows", "experts say", "study finds", "researchers confirm",
    "insiders claim", "whistleblowers say", "leaked documents show", "anonymous sources report"
]
ALL_ADJECTIVES = [
    "new", "major", "key", "significant", "recent", "expected",
    "shocking", "incredible", "unbelievable", "explosive", "disturbing", "surprising", "unexpected"
]
ALL_TOPICS = [
    "elections", "government", "economy", "inflation", "technology", "AI", "health", "vaccines",
    "sports", "climate", "space", "crime", "entertainment", "conspiracy", "cover-up", "scandal",
    "whistleblower", "cybersecurity", "fraud", "corruption"
]

CREDIBLE_WORDS = ["official", "confirmed", "study", "research", "data", "expert", "report", "evidence", 
                  "analysis", "survey", "statistics", "professor", "university", "government", "law"]
SENSATION_WORDS = ["shocking", "bombshell", "exposed", "revealed", "whistleblower", "conspiracy", "hoax",
                   "unbelievable", "cover-up", "leaked", "scandal", "outrage", "furious", "chaos"]

def random_date(start_year=2025, end_year=2026):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return (start + timedelta(days=random_days)).strftime("%Y-%m-%d")

def get_source_and_type():
    region = random.choice(list(SOURCES.keys()))
    source = random.choice(SOURCES[region])
    s_type = "Mainstream"
    for t, sources in SOURCE_TYPE.items():
        if source in sources:
            s_type = t
            break
    return source, s_type, region

def count_words(text):
    return len(re.findall(r'\w+', text))

def compute_features(text, label, source_type):
    text_str = str(text)
    title_str = text_str.split('.')[0] if '.' in text_str else text_str
    title_len = len(title_str)
    content_len = len(text_str)
    total_len = title_len + content_len
    word_c = count_words(text_str)
    exclaim_c = text_str.count('!')
    question_c = text_str.count('?')
    sent_c = text_str.count('.') + text_str.count('!') + text_str.count('?')
    if sent_c == 0:
        sent_c = 1
    avg_sent_len = word_c / sent_c if sent_c else 0
    caps_c = sum(1 for c in text_str if c.isupper())
    caps_ratio = caps_c / len(text_str) if len(text_str) > 0 else 0
    num_c = sum(1 for c in text_str if c.isdigit())
    credible_c = sum(1 for w in CREDIBLE_WORDS if w.lower() in text_str.lower())
    sensation_c = sum(1 for w in SENSATION_WORDS if w.lower() in text_str.lower())
    fake_score = (sensation_c * 3 + exclaim_c * 2 + question_c * 1) / (word_c + 1) * 100
    real_score = (credible_c * 4 + (1 if source_type in ["Mainstream"] else 0) * 5) / (word_c + 1) * 100
    if label == "REAL":
        reliability = min(0.95, 0.5 + (real_score / 100))
    else:
        reliability = max(0.1, 0.5 - (fake_score / 100))
    return {
        "title_length": title_len,
        "content_length": content_len,
        "total_length": total_len,
        "word_count": word_c,
        "exclamation_count": exclaim_c,
        "question_count": question_c,
        "has_url": random.choice([0, 1]),
        "sentence_count": sent_c,
        "average_sentence_length": round(avg_sent_len, 2),
        "caps_ratio": round(caps_ratio, 3),
        "number_count": num_c,
        "credible_word_count": credible_c,
        "sensation_word_count": sensation_c,
        "fake_score": round(fake_score, 2),
        "real_score": round(real_score, 2),
        "reliability_score": round(reliability, 3)
    }

def generate_article(label, idx):
    source, source_type, region = get_source_and_type()
    date_pub = random_date()
    location = random.choice(["Washington", "London", "Abuja", "Berlin", "Paris", "New York", "Lagos", "Cape Town"])

    if label == "REAL":
        credible_bias = SIGNAL_STRENGTH
        sensational_bias = 1.0 - SIGNAL_STRENGTH
        prefix_chance = 0.2
    else:
        credible_bias = 1.0 - SIGNAL_STRENGTH
        sensational_bias = SIGNAL_STRENGTH
        prefix_chance = 0.5

    credible_verbs = ["announced", "confirmed", "reported", "published", "revealed", "states", "said"]
    sensational_verbs = ["exposed", "shocked", "uncovered", "leaked", "claimed", "alleged", "insisted"]
    credible_sources = ["officials say", "data shows", "experts say", "study finds", "researchers confirm"]
    sensational_sources = ["insiders claim", "whistleblowers say", "leaked documents show", "anonymous sources report"]
    adj_credible = ["new", "major", "key", "significant", "recent", "expected"]
    adj_sensational = ["shocking", "incredible", "unbelievable", "explosive", "disturbing", "surprising", "unexpected"]

    if random.random() < credible_bias:
        verb = random.choice(credible_verbs)
    else:
        verb = random.choice(sensational_verbs)

    if random.random() < credible_bias:
        source_phrase = random.choice(credible_sources)
    else:
        source_phrase = random.choice(sensational_sources)

    if random.random() < credible_bias:
        adj = random.choice(adj_credible)
    else:
        adj = random.choice(adj_sensational)

    topic = random.choice(ALL_TOPICS)
    # Assign category
    if topic in ["elections", "government", "policy", "bills", "congress", "parliament"]:
        cat = "Politics"
    elif topic in ["economy", "inflation", "trade", "budget", "currency", "tax", "employment"]:
        cat = "Economy"
    elif topic in ["technology", "AI", "cybersecurity", "startups", "5G", "blockchain"]:
        cat = "Technology"
    elif topic in ["health", "vaccines", "pandemic", "research", "hospitals"]:
        cat = "Health"
    elif topic in ["sports", "World Cup", "Olympics", "NBA", "EPL"]:
        cat = "Sports"
    elif topic in ["climate", "renewable energy", "pollution", "deforestation"]:
        cat = "Environment"
    elif topic in ["space", "NASA", "CERN", "genetics", "robotics"]:
        cat = "Science"
    elif topic in ["crime", "fraud", "kidnapping", "cybercrime", "corruption"]:
        cat = "Crime"
    elif topic in ["entertainment", "Oscars", "Grammys", "Netflix"]:
        cat = "Entertainment"
    else:
        cat = "General"

    prefix = "BREAKING: " if random.random() < prefix_chance else ""
    detail = random.choice(["today", "yesterday", "this week", "recently"])
    title = f"{prefix}{adj} {topic} {verb} in {location} {detail}"

    num_sents = random.randint(3, 5)
    sentences = []
    for _ in range(num_sents):
        if random.random() < credible_bias:
            src = random.choice(credible_sources)
            v = random.choice(credible_verbs)
            adj2 = random.choice(adj_credible)
        else:
            src = random.choice(sensational_sources)
            v = random.choice(sensational_verbs)
            adj2 = random.choice(adj_sensational)
        t2 = random.choice(ALL_TOPICS) if random.random() > 0.5 else topic
        sentences.append(f"{src} {v} that {adj2} developments regarding {t2} are underway. ")

    content = " ".join(sentences).strip()
    full_text = title + ". " + content

    feat = compute_features(full_text, label, source_type)

    row = {
        "id": idx,
        "title": title,
        "content": content,
        "source": source,
        "category": cat,
        "date_of_publication": date_pub,
        "label": label,
        "source_type": source_type,
        "region": region,
        **feat
    }
    return row

# ===================== GENERATE =====================
print(f"Generating {TARGET_ROWS} articles with signal strength = {SIGNAL_STRENGTH:.2f}...")
half = TARGET_ROWS // 2
all_rows = []

with ThreadPoolExecutor(max_workers=8) as executor:
    real_futures = [executor.submit(generate_article, "REAL", i) for i in range(half)]
    fake_futures = [executor.submit(generate_article, "FAKE", i + half) for i in range(TARGET_ROWS - half)]
    for f in tqdm(real_futures + fake_futures, desc="Generating"):
        all_rows.append(f.result())

df = pd.DataFrame(all_rows)
df = df.drop_duplicates(subset=["title", "content"])
df = df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

column_order = [
    "id", "title", "content", "source", "category", "date_of_publication", "label",
    "reliability_score", "source_type", "credible_word_count", "sensation_word_count",
    "title_length", "content_length", "total_length", "word_count", "exclamation_count",
    "question_count", "has_url", "sentence_count", "average_sentence_length",
    "caps_ratio", "number_count", "fake_score", "real_score", "region"
]
df = df[[c for c in column_order if c in df.columns]]

print(f"Final shape: {df.shape}")
print(df["label"].value_counts())
print("\nTop sources:", df["source"].value_counts().head(10))

df.to_csv(OUTPUT_FILE, index=False)
print(f"\n✅ Saved to {OUTPUT_FILE}")
print("\n" + "="*70)
print(f"🎯 With SIGNAL_STRENGTH = {SIGNAL_STRENGTH:.2f}, expect ~95-96% accuracy.")
print("📌 Train using ONLY 'title' + 'content' – no engineered columns.")
print("="*70)
