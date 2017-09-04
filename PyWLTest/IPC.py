import socket
import threading
import time
import progress
import enum
import ctypes
import sys

#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#conn = socket.socket()

c_byte256 = ctypes.c_byte * 256

class PayloadType(enum.Enum):
	status = 1
	total_progress = 2
	sub_progress = 3	

class status_payload(ctypes.Structure):
	_fields_ = [('signature', ctypes.c_int16),
				('type', ctypes.c_byte),
				('msg', c_byte256)]

class IPC:
			
	def __init__(self):
		self.sock = None
		self.conn = None
		self.terminated = False
		self.check_thread = None
		self.connected = False
		self.progress = progress.progress(0, 100)

	def create_server_socket(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind(('127.0.0.1', 50001))  				
		self.sock.listen(5)
		conn, addr = self.sock.accept()
		self.conn  = conn
		self.connected = True

	def start_check_thread(self):
		self.check_thread = threading.Thread(target=self.check_terminated_thread, name = 'check_terminated')
		self.check_thread.start()
		
	def stop_check_thread(self):
		del self.check_thread

	def check_terminated_thread(self):
		while (True):
			self.read_terminated()
			if (self.terminated):
				break
			time.sleep(1)	

	def read_terminated(self):
		self.conn.setblocking(0)
		try:
			self.sock.settimeout(1)
			data = self.conn.recv(10)
		except:
			data = None

		self.terminated = False
		if (data != None):
			if ('terminated'.encode('utf-8') in data):
				self.conn.setblocking(True)
				self.conn.sendall('i got it'.encode())
				self.terminated = True
			else:
				self.terminated = False

		time.sleep(1)
		return self.terminated

	def send_status(self, status:str):
		self.conn.setblocking(True)

		if (len(status) < 256):
			status = status + '\0' * (256-len(status))

		ba = bytearray(status.encode())
		msg = c_byte256.from_buffer(ba)

		p = status_payload(0x55aa, PayloadType.status.value, msg)

		buff = bytes(ctypes.sizeof(p))
		ctypes.memmove(buff, ctypes.byref(p), ctypes.sizeof(p))
	
		self.conn.sendall(buff)