import pandas as pd

df = pd.read_csv("data/results_openai_gpt-oss-20b_free.csv", encoding="utf-8", encoding_errors="replace")

# Force these 5 rows to be retried by marking them as ERROR
retry_ids = [44, 45, 46, 47, 48]
df.loc[df["id"].isin(retry_ids), "response"] = "ERROR: forced retry - corrupted response"

df.to_csv("data/results_openai_gpt-oss-20b_free.csv", index=False)
print(f"Marked {len(retry_ids)} rows for retry.")