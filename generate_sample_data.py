"""
generate_sample_data.py
Creates synthetic sample data mimicking NDHS 2022 structure.
Run this script locally to generate safe, public-friendly CSV files.
"""

import pandas as pd
import numpy as np

np.random.seed(42)  # for reproducibility

# Number of sample rows
n_women = 500
n_children = 300

# ---------- Women Sample (IR) ----------
women_sample = pd.DataFrame({
    'caseid': [f"NP{str(i).zfill(6)}" for i in range(1, n_women + 1)],
    'v001': np.random.randint(1, 500, n_women),
    'v002': np.random.randint(1, 50, n_women),
    'v005': np.random.randint(500000, 2000000, n_women),  # raw weight
    'v024': np.random.choice(range(1, 8), n_women, p=[0.1, 0.2, 0.15, 0.1, 0.2, 0.1, 0.15]),
    'v025': np.random.choice([1, 2], n_women, p=[0.3, 0.7]),  # 1=urban, 2=rural
    'v190': np.random.choice(range(1, 6), n_women),  # wealth quintile
    'v201': np.random.poisson(2.2, n_women).clip(0, 10)  # total children ever born
})

# ---------- Children Sample (KR) ----------
# Create a linkage: each child belongs to a woman
child_woman_idx = np.random.choice(n_women, n_children)
child_sample = pd.DataFrame({
    'caseid': women_sample['caseid'].iloc[child_woman_idx].values,
    'v001': women_sample['v001'].iloc[child_woman_idx].values,
    'v002': women_sample['v002'].iloc[child_woman_idx].values,
    'v005': women_sample['v005'].iloc[child_woman_idx].values,
    'v024': women_sample['v024'].iloc[child_woman_idx].values,
    'v025': women_sample['v025'].iloc[child_woman_idx].values,
    'v190': women_sample['v190'].iloc[child_woman_idx].values,
    'bidx': np.random.choice([1, 2, 3], n_children, p=[0.6, 0.3, 0.1]),  # birth order
    'midx': np.random.choice([1, 0], n_children, p=[0.5, 0.5]),  # most recent flag
    'b3': np.random.randint(2000, 2022, n_children),
    'b5': np.random.choice([1, 0], n_children, p=[0.95, 0.05]),  # child alive
    'b8': np.random.randint(20, 60, n_children),  # age in months
    'hw1': np.random.randint(0, 59, n_children),  # age in months for anthropometry
    'hc70': np.random.normal(-150, 120, n_children).astype(int),  # HAZ * 100
    'm14': np.random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 99], n_children, 
                            p=[0.01, 0.02, 0.05, 0.10, 0.25, 0.25, 0.15, 0.10, 0.05, 0.02]),
    'm15': np.random.choice([11, 12, 21, 22, 31, 32, 99], n_children,
                            p=[0.05, 0.10, 0.30, 0.20, 0.15, 0.10, 0.10])
})

# Add Province name for convenience
province_map = {1:'Koshi',2:'Madhesh',3:'Bagmati',4:'Gandaki',5:'Lumbini',6:'Karnali',7:'Sudurpashchim'}
women_sample['Province'] = women_sample['v024'].map(province_map)
child_sample['Province'] = child_sample['v024'].map(province_map)

# Save to CSV
women_sample.to_csv('sample_women.csv', index=False)
child_sample.to_csv('sample_child.csv', index=False)

print("✅ Sample data files created: sample_women.csv and sample_child.csv")
print(f"Women rows: {len(women_sample)}")
print(f"Children rows: {len(child_sample)}")