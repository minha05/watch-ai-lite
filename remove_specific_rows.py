import pandas as pd
# removing unrelated rows from the injection test questions
df = pd.read_csv("data/test_questions.csv")

# Remove the Spanish row and the non-injection "generate c++" row
df = df[~df["id"].isin([40, 42])]

df.to_csv("data/test_questions.csv", index=False)
print(f"Removed 2 rows. Total questions now: {len(df)}")