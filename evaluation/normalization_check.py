import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import shapiro
import os

data = {
    'Factor 2': [0.6667, 1, 0.6667, 0.3333, -0.6667, -0.3333, 0.3333, 0.3333, 0, -0.3333, -0.3333, 1.6667, 1.3333, 0, -0.6667, -0.3333, 0, 1.6667, 0.3333, 1.3333, 2, -0.6667, -1.3333, 0, -1.3333, 0.3333, -0.3333, -0.3333, 1, 1],
    'Factor 3': [0.5, 1.5, 0.5, 0.75, -0.75, -0.75, 0.5, 0, 0.25, -0.25, -0.25, 1, 0.5, 0.25, -0.5, 0.75, 1.5, 0, 2, 0.5, 1.5, -1, 0.25, 0.25, -0.5, -0.5, -0.25, 1.5, 1.25, -0.75],
    'Factor 5': [0, -1, 0, 0, 0, 1, 1, -1, 0, 0, -1, -1, -1, -1, 0, -1, 0, 0, 0, 0, 0, -1, 0, -1, 0, 0, 0, 0, -1, 1]
}

df = pd.DataFrame(data)

output_dir = "histograms"
os.makedirs(output_dir, exist_ok=True)

for factor in df.columns:
    plt.figure()
    plt.hist(df[factor], bins=7, edgecolor='black')
    plt.title(f'Histogram of {factor} Difference Scores')
    plt.xlabel('Difference Score (Condition 1 - Condition 2)')
    plt.ylabel('Frequency')
    plt.grid(True)
    
    filename = f"{output_dir}/{factor}_histogram.png"
    plt.savefig(filename)
    plt.close()

print("Histograms are saved to the 'histograms' directory.")

for factor in df.columns:
    stat, p = shapiro(df[factor])
    print(f'{factor} Shapiro-Wilk Test: W={stat:.3f}, p={p:.4f} → {"Normal" if p > 0.05 else "Not Normal"}')

