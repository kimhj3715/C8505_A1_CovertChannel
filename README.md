README

Disable firewall server side or bounce server
	iptables -F
	iptables -X


RUN

Example: Server - receiver
python covert.py -source 192.168.0.1 -dest 192.168.0.2 -dest_port 80 
-server -file receive.txt

Example: Client - sender
python covert.py -source 192.168.0.1 -dest 192.168.0.2 -source_port 8000 
-dest_port 80 -file send.txt

