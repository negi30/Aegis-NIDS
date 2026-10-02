import json
import asyncio
import os
import random
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
from typing import List

from src.models.ml_engine import ml_engine
from src.response.mitigation import defense_system

from src.api.sniffer import BackgroundSniffer

# Setup templates
app = FastAPI(title="Aegis-NIDS Security Operations Center API")
templates = Jinja2Templates(directory="templates")

ml_engine._train_dummy_if_needed()

class FlowFeatures(BaseModel):
    features: List[float]
    src_ip: str
    dst_ip: str

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass
    async def broadcast_dict(self, data: dict):
        await self.broadcast(json.dumps(data))

manager = ConnectionManager()

# Create a global event loop reference
main_loop = None

@app.on_event("startup")
async def startup_event():
    global main_loop
    main_loop = asyncio.get_running_loop()

# Threadsafe wrapper for broadcasting UI updates from Sniffer Thread
def threadsafe_broadcast(data: dict):
    if main_loop and main_loop.is_running():
        asyncio.run_coroutine_threadsafe(manager.broadcast_dict(data), main_loop)

# Threadsafe wrapper for ML predictions from Sniffer Thread
def threadsafe_ml_predict(features, src_ip, dst_ip):
    if main_loop and main_loop.is_running():
        flow = FlowFeatures(features=features, src_ip=src_ip, dst_ip=dst_ip)
        asyncio.run_coroutine_threadsafe(predict_flow(flow), main_loop)

live_tap = BackgroundSniffer(threadsafe_broadcast, threadsafe_ml_predict)

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    demo_mode = os.getenv("CLOUD_DEMO_MODE", "False") == "True"
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request, "demo_mode": demo_mode})

@app.post("/api/v1/predict")
async def predict_flow(flow: FlowFeatures):
    start_time = time.time()
    result = ml_engine.predict(flow.features)
    mitigation = None
    if result["is_threat"]:
        mitigation = defense_system.block_ip(flow.src_ip, result["prediction"])
    
    latency = round((time.time() - start_time) * 1000, 2)
    response = {
        "type": "ml_alert",
        "src_ip": flow.src_ip,
        "prediction": result["prediction"],
        "confidence": result["confidence"],
        "mitre_tactic": result["mitre_tactic"],
        "shap_values": result.get("shap_values", []),
        "latency_ms": latency,
        "mitigation": mitigation
    }
    await manager.broadcast_dict(response)
    return response

@app.get("/api/v1/bans")
async def get_bans():
    return {"banned_ips": defense_system.get_active_bans()}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            cmd = json.loads(data)
            
            if cmd.get("action") == "toggle_sniffer":
                if cmd.get("state"):
                    live_tap.start()
                else:
                    live_tap.stop()
                    
            elif cmd.get("action") == "simulate":
                attack_type = cmd.get("type")
                dummy_features = [random.uniform(0, 0.1) for _ in range(78)]
                if attack_type == "dos":
                    dummy_features[0] = 100.0 
                elif attack_type == "portscan":
                    dummy_features[1] = 50.0   
                src_ip = f"{random.randint(10,192)}.{random.randint(0,255)}.1.{random.randint(2,254)}"
                flow = FlowFeatures(features=dummy_features, src_ip=src_ip, dst_ip="10.0.0.1")
                await predict_flow(flow)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
