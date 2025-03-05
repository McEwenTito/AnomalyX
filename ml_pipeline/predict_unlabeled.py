import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from utils import load_object, preprocess_chunk

# Define categorical and numeric columns (must match training script)
categorical_cols = [
    'Fwd PSH Flags', 'Bwd PSH Flags', 'Fwd URG Flags', 'Bwd URG Flags',
    'FIN Flag Count', 'SYN Flag Count', 'RST Flag Count', 'PSH Flag Count',
    'ACK Flag Count', 'URG Flag Count', 'CWE Flag Count', 'ECE Flag Count'
]

numeric_cols = [
    'Destination Port', 'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets',
    'Total Length of Fwd Packets', 'Total Length of Bwd Packets', 'Fwd Packet Length Max',
    'Fwd Packet Length Min', 'Fwd Packet Length Mean', 'Fwd Packet Length Std',
    'Bwd Packet Length Max', 'Bwd Packet Length Min', 'Bwd Packet Length Mean',
    'Bwd Packet Length Std', 'Flow Bytes/s', 'Flow Packets/s', 'Flow IAT Mean',
    'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min', 'Fwd IAT Total', 'Fwd IAT Mean',
    'Fwd IAT Std', 'Fwd IAT Max', 'Fwd IAT Min', 'Bwd IAT Total', 'Bwd IAT Mean',
    'Bwd IAT Std', 'Bwd IAT Max', 'Bwd IAT Min', 'Fwd Header Length', 'Bwd Header Length',
    'Fwd Packets/s', 'Bwd Packets/s', 'Min Packet Length', 'Max Packet Length',
    'Packet Length Mean', 'Packet Length Std', 'Packet Length Variance', 'Down/Up Ratio',
    'Average Packet Size', 'Avg Fwd Segment Size', 'Avg Bwd Segment Size',
    'Fwd Avg Bytes/Bulk', 'Fwd Avg Packets/Bulk', 'Fwd Avg Bulk Rate',
    'Bwd Avg Bytes/Bulk', 'Bwd Avg Packets/Bulk', 'Bwd Avg Bulk Rate',
    'Subflow Fwd Packets', 'Subflow Fwd Bytes', 'Subflow Bwd Packets',
    'Subflow Bwd Bytes', 'Init_Win_bytes_forward', 'Init_Win_bytes_backward',
    'act_data_pkt_fwd', 'min_seg_size_forward', 'Active Mean', 'Active Std',
    'Active Max', 'Active Min', 'Idle Mean', 'Idle Std', 'Idle Max', 'Idle Min'
]

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
