from datasets import load_dataset
import pandas as pd
import re

dataset = load_dataset("Anthropic/hh-rlhf", data_dir="harmless-base")
df = dataset["test"].to_pandas()

def extract_question(text):
    match = re.search(r"Human:\s*(.*?)\s*Assistant:", text, re.DOTALL)
    return match.group(1).strip() if match else None

df["question"] = df["chosen"].apply(extract_question)
df = df.dropna(subset=["question"])

# Search for questions containing student/academic-life relevant keywords
keywords = ["exam", "essay", "assignment", "plagiar", "cheat", "resume", "cv ",
            "deadline", "study", "college", "university", "student", "grade",
            "drink", "alcohol", "coursework", "degree", "tuition",
            "stressed", "anxious", "overwhelmed", "sleep", "tired", "burnout"]

pattern = "|".join(keywords)
matches = df[df["question"].str.contains(pattern, case=False, na=False)]

print(f"Found {len(matches)} questions matching student/academic themes.\n")
for i, row in enumerate(matches.head(20).itertuples()):
    print(f"[{i}] {row.question}\n")