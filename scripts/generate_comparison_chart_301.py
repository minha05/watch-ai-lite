import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

gemma = pd.read_csv("data/scorecard_summary_gemma_301.csv").set_index("category")["average_score"]
nemotron = pd.read_csv("data/scorecard_summary_nemotron_301.csv").set_index("category")["average_score"]
gptoss = pd.read_csv("data/scorecard_summary_gptoss_301.csv").set_index("category")["average_score"]

categories = ["bias", "hallucination", "prompt_injection", "relevance_completeness", "uncertainty_refusal", "unsafe_advice"]

missing_notes = []

def safe_vals(series, model_name):
    vals = []
    for c in categories:
        v = series.get(c, np.nan)
        if pd.isna(v):
            vals.append(0)
            missing_notes.append(f"{model_name}/{c}")
        else:
            vals.append(v)
    return vals

gemma_vals = safe_vals(gemma, "Gemma")
nemotron_vals = safe_vals(nemotron, "Nemotron")
gptoss_vals = safe_vals(gptoss, "GPT-OSS-20B")

x = np.arange(len(categories))
width = 0.25

fig, ax = plt.subplots(figsize=(11, 6))
ax.bar(x - width, gemma_vals, width, label="Gemma", color="#2a78d6")
ax.bar(x, nemotron_vals, width, label="Nemotron", color="#2a9d5c")
ax.bar(x + width, gptoss_vals, width, label="GPT-OSS-20B", color="#d64545")

ax.set_ylim(0, 2)
ax.set_ylabel("Average score (out of 2)")
ax.set_title("Cross-Model Comparison (301-question set): Average Score by Category")
ax.set_xticks(x)
ax.set_xticklabels([c.replace("_", "\n") for c in categories], rotation=0)
ax.legend()

plt.tight_layout()
plt.savefig("data/chart_cross_model_comparison_301.png", dpi=150)
print("Done! Chart saved to data/chart_cross_model_comparison_301.png")

if missing_notes:
    print("\nNote: the following model/category combinations had missing or NaN average scores and were shown as 0:")
    for note in missing_notes:
        print(f"  - {note}")
else:
    print("\nNo missing/NaN category values - all model/category combinations had data.")
