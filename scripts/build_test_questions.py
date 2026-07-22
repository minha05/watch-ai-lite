"""Rebuild data/test_questions.csv with ~70 questions per category, sourced from
Hugging Face datasets. Categories 1-5 go into test_questions.csv; unsafe_advice
candidates are written separately for manual review.
"""
import re
import csv

from datasets import load_dataset

TARGET_PER_CATEGORY = 70
SEED = 42

rows = []  # list of (category, question)


def add_category(name, questions, target=TARGET_PER_CATEGORY):
    questions = list(dict.fromkeys(q.strip() for q in questions if q and q.strip()))
    questions = questions[:target]
    for q in questions:
        rows.append((name, q))
    print(f"{name}: added {len(questions)} questions")


# ---------------------------------------------------------------------------
# 1. hallucination: truthfulqa/truthful_qa (generation, validation)
# ---------------------------------------------------------------------------
ds = load_dataset("truthfulqa/truthful_qa", "generation", split="validation")
ds = ds.shuffle(seed=SEED)
questions = [row["question"] for row in ds]
add_category("hallucination", questions)

# ---------------------------------------------------------------------------
# 2. bias: walledai/BBQ (default config, "nationality" split)
# ---------------------------------------------------------------------------
ds = load_dataset("walledai/BBQ", "default")["nationality"]
ds = ds.shuffle(seed=SEED)
questions = [f"{row['context']} {row['question']}" for row in ds]
add_category("bias", questions)

# ---------------------------------------------------------------------------
# 3. prompt_injection: deepset/prompt-injections (train), label == 1, English only
# ---------------------------------------------------------------------------
ds = load_dataset("deepset/prompt-injections", split="train")
ds = ds.shuffle(seed=SEED)

NON_ENGLISH_MARKERS = ["ß", "ü", "ö", "ä", "der ", "die ", "el ", "la "]

# Broader whole-word stopword check (German/Spanish) to catch mixed-language
# rows that don't contain the diacritic/substring markers above.
NON_ENGLISH_WORDS = {
    # German
    "ich", "und", "nicht", "ist", "sie", "auf", "mit", "fur", "für", "von",
    "zu", "werden", "kann", "wird", "kannst", "bitte", "wie", "was", "das",
    "ein", "eine", "einen", "einem", "eines", "vergiss", "vorherigen",
    "instruktionen", "instruction", "gesagte", "schreibe", "alle", "alles",
    "wer", "warum", "wo", "wann", "jetzt", "neue", "deine", "dich", "dir",
    "gut", "sehr", "auch", "nach", "aber", "oder", "so", "im", "am",
    # Spanish
    "que", "para", "por", "con", "una", "uno", "los", "las", "del", "esta",
    "este", "eres", "como", "hola", "gracias", "ahora",
}


def is_english(text):
    lower = text.lower()
    if any(marker in lower for marker in NON_ENGLISH_MARKERS):
        return False
    words = set(re.findall(r"[a-zà-ÿ]+", lower))
    return words.isdisjoint(NON_ENGLISH_WORDS)


questions = [
    row["text"] for row in ds if row["label"] == 1 and is_english(row["text"])
]
add_category("prompt_injection", questions)

# ---------------------------------------------------------------------------
# 4. uncertainty_refusal: Paul/XSTest (train), label == "safe"
# ---------------------------------------------------------------------------
ds = load_dataset("Paul/XSTest", split="train")
ds = ds.shuffle(seed=SEED)
questions = [row["prompt"] for row in ds if row["label"] == "safe"]
add_category("uncertainty_refusal", questions)

# ---------------------------------------------------------------------------
# 5. relevance_completeness: rajpurkar/squad (validation)
# ---------------------------------------------------------------------------
ds = load_dataset("rajpurkar/squad", split="validation")
ds = ds.shuffle(seed=SEED)
questions = [
    f"Context: {row['context']}\n\nQuestion: {row['question']}" for row in ds
]
add_category("relevance_completeness", questions)

# ---------------------------------------------------------------------------
# Assign sequential ids and save categories 1-5
# ---------------------------------------------------------------------------
with open("data/test_questions.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "category", "question"])
    for i, (category, question) in enumerate(rows, start=1):
        writer.writerow([i, category, question])

print(f"\nSaved {len(rows)} questions to data/test_questions.csv")

# ---------------------------------------------------------------------------
# 6. unsafe_advice candidates: Anthropic/hh-rlhf (harmless-base, test)
#    Extract human's first turn, filter to student/wellbeing keywords,
#    write to a separate file for manual review (NOT auto-included).
# ---------------------------------------------------------------------------
ds = load_dataset("Anthropic/hh-rlhf", data_dir="harmless-base", split="test")

KEYWORDS = [
    "exam", "essay", "deadline", "cheat", "resume", "drink", "alcohol",
    "stressed", "anxious", "anxiety", "sleep", "burnout", "medication",
    "study", "studying", "college", "university", "assignment", "homework",
    "grade", "grades", "tuition", "student", "depressed", "depression",
    "overwhelmed", "insomnia",
]

HUMAN_TURN_RE = re.compile(r"Human:\s*(.*?)\s*(?:\n\nAssistant:|$)", re.DOTALL)


def first_human_question(text):
    match = HUMAN_TURN_RE.search(text)
    if not match:
        return None
    return " ".join(match.group(1).split())


candidates = []
seen = set()
for row in ds:
    text = row["chosen"]
    question = first_human_question(text)
    if not question:
        continue
    lower = question.lower()
    if not any(kw in lower for kw in KEYWORDS):
        continue
    if question in seen:
        continue
    seen.add(question)
    candidates.append(question)

with open("data/unsafe_advice_candidates.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["candidate_id", "question"])
    for i, question in enumerate(candidates, start=1):
        writer.writerow([i, question])

print(f"unsafe_advice: found {len(candidates)} candidate questions for manual review")
print("Saved candidates to data/unsafe_advice_candidates.csv")
