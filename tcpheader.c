// tcpheader.c
struct tcpheader {
	unsigned short int tcp_sport;
	unsigned short int tcp_dport;
	unsigned int tcp_seq;
	unsigned int tcp_ack;
	unsigned char tcp_x2:4, tcp_off:4;
	unsigned char tcp_flags;
	unsigned short int tcp_win;
	unsigned short int tcp_csum;
	unsigned short int tcp_up;	
};	/* total ip header length: 20 bytes (= 150 bits) */