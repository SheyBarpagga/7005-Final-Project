class Header:
	def __init__(self, seq_num, ack_num, syn, ack):
		self.seq_num = seq_num
		self.ack_num = ack_num
		self.syn = syn
		self.ack = ack

	def bits(self):
		bits = format(self.seq_num)
		bits += format(self.ack_num)
		bits += format(self.syn)
		bits += format(self.ack)
		bits += format(0)
		return bits.encode()
	
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