import os
import pandas as pd
import numpy as np
from collections import defaultdict
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from utils import save_object
from columns import categorical_cols, numeric_cols

# Initialize containers
label_set = set()
categorical_dict = defaultdict(set)
numeric_stats = defaultdict(lambda: {'sum': 0, 'sq_sum': 0, 'count': 0})



# Process files in chunks
chunk_size = 5000
data_dir = 'data'
train_files = [os.path.join(data_dir, filename) for filename in os.listdir(data_dir) if filename.endswith('.csv')]


for file in train_files:
    try:
        for chunk in pd.read_csv(file, chunksize=chunk_size, encoding='utf-8-sig'):
            chunk.columns = chunk.columns.str.strip()
            
            if 'Label' not in chunk.columns:
                print(f"Skipping file (missing 'Label' column): {file}")
                break
            
            # Collect labels (strip whitespace and lowercase)
            labels = chunk['Label'].astype(str).str.strip().str.lower().unique()
            label_set.update(labels)
            
            # Collect categorical features
            for col in categorical_cols:
                if col in chunk.columns:  # Check if column exists
                    categorical_dict[col].update(chunk[col].unique())
                else:
                    print(f"Warning: Column '{col}' not found in file: {file}")
            
            # Accumulate numeric stats
            for col in numeric_cols:
                if col in chunk.columns:  # Check if column exists
                    chunk[col] = chunk[col].replace([np.inf, -np.inf], np.nan)  # Replace inf with NaN
                    chunk[col] = chunk[col].fillna(0) 
                    chunk[col] = chunk[col].astype(np.float64)
                    numeric_stats[col]['sum'] += chunk[col].sum()
                    numeric_stats[col]['sq_sum'] += (chunk[col]**2).sum()
                    numeric_stats[col]['count'] += len(chunk[col])
                else:
                    print(f"Warning: Column '{col}' not found in file: {file}")
    except Exception as e:
        print(f"Error processing file: {file}. Error: {e}")
        continue

# Calculate global mean/std for scaling
scaler_params = {}
for col in numeric_stats:
    if numeric_stats[col]['count'] > 0:  # Ensure count is nonzero
        mean = numeric_stats[col]['sum'] / numeric_stats[col]['count']
        std = np.sqrt(
            (numeric_stats[col]['sq_sum'] / numeric_stats[col]['count']) - mean**2
        )
    else:
        mean, std = 0, 0  # Assign default values
    scaler_params[col] = {'mean': mean, 'std': std}

# After collecting categorical data, fit the OneHotEncoder
ohe = OneHotEncoder(
    categories=[sorted(categorical_dict[col]) for col in categorical_cols],
    handle_unknown='ignore',
    sparse_output=False
)

# Pad shorter sets with None to ensure equal lengths
max_length = max(len(categorical_dict[col]) for col in categorical_cols)
padded_data = {
    col: list(categorical_dict[col]) + [None] * (max_length - len(categorical_dict[col]))
    for col in categorical_cols
}

# Fit the encoder on the padded categorical data
ohe.fit(pd.DataFrame(padded_data))
print("All labels collected:", label_set)
print("All labels collected:", ohe)
print("All categories collected:", categorical_dict)
print("All scalar_params collected:", scaler_params)


# Save the fitted encoder
save_object(ohe, "models/onehot_encoder.pkl")  # Save the OneHotEncoder, not categorical_dict

# Save metadata
save_object(label_set, "models/label_encoder.pkl")
save_object(categorical_dict, "models/categorical_dict.pkl")  # Save categorical_dict separately
save_object(scaler_params, "models/scaler_params.pkl")