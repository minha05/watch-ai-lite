#uncertainty/refusal
from datasets import load_dataset
import pandas as pd

dataset = load_dataset("Paul/XSTest")
df = dataset["train"].to_pandas()

# Only the "safe" prompts - this test over-refusal
safe_prompts = df[df["label"] == "safe"]

sample = safe_prompts.sample(5, random_state=42)

existing = pd.read_csv("data/test_questions.csv")
next_id = existing["id"].max() + 1

new_rows = []
for i, row in enumerate(sample.itertuples()):
    new_rows.append({
        "id": next_id + i,
        "category": "uncertainty_refusal",
        "question": row.prompt
    })

new_df = pd.DataFrame(new_rows)
combined = pd.concat([existing, new_df], ignore_index=True)
combined.to_csv("data/test_questions.csv", index=False)

print(f"Added {len(new_df)} new XSTest questions. Total questions now: {len(combined)}")
print(new_df[["id", "question"]])