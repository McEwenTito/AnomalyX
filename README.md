# AnomalyX

# 🚀 AI-Powered Network Threat Detection

## 📌 Project Overview
This project is an AI-powered **Network Threat Detection System** using machine learning to detect anomalies in network traffic. It is based on the **CIC-IDS-2017** dataset and utilizes **FastAPI** to provide real-time inference on network logs. The frontend will be built later to visualize detected threats.

## 📂 Project Structure
```
.
├── data
│   ├── *.csv                  # Raw CIC-IDS-2017 dataset files
├── models
│   ├── categorical_dict.pkl   # Categorical encoding metadata
│   ├── label_encoder.pkl      # Label encoder for classification
│   ├── onehot_encoder.pkl     # OneHotEncoder for categorical features
│   ├── scaler_params.pkl      # Feature scaling parameters
│   ├── trained_model.pkl      # Trained machine learning model
├── results
│   ├── labeled_predictions.csv # Predictions from the model
├── scripts
│   ├── collect_metadata.py    # Metadata collection
│   ├── predict_unlabeled.py   # Runs inference on new network logs
│   ├── train_incrementally.py # Model training/updating script
│   ├── utils.py               # Helper functions
├── test_data
│   ├── unlabeled_test_data.csv # Sample network logs for testing
├── endpoints
│   ├── __init__.py
│   ├── health.py              # API health check endpoint
│   ├── threat_detection.py    # Main prediction endpoint
│   ├── logs.py                # Endpoint for viewing past logs
│   ├── alerts.py              # Alerts management
│   ├── model_status.py        # Endpoint to check model version
└── venv                       # Virtual environment
```

## 🏗️ Tech Stack
- **Backend**: FastAPI (Python)
- **Machine Learning**: Scikit-learn
- **Data Processing**: Pandas, NumPy
- **Frontend (Coming Soon)**: Angular with Material UI
- **Database (Planned)**: PostgreSQL for logs & alerts

## 🔧 Installation & Setup
### 1️⃣ Clone the Repository
```bash
git clone <repo_url>
cd <project_folder>
```

### 2️⃣ Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Run the FastAPI Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5️⃣ Access API Docs
After starting the server, visit:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🚀 API Endpoints
### 🔹 **Health Check**
```http
GET /health
```
Response:
```json
{"status": "ok"}
```

### 🔹 **Predict Threats from Network Logs**
```http
POST /threat-detection
```
**Request Body:**
```json
{
  "log_entries": [
    {"Destination Port": 80, "Flow Duration": 1000, ...},
    {"Destination Port": 443, "Flow Duration": 2000, ...}
  ]
}
```
**Response:**
```json
{
  "predictions": [
    {"id": 1, "threat_type": "Benign"},
    {"id": 2, "threat_type": "DDoS"}
  ]
}
```

### 🔹 **Retrieve Past Predictions**
```http
GET /logs
```
Response:
```json
[
  {"timestamp": "2025-03-05T12:00:00Z", "threat_type": "DDoS"},
  {"timestamp": "2025-03-05T12:05:00Z", "threat_type": "Benign"}
]
```

## ⚠️ Handling Model & Data
### Should I Commit Model Files?
❌ **No!** Trained models (`.pkl` files) should not be stored in Git. Instead:
- Use **DVC** to track models
- Store models in **S3 / GCS** and download them dynamically

### Training Data
❌ **Avoid committing raw datasets.** Instead, use `data/` in `.gitignore`.

## 🔮 Future Plans
- ✅ FastAPI Backend for Predictions
- 🔲 Frontend Dashboard (Angular)
- 🔲 Real-Time Log Processing
- 🔲 Database Storage for Logs & Alerts
- 🔲 Model Retraining Automation

## 📌 Contributing
1. Fork the repo
2. Create a new branch: `git checkout -b feature-new-endpoint`
3. Commit your changes: `git commit -m "Added new endpoint"`
4. Push to the branch: `git push origin feature-new-endpoint`
5. Submit a pull request

## 📜 License
MIT License. See `LICENSE` for details.

