import subprocess
import json
import asyncio
import websockets
from datetime import datetime, timedelta, timezone
import os
import socket

# === Config ===
WS_SERVER = "ws://192.168.1.12:8765"  # Dashboard IP
INTERFACE = "enp0s3"                  # Network interface
THRESHOLD = 100                       # Ban IP after this many SYN packets
BAN_DURATION = 3600                  # (Optional) duration in seconds

# IST Timezone
IST = timezone(timedelta(hours=5, minutes=30))

# Track counts and bans
ip_counter = {}
banned_ips = set()

# === Get Victim's Own IP Dynamically ===
def get_own_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

own_ip = get_own_ip()
print(f"[🔍] Ignoring Victim's Own IP: {own_ip}")

# === WebSocket Send ===
async def send_data(data):
    try:
        async with websockets.connect(WS_SERVER) as ws:
            await ws.send(json.dumps(data))
    except Exception as e:
        print(f"[!] WebSocket error: {e}")

# === Load IPs already blocked via iptables ===
def load_banned_ips_from_iptables():
    print("[🔎] Loading banned IPs from iptables...")
    try:
        result = subprocess.run(["sudo", "iptables", "-L", "INPUT", "-n"], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        for line in lines:
            if "DROP" in line:
                parts = line.split()
                if len(parts) >= 4:
                    ip = parts[3]
                    if ip not in banned_ips:
                        banned_ips.add(ip)

                        # Send to dashboard (only once per IP)
                        timestamp = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
                        banned_msg = {
                            "ip": ip,
                            "timestamp": timestamp,
                            "banned": True
                        }
                        asyncio.run(send_data(banned_msg))

        print(f"[✅] Loaded {len(banned_ips)} unique banned IPs from iptables")
    except Exception as e:
        print(f"[!] Error loading iptables rules: {e}")

# === Ban IP ===
def ban_ip(ip):
    if ip in banned_ips:
        return
    print(f" BANNING IP: {ip}")
    banned_ips.add(ip)
    os.system(f"sudo iptables -A INPUT -s {ip} -j DROP")

# === SYN Monitor ===
async def monitor_syn():
    print("[+] Starting tshark listener...")
    proc = await asyncio.create_subprocess_exec(
        "tshark", "-i", INTERFACE,
        "-Y", "tcp.flags.syn==1 && tcp.flags.ack==0",
        "-T", "fields", "-e", "ip.src", "-l",
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )

    while True:
        line = await proc.stdout.readline()
        if not line:
            continue

        ip = line.decode().strip()
        if not ip or ip == own_ip:
            continue  

        # Timestamp in IST
        timestamp = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")

        # Update count
        ip_counter[ip] = ip_counter.get(ip, 0) + 1
        syn_count = ip_counter[ip]

        # Ban if threshold exceeded
        if syn_count >= THRESHOLD and ip not in banned_ips:
            ban_ip(ip)
            banned_msg = {
                "ip": ip,
                "timestamp": timestamp,
                "banned": True
            }
            await send_data(banned_msg)

        if ip not in banned_ips:
            data = {
                "ip": ip,
                "timestamp": timestamp,
                "syn_count": syn_count
            }
            print(f"[📡] Sending to dashboard: {data}")
            await send_data(data)

# === MAIN ===
if __name__ == "__main__":
    load_banned_ips_from_iptables()
    asyncio.run(monitor_syn())
