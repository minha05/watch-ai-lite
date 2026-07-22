import pandas as pd
import matplotlib.pyplot as plt

summary = pd.read_csv("data/scorecard_summary_gpt_oss.csv")

plt.figure(figsize=(8, 5))
bars = plt.bar(summary["category"], summary["average_score"], color="#d64545")

plt.ylim(0, 2)
plt.ylabel("Average score (out of 2)")
plt.title("GPT-OSS-20B: Average Score by Category")
plt.xticks(rotation=20, ha="right")

for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 0.03, f"{height:.2f}", ha="center")

plt.tight_layout()
plt.savefig("data/chart_gptoss_categories.png", dpi=150)
print("Done! Chart saved to data/chart_gptoss_categories.png")