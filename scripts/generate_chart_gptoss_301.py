import pandas as pd
import matplotlib.pyplot as plt

# Load the category summary already generated
summary = pd.read_csv("data/scorecard_summary_gptoss_301.csv")
#draws barcharts
plt.figure(figsize=(8, 5))
bars = plt.bar(summary["category"], summary["average_score"], color="#d64545")

plt.ylim(0, 2)
plt.ylabel("Average score (out of 2)")
plt.title("GPT-OSS-20B (301-question set): Average Score by Category")
plt.xticks(rotation=20, ha="right")

# Add the actual number on top of each bar
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 0.03, f"{height:.2f}", ha="center")
#safe as png
plt.tight_layout()
plt.savefig("data/chart_gptoss_301_categories.png", dpi=150)
print("Done! Chart saved to data/chart_gptoss_301_categories.png")
