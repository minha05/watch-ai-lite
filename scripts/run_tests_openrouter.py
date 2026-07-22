from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd
import time
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Pass the model name as a command-line argument
model_name = sys.argv[1]  # e.g. "google/gemma-4-31b:free"
safe_model_name = model_name.replace("/", "_").replace(":", "_")

results_path = f"data/results_{safe_model_name}.csv"
questions_path = "data/test_questions.csv"

questions_df = pd.read_csv(questions_path)

if os.path.exists(results_path):
    results_df = pd.read_csv(results_path)
    failed_mask = results_df["response"].str.startswith("ERROR", na=False)
    error_ids = results_df.loc[failed_mask, "id"].tolist()
    missing_ids = questions_df.loc[~questions_df["id"].isin(results_df["id"]), "id"].tolist()
    to_retry_ids = error_ids + missing_ids
else:
    results_df = pd.DataFrame(columns=["id", "category", "question", "response"])
    to_retry_ids = questions_df["id"].tolist()

questions_to_run = questions_df[questions_df["id"].isin(to_retry_ids)]

CHECKPOINT_EVERY = 10

for i, (index, row) in enumerate(questions_to_run.iterrows(), start=1):
    print(f"Testing question {row['id']}: {row['question'][:50]}...")

    answer = None
    last_error = None
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": row["question"]}]
            )
            answer = response.choices[0].message.content
            break
        except Exception as e:
            last_error = e
            print(f"  Attempt {attempt + 1} failed: {e}")
            time.sleep(5)

    if answer is None:
        answer = f"ERROR: Failed after 3 attempts. Last error: {last_error}"

    if row["id"] in results_df["id"].values:
        results_df.loc[results_df["id"] == row["id"], "response"] = answer
    else:
        new_row = {"id": row["id"], "category": row["category"], "question": row["question"], "response": answer}
        results_df = pd.concat([results_df, pd.DataFrame([new_row])], ignore_index=True)

    if i % CHECKPOINT_EVERY == 0:
        results_df.sort_values("id").to_csv(results_path, index=False)
        print(f"  [checkpoint] saved progress after {i}/{len(questions_to_run)} questions")

    time.sleep(3)

results_df = results_df.sort_values("id")
results_df.to_csv(results_path, index=False)
print(f"\nDone! Results saved to {results_path}")