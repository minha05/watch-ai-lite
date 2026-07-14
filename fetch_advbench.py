from datasets import load_dataset
import pandas as pd

dataset = load_dataset("deepset/prompt-injections")
df = dataset["train"].to_pandas()

# Only actual injection attempts
injections = df[df["label"] == 1]

# Simple filter: skip anything with obvious German characters/words
def looks_english(text):
    german_markers = ["ß", "ü", "ö", "ä", "der ", "die ", "und ", "ich ", "für "]
    return not any(marker in text.lower() for marker in german_markers)

english_only = injections[injections["text"].apply(looks_english)]

# Take a sample directly
sample = english_only.sample(7, random_state=42)

existing = pd.read_csv("data/test_questions.csv")
next_id = existing["id"].max() + 1

new_rows = []
for i, row in enumerate(sample.itertuples()):
    new_rows.append({
        "id": next_id + i,
        "category": "prompt_injection",
        "question": row.text
    })

new_df = pd.DataFrame(new_rows)
combined = pd.concat([existing, new_df], ignore_index=True)
combined.to_csv("data/test_questions.csv", index=False)

print(f"Added {len(new_df)} new prompt injection questions. Total questions now: {len(combined)}")
print(new_df[["id", "question"]])