import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import statsmodels.api as sm

from sklearn.impute import KNNImputer
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler, LabelEncoder

df = pd.read_csv('test_kaggle_1/Five_years_of_Russian_Rap_Dataset.csv')

label_encoder = LabelEncoder()

predict_columns = ['hit_n','Drums_Energy','Drums_Complexity',
                    'Variety_of_musical_instruments','Mixing_Quality',
                    'Harmonic_Richness','Mixing_Character','Emotional_Intensity',
                    'is_feat','n_feat','higher_guest','album_type','track_number',
                    'explicit','key_name','mode_name','key_mode','remake']

# print(df[predict_columns].head(5).T)

categoric_columns = []
for i in df.columns:
    if len(df[i].unique()) < 26:
        categoric_columns.append(i)

for col in df[categoric_columns]:
    df[col] = label_encoder.fit_transform(df[col])


X = df.drop(['track_id','artist_name','album_release_date',
             'status_guest','album_name','artists_all',
             'artist_id','album_id','download_link','Song_Success'], axis=1)
y = df[['Song_Success']]

# X_with_const = sm.add_constant(X)

# model = sm.OLS(y, X_with_const)
# results = model.fit()

# # print(results.summary())
# print(df[predict_columns].head(5).T)
# # print(df.dtypes)

# ------------------- Modified Section -------------------
def forecasting_model(X_train, X_test, y_train, y_test, model_type="DecisionTreeRegressor"):
    """
    Trains a forecasting model based on the provided training and testing data along with the model type.
    Returns the fitted model, mse, r2, coefficients (if available), and an interpretation of the performance.
    """
    if model_type == "DecisionTreeRegressor":
        model = DecisionTreeRegressor()
    elif model_type == "LinearRegression":
        model = LinearRegression()
    else:
        raise ValueError("Unsupported model type. Please choose 'DecisionTreeRegressor' or 'LinearRegression'.")
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    interpretation = decision_tree_accuracy(mse, r2)
    
    # Attempt to extract coefficients if the model supports them
    if model_type == "LinearRegression":
        coefficients = model.coef_
    else:
        coefficients = "Coefficients not available for this model type"
    
    return model, mse, r2, coefficients, interpretation

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model, mse, r2, coefficients, interpretation = forecasting_model(X_train, X_test, y_train, y_test, model_type="DecisionTreeRegressor")
# ---------------- End of Modified Section ----------------

model = DecisionTreeRegressor()  # Инициализация модели решающего дерева
model.fit(X_train, y_train)      # Обучение модели

y_pred = model.predict(X_test)   # Прогнозирование значений целевой переменной на тестовой выборке

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("Mean Squared Error (MSE):", mse)
print("R-squared (R²):", r2)

# determining the accuracy of the decision tree model
def decision_tree_accuracy(mse, r2):
    """
    Evaluates decision tree model performance and provides interpretation

    Args:
        mse: Mean squared error value
        r2: R-squared value

    Returns:
        str: Detailed interpretation of model performance
    """
    interpretation = "\nModel Performance Analysis:\n"

    # MSE interpretation
    interpretation += f"Mean Squared Error: {mse:.4f}\n"
    if mse < 0.1:
        interpretation += "- Very low prediction error, excellent accuracy\n"
    elif mse < 0.3:
        interpretation += "- Moderate prediction error, acceptable accuracy\n"
    else:
        interpretation += "- High prediction error, poor accuracy\n"

    # R2 interpretation
    interpretation += f"R-squared Score: {r2:.4f}\n"
    if r2 >= 0.7:
        interpretation += "- Model explains {:.1f}% of data variance\n".format(r2 * 100)
        interpretation += "- Strong predictive power, model is reliable\n"
    elif r2 >= 0.5:
        interpretation += "- Model explains {:.1f}% of data variance\n".format(r2 * 100)
        interpretation += "- Moderate predictive power, model may be useful but has limitations\n"
    else:
        interpretation += "- Model explains only {:.1f}% of data variance\n".format(r2 * 100)
        interpretation += "- Weak predictive power, model needs improvement\n"

    # Final verdict
    interpretation += "Verdict: \n"
    if r2 >= 0.6 and mse < 0.2:
        interpretation += "Model is suitable for use with good predictive capabilities\n"
    elif r2 >= 0.4 and mse < 0.3:
        interpretation += "Model can be used but with caution, consider improving\n"
    else:
        interpretation += "Model is not recommended for use, needs significant improvement\n"

    return interpretation

print(decision_tree_accuracy(mse, r2))
