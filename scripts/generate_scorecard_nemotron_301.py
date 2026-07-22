import pandas as pd

scores_df = pd.read_csv("data/scores_nemotron_301.csv", encoding="utf-8", encoding_errors="replace")
scores_df["score"] = pd.to_numeric(scores_df["score"], errors="coerce")

overall_average = scores_df["score"].mean()
total_tests = scores_df["score"].notna().sum()
excluded_count = scores_df["score"].isna().sum()
pass_count = (scores_df["score"] == 2).sum()
partial_count = (scores_df["score"] == 1).sum()
fail_count = (scores_df["score"] == 0).sum()

print("=== NEMOTRON OVERALL SCORECARD (301-question set, LLM-Judged) ===")
print(f"Total tests scored: {total_tests} (excluded/N/A: {excluded_count})")
print(f"Average score: {overall_average:.2f} / 2")
print(f"Fully passed (2): {pass_count} ({pass_count/total_tests*100:.0f}%)")
print(f"Partial (1): {partial_count} ({partial_count/total_tests*100:.0f}%)")
print(f"Failed (0): {fail_count} ({fail_count/total_tests*100:.0f}%)")

category_summary = scores_df.groupby("category")["score"].agg(["mean", "count"])
category_summary = category_summary.rename(columns={"mean": "average_score", "count": "num_tests"})
print("\n=== BREAKDOWN BY CATEGORY ===")
print(category_summary)

category_summary.to_csv("data/scorecard_summary_nemotron_301.csv")
print("\nDone! Saved to data/scorecard_summary_nemotron_301.csv")
