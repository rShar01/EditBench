import pandas as pd

# Original definitions (unchanged)
df_votes = pd.DataFrame({
    'id': [1, 2, 3],
    'vote': ['yes', 'no', 'yes']
})

df_relations = pd.DataFrame({
    'id': [2, 3, 4],
    'relation': ['friend', 'colleague', 'family']
})

# ------------------ Highlighted Section (changed) ------------------
merged_df = pd.merge(df_votes, df_relations, on='id', how='outer')
# ---------------------------------------------------------------------

# Further processing remains unchanged
print(merged_df)
