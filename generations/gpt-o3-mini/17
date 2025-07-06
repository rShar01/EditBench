import pandas as pd

# Load the dataset from a CSV file
df = pd.read_csv('events.csv')

# ----------------------- Unchanged code -----------------------

# Other processing steps (if any) go here
# For example, some previous analysis or transformation of df

# ----------------- Highlighted section (modified) -----------------
# Create a new column 'Frequency' and put 117 on every row that has 'E16' in 'EventId'
df.loc[df['EventId'].str.contains('E16', na=False), 'Frequency'] = 117

# ----------------------- Unchanged code -----------------------

# Continue with the rest of the code
df.to_csv('events_modified.csv', index=False)
print("File has been modified and saved as 'events_modified.csv'")
