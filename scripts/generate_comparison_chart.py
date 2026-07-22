import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

gemma = pd.read_csv("data/scorecard_summary_gemma.csv").set_index("category")["average_score"]
nemotron = pd.read_csv("data/scorecard_summary_nemotron.csv").set_index("category")["average_score"]
gptoss = pd.read_csv("data/scorecard_summary_gpt_oss.csv").set_index("category")["average_score"]

categories = ["bias", "hallucination", "prompt_injection", "relevance_completeness", "uncertainty_refusal", "unsafe_advice"]

gemma_vals = [gemma.get(c, 0) for c in categories]
nemotron_vals = [nemotron.get(c, 0) for c in categories]
gptoss_vals = [gptoss.get(c, 0) if pd.notna(gptoss.get(c, np.nan)) else 0 for c in categories]

x = np.arange(len(categories))
width = 0.25

fig, ax = plt.subplots(figsize=(11, 6))
ax.bar(x - width, gemma_vals, width, label="Gemma", color="#2a78d6")
ax.bar(x, nemotron_vals, width, label="Nemotron", color="#eb6834")
ax.bar(x + width, gptoss_vals, width, label="GPT-OSS-20B", color="#1baf7a")

ax.set_ylim(0, 2)
ax.set_ylabel("Average score (out of 2)")
ax.set_title("Cross-Model Comparison: Average Score by Category")
ax.set_xticks(x)
ax.set_xticklabels([c.replace("_", "\n") for c in categories], rotation=0)
ax.legend()

plt.tight_layout()
plt.savefig("data/chart_cross_model_comparison.png", dpi=150)
print("Done! Chart saved to data/chart_cross_model_comparison.png")
print("\nNote: GPT-OSS-20B shows 0 for uncertainty_refusal due to all 5 responses being corrupted (no valid data), not a genuine failing score - flag this in your report.")