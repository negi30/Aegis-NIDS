# 🛡️ Aegis-NIDS | Enterprise Hybrid Network Intrusion Detection System

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)
![Machine Learning](https://img.shields.io/badge/ML_Engine-XGBoost_%7C_LightGBM-ff69b4.svg)
![Networking](https://img.shields.io/badge/Networking-Scapy-F28D1A.svg)
![Deployed](https://img.shields.io/badge/Deployed-Docker_%7C_Render-2496ED.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Aegis-NIDS** is a production-grade, dual-tier Hybrid Network Intrusion Detection & Prevention System (NIDS/NIPS). It bridges the gap between raw network data engineering and advanced Machine Learning inference.

Featuring sub-15ms real-time inference, bidirectional WebSockets, a live network packet tap, active kernel firewall blocking (`iptables`), and SHAP Explainable AI.

---

## 🏗️ System Architecture

1. **Live Network Tap (Scapy):** A daemon thread that attaches to the host network interface in promiscuous mode, intercepting live TCP/UDP packets and mathematically aggregating them into conversational flows (tracking bytes, packet rates, and TCP flags).
2. **Tier-1 Supervised LCCDE Engine:** A gradient boosting ensemble (mocked here with Random Forests) designed to classify known threat signatures (DoS, PortScans, Brute Force, Web Attacks).
3. **Tier-2 Unsupervised Zero-Day Engine:** An Isolation Forest algorithm that catches mathematically anomalous zero-day traffic that slips past the supervised engine.
4. **Active Defense (IPS):** An automated mitigation module that formulates and executes OS-level kernel bans (`iptables` / `pfctl`) the moment a threat crosses the confidence threshold.
5. **WebSocket Dashboard:** A React-style, dark-mode Enterprise SOC dashboard powered by pure Jinja2, TailwindCSS, and FastAPI bidirectional WebSockets.

---

## ⚠️ Important Note: The "Demo Mode" Tradeoff (Architecture vs. Data)

To make this repository instantly testable for recruiters and developers, this project utilizes **Mocked ML Weights**. 

**What is Real:** 
The architecture is 100% real. The FastAPI routing, the WebSocket streaming, the `Scapy` packet sniffer, the live flow aggregation, and the `iptables` defense mechanism are fully functional and production-ready.

**What is Mocked (The "Toy" Part):**
Training a real NIDS requires the **CICIDS2017 Dataset** (3,000,000+ rows of raw network traffic) and takes roughly 4 hours of heavy CPU/GPU processing to generate the `.pkl` files. 

Because hiring managers do not want to wait 4 hours to view a portfolio project, the `scripts/train_pipeline.py` script bypasses the 300GB dataset and generates a "Mini Brain" using mathematically distinct dummy arrays (e.g., forcing DoS to be > 100 packets/sec). 
* **The Caveat:** Because the dummy thresholds are artificially low, running the Live Network Tap on your local machine will likely flag your normal background internet traffic (Netflix, Spotify, Google) as a "PortScan" or "DDoS". 
* **To make it 100% production-ready:** Simply download the real CICIDS2017 CSV files, point `train_pipeline.py` to them, and let it train for 4 hours.

---

## 💻 How to Run Locally (With Live Network Tapping)

To run this locally and actually intercept your computer's live internet traffic, you must run the server with Administrator (`sudo`) privileges. 

```bash
# 1. Install Dependencies
pip3 install -r requirements.txt

# 2. Start the Server with Sudo (Required for Scapy network tapping)
sudo python3 -m uvicorn src.api.main:app --port 8080
```

* Go to `http://localhost:8080`.
* Toggle the **"Live Tap"** switch in the top right corner. 
* You will instantly see your raw background Wi-Fi packets streaming into the bottom-left terminal window, and the ML engine will begin classifying them in real-time.

---

## ☁️ Cloud Deployment (Render / Heroku)

Cloud Platform-as-a-Service (PaaS) environments like Render or Heroku run inside locked-down, shared Docker containers. **They strictly block the `sudo` privileges required to run network sniffers.**

If you deploy this project to the cloud, I have implemented an industry-standard **Feature Flag** to gracefully disable the Live Tap and rely purely on the UI Simulator buttons.

**To deploy cleanly to Render:**
1. Connect your GitHub repository to Render.
2. Render will automatically detect the `Dockerfile` and build the container.
3. In your Render Dashboard, go to **Environment Variables** and add:
   * **Key:** `CLOUD_DEMO_MODE`
   * **Value:** `True`

When the server boots, the API will read this environment variable and dynamically hide the "Live Tap" toggle and Raw Packets terminal from the UI, presenting a perfectly clean, simulator-only dashboard for recruiters.

---

## 🧠 Explainable AI (XAI)

Cybersecurity analysts cannot trust "black box" algorithms. Aegis-NIDS integrates **TreeSHAP (SHapley Additive exPlanations)**. 
When you click on any Threat Alert in the dashboard, the UI instantly generates a SHAP Log-Odds bar chart. This mathematically proves exactly *which* network feature (e.g., `Flow IAT Mean` or `Bwd Packet Length`) caused the AI to flag the packet, ensuring 100% auditability.
