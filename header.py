class Header:
	def __init__(self, seq_num, ack_num, syn, ack):
		self.seq_num = seq_num
		self.ack_num = ack_num
		self.syn = syn
		self.ack = ack

	def bits(self):
		bits = format(self.seq_num, '032b')
		bits += format(self.ack_num, '032b')
		bits += format(self.syn, '01b')
		bits += format(self.ack, '01b')
		bits += '0' * 30
		return bits.encode()
	
	# Remove later (just for testing)
	def details(self):
		print(f'seq num: {self. seq_num}, ack_num: {self.ack_num}, syn: {self.syn}, ack: {self.ack}')

	def get_seq_num(self):
		return self.seq_num
	
	def get_ack_num(self):
		return self.ack_num
	
	def get_syn(self):
		return self.syn
	
	def get_ack(self):
		return self.ack
	
	def set_seq_num(self, seq_num):
		self.seq_num = seq_num

	def set_ack_num(self, ack_num):
		self.ack_num = ack_num

	def set_syn(self, syn):
		self.syn = syn
	
	def set_ack(self, ack):
		self.ack = ack

def bits_to_header(bits):
	bits = bits.decode()
	seq_num = int(bits[:32], 2)
	ack_num = int(bits[32:64], 2)
	syn = int(bits[64], 2)
	ack = int(bits[65], 2)
	return Header(seq_num, ack_num, syn, ack)

def get_body(data):
	data = data.decode()
	return data[96:]
