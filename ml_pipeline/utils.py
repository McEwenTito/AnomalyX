import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

def save_object(obj, filepath):
    """Save an object to disk using pickle."""
    with open(filepath, 'wb') as f:
        pickle.dump(obj, f)

def load_object(filepath):
    """Load an object from disk using pickle."""
    with open(filepath, 'rb') as f:
        return pickle.load(f)

def preprocess_chunk(chunk, numeric_cols, categorical_cols, scaler_params, ohe):
    # Extract numeric features
    X_numeric = chunk[numeric_cols].copy()
    
    # Replace infinite values with NaN and fill them with 0
    X_numeric = X_numeric.replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # Optionally clip extreme values to a reasonable range (adjust thresholds as needed)
    X_numeric = X_numeric.clip(lower=-1e9, upper=1e9)
    
    # Apply scaling. Here we use StandardScaler.
    # If you have precomputed scaler_params and wish to use them, you can load/apply them here.
    scaler = StandardScaler()
    X_numeric_scaled = scaler.fit_transform(X_numeric)
    
    # Process categorical features using the provided one-hot encoder (ohe)
    X_categorical = ohe.transform(chunk[categorical_cols])
    
    # Combine numeric and categorical features
    X = np.hstack((X_numeric_scaled, X_categorical))
    
    return X
