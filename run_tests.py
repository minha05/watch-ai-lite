# from google import genai
# from dotenv import load_dotenv
# import os
# import pandas as pd
# import time

# load_dotenv()
# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# # Load the test questions
# questions_df = pd.read_csv("data/test_questions.csv")

# results = []

# # Going through the table, one row at a time
# for index, row in questions_df.iterrows():
#     print(f"Testing question {row['id']}: {row['question'][:50]}...")

# ##incase a question fails
#     answer = None
#     for attempt in range(3):  # try up to 3 times
#         try:
#             response = client.models.generate_content(
#                 model="gemini-2.5-flash-lite",
#                 contents=row["question"]
#             )
#             answer = response.text
#             break  # success, stop retrying
#         except Exception as e:
#             print(f"  Attempt {attempt + 1} failed: {e}")
#             time.sleep(10)  # wait a bit before retrying

#     if answer is None:
#         answer = "ERROR: Failed after 3 attempts"

#     results.append({
#         "id": row["id"],
#         "category": row["category"],
#         "question": row["question"],
#         "response": answer
#     })

#     time.sleep(5)  
    
#     # small pause to avoid hitting rate limits too fast

# # Save all results to a new CSV
# results_df = pd.DataFrame(results)
# #writes the results in a new csv file
# results_df.to_csv("data/results_baseline.csv", index=False)

# print("\nDone! Results saved to data/results_baseline.csv")

from google import genai
from dotenv import load_dotenv
import os
import pandas as pd
import time

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

results_path = "data/results_baseline.csv"
questions_path = "data/test_questions.csv"

# Load the full question set
questions_df = pd.read_csv(questions_path)

# Check if we already have some results saved
if os.path.exists(results_path):
    results_df = pd.read_csv(results_path)
    # Find which ones previously failed
    failed_mask = results_df["response"].str.startswith("ERROR", na=False)
    to_retry_ids = results_df.loc[failed_mask, "id"].tolist()
    print(f"Found existing results. Retrying {len(to_retry_ids)} failed question(s): {to_retry_ids}")
else:
    # No existing results yet — treat everything as needing a run
    results_df = pd.DataFrame(columns=["id", "category", "question", "response"])
    to_retry_ids = questions_df["id"].tolist()
    print(f"No existing results found. Running all {len(to_retry_ids)} questions.")

# Only loop through the ones that need (re)running
questions_to_run = questions_df[questions_df["id"].isin(to_retry_ids)]

for index, row in questions_to_run.iterrows():
    print(f"Testing question {row['id']}: {row['question'][:50]}...")

    answer = None
    last_error = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=row["question"]
            )
            answer = response.text
            break
        except Exception as e:
            last_error = e
            print(f"  Attempt {attempt + 1} failed: {e}")
            time.sleep(10)

    if answer is None:
        answer = f"ERROR: Failed after 3 attempts. Last error: {last_error}"

    # Update or insert this result into results_df
    if row["id"] in results_df["id"].values:
        results_df.loc[results_df["id"] == row["id"], "response"] = answer
    else:
        new_row = {"id": row["id"], "category": row["category"], "question": row["question"], "response": answer}
        results_df = pd.concat([results_df, pd.DataFrame([new_row])], ignore_index=True)

    time.sleep(5)

# Save the updated, merged results
results_df = results_df.sort_values("id")
results_df.to_csv(results_path, index=False)

print(f"\nDone! Results saved to {results_path}")