import pandas as pd

df = pd.read_csv('metadata.csv')
total_images = len(df)
yellow_images = (df['Label'] == 'Yellow').sum()
blue_images = (df['Label'] == 'Blue').sum()
purple_images = (df['Label'] == 'Purple').sum()

print(f"Total Images: {total_images}")
print(f"Yellow Images: {yellow_images}")
print(f"Blue Images: {blue_images}")
print(f"Purple Images: {purple_images}")
print("\n" + "="*50 + "\n")

contributor_counts = pd.crosstab(df['Contributor'], df['Label'])

for label in ['Yellow', 'Blue', 'Purple']:
    if label not in contributor_counts.columns:
        contributor_counts[label] = 0

summary_table = contributor_counts[['Yellow', 'Blue', 'Purple']].sort_index(ascending=False)
print(summary_table)