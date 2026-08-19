
from pathlib import Path
import numpy as np
import joblib
from PIL import Image
from sklearn.ensemble import RandomForestClassifier

BASE = Path(__file__).parent
MODEL = BASE / "model.joblib"

def features(path):
    a = np.asarray(Image.open(path).convert("RGB").resize((32,32)), dtype=float)/255.0
    green = a[:,:,1] - (a[:,:,0] + a[:,:,2])/2
    # compact colour + vegetation + spatial features
    return np.r_[a.mean((0,1)), a.std((0,1)), green.mean(), green.std(),
                 a.reshape(-1,3)[::8].ravel()]

def train():
    X, y = [], []
    for name, label in [("forest",0),("deforestation",1)]:
        for p in (BASE/"dataset"/name).glob("*.jpg"):
            X.append(features(p)); y.append(label)
    m = RandomForestClassifier(n_estimators=120, random_state=42, class_weight="balanced")
    m.fit(X,y)
    joblib.dump(m, MODEL)
    return m

def get_model():
    if MODEL.exists():
        return joblib.load(MODEL)
    return train()

def predict(path):
    m = get_model()
    x = features(path).reshape(1,-1)
    cls = int(m.predict(x)[0])
    confidence = float(m.predict_proba(x)[0][cls] * 100)
    prediction = "DEFORESTATION" if cls else "FOREST"
    risk = "HIGH" if cls else "LOW"
    # Risk score is the actual deforestation probability, not a fixed demo number.
    proba = m.predict_proba(x)[0]
    risk_score = float(proba[1] * 100)
    if risk_score >= 75: risk="CRITICAL"
    elif risk_score >= 50: risk="HIGH"
    elif risk_score >= 25: risk="MEDIUM"
    else: risk="LOW"
    return {"prediction":prediction, "confidence":round(confidence,2),
            "risk":risk, "risk_score":round(risk_score,2)}
