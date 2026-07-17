import pandas as pd

results_df = pd.read_csv("data/results_nvidia_nemotron-3-super-120b-a12b_free.csv", encoding="utf-8", encoding_errors="replace")

results_df["score"] = ""
results_df["notes"] = ""

results_df.to_csv("data/scores_nemotron.csv", index=False)
print("Done! Template created at data/scores_nemotron.csv")