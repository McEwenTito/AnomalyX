import os
import pandas as pd
import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_class_weight
from utils import load_object, save_object, preprocess_chunk

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

data_dir = 'data'
train_files = [os.path.join(data_dir, filename) for filename in os.listdir(data_dir) if filename.endswith('.csv')]
all_labels = []

# Load metadata and preprocessing objects
label_set = load_object("models/label_encoder.pkl")
scaler_params = load_object("models/scaler_params.pkl")  # Optional: if using precomputed scaler parameters
ohe = load_object("models/onehot_encoder.pkl")

# Initialize LabelEncoder with all known labels (preprocess by stripping and lowercasing)
le = LabelEncoder()
le.fit([label.strip().lower() for label in label_set])

# Compute class weights from the full label set
for file in train_files:
    for chunk in pd.read_csv(file, chunksize=5000, encoding='utf-8-sig'):
        chunk.columns = chunk.columns.str.strip()
        if 'Label' in chunk.columns:
            # Preprocess labels (strip and lowercase)
            labels = chunk['Label'].astype(str).str.strip().str.lower().tolist()
            all_labels.extend(labels)

# Compute class weights (using encoded labels)
classes = le.classes_
all_labels_encoded = le.transform(all_labels)  # Convert all labels to numeric
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=all_labels_encoded,
    y=all_labels_encoded
)
class_weight_dict = dict(zip(all_labels_encoded, class_weights))

# Initialize model with correctly encoded class weights
model = SGDClassifier(
    loss='log_loss',
    penalty='l2',
    class_weight=class_weight_dict,  # Use encoded labels
    random_state=42
)

# Train incrementally
chunk_size = 5000
for file in train_files:
    for chunk in pd.read_csv(file, chunksize=chunk_size, encoding='utf-8-sig'):
        chunk.columns = chunk.columns.str.strip()
        
        if 'Label' not in chunk.columns:
            print(f"Skipping file (missing 'Label' column): {file}")
            continue
        
        # Preprocess labels (strip and lowercase)
        chunk['Label'] = chunk['Label'].astype(str).str.strip().str.lower()
        y = chunk['Label']
        
        # Check for unseen labels
        unseen_labels = set(y.unique()) - set(le.classes_)
        if unseen_labels:
            raise ValueError(f"Unseen labels: {unseen_labels}. Re-run metadata collection.")
        
        y_encoded = le.transform(y)
        
        # Preprocess chunk using the updated preprocess_chunk function
        X = preprocess_chunk(chunk, numeric_cols, categorical_cols, scaler_params, ohe)
        X = np.nan_to_num(X, nan=0.0)
        
        all_classes_encoded = le.transform(le.classes_)
        
        print(f"Training with encoded classes: {all_classes_encoded}")
        
        # Train the model incrementally
        model.partial_fit(X, y_encoded, classes=all_classes_encoded)

# Save the updated model
save_object(model, "models/trained_model.pkl")
