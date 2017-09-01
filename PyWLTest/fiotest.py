import random
import logging
import os
import pattern
import time
import iolib

import win32pipe, win32file
import win32file

import socket

from filematrix import *
from fileset import *
from diskutil import *
from ctypes import *
from contextlib import contextmanager

def debug_info_en():
	logging.basicConfig(level=logging.INFO)

class fio_test(object):
	"""test by file read write to a disk"""
	def __init__(self, root: str, matrix: filematrix, random_seed: int):
		thisdir = os.path.dirname(__file__)
		self.root = root
		self.seed = random_seed
		self.filematrix = matrix
		self.max_buff_size = 4096
		self.buffer_cnt = 32
		self.write_elapsed = 0.0							   
		self.read_elapsed = 0.0		
		self.written_sectors = 0
		self.readed_sectors = 0
		self.randlib = WinDLL(thisdir + '\\random.dll')
		self.terminated = False				
		self.__prepair_patterns()
		self.__create_read_pipe()
		self.reset()

	def __exit__(self):
		self.sock.close()

	def __create_read_pipe(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind(('127.0.0.1', 50001))  		
		self.sock.setblocking(0)

	def __check_terminated(self):
		if (self.terminated == True):
			return True

		try:
			data = self.sock.recvfrom(1024)
		except:
			data = None
		
		self.terminated = False
		if (data != None):
			if ('terminated'.encode('utf-8') in data[0]):
				self.terminated = True
			else:
				self.terminated = False
		return self.terminated

	def __prepair_patterns(self):
		""" Create an amount of bytearray of test patterns, these is a ring to make contents of the test files.
		"""

		gen = self.randlib.Generate
		buff_type = c_ubyte * (self.max_buff_size * 512)
		self.pat_array = []
		
		for i in range(self.buffer_cnt):
			temp = buff_type()
			gen(temp, self.max_buff_size * 512, self.seed+i)   
			self.pat_array.append(temp)

	def __reset_pat(self):
		""" [private method] Reset the pattern array iterator """
		self.pat_it = iter(self.pat_array)

	def reset(self):		
		self.rand = random.Random(self.seed)
		self.__reset_pat()
		self.filematrix.reset()

	def delete_all(self):
		""" delete all files in the root path """ 
		if (self.__check_terminated()):
			return;	
		delete_dir(self.root)
		time.sleep(0.3)		

	def __make_chunk_pattern(self, chunk_sectors:int):
		""" [private method] this is for create the chunk data """
		curr_pat = next(self.pat_it, None)
			
		if (curr_pat is None):
			self.__reset_pat()
			curr_pat = next(self.pat_it, None)
					
		return bytearray(curr_pat[0:chunk_sectors * 512])		

	def write_all(self):
		""" write both static and dynamic files """
		self.__write_files('all')

	def write_dynamic(self):
		""" write only dynamic files """
		self.__write_files('dynamic')

	def __write_files(self, kind:str):
		""" [private method] the real write function """
		self.reset()
		self.written_sectors = 0
		self.write_elapsed = 0.0		
		
		while not self.filematrix.done():		
			if (self.__check_terminated()):
				return;

			if (kind == 'all'):
				fp = self.filematrix.next()
			elif (kind == 'dynamic'):
				fp = self.filematrix.next_dynamic()				

			logging.info('write path:', fp.path, ', size: ', fp.size, ', seed: ', fp.rand_seed)

			if not os.path.exists(fp.folder):
				try:
					os.mkdir(fp.folder)							
				except:
					raise(FileNotFoundError("create directory fail"))
			elif not os.access(fp.folder, os.F_OK):

				os.mkdir(fp.folder)	
				
			time.sleep(0.001)				
				
			try:							
				with iolib.fopen(fp.path, 'wb') as f:
					pass				
			except (PermissionError) as err:			
				raise(err)
											 
			with iolib.fopen(fp.path, 'ab') as f:
				remain = fp.size
				file_time = 0.0
				start = 0.0
				elapsed = 0.0
				
				while (remain != 0):
					if (self.__check_terminated()):
						return;

					chunk_sectors = min(remain, self.max_buff_size)									
					buff = self.__make_chunk_pattern(chunk_sectors)					
					written, elapsed = iolib.write(buff, 512, chunk_sectors, f)
					file_time += elapsed
																						   
					self.written_sectors += int(written)
					remain = remain - chunk_sectors
				
				self.write_elapsed += file_time
		
				time.sleep(0.001)

	def read_all(self, max_sectors:int=0):
		""" read and compare both static and dynamic files """						 
		self.__read_files('all')

	def read_dynamic(self, max_sectors:int=0):
		""" read and compare only dynamic files """						 
		self.__read_files('dynamic')

	def __read_files(self, kind:str):
		""" [private method] the real read function """
		self.reset()
		self.readed_sectors = 0
		self.read_elapsed = 0.0	

		while not self.filematrix.done():		
			if (self.__check_terminated()):
				return;			
				
			if (kind == 'all'):
				fp = self.filematrix.next()
			elif (kind == 'dynamic'):
				fp = self.filematrix.next_dynamic()

			logging.info('read path:', fp.path, ', size: ', fp.size, ', seed: ', fp.rand_seed)
			
			if not os.path.exists(fp.folder):
				raise FileExistsError()

			file_time = 0.0
			start = time.time()
			
			with iolib.fopen(fp.path, 'rd') as f:
				remain = fp.size
				file_time = 0.0
				start = 0.0
				elapsed = 0.0
				
				while (remain != 0):
					if (self.__check_terminated()):
						return;

					chunk_sectors = min(remain, self.max_buff_size)									
					expected = self.__make_chunk_pattern(chunk_sectors)					

					real, bytesRead, elapsed = iolib.read(512 * chunk_sectors, f)
					file_time += elapsed
							
					if (real != expected):
						raise(Exception("compare error at the file:" + fp.path))					
																				   
					self.readed_sectors += int(bytesRead / 512)
					remain = remain - chunk_sectors
				
				self.read_elapsed += file_time
		
				time.sleep(0.001)					

	def delete_dynamic(self):
		if (self.__check_terminated()):
			return;	
		self.reset()

		for fs in self.filematrix.filesets:
			if (self.__check_terminated()):
				return;	
			if (fs.active is Active.dynamic):
				delete_dir(fs.path)
				os.rmdir(fs.path)
						
	def get_last_write_perf(self):
		if (self.write_elapsed == 0):
			return 0
		return (float(self.written_sectors / 2048) / self.write_elapsed)
				
	def get_last_read_perf(self):
		if (self.read_elapsed == 0):
			return 0
		return (float(self.readed_sectors / 2048) / self.read_elapsed)					
					
			


