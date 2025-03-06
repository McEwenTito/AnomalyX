import os
import pandas as pd
import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_class_weight
from utils import load_object, save_object, preprocess_chunk
from columns import categorical_cols, numeric_cols


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
