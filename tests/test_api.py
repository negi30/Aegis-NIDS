import pytest
import asyncio
from fastapi.testclient import TestClient
from src.api.main import app
import time

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200

def test_predict_normal_traffic():
    payload = {
        "features": [0.1] * 78,
        "src_ip": "192.168.1.5",
        "dst_ip": "10.0.0.1"
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "latency_ms" in data

def test_active_defense_ban_list():
    response = client.get("/api/v1/bans")
    assert response.status_code == 200
    assert "banned_ips" in response.json()
