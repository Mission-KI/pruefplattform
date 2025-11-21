import json
import pickle
import os
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

# Ensure the "sample_data" directory exists
os.makedirs("sample_data", exist_ok=True)

# Generate sample dataset
X, y = make_classification(n_samples=200, n_features=5, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train a simple Logistic Regression model
model = LogisticRegression()
model.fit(X_train, y_train)

# Save the model
with open("sample_data/model.pkl", "wb") as f:
    pickle.dump(model, f)

# Save the test features
with open("sample_data/X_test.json", "w") as f:
    json.dump(X_test.tolist(), f)

# Save the true labels
with open("sample_data/true_labels.json", "w") as f:
    json.dump(y_test.tolist(), f)

# Predict labels using the trained model
y_pred = model.predict(X_test)

# Save predictions
with open("sample_data/pred_labels.json", "w") as f:
    json.dump(y_pred.tolist(), f)

print("Sample data generated successfully.")
