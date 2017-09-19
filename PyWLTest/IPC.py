import socket
import threading
import time
import progress
import enum
import ctypes
import sys

import progress

#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#conn = socket.socket()

c_byte256 = ctypes.c_byte * 256

sock_lock = threading.Lock()

class locker:
	def __init__(self, lock):
		self.lock = lock
		self.entered = False
	
	def acquired(self):
		if (not self.entered):
			if (self.lock.acquire(False)):
				self.entered = True
		return self.entered

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		if (self.entered):
			self.lock.release()


class PayloadType(enum.Enum):
	status = 1
	sub_progress = 2	
	total_progress = 3
	write_perf = 4
	read_perf = 5
	error_str = 6
	

class status_payload(ctypes.Structure):
	_fields_ = [('signature', ctypes.c_int16),
				('type', ctypes.c_int16),				
				('msg', c_byte256)]

class progress_payload(ctypes.Structure):
	_fields_ = [('signature', ctypes.c_int16),
				('type', ctypes.c_int16),
				('progress', ctypes.c_float)]

class performance_payload(ctypes.Structure):
	_fields_ = [('signature', ctypes.c_int16),
				('type', ctypes.c_int16),
				('performance', ctypes.c_float)]

class IPC(object):
			
	def __init__(self):
		self.sock = None
		self.conn = None
		self.terminated = False
		self.check_thread = None
		self.connected = False
		self.prev_prog = 0
		self.perf_sender_timer = None
		
	def create_server_socket(self):
		""" initial socket and wait connection """
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind(('127.0.0.1', 50001))  				
		self.sock.listen(5)
		conn, addr = self.sock.accept()
		self.conn  = conn
		self.connected = True

	def start_terminate_check(self):
		""" start a thread to polling terminate signal from AP """
		self.check_thread = threading.Thread(target=self.check_terminated_thread, name = 'check_terminated')
		self.check_thread.daemon = True
		self.check_thread.start()
		
	def stop_check_thread(self):
		""" the deamon thread no need to terminate manually"""
		pass

	def check_terminated_thread(self):
		while (True):
			self.read_terminated()
			if (self.terminated):
				break
			time.sleep(1)	

	def read_terminated(self):
		if (self.conn == None):
			return

		with locker(sock_lock) as lock:
			if not lock.acquired():
				return False
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

		#time.sleep(1)
		return self.terminated

	def send_status(self, status:str):
		if (self.conn == None):
			return
		with locker(sock_lock) as lock:
			if not lock.acquired():
				return
			self.conn.setblocking(True)

			if (len(status) < 256):
				status = status + '\0' * (256-len(status))

			ba = bytearray(status.encode())
			msg = c_byte256.from_buffer(ba)

			p = status_payload(0x55aa, PayloadType.status.value, msg)

			buff = bytes(ctypes.sizeof(p))
			ctypes.memmove(buff, ctypes.byref(p), ctypes.sizeof(p))
	
			self.conn.sendall(buff)

	def send_error_str(self, status:str):
		if (self.conn == None):
			return
		with locker(sock_lock) as lock:
			while not lock.acquired():
				pass
			self.conn.setblocking(True)

			if (len(status) < 256):
				status = status + '\0' * (256-len(status))

			ba = bytearray(status.encode())
			msg = c_byte256.from_buffer(ba)

			p = status_payload(0x55aa, PayloadType.error_str.value, msg)

			buff = bytes(ctypes.sizeof(p))
			ctypes.memmove(buff, ctypes.byref(p), ctypes.sizeof(p))
	
			self.conn.sendall(buff)

	def send_sub_progress(self, prog):
		if (self.conn == None):
			return
		with locker(sock_lock) as lock:
			if not lock.acquired():
				return
			self.conn.setblocking(True)	

			if (type(prog)==progress.sub_progress):			
				p = progress_payload(0x55aa, PayloadType.sub_progress.value, prog.get_position())
			elif (type(prog)==float or type(prog)==int):
				p = progress_payload(0x55aa, PayloadType.sub_progress.value, prog)
				
			buff = bytes(ctypes.sizeof(p))
			ctypes.memmove(buff, ctypes.byref(p), ctypes.sizeof(p))

			self.conn.sendall(buff)	

	def send_total_progress(self, prog):
		if (self.conn == None):
			return
		with locker(sock_lock) as lock:
			if not lock.acquired():
				return
			self.conn.setblocking(True)		
	
			if (type(prog)==progress.progress):			
				p = progress_payload(0x55aa, PayloadType.total_progress.value, prog.get_position())
			elif (type(prog)==float or type(prog)==int):
				p = progress_payload(0x55aa, PayloadType.total_progress.value, prog)
		
			buff = bytes(ctypes.sizeof(p))
			ctypes.memmove(buff, ctypes.byref(p), ctypes.sizeof(p))

			self.conn.sendall(buff)
			
	def send_write_performance(self, write_perf:float):
		if (self.conn == None):
			return

		with locker(sock_lock) as lock:
			if not lock.acquired():
				return
			self.conn.setblocking(True)		
	
			p = performance_payload(0x55aa, PayloadType.write_perf.value, write_perf)
		
			buff = bytes(ctypes.sizeof(p))
			ctypes.memmove(buff, ctypes.byref(p), ctypes.sizeof(p))

			self.conn.sendall(buff)

	def send_read_performance(self, read_perf:float):
		if (self.conn == None):
			return

		with locker(sock_lock) as lock:
			if not lock.acquired():
				return
			self.conn.setblocking(True)		
	
			p = performance_payload(0x55aa, PayloadType.read_perf.value, read_perf)
		
			buff = bytes(ctypes.sizeof(p))
			ctypes.memmove(buff, ctypes.byref(p), ctypes.sizeof(p))

			self.conn.sendall(buff)