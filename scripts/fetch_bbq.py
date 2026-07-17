# bias 
from datasets import load_dataset
import pandas as pd

dataset = load_dataset("walledai/BBQ", "default")
df = dataset["nationality"].to_pandas()

# Take a small sample - 7 questions
sample = df.sample(7, random_state=42)

# Combine context + question into one natural prompt
sample["combined_question"] = sample["context"] + " " + sample["question"]

# Load existing test questions to find next available id
existing = pd.read_csv("data/test_questions.csv")
next_id = existing["id"].max() + 1

new_rows = []
for i, row in enumerate(sample.itertuples()):
    new_rows.append({
        "id": next_id + i,
        "category": "bias",
        "question": row.combined_question
    })

new_df = pd.DataFrame(new_rows)
combined = pd.concat([existing, new_df], ignore_index=True)
combined.to_csv("data/test_questions.csv", index=False)

print(f"Added {len(new_df)} new BBQ questions. Total questions now: {len(combined)}")
print(new_df[["id", "question"]])