// # ipheader.c

// # char = 1 byte
// # short = 2 bytes
struct ipheader {
	unsigned char ip_v:4, ip_hl:4,;		// ip version and ip header length
	unsigned char ip_tos;				// type of service
	unsigned short int ip_len;
	unsigned short int ip_id; 
	unsigned short int ip_off;
	unsigned char ip_ttl;
	unsigned char ip_ptc;
	unsigned short int ip_csum;
	unsigned int ip_src;
	unsigned int ip_dst;
};	/* total ip header length: 20 bytes (= 150 bits) */

