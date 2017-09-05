import random
import logging
import os
import pattern
import time
import iolib

import win32pipe, win32file
import win32file

import socket
import IPC

from filematrix import *
from fileset import *
from diskutil import *
from ctypes import *
from contextlib import contextmanager
from errorcode import *
from progress import *

def debug_info_en():
	logging.basicConfig(level=logging.INFO)

class fio_test(object):
	"""test by file read write to a disk"""
	def __init__(self, root: str, matrix: filematrix, random_seed: int, IPC:IPC=None):
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
		self.IPC = IPC
		self.reset()

	def reset(self, lock_static:bool=None):		
		self.__reset_pat()
		self.filematrix.reset(lock_static)

	def __exit__(self):
		self.sock.close()

	def __output_status(self, msg:str):
		logging.info(msg)
		self.__ipc_send_status(msg)

	def __check_terminated(self):
		if (self.IPC != None):
			self.terminated = self.IPC.terminated
			return self.terminated
		else:
			return False
	
	def __ipc_send_status(self, input):
		if ((self.IPC != None) and (self.IPC.connected)):
			self.IPC.send_status(input)

	def __ipc_send_progress(self, prog:progress, position):
		if ((self.IPC != None) and (self.IPC.connected) and (prog != None)):
			prog.set_position(position)
			self.IPC.send_sub_progress(prog)

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

	def __next_chunk_pattern(self, chunk_sectors:int):
		""" [private method] this is for create the chunk data """
		curr_pat = next(self.pat_it, None)			

		if (curr_pat is None):
			self.__reset_pat()
			curr_pat = next(self.pat_it, None)
					
		return bytearray(curr_pat[0:chunk_sectors * 512])		

	def __random_chunk_pattern(self, chunk_sectors:int, rand_seed:int):
		idx = rand_seed % len(self.pat_array)
		return bytearray(self.pat_array[idx][0:chunk_sectors * 512])

	def __write_files(self, kind:str, prog:progress=None):
		""" [private method] the real write function """
		self.written_sectors = 0
		self.write_elapsed = 0.0		
		
		self.filematrix.reset(kind == 'dynamic')
	
		self.__ipc_send_progress(prog, 0)

		while not self.filematrix.done():		
			if (self.__check_terminated()):
				return;

			fp = self.filematrix.next()

			if (kind == 'all'):
				if (self.filematrix.current.mode == fsmode.dynamic):
					self.__ipc_send_status("Write all files - DYNAMIC")	
				else:
					self.__ipc_send_status("Write all files - STATIC")							

			logging.info('write path:' + fp.path + ', size: ' + str(fp.size) + ', seed: ' + str(fp.rand_seed))

			if not os.path.exists(fp.folder):
				try:
					os.mkdir(fp.folder)							
				except:
					 raise_error(FileNotFoundError, myerror.dir_error, "create directory fail")
			elif not os.access(fp.folder, os.F_OK):

				os.mkdir(fp.folder)	
				
			time.sleep(0.001)				
				
			try:							
				with iolib.fopen(fp.path, 'wb') as f:
					pass				
			except (PermissionError) as err:			
				raise_error(PermissionError, myerror.dir_error, str(err))
											 
			with iolib.fopen(fp.path, 'ab') as f:
				remain = fp.size
				file_time = 0.0
				start = 0.0
				elapsed = 0.0
				
				while (remain != 0):
					if (self.__check_terminated()):
						return;

					chunk_sectors = min(remain, self.max_buff_size)									
					buff = self.__random_chunk_pattern(chunk_sectors, fp.rand_seed)					
					#buff = self.__next_chunk_pattern(chunk_sectors)	
					written, elapsed = iolib.write(buff, 512, chunk_sectors, f)
					file_time += elapsed
																						   
					self.written_sectors += int(written)
					remain = remain - chunk_sectors
				
				self.write_elapsed += file_time
		
				time.sleep(0.001)
			
			self.__ipc_send_progress(prog, self.filematrix.get_progress())
			
	def __read_files(self, kind:str, prog:progress=None):
		""" [private method] the real read function """
		self.readed_sectors = 0
		self.read_elapsed = 0.0	
		
		self.__ipc_send_progress(prog, 0)

		self.filematrix.reset(kind=='dynamic')

		while not self.filematrix.done():		
			if (self.__check_terminated()):
				return;			
						
			fp = self.filematrix.next()	

			logging.info('read path:' + fp.path + ', size: ' + str(fp.size) + ', seed: ' + str(fp.rand_seed))
			
			if not os.path.exists(fp.folder):
				raise_error(FileExistsError, myerror.dir_error)

			file_time = 0.0
			start = time.time()			
			
			with iolib.fopen(fp.path, 'rd') as f:
				remain = fp.size
				file_time = 0.0
				start = 0.0
				elapsed = 0.0				
				
				while (remain != 0):
					chunk_sectors = min(remain, self.max_buff_size)									
					expected = self.__random_chunk_pattern(chunk_sectors, fp.rand_seed)					
					#expected = self.__next_chunk_pattern(chunk_sectors)	

					if (self.__check_terminated()):
						return;

					real, bytesRead, elapsed = iolib.read(512 * chunk_sectors, f)
					file_time += elapsed
							
					if (real != expected):
						if (self.__check_terminated()):
							return;
						raise_exception(BaseException, myerror.pattern_error, "compare error at the file:" + fp.path)
																				   
					self.readed_sectors += int(bytesRead / 512)
					remain = remain - chunk_sectors
				
				self.read_elapsed += file_time		
				time.sleep(0.001)		

			self.__ipc_send_progress(prog, self.filematrix.get_progress())


	def write_all(self, prog:progress=None):
		""" write both static and dynamic files """
		self.__output_status("Write all files")
		self.__write_files('all', prog)

	def write_dynamic(self, prog:progress=None):
		""" write only dynamic files """
		self.__output_status("Write DYNAMIC files")
		self.__write_files('dynamic', prog)

	def read_all(self, prog:progress=None):
		""" read and compare both static and dynamic files """			
		self.__output_status("Read & compare all files")
		self.__read_files('all', prog)

	def read_dynamic(self, prog:progress=None):
		""" read and compare only DYNAMIC files """			
		self.__output_status("Read & compare DYNAMIC files")
		self.__read_files('dynamic', prog)		
						
	def delete_all(self, prog:progress=None):
		""" delete all files in the root path """ 
		self.__output_status('Delete all files')
		if (self.__check_terminated()):
			return;	
		delete_dir(self.root)
		time.sleep(0.3)		

	def delete_dynamic(self, prog:progress=None):
		self.__output_status('Delete DYNAMIC files')
		if (self.__check_terminated()):
			return;	
		self.reset()

		for fs in self.filematrix.filesets:
			if (self.__check_terminated()):
				return;	
			if (fs.mode is fsmode.dynamic):
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
					
			


