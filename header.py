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