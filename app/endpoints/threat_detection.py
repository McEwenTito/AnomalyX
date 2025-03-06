from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional, List, Dict
import pandas as pd
import numpy as np
from io import StringIO
import joblib
from ml_pipeline.columns import categorical_cols, numeric_cols
# Import our utility function from your scripts (adjust the import as needed)
from ml_pipeline.utils import load_object, preprocess_chunk

router = APIRouter()


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
