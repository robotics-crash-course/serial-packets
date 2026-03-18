#!/usr/bin/python3
# mostly stolen from Mike's/Jeannette's code
# adapted for Pico communications

from queue import Queue
from PyQt6.QtCore import QThread, QObject, QRunnable, pyqtSlot
from threading import Thread
import serial
import time
import traceback
import socket
from messages import *
from packet import Packet

class Worker(QRunnable):
	pass

class CommsController(QObject):
	read_buffer: bytes
	
	def __init__(self, port, baudrate=115200, timeout=10):
		super().__init__()
		self.read_buffer = bytes()
		# self.outbound_thread =  Thread(target=self.handle_outbound)
		# self.inbound_thread =  Thread(target=self.handle_inbound)  
		self.outbound_thread = Worker()
		# self.inbound_thread  = Worker()
		self.outbound_thread.run = self.handle_outbound
		# self.inbound_thread.run = self.handle_inbound

		self.outbound = Queue()
		self.inbound = Queue()

		self.ser = serial.Serial(
			port=port, baudrate=baudrate,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			bytesize=serial.EIGHTBITS,
			timeout=timeout
		)
		self.connected = True # sort of vestigial

	def fake_inbound(self):
		x=0
		while True:
			x+=1
			self.inbound.put(Position(x).pack())
			time.sleep(0.05)

	def handle_outbound(self):
		while True:
			try:
				# print(f"OUTBOUND QUEUE: {self.outbound.qsize()}")
				if self.outbound.empty() == False:
					p = self.outbound.get()
					p.write_to(self.ser)
			except:
				print('exception in outbound loop:')
				print(traceback.format_exc())
			try:
				# print("INBOUND")
				if self.ser.inWaiting() > 0:
					# p = Packet.read_from(self.ser)
					# self.inbound.put(p)
					incoming = self.ser.read(self.ser.inWaiting())
					self.read_buffer += incoming
					# print(f"READ BUFFER: {self.read_buffer}")
					# p = Packet.from_bytes(self.read_buffer)
				# print(f"read buffer handle inbound: {self.read_buffer}")
				if(self.read_buffer != b''):
					packet_list, ret_buffer = Packet.read_and_remove_from_buffer(self.read_buffer)
					self.read_buffer = ret_buffer
					# print(f"RETURN BUFFER: {self.read_buffer}")
					# print(f"packetlist: {packet_list}")
					for p in packet_list: self.inbound.put(p)
					# print(f"INBOUND QUEUE: {self.inbound.qsize()}")
			except:
				print('exception in inbound loop:')
				print(traceback.format_exc())

	def handle_inbound(self):
		while True:
			try:
				print("INBOUND")
				if self.ser.inWaiting() > 0:
					# p = Packet.read_from(self.ser)
					# self.inbound.put(p)
					incoming = self.ser.read(self.ser.inWaiting())
					self.read_buffer += incoming
					# p = Packet.from_bytes(self.read_buffer)
					print(f"read buffer handle inbound: {self.read_buffer}")
					packet_list = Packet.read_and_remove_from_buffer(self)
					print(f"packetlist: {packet_list}")
					if packet_list is not None:
						for p in packet_list: self.inbound.put(p)
			except:
				print('exception in inbound loop:')
				print(traceback.format_exc())

	def send(self, p):
		self.outbound.put(p)

	def has_packet(self):
		return not self.inbound.empty()

	def get_packet(self):
		return self.inbound.get()
	
class WirelessInterface:
	picoip = '192.168.1.37'
	porttopico = 9900
	computerip = '192.168.1.35'
	porttocomputer = 9999
	picohostname = 'PICOHOME'
	computerhostname = 'localhost'

	def __init__(self, picohostname, picoip, porttopico, computerhostname, computerip, porttocomputer):
		self.picoip = picoip
		self.porttopico = porttopico
		self.computerip = computerip
		self.porttocomputer = porttocomputer
		self.picohostname = picohostname
		self.computerhostname = computerhostname

class WirelessController(CommsController):
	def __init__(self, interface:WirelessInterface):
		self.outbound_thread = Thread(
		target=self.handle_outbound, daemon=True
		)
		self.inbound_thread = Thread(
			target=self.handle_inbound, daemon=True
		)
		self.outbound = Queue()
		self.inbound = Queue()

		# Setup UDP comm interface
		self.interface = interface
		self.sockout = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sockin = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		# Check the local ip and pico ip and warn if they are not equivalent
		try:
			# computerip = socket.gethostbyname("localhost")
			# picoip = socket.gethostbyname("picohostname")
			# assert computerip 	== interface.computerip, 'Computer ip is different'
			# assert picoip  		== interface.picoip, 'Pico ip is different'
			self.sockin.bind((self.interface.computerip, self.interface.porttocomputer))
			self.connected = True
		except Exception as e:
			print('exception in setup:')
			print(traceback.format_exc())
			self.connected = False
			print("Socket setup failed")
		self.outbound_thread.start()
		self.inbound_thread.start()

	def handle_outbound(self):
		while True:
			try:
				if not self.outbound.empty():
					p = self.outbound.get()
					p.wireless_write_to(self)
			except:
				print('exception in outbound loop:')
				print(traceback.format_exc())

	def handle_inbound(self):
		while True:
			try:
				data, addr = self.sockin.recvfrom(512)
				assert addr[0] == self.interface.picoip, 'Incoming data not from pico'
				p = Packet.read_from_raw(data)
				self.inbound.put(p)
			except:
				print('exception in inbound loop:')
				print(traceback.format_exc())


def packet_receive(p):
	if p.id_ == Twist.id():
		print(f"Received: {Twist(p)}")
	if p.id == Test_Inbound.id():
		print(f"Received: {Test_Inbound(p)}")

if __name__ == "__main__":
	c = WirelessController(WirelessInterface)

	f1 = 0.0
	f2 = 1.0

	loop_time = 1
	while True:
		time.sleep(loop_time/3)

		# tout = Test_Outbound(f1, f2)
		# pout = tout.pack()
		# c.send(pout)
		time.sleep(loop_time/3)
		tout = Twist((1.5, 0.05))
		pout = tout.pack()
		c.send(pout)

		print(f'sending:    {tout}')
		print(f'packet out: {pout}')

		time.sleep(loop_time/3)
		while c.has_packet():
			pin = c.get_packet()
			packet_receive(pin)
