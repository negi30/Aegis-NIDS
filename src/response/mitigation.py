import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ActiveDefense")

class ActiveDefenseSystem:
    """
    Simulates / Executes Active IPS Remediation via IPTables and TCP RST.
    """
    def __init__(self, mode="IPS"):
        self.mode = mode # 'IDS' (Passive) or 'IPS' (Active Block)
        self.banned_ips = {}
        
    def block_ip(self, ip_address: str, reason: str, ttl_minutes: int = 30):
        if self.mode == "IDS":
            logger.info(f"[PASSIVE] Threat detected from {ip_address} ({reason}). No action taken.")
            return {"status": "Logged only (IDS Mode)"}
            
        if ip_address in self.banned_ips:
            return {"status": "Already Blocked"}
            
        # Simulating iptables command execution
        cmd = f"iptables -I INPUT -s {ip_address} -j DROP -m comment --comment 'AegisNIDS-{reason}'"
        logger.warning(f"🚨 [ACTIVE DEFENSE] Executing Kernel Ban: {cmd}")
        
        self.banned_ips[ip_address] = {
            "reason": reason,
            "banned_at": time.time(),
            "ttl": ttl_minutes
        }
        
        return {"status": "IPTables Blocked", "ip": ip_address, "ttl": ttl_minutes}

    def inject_tcp_rst(self, src_ip, dst_ip, src_port, dst_port):
        if self.mode == "IDS":
            return {"status": "Logged only (IDS Mode)"}
            
        logger.warning(f"🚨 [ACTIVE DEFENSE] Injecting Scapy TCP RST -> {src_ip}:{src_port}")
        # Real implementation uses scapy: send(IP(src=dst_ip, dst=src_ip)/TCP(sport=dst_port, dport=src_port, flags="R"))
        return {"status": "TCP Session Killed"}

    def get_active_bans(self):
        current_time = time.time()
        active = []
        for ip, data in list(self.banned_ips.items()):
            time_passed = (current_time - data["banned_at"]) / 60
            if time_passed > data["ttl"]:
                del self.banned_ips[ip] # TTL expired
            else:
                active.append({
                    "ip": ip,
                    "reason": data["reason"],
                    "time_remaining_min": round(data["ttl"] - time_passed, 1)
                })
        return active

defense_system = ActiveDefenseSystem(mode="IPS")
