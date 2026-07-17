import pandas as pd

# Load your completed OpenRouter scores
scores_df = pd.read_csv("data/scores_openrouter.csv", encoding="utf-8", encoding_errors="replace")

# Make sure the score column is treated as numbers, not text
scores_df["score"] = pd.to_numeric(scores_df["score"], errors="coerce")

# --- Overall summary ---
# Note: N/A rows (corrupted responses) are automatically excluded since
# pd.to_numeric turns "N/A" into a missing value, and .mean()/.sum() skip those
overall_average = scores_df["score"].mean()
total_tests = scores_df["score"].notna().sum()  # count only valid, scored rows
excluded_count = scores_df["score"].isna().sum()
pass_count = (scores_df["score"] == 2).sum()
partial_count = (scores_df["score"] == 1).sum()
fail_count = (scores_df["score"] == 0).sum()

print("=== OPENROUTER OVERALL SCORECARD ===")
print(f"Total tests scored: {total_tests} (excluded due to corruption: {excluded_count})")
# --- Reliability metric: how often did we get an unusable response? ---
invalid_percentage = (excluded_count / len(scores_df)) * 100
print(f"Response reliability: {excluded_count}/{len(scores_df)} responses were unusable/corrupted ({invalid_percentage:.1f}%)")
print(f"Average score: {overall_average:.2f} / 2")
print(f"Fully passed (2): {pass_count} ({pass_count/total_tests*100:.0f}%)")
print(f"Partial (1): {partial_count} ({partial_count/total_tests*100:.0f}%)")
print(f"Failed (0): {fail_count} ({fail_count/total_tests*100:.0f}%)")

# --- Breakdown by category ---
print("\n=== BREAKDOWN BY CATEGORY ===")
category_summary = scores_df.groupby("category")["score"].agg(["mean", "count"])
category_summary = category_summary.rename(columns={"mean": "average_score", "count": "num_tests"})
print(category_summary)

category_summary.to_csv("data/scorecard_summary_openrouter.csv")

print("\nDone! Category summary also saved to data/scorecard_summary_openrouter.csv")