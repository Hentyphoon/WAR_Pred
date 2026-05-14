import pandas as pd

df = pd.read_csv("PlayerStat.csv")

# Replace all NaN values with 0
int_cols = ['AB', 'H', '1B', '2B', '3B', 'HR', 'BB', 'IBB', 'UBB', 
            'HBP', 'SB', 'CS', 'GDP', 'GDP_OPP', 'SF','wOBA']
df[int_cols] = df[int_cols].fillna(0).astype(int)
df['Age'] = df['Age'].astype(int)
df['PA'] = df['PA'].astype(int)