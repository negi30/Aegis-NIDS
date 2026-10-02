import os
import time
import requests
import random
from collections import defaultdict
import threading

try:
    from scapy.all import sniff, IP, TCP, UDP
except ImportError:
    print("Scapy not found. Please run: pip3 install scapy")
    exit(1)

API_URL = "http://127.0.0.1:8080/api/v1/predict"
FLOW_TIMEOUT = 2.0  # seconds to aggregate packets before sending to AI

class LiveFlowSniffer:
    def __init__(self):
        # Maps a 5-tuple (src, dst, sport, dport, proto) to flow statistics
        self.active_flows = defaultdict(lambda: {
            "packet_count": 0,
            "total_bytes": 0,
            "start_time": time.time(),
            "last_time": time.time(),
            "syn_count": 0,
            "src_ip": "",
            "dst_ip": ""
        })
        self.lock = threading.Lock()

    def packet_callback(self, packet):
        if IP not in packet:
            return
            
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        proto = packet[IP].proto
        
        sport, dport = 0, 0
        syn_flag = 0
        
        if TCP in packet:
            sport = packet[TCP].sport
            dport = packet[TCP].dport
            if packet[TCP].flags == 'S':
                syn_flag = 1
        elif UDP in packet:
            sport = packet[UDP].sport
            dport = packet[UDP].dport

        # Flow key (directional)
        flow_key = f"{src_ip}:{sport}-{dst_ip}:{dport}-{proto}"
        
        with self.lock:
            flow = self.active_flows[flow_key]
            flow["packet_count"] += 1
            flow["total_bytes"] += len(packet)
            flow["last_time"] = time.time()
            flow["syn_count"] += syn_flag
            flow["src_ip"] = src_ip
            flow["dst_ip"] = dst_ip

    def _extract_features_and_send(self, flow):
        """
        Approximates the 78 CICFlowMeter features.
        Calculates the real metrics we have (packet rates, sizes) and pads the rest.
        """
        duration = flow["last_time"] - flow["start_time"]
        if duration <= 0:
            duration = 0.0001
            
        flow_bytes_s = flow["total_bytes"] / duration
        flow_packets_s = flow["packet_count"] / duration
        
        # Base template for 78 features
        features = [random.uniform(0, 0.1) for _ in range(78)]
        
        # Inject our REAL live calculations into the feature vector
        # (Assuming indices based on standard CIC flow mappings)
        features[0] = flow_packets_s       # e.g., Flow Packets/s
        features[1] = flow["total_bytes"]  # e.g., Total Fwd Packets/Bytes
        features[2] = flow["syn_count"]    # e.g., SYN Flag Count
        
        payload = {
            "features": features,
            "src_ip": flow["src_ip"],
            "dst_ip": flow["dst_ip"]
        }
        
        try:
            requests.post(API_URL, json=payload, timeout=0.5)
        except requests.exceptions.RequestException:
            pass # Ignore if dashboard is off or busy

    def flow_flusher(self):
        """
        Background thread that checks for completed flows and sends them to the ML API.
        """
        while True:
            time.sleep(1)
            current_time = time.time()
            
            with self.lock:
                keys_to_delete = []
                for key, flow in self.active_flows.items():
                    # If flow has been quiet for FLOW_TIMEOUT
                    if current_time - flow["last_time"] > FLOW_TIMEOUT:
                        if flow["packet_count"] > 2: # Ignore random 1-packet noise
                            self._extract_features_and_send(flow)
                        keys_to_delete.append(key)
                        
                for key in keys_to_delete:
                    del self.active_flows[key]

    def start(self):
        print("🛡️ Aegis-NIDS Live Sniffer Started")
        print("Listening for Wi-Fi traffic (Requires sudo privileges)...")
        print("Press Ctrl+C to stop.")
        
        # Start flusher thread
        flusher = threading.Thread(target=self.flow_flusher, daemon=True)
        flusher.start()
        
        # Start sniffing (store=0 prevents memory leaks)
        # Using prn callback for every packet
        sniff(prn=self.packet_callback, store=0)

if __name__ == "__main__":
    sniffer = LiveFlowSniffer()
    sniffer.start()
