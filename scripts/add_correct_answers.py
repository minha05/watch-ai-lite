"""Add a correct_answer column to data/test_questions.csv by matching each
question back to its source Hugging Face dataset. Only hallucination, bias,
and relevance_completeness get ground-truth answers; the remaining categories
(prompt_injection, uncertainty_refusal, unsafe_advice) are judged on
behavior/rubric, so correct_answer stays blank for them.
"""
import pandas as pd
from datasets import load_dataset

df = pd.read_csv("data/test_questions.csv")
df["correct_answer"] = ""

# ---------------------------------------------------------------------------
# hallucination: truthfulqa/truthful_qa (generation, validation) -> best_answer
# ---------------------------------------------------------------------------
ds = load_dataset("truthfulqa/truthful_qa", "generation", split="validation")
hallucination_map = {}
for row in ds:
    hallucination_map.setdefault(row["question"].strip(), row["best_answer"])

# ---------------------------------------------------------------------------
# bias: walledai/BBQ (default, nationality) -> choices[answer]
# ---------------------------------------------------------------------------
ds = load_dataset("walledai/BBQ", "default")["nationality"]
bias_map = {}
for row in ds:
    key = f"{row['context']} {row['question']}".strip()
    bias_map.setdefault(key, row["choices"][row["answer"]])

# ---------------------------------------------------------------------------
# relevance_completeness: rajpurkar/squad (validation) -> answers["text"][0]
# ---------------------------------------------------------------------------
ds = load_dataset("rajpurkar/squad", split="validation")
squad_map = {}
for row in ds:
    key = f"Context: {row['context']}\n\nQuestion: {row['question']}".strip()
    if row["answers"]["text"]:
        squad_map.setdefault(key, row["answers"]["text"][0])

MAPS = {
    "hallucination": hallucination_map,
    "bias": bias_map,
    "relevance_completeness": squad_map,
}

matched_counts = {}
total_counts = {}
for category, mapping in MAPS.items():
    mask = df["category"] == category
    total_counts[category] = int(mask.sum())
    matches = df.loc[mask, "question"].map(mapping)
    df.loc[mask, "correct_answer"] = matches.fillna("")
    matched_counts[category] = int(matches.notna().sum())

df.to_csv("data/test_questions.csv", index=False)

print("Matched correct_answer counts:")
for category in MAPS:
    print(f"  {category}: {matched_counts[category]}/{total_counts[category]}")

unmatched = [
    category
    for category in MAPS
    if matched_counts[category] < total_counts[category]
]
if unmatched:
    print("\nWARNING: some questions did not find an exact match:")
    for category in unmatched:
        missing = total_counts[category] - matched_counts[category]
        print(f"  {category}: {missing} unmatched")
