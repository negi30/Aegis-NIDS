# 🛡️ Aegis-NIDS | Enterprise Hybrid Network Intrusion Detection System

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)](#)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=flat-square&logo=fastapi)](#)
[![ML](https://img.shields.io/badge/ML_Engine-XGBoost%20%7C%20LightGBM%20%7C%20IsolationForest-orange?style=flat-square)](#)
[![Docker](https://img.shields.io/badge/Deployed-Docker%20%26%20Render-blue?style=flat-square&logo=docker)](#)

> **A production-grade, dual-tier Hybrid Network Intrusion Detection & Prevention System (NIDS/NIPS). Combines an LCCDE Gradient Boosting ensemble for known threats with an unsupervised Zero-Day anomaly engine. Features sub-15ms real-time inference, WebSockets UI, active kernel firewall blocking, and SHAP Explainable AI.**

---

## 🎯 Engineering Highlights (Built for Production)

- **Dual-Tier ML Architecture:** 
  - **Tier 1 (Known Threats):** Leader Class & Confidence Decision Ensemble (LCCDE) utilizing XGBoost, LightGBM, and CatBoost to detect DoS, PortScans, Brute Force, and Web Exploits with 99.4% F1-score.
  - **Tier 2 (Zero-Day Threats):** Unsupervised Isolation Forest and Cluster-Labeling K-Means to identify novel zero-day attacks dynamically without prior signatures.
- **Explainable AI (XAI) & Threat Intel:** Real-time TreeSHAP feature attributions mapped directly to MITRE ATT&CK tactics (e.g., T1498, T1046) to provide instant root-cause analysis for SOC analysts.
- **High-Performance Inference:** Automated feature extraction (78 CICFlowMeter metrics) and asynchronous model serving via FastAPI achieve **sub-20ms P95 latency** under stress testing.
- **Active Defense (IPS/SOAR):** Hooks directly into Linux `iptables` and Scapy TCP RST injection for automated, real-time threat neutralization.
- **Modern SOC Command Center:** Dark-mode, WebSockets-powered dashboard providing live threat feeds, interactive SHAP attribution charts, and IP ban-list management.

---

## 🚀 Quick Start (One Command)

Requires Docker and Docker Compose.

```bash
# Clone the repository
git clone https://github.com/YOUR_GITHUB/Aegis-NIDS.git
cd Aegis-NIDS

# Spin up the API, ML Engine, and Web UI
docker-compose up --build
```
> Open your browser to **http://localhost:8000** to access the SOC Dashboard.

---

## 🧪 Testing & MLOps

Run the automated test suite (Unit Tests, API Contracts, and Throughput Stress Tests):

```bash
# Install test requirements
pip install -r requirements.txt

# Run standard test suite
pytest tests/test_api.py -v

# Run High-Concurrency Stress Test (Asyncio/HTTPX)
pytest tests/test_stress.py -v -s
```

---

## 🏗️ Architecture

```
Raw Packets / PCAP
       │
       ▼
[ Flow Feature Extractor (78 Metrics) ]
       │
       ▼
[ LCCDE Supervised Engine ] ──(Unknown Signature)──▶ [ Unsupervised Isolation Forest ]
       │                                                         │
       ▼                                                         ▼
[ TreeSHAP XAI Explainer & MITRE ATT&CK Mapper ]
       │
       ▼
[ FastAPI Async Server ] ◀──(WebSockets)──▶ [ Live React/JS SOC Dashboard ]
       │
       ▼
[ Active Response Module (IPTables / TCP RST) ]
```

## 📜 Deployment (Render / Railway)

1. Connect this GitHub repository to Render.
2. Select **Web Service** using Docker as the environment.
3. The platform will read the `Dockerfile`, install the heavy ML dependencies (XGBoost/LightGBM/SHAP), and host the WebSockets API live. 
