from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional, List, Dict
import pandas as pd
import numpy as np
from io import StringIO
import joblib

# Import our utility function from your scripts (adjust the import as needed)
from ml_pipeline.utils import load_object, preprocess_chunk

router = APIRouter()

# Define the numeric and categorical columns (should match your training configuration)
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

# Load model artifacts from disk
model = load_object("models/trained_model.pkl")
label_enc = load_object("models/label_encoder.pkl")
ohe = load_object("models/onehot_encoder.pkl")
scaler_params = load_object("models/scaler_params.pkl")

@router.post("/predict")
async def predict_threat(
    file: Optional[UploadFile] = File(None),
    logs: Optional[List[Dict]] = None  # JSON payload: a list of log records
):
    """
    Predict threats from input logs.
    Accepts either a CSV file upload or a JSON payload.
    Returns predictions as JSON.
    """
    if file is None and logs is None:
        raise HTTPException(status_code=400, detail="No input provided. Please upload a CSV file or provide JSON payload.")

    # If file is provided, read CSV data
    if file is not None:
        try:
            contents = await file.read()
            s = str(contents, "utf-8")
            df = pd.read_csv(StringIO(s))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading CSV file: {e}")
    else:
        # Otherwise, assume logs provided as JSON payload
        try:
            df = pd.DataFrame(logs)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing JSON payload: {e}")

    # Preprocess data using your utility function
    try:
        X_test = preprocess_chunk(df, numeric_cols, categorical_cols, scaler_params, ohe)
        X_test = np.nan_to_num(X_test, nan=0.0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error preprocessing data: {e}")

    # Predict using the trained model
    try:
        preds = model.predict(X_test)
        decoded_preds = label_enc.inverse_transform(preds)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during prediction: {e}")

    # Return predictions as JSON
    return {"predictions": decoded_preds.tolist()}
