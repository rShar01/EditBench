import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import statsmodels.api as sm

from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder

df = pd.read_csv('/Users/nnm_wm/python/test_kaggle_1/Five_years_of_Russian_Rap_Dataset.csv')

label_encoder = LabelEncoder()

predict_columns = ['hit_n', 'Drums_Energy', 'Drums_Complexity',
                   'Variety_of_musical_instruments', 'Mixing_Quality',
                   'Harmonic_Richness', 'Mixing_Character', 'Emotional_Intensity',
                   'is_feat', 'n_feat', 'higher_guest', 'album_type', 'track_number',
                   'explicit', 'key_name', 'mode_name', 'key_mode', 'remake']

# First, define candidate categorical columns from the entire dataframe
candidate_categoric_columns = ['status_guest']
for i in df.columns:
    if len(df[i].unique()) < 26:
        candidate_categoric_columns.append(i)

# Remove duplicates if any
candidate_categoric_columns = list(set(candidate_categoric_columns))

# Apply label encoding to these candidate categorical columns
for col in candidate_categoric_columns:
    df[col] = label_encoder.fit_transform(df[col])

# Create the feature matrix X and target vector y by dropping specific columns
X = df.drop(columns=['track_id', 'artist_name', 'album_release_date',
                     'status_guest', 'album_name', 'artists_all',
                     'artist_id', 'album_id', 'download_link', 'Song_Success'])
y = df['Song_Success']

# Only keep those predictor columns that exist in X
valid_predict_columns = [col for col in predict_columns if col in X.columns]
# Only keep those categorical columns that still remain in X.
valid_categoric_columns = [col for col in candidate_categoric_columns if col in X.columns]

# Now create the preprocessor using the valid column lists
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), valid_predict_columns),
        ('cat', OneHotEncoder(), valid_categoric_columns)
    ])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier())
])

pipeline.fit(X_train, y_train)
