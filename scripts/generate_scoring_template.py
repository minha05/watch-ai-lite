import pandas as pd

# Loads existing results into a table
results_df = pd.read_csv("data/results_openrouter.csv")


# Add two new empty columns to be filled in manually later
results_df["score"] = ""      # score of 0, 1, or 2
results_df["notes"] = ""      # short justification

# Save as a new file for manual scoring
results_df.to_csv("data/scores_openrouter.csv", index=False)

print("Done! Template created at data/scores_openrouter.csv - open it and fill in the score and notes columns.")
