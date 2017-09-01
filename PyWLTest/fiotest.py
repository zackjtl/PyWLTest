import random
import logging
import os
import pattern
import time
import win32file

from filematrix import *
from fileset import *
from diskutil import *
from ctypes import *

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
				
		self.__prepair_patterns()
		self.reset()

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
				with open(fp.path, 'wb', 0) as f:
					pass				
			except (PermissionError) as err:			
				raise(err)
											 
			with open(fp.path, 'ab', 0) as f:
				remain = fp.size
				file_time = 0.0
				start = 0.0
				elapsed = 0.0
				
				while (remain != 0):
					chunk_sectors = min(remain, self.max_buff_size)									
					buff = self.__make_chunk_pattern(chunk_sectors)

					start = time.time()					
					written = f.write(buff)
					f.flush()
					os.fsync(f)
					elapsed = time.time() - start
					file_time += elapsed
																						   
					self.written_sectors += int(written / 512)
					remain = remain - chunk_sectors
				
				self.write_elapsed += file_time
		
				f.close()
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
			if (kind == 'all'):
				fp = self.filematrix.next()
			elif (kind == 'dynamic'):
				fp = self.filematrix.next_dynamic()

			logging.info('read path:', fp.path, ', size: ', fp.size, ', seed: ', fp.rand_seed)
			
			if not os.path.exists(fp.folder):
				raise FileExistsError()

			file_time = 0.0
			start = time.time()
									
			try:
				handle = win32file.CreateFile(fp.path, win32file.GENERIC_READ, win32file.FILE_SHARE_READ, None, win32file.OPEN_EXISTING, win32file.FILE_ATTRIBUTE_NORMAL | win32file.FILE_FLAG_NO_BUFFERING, None)
				remain = fp.size	

				while (remain != 0):
					chunk_sectors = min(remain, self.max_buff_size)						
					pat = self.__make_chunk_pattern(chunk_sectors)
					read_len = chunk_sectors * 512	
					start = time.time()		
					result, data = win32file.ReadFile(handle, read_len, None)
					elapsed = time.time() - start
					file_time += elapsed
					if (data != pat):
						raise(Exception("compare error at the file:" + fp.path))

					remain = remain - chunk_sectors
					self.readed_sectors += int(len(data) / 512)

			except (Exception) as err:
				win32file.CloseHandle(handle)
				raise(err)
			except (IOError):
				win32file.CloseHandle(handle)
				raise(BaseException("read file error"))
			else:
				win32file.CloseHandle(handle)
			
			self.read_elapsed += file_time		 
			time.sleep(0.001)

	def delete_dynamic(self):
		self.reset()

		for fs in self.filematrix.filesets:
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
					
			


