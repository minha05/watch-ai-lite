# Hallucination / Factual Accuracy
import pandas as pd

url = "https://huggingface.co/datasets/truthfulqa/truthful_qa/resolve/main/generation/validation-00000-of-00001.parquet"
df = pd.read_parquet(url)

# Take a small sample - 7 questions
sample = df.sample(7, random_state=42)[["question"]].copy()

# Load existing questions to find the next available id
existing = pd.read_csv("data/test_questions.csv")
next_id = existing["id"].max() + 1

# Build new rows matching existing format
new_rows = []
for i, row in enumerate(sample.itertuples()):
    new_rows.append({
        "id": next_id + i,
        "category": "hallucination",
        "question": row.question
    })

new_df = pd.DataFrame(new_rows)

# Combine with existing questions and save
combined = pd.concat([existing, new_df], ignore_index=True)
combined.to_csv("data/test_questions.csv", index=False)

print(f"Added {len(new_df)} new TruthfulQA questions. Total questions now: {len(combined)}")
print(new_df)