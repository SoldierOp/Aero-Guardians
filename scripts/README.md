# 🧪 Scripts

Utility scripts for testing, training, and deployment.

---

## 📁 Files

### Machine Learning
- **train_fire_prediction_model.py** - Train TinyML fire prediction model
  - Generates TensorFlow Lite model (6.53 KB)
  - Creates C headers for ESP32 deployment
  - Usage: `python scripts/train_fire_prediction_model.py`

### Testing
- **test_api.py** - Test backend API endpoints
- **test_backend.py** - Backend integration tests
- **test_whatsapp.py** - Test WhatsApp alert delivery
- **check_twilio_status.py** - Check Twilio message delivery status

---

## 🚀 Usage

### Train ML Model
```bash
cd C:\Users\Mayan\Downloads\aero-guardians-master
python scripts/train_fire_prediction_model.py
```

Output:
- `models/fire_prediction_model.tflite`
- `models/fire_prediction_model_data.h` (for ESP32)
- `models/scaler_params.h` (for ESP32)

### Test WhatsApp
```bash
python scripts/test_whatsapp.py
```

### Test Backend
```bash
# Start backend first
python -m uvicorn backend_api:app --reload

# Then test
python scripts/test_backend.py
```

---

## 📦 Dependencies

All scripts use dependencies from `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

**Last Updated:** February 6, 2026
