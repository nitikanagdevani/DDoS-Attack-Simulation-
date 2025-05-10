## Cybersecurity Cookbook: Simulating a DDoS Attack #

This project demonstrates the simulation and real-time mitigation of a SYN flood DDoS attack using GNS3 and VirtualBox. It involves setting up a virtual environment with a Command & Control (C2) server, bot machine, and a victim server.

# Key Features:

1. Attack Simulation: Python-based C2 server triggers bots to launch SYN flood attacks on the victim.

2. Traffic Monitoring: tshark used on the victim VM to observe and analyze incoming SYN packets.

3. Real-Time Mitigation: Custom Python script monitors traffic, auto-bans IPs exceeding a threshold using iptables.

4. Live Dashboard: Flask + WebSocket-based dashboard displays SYN activity and blocked IPs in real time.


# Tools & Technologies:

1. Kali Linux, Ubuntu Server

2. VirtualBox, GNS3

3. Python, tshark, iptables

4. Flask, Socket.IO, Chart.js
