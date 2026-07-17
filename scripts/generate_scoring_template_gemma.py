import pandas as pd

results_df = pd.read_csv("data/results_google_gemma-4-26b-a4b-it_free.csv", encoding="utf-8", encoding_errors="replace")

results_df["score"] = ""
results_df["notes"] = ""

results_df.to_csv("data/scores_gemma.csv", index=False)

print("Done! Template created at data/scores_gemma.csv")