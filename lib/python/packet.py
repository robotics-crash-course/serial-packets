# /**
#  * Copyright (c) 2023  Catherine Van West <catherine.vanwest@cooper.edu>
#  * SPDX-License-Identifier: GPL-3.0-or-later
#  */

from ctypes import c_int32, c_uint32
from serialize import *
import struct
import base64
import hashlib
import traceback

# start_tx =   b'\x01' # SOH (start of heading)
# start_data = b'\x02' # STX (start of text)
# end_data =   b'\x03' # ETX (end of text)
# end_tx =     b'\x04' # EOT (end of transmission)
# Alternate
start_tx =   b'#' # SOH (start of heading)
start_data = b'$' # STX (start of text)
end_data =   b'%' # ETX (end of text)
end_tx =     b'&' # EOT (end of transmission)

class Packet:
	def __init__(self, p_id = None, data = None):
		self.id_ = p_id or 0
		self.data_ = data or ''


	def checksum(self, cksum = None):
		ser_id = serialize((Int32, ), [self.id_])
		self_sum = hashlib.sha1(ser_id + self.data_).hexdigest().encode('utf-8')

		if cksum:
			return cksum == self_sum
		else:
			return self_sum[0:4]

	# sort of for interface completeness, but... sure
	def id(self):
		return self.id_

	def data(self):
		if(True): pass
		return self.data_

	def to_bytes(self):
		return \
			start_tx + \
			base64.b64encode(serialize((Int32, ), [self.id_])) + \
			start_data + \
			base64.b64encode(self.data_) + \
			end_data + \
			self.checksum() + \
			end_tx
	
	@classmethod
	# def from_bytes(cls, b: bytearray):
	# 	if b[0] == start_tx:
	# 		b = b[1:]
	# 	b = b[:b.find(end_tx)]
	# 	bid, remainder = b.split(start_data, 1)
	# 	bdata, cksum = remainder.split(end_data, 1)
	# 	if cksum[-1:] == end_tx:
	# 		cksum = cksum[:-1]
		
	# 	p_id 	= struct.unpack('I', bid)
	# 	p_data	= struct.unpack('i', bdata)
	# 	p = cls(p_id[0], p_data[0])
	# 	return p
	
	def from_bytes(cls, b):
		try:
			if b.find(start_tx) == 0:
				b = b[1:]
			b = b[:b.find(end_tx)]
			b64_id, remainder = b.split(start_data, 1)
			b64_data, cksum = remainder.split(end_data, 1)
			if cksum[-1:] == end_tx:
				cksum = cksum[:-1]

			p_id, _ = deserialize((Int32, ), base64.b64decode(b64_id))
			p = cls(p_id[0], base64.b64decode(b64_data))

			# if not p.checksum(cksum):
			# 	raise Exception('checksum failed!')

			return p
		except Exception as e:
			traceback.print_exc()
			return Packet()

	def write_to(self, ser):
		ser.write(self.to_bytes())
	
	# Write to socket
	def wireless_write_to(self, wireless):
		wireless.sockout.sendto(self.to_bytes(), (wireless.interface.picoip, wireless.interface.porttopico))
		pass

	@classmethod
	def read_from_raw(cls, data):
		if type(data) == str:
			return cls.from_bytes(bytes(data, encoding='utf-8'))
		if type(data) == bytes:
			return cls.from_bytes(data)
		return cls.from_bytes(data)


	# will block until a verified packet gets through!
	@classmethod
	def read_from(cls, ser):
		while True:
			try:
				ser.read_until(expected=start_tx)
				return cls.from_bytes(ser.read_until(expected=end_tx))
			except:
				pass

	@classmethod
	def read_and_remove_from_buffer(cls, buf):
		try:
			packet_list = []
			ret_buf = b''
			start_tx_index = buf.find(start_tx)
			buf = buf[start_tx_index:]
			pbytes, ret_buf = buf.split(end_tx, 1)
			pbytes = pbytes + end_tx
			packet_list.append(Packet.from_bytes(pbytes))
			return packet_list, ret_buf
		except Exception as e:
			return packet_list, buf
	"""
	Find first start_tx
	find end_tx, if no end_tx, return
	if start and end, pull out msg (including start and end bits)
	p = cls.from_bytes, append to output list,
	repeat
	return list of found packets in buffer
	"""

	def __repr__(self):
		return f'Packet<id_={self.id_}, data_={self.data_} ; Checksum Not Implemented!>'
