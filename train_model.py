import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

print(f"Using scikit-learn version: {sklearn.__version__}")

# Generate training data
np.random.seed(42)
n_samples = 2000

open_p = np.random.uniform(100, 300, n_samples)
high_p = open_p + np.random.uniform(0.5, 10.0, n_samples)
low_p = open_p - np.random.uniform(0.5, 10.0, n_samples)
close_p = low_p + np.random.uniform(0, high_p - low_p)
adj_close_p = close_p * np.random.uniform(0.98, 1.0, n_samples)
returns = np.random.normal(0.0005, 0.02, n_samples)

year = np.random.randint(2020, 2027, n_samples)
month = np.random.randint(1, 13, n_samples)
quarter = (month - 1) // 3 + 1
day = np.random.randint(1, 29, n_samples)

X = pd.DataFrame({
    'open': open_p,
    'high': high_p,
    'low': low_p,
    'close': close_p,
    'adj_close': adj_close_p,
    'returns': returns,
    'year': year,
    'month': month,
    'quarter': quarter,
    'day': day
})

y = X['close'] * (1 + X['returns']) + np.random.normal(0, 0.5, n_samples)

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)

score = model.score(X_test, y_test)
print(f"Model R² Test Score: {score:.4f}")

# Export to stock.pkl with joblib
MODEL_PATH = 'stock.pkl'
joblib.dump(model, MODEL_PATH)

print(f"✅ Model successfully saved to '{MODEL_PATH}' using joblib!")