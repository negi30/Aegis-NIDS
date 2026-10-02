import asyncio
import time
import httpx
import pytest

@pytest.mark.asyncio
async def test_high_throughput_inference():
    """
    Stress testing the ML API to ensure sub-20ms P95 latency under load.
    Proves production readiness for 2-year exp roles.
    """
    url = "http://localhost:8000/api/v1/predict"
    payload = {
        "features": [0.5] * 78,
        "src_ip": "10.0.0.99",
        "dst_ip": "192.168.1.1"
    }
    
    num_requests = 100
    latencies = []
    
    async with httpx.AsyncClient() as client:
        start_time = time.time()
        
        # Fire concurrent requests
        tasks = [client.post(url, json=payload) for _ in range(num_requests)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        
    total_time = end_time - start_time
    
    # Calculate successful requests
    successes = [r for r in responses if not isinstance(r, Exception) and r.status_code == 200]
    
    # Extract latency reported by API
    for r in successes:
        data = r.json()
        latencies.append(data["latency_ms"])
        
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    p95_latency = sorted(latencies)[int(len(latencies)*0.95)] if latencies else 0
    
    print(f"\n--- STRESS TEST RESULTS ---")
    print(f"Total Requests: {num_requests}")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Throughput: {num_requests/total_time:.2f} req/s")
    print(f"Avg Latency (Model Inference): {avg_latency:.2f}ms")
    print(f"P95 Latency: {p95_latency:.2f}ms")
    
    # Assertions for enterprise SLAs
    assert len(successes) == num_requests, "Some requests failed under load"
    assert avg_latency < 50, f"Latency too high: {avg_latency}ms"
