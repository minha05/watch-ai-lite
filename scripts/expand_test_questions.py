"""Expand data/test_questions.csv by pulling additional unique questions per
category from the same Hugging Face sources used in build_test_questions.py.
Appends new rows with continuing sequential ids; does not touch unsafe_advice.
"""
import re
import csv

import pandas as pd
from datasets import load_dataset

SEED = 42
PER_CATEGORY_TARGET_NEW = 28

df = pd.read_csv("data/test_questions.csv")
max_id = int(df["id"].max())

existing_by_category = {
    cat: set(sub["question"].tolist())
    for cat, sub in df.groupby("category")
}

new_rows = []  # (category, question)
shortfalls = {}


def collect_new(category, pool, target=PER_CATEGORY_TARGET_NEW):
    existing = existing_by_category.get(category, set())
    seen_new = set()
    added = 0
    for q in pool:
        q = q.strip()
        if not q or q in existing or q in seen_new:
            continue
        seen_new.add(q)
        new_rows.append((category, q))
        added += 1
        if added >= target:
            break
    if added < target:
        shortfalls[category] = (added, target)
    print(f"{category}: added {added} new questions (target {target})")


# ---------------------------------------------------------------------------
# 1. hallucination: truthfulqa/truthful_qa
# ---------------------------------------------------------------------------
ds = load_dataset("truthfulqa/truthful_qa", "generation", split="validation")
ds = ds.shuffle(seed=SEED)
pool = [row["question"] for row in ds]
collect_new("hallucination", pool)

# ---------------------------------------------------------------------------
# 2. bias: walledai/BBQ (default config, nationality split)
# ---------------------------------------------------------------------------
ds = load_dataset("walledai/BBQ", "default")["nationality"]
ds = ds.shuffle(seed=SEED)
pool = [f"{row['context']} {row['question']}" for row in ds]
collect_new("bias", pool)

# ---------------------------------------------------------------------------
# 3. prompt_injection: deepset/prompt-injections, label == 1, English only
# ---------------------------------------------------------------------------
NON_ENGLISH_MARKERS = ["ß", "ü", "ö", "ä", "der ", "die ", "el ", "la "]
NON_ENGLISH_WORDS = {
    "ich", "und", "nicht", "ist", "sie", "auf", "mit", "fur", "für", "von",
    "zu", "werden", "kann", "wird", "kannst", "bitte", "wie", "was", "das",
    "ein", "eine", "einen", "einem", "eines", "vergiss", "vorherigen",
    "instruktionen", "instruction", "gesagte", "schreibe", "alle", "alles",
    "wer", "warum", "wo", "wann", "jetzt", "neue", "deine", "dich", "dir",
    "gut", "sehr", "auch", "nach", "aber", "oder", "so", "im", "am",
    "que", "para", "por", "con", "una", "uno", "los", "las", "del", "esta",
    "este", "eres", "como", "hola", "gracias", "ahora",
}


def is_english(text):
    lower = text.lower()
    if any(marker in lower for marker in NON_ENGLISH_MARKERS):
        return False
    words = set(re.findall(r"[a-zà-ÿ]+", lower))
    return words.isdisjoint(NON_ENGLISH_WORDS)


ds = load_dataset("deepset/prompt-injections", split="train")
ds = ds.shuffle(seed=SEED)
pool = [row["text"] for row in ds if row["label"] == 1 and is_english(row["text"])]
collect_new("prompt_injection", pool)

# ---------------------------------------------------------------------------
# 4. uncertainty_refusal: Paul/XSTest, label == "safe"
# ---------------------------------------------------------------------------
ds = load_dataset("Paul/XSTest", split="train")
ds = ds.shuffle(seed=SEED)
pool = [row["prompt"] for row in ds if row["label"] == "safe"]
collect_new("uncertainty_refusal", pool)

# ---------------------------------------------------------------------------
# 5. relevance_completeness: rajpurkar/squad
# ---------------------------------------------------------------------------
ds = load_dataset("rajpurkar/squad", split="validation")
ds = ds.shuffle(seed=SEED)
pool = [f"Context: {row['context']}\n\nQuestion: {row['question']}" for row in ds]
collect_new("relevance_completeness", pool)

# ---------------------------------------------------------------------------
# Append new rows with continuing sequential ids
# ---------------------------------------------------------------------------
with open("data/test_questions.csv", "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for i, (category, question) in enumerate(new_rows, start=max_id + 1):
        writer.writerow([i, category, question])

print(f"\nAppended {len(new_rows)} new rows to data/test_questions.csv")

if shortfalls:
    print("\nSHORTFALLS (dataset exhausted before reaching target):")
    for cat, (added, target) in shortfalls.items():
        print(f"  {cat}: only {added}/{target} new unique rows available")

final_df = pd.read_csv("data/test_questions.csv")
print(f"\nFinal total: {len(final_df)} rows")
print(final_df["category"].value_counts())
