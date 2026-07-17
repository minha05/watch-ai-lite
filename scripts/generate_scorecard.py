import pandas as pd

# Load the completed scores
scores_df = pd.read_csv("data/scores.csv")

# Makes sure the score column is treated as numbers, not text
scores_df["score"] = pd.to_numeric(scores_df["score"], errors="coerce")

# Overall summary
overall_average = scores_df["score"].mean()
total_tests = len(scores_df)
pass_count = (scores_df["score"] == 2).sum()
partial_count = (scores_df["score"] == 1).sum()
fail_count = (scores_df["score"] == 0).sum()

print("=== OVERALL SCORECARD ===")
print(f"Total tests: {total_tests}")
print(f"Average score: {overall_average:.2f} / 2")
print(f"Fully passed (2): {pass_count} ({pass_count/total_tests*100:.0f}%)")
print(f"Partial (1): {partial_count} ({partial_count/total_tests*100:.0f}%)")
print(f"Failed (0): {fail_count} ({fail_count/total_tests*100:.0f}%)")

# Breakdown by category
print("\n=== BREAKDOWN BY CATEGORY ===")
category_summary = scores_df.groupby("category")["score"].agg(["mean", "count"])
category_summary = category_summary.rename(columns={"mean": "average_score", "count": "num_tests"})
print(category_summary)

# Save the category summary as its own CSV too
category_summary.to_csv("data/scorecard_summary.csv")

print("\nDone! Category summary also saved to data/scorecard_summary.csv")