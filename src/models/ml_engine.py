import os
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import RobustScaler
import joblib

class LCCDE_Engine:
    """
    Leader Class & Confidence Decision Ensemble (LCCDE)
    Combines XGBoost, LightGBM, and CatBoost (mocked here with RF for instant out-of-box demo).
    """
    def __init__(self):
        self.scaler = RobustScaler()
        self.supervised_model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.anomaly_detector = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
        self.is_trained = False
        
        # Attack mapping (0: Normal, 1: DoS, 2: PortScan, 3: BruteForce, 4: WebAttack)
        self.class_mapping = {
            0: "Normal",
            1: "DoS / DDoS",
            2: "PortScan",
            3: "Brute Force",
            4: "Web Attack"
        }

    def _train_dummy_if_needed(self):
        # 1. Attempt to load production serialized models first
        try:
            model_dir = os.path.join(os.path.dirname(__file__), "../../models_saved")
            if os.path.exists(os.path.join(model_dir, "lccde_supervised.pkl")):
                print("[*] Loading serialized ML models from disk (/models_saved)...")
                self.scaler = joblib.load(os.path.join(model_dir, "robust_scaler.pkl"))
                self.supervised_model = joblib.load(os.path.join(model_dir, "lccde_supervised.pkl"))
                self.anomaly_detector = joblib.load(os.path.join(model_dir, "anomaly_detector.pkl"))
                self.is_trained = True
                print("[+] Models successfully loaded into memory.")
                return
        except Exception as e:
            print(f"[-] Failed to load models: {e}. Falling back to instant demo mode.")

        # 2. Fallback: Instant Demo Mode (generates synthetic data if .pkl missing)
        if self.is_trained:
            return
            
        print("[*] Instant Demo Mode: Training ML models on synthetic flow data...")
        X_dummy = np.random.rand(500, 78)
        X_dummy[100:200, 0] = X_dummy[100:200, 0] * 10
        X_dummy[200:300, 1] = X_dummy[200:300, 1] * 5 
        
        y_dummy = np.random.choice([0, 1, 2, 3, 4], 500)
        
        self.scaler.fit(X_dummy)
        X_scaled = self.scaler.transform(X_dummy)
        
        self.supervised_model.fit(X_scaled, y_dummy)
        self.anomaly_detector.fit(X_scaled[y_dummy == 0])
        self.is_trained = True
        print("[+] Instant Demo Models ready.")

    def predict(self, features: list):
        if not self.is_trained:
            self._train_dummy_if_needed()
            
        X = np.array([features])
        X_scaled = self.scaler.transform(X)
        
        # 1. Check Zero-Day Anomaly (Tier 2)
        anomaly_score = self.anomaly_detector.decision_function(X_scaled)[0]
        is_anomaly = self.anomaly_detector.predict(X_scaled)[0] == -1
        
        if is_anomaly and anomaly_score < -0.1:
            return {
                "prediction": "Zero-Day Anomaly",
                "confidence": round(abs(anomaly_score) * 100, 2),
                "is_threat": True,
                "mitre_tactic": "T1190 - Exploit Public-Facing App",
                "shap_values": self._generate_shap(X_scaled, is_anomaly=True)
            }
            
        # 2. Check Known Signatures (Tier 1 - LCCDE)
        probs = self.supervised_model.predict_proba(X_scaled)[0]
        class_idx = np.argmax(probs)
        confidence = probs[class_idx]
        
        pred_label = self.class_mapping.get(class_idx, "Unknown")
        is_threat = class_idx != 0
        
        mitre_map = {
            "DoS / DDoS": "T1498 - Network Denial of Service",
            "PortScan": "T1046 - Network Service Discovery",
            "Brute Force": "T1110 - Brute Force",
            "Web Attack": "T1210 - Exploitation of Remote Services",
            "Normal": "None"
        }
        
        return {
            "prediction": pred_label,
            "confidence": round(confidence * 100, 2),
            "is_threat": is_threat,
            "mitre_tactic": mitre_map.get(pred_label, "Unknown"),
            "shap_values": self._generate_shap(X_scaled) if is_threat else []
        }
        
    def _generate_shap(self, X_scaled, is_anomaly=False):
        # Simulating TreeSHAP output for the UI waterfall chart
        # In a real environment, `shap.TreeExplainer(model).shap_values(X)` is used.
        features = ["Flow_IAT_Mean", "Bwd_Packet_Length_Std", "SYN_Flag_Count", "Fwd_Packets_s", "Dst_Port"]
        impacts = np.random.uniform(0.1, 0.6, 5)
        impacts = sorted(impacts, reverse=True)
        
        return [
            {"feature": f, "impact": round(i, 3)} for f, i in zip(features, impacts)
        ]

ml_engine = LCCDE_Engine()
