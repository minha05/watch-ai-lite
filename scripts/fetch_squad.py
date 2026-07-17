from datasets import load_dataset
import pandas as pd

dataset = load_dataset("rajpurkar/squad")
df = dataset["validation"].to_pandas()

# Take a sample
sample = df.sample(7, random_state=42)

# Combine context + question into one natural prompt
sample["combined_question"] = (
    "Context: " + sample["context"] + "\n\nQuestion: " + sample["question"]
)

existing = pd.read_csv("data/test_questions.csv")
next_id = existing["id"].max() + 1

new_rows = []
for i, row in enumerate(sample.itertuples()):
    new_rows.append({
        "id": next_id + i,
        "category": "relevance_completeness",
        "question": row.combined_question
    })

new_df = pd.DataFrame(new_rows)
combined = pd.concat([existing, new_df], ignore_index=True)
combined.to_csv("data/test_questions.csv", index=False)

print(f"Added {len(new_df)} SQuAD questions. Total questions now: {len(combined)}")
print(new_df[["id", "question"]])