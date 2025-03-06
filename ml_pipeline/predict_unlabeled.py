import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from utils import load_object, preprocess_chunk
from columns import numeric_cols, categorical_cols

import pickle

# For debugging: Print the loaded model
with open("models/trained_model.pkl", "rb") as f:
    print(pickle.load(f))

# Load metadata and model
label_set = load_object("models/label_encoder.pkl")  # This is a set of labels
# Reinitialize and fit LabelEncoder using the label set
le = LabelEncoder()
le.fit([label.strip().lower() for label in label_set])  # Make sure to match the preprocessing

ohe = load_object("models/onehot_encoder.pkl")  # Load the OneHotEncoder
scaler_params = load_object("models/scaler_params.pkl")  # Load the scaler parameters
model = load_object("models/trained_model.pkl")  # Load the trained model (e.g., SGDClassifier)

# Predict unlabeled data
chunk_size = 5000
predictions = []

for chunk in pd.read_csv("test_data/unlabeled_test_data.csv", chunksize=chunk_size):
    # Strip whitespace from column names
    chunk.columns = chunk.columns.str.strip()
    
    # Preprocess chunk
    X_test = preprocess_chunk(chunk, numeric_cols, categorical_cols, scaler_params, ohe)
    
    # Handle missing values (replace NaN with 0)
    X_test = np.nan_to_num(X_test, nan=0.0)
    
    print(f"Missing values in chunk: {np.isnan(X_test).sum()}")
    
    # Predict labels
    preds = model.predict(X_test)  # Use the trained model for prediction
    
    # Decode predicted labels using the fitted LabelEncoder
    chunk['Predicted_Label'] = le.inverse_transform(preds)
    predictions.append(chunk)

# Save results
final_predictions = pd.concat(predictions)
final_predictions.to_csv("results/labeled_predictions.csv", index=False)
