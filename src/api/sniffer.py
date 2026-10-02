import time
import threading
import random
import asyncio
from collections import defaultdict
try:
    from scapy.all import sniff, IP, TCP, UDP
except ImportError:
    pass

class BackgroundSniffer:
    def __init__(self, broadcast_callback, ml_predict_callback):
        self.is_running = False
        self.thread = None
        self.broadcast = broadcast_callback
        self.ml_predict = ml_predict_callback
        self.active_flows = defaultdict(lambda: {
            "packet_count": 0, "total_bytes": 0, "start_time": time.time(),
            "last_time": time.time(), "syn_count": 0, "src_ip": "", "dst_ip": "", "proto": ""
        })
        self.lock = threading.Lock()

    def packet_callback(self, packet):
        if not self.is_running or IP not in packet:
            return
            
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        
        sport, dport = 0, 0
        syn_flag = 0
        proto_name = "IP"
        
        if TCP in packet:
            sport = packet[TCP].sport
            dport = packet[TCP].dport
            proto_name = "TCP"
            if packet[TCP].flags == 'S':
                syn_flag = 1
        elif UDP in packet:
            sport = packet[UDP].sport
            dport = packet[UDP].dport
            proto_name = "UDP"

        # 1. Send raw packet to frontend UI instantly
        self.broadcast({
            "type": "raw_packet",
            "src": f"{src_ip}:{sport}",
            "dst": f"{dst_ip}:{dport}",
            "proto": proto_name,
            "len": len(packet)
        })

        # 2. Aggregate flow for ML Engine
        flow_key = f"{src_ip}:{sport}-{dst_ip}:{dport}-{proto_name}"
        with self.lock:
            flow = self.active_flows[flow_key]
            flow["packet_count"] += 1
            flow["total_bytes"] += len(packet)
            flow["last_time"] = time.time()
            flow["syn_count"] += syn_flag
            flow["src_ip"] = src_ip
            flow["dst_ip"] = dst_ip

    def flow_flusher(self):
        while self.is_running:
            time.sleep(1)
            current_time = time.time()
            with self.lock:
                keys_to_delete = []
                for key, flow in self.active_flows.items():
                    if current_time - flow["last_time"] > 2.0: # 2s timeout
                        if flow["packet_count"] > 2:
                            features = [random.uniform(0, 0.1) for _ in range(78)]
                            features[0] = flow["packet_count"] / (flow["last_time"] - flow["start_time"] + 0.001)
                            features[1] = flow["total_bytes"]
                            features[2] = flow["syn_count"]
                            # Trigger ML prediction internally
                            self.ml_predict(features, flow["src_ip"], flow["dst_ip"])
                        keys_to_delete.append(key)
                for key in keys_to_delete:
                    del self.active_flows[key]

    def _start_sniffing(self):
        try:
            sniff(prn=self.packet_callback, store=0, stop_filter=lambda x: not self.is_running)
        except PermissionError:
            self.broadcast({"type": "error", "msg": "Permission Denied. You must run the server with 'sudo' to sniff packets."})
            self.is_running = False

    def start(self):
        if self.is_running: return
        self.is_running = True
        self.thread = threading.Thread(target=self._start_sniffing, daemon=True)
        self.flusher_thread = threading.Thread(target=self.flow_flusher, daemon=True)
        self.thread.start()
        self.flusher_thread.start()
        self.broadcast({"type": "status", "msg": "Live Tap ACTIVE"})

    def stop(self):
        self.is_running = False
        self.broadcast({"type": "status", "msg": "Live Tap OFFLINE"})
