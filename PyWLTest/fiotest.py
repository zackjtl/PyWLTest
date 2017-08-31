import random
import logging
import os
import pattern
import time
import win32file

from filematrix import *
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
				
		self.prepair_patterns()
		self.reset()

	def prepair_patterns(self):
		""" Create an amount of bytearray of test patterns, these is a ring to make contents of the test files.
		"""

		gen = self.randlib.Generate
		buff_type = c_ubyte * (self.max_buff_size * 512)
		self.pat_array = []
		
		for i in range(self.buffer_cnt):
			temp = buff_type()
			gen(temp, self.max_buff_size * 512, self.seed+i)   
			self.pat_array.append(temp)

	def reset_pat(self):
		""" Reset the pattern array iterator """
		self.pat_it = iter(self.pat_array)

	def reset(self):		
		self.rand = random.Random(self.seed)
		self.reset_pat()
		self.filematrix.reset()

	def delete_all(self):
		""" delete all files in the root path """ 
		delete_dir(self.root)
		time.sleep(0.3)

	def make_chunk_pattern(self, chunk_sectors:int):
		curr_pat = next(self.pat_it, None)
			
		if (curr_pat is None):
			self.reset_pat()
			curr_pat = next(self.pat_it, None)
					
		return bytearray(curr_pat[0:chunk_sectors * 512])		

	def write_all(self):
		""" write both static and dynamic files """
		self.reset()
		self.written_sectors = 0
		self.write_elapsed = 0.0					 

		while not self.filematrix.done():			
			fp = self.filematrix.next()
			logging.info('write path:', fp.path, ', size: ', fp.size, ', seed: ', fp.rand_seed)
			filenew = False

			if not os.path.exists(fp.folder):
				try:
					os.mkdir(fp.folder)							
					filenew = True
				except:
					raise(FileNotFoundError("create directory fail"))
			elif not os.access(fp.folder, os.F_OK):
				os.mkdir(fp.folder)	
				
			time.sleep(0.001)				
					
			try:							
				with open(fp.path, 'wb', 0) as f:
					pass				
			except (PermissionError) as err:			
				raise(PermissionError("{0}: {1}, file is new ? {2}".format(err, fp.path, filenew)))
											 
			with open(fp.path, 'ab', 0) as f:
				remain = fp.size
				file_time = 0.0
				start = 0.0
				elapsed = 0.0
				
				while (remain != 0):
					chunk_sectors = min(remain, self.max_buff_size)									
					buff = self.make_chunk_pattern(chunk_sectors)

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
		self.reset()
		self.readed_sectors = 0
		self.read_elapsed = 0.0					 

		while not self.filematrix.done():			
			fp = self.filematrix.next()
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
					pat = self.make_chunk_pattern(chunk_sectors)
					read_len = chunk_sectors * 512	
					start = time.time()		
					result, data = win32file.ReadFile(handle, read_len, None)
					elapsed = time.time() - start
					file_time += elapsed
					if (data != pat):
						raise(Exception("compare error at the file:" + fp.path))

					remain = remain - chunk_sectors
					self.readed_sectors += int(len(data) / 512)

			except:
				win32file.CloseHandle(handle)
				raise(BaseException("read file error"))
			else:
				win32file.CloseHandle(handle)
			
			self.read_elapsed += file_time		 
			time.sleep(0.001)


	def get_last_write_perf(self):
		if (self.write_elapsed == 0):
			return 0
		return (float(self.written_sectors / 2048) / self.write_elapsed)
				
	def get_last_read_perf(self):
		if (self.read_elapsed == 0):
			return 0
		return (float(self.readed_sectors / 2048) / self.read_elapsed)					
					
			


