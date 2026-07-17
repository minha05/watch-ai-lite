import pandas as pd
from datasets import load_dataset

# Load your current test questions
questions_df = pd.read_csv("data/test_questions.csv")
questions_df["correct_answer"] = ""

# --- 1. TruthfulQA (hallucination questions) ---
print("Matching TruthfulQA answers...")
tqa_url = "https://huggingface.co/datasets/truthfulqa/truthful_qa/resolve/main/generation/validation-00000-of-00001.parquet"
tqa_df = pd.read_parquet(tqa_url)
tqa_lookup = dict(zip(tqa_df["question"], tqa_df["best_answer"]))

for i, row in questions_df.iterrows():
    if row["question"] in tqa_lookup:
        questions_df.at[i, "correct_answer"] = tqa_lookup[row["question"]]

# --- 2. BBQ (bias questions) ---
print("Matching BBQ answers...")
bbq_dataset = load_dataset("walledai/BBQ", "default")
bbq_df = bbq_dataset["nationality"].to_pandas()
bbq_df["combined_question"] = bbq_df["context"] + " " + bbq_df["question"]

for i, row in questions_df.iterrows():
    match = bbq_df[bbq_df["combined_question"] == row["question"]]
    if not match.empty:
        choices = match.iloc[0]["choices"]
        answer_idx = match.iloc[0]["answer"]
        questions_df.at[i, "correct_answer"] = choices[answer_idx]

# --- 3. SQuAD (relevance_completeness questions) ---
print("Matching SQuAD answers...")
squad_dataset = load_dataset("rajpurkar/squad")
squad_df = squad_dataset["validation"].to_pandas()
squad_df["combined_question"] = "Context: " + squad_df["context"] + "\n\nQuestion: " + squad_df["question"]

for i, row in questions_df.iterrows():
    match = squad_df[squad_df["combined_question"] == row["question"]]
    if not match.empty:
        answers_list = match.iloc[0]["answers"]["text"]
        if len(answers_list) > 0:
            questions_df.at[i, "correct_answer"] = answers_list[0]

questions_df.to_csv("data/test_questions.csv", index=False)

matched_count = (questions_df["correct_answer"] != "").sum()
print(f"\nDone! {matched_count} out of {len(questions_df)} questions now have a ground-truth answer.")
print(questions_df[questions_df["correct_answer"] != ""][["id", "category", "correct_answer"]])