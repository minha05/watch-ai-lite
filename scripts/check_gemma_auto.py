import pandas as pd

scores_df = pd.read_csv("data/scores_gemma_auto.csv", encoding="utf-8", encoding_errors="replace")
scores_df["score"] = pd.to_numeric(scores_df["score"], errors="coerce")

print(f"Average score: {scores_df['score'].mean():.2f} / 2")
print(f"Total scored: {scores_df['score'].notna().sum()} / {len(scores_df)}")

category_summary = scores_df.groupby("category")["score"].agg(["mean", "count"])
print(category_summary)