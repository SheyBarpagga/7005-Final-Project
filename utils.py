import header

def bits_to_header(bits):
	bits = bits.decode()
	seq_num = int(bits[:32], 2)
	ack_num = int(bits[32:64], 2)
	syn = int(bits[64], 2)
	ack = int(bits[65], 2)
	return header.Header(seq_num, ack_num, syn, ack)

def get_body(data):
	data = data.decode()
	return data[96:]