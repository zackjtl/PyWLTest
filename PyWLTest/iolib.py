import os
from contextlib import contextmanager
from ctypes import *
import time
import osinfo
from errorcode import *

class fio_res(Structure):
	_fields_ = [
		("io_count", c_int),
		("spend_time", c_int),
		("error_code", c_int),
		("rsvd", c_int)]

__iolib=WinDLL(osinfo.libdir + '\\io.dll')

__file = None
__flag = None

__iolib.file_write_auto_pattern.restype = fio_res
__iolib.file_read_auto_pattern.restype = fio_res

@contextmanager
def fopen(fileName:str, flags:str):
	global __iolib, __file, __flag

	buff1 = create_string_buffer(fileName.encode('utf-8'))
	buff2 = create_string_buffer(flags.encode('utf-8'))
	__flag = flags

	if (('w' in flags) or ('a' in flags)):
		if ('r' in flags):
			raise(ArgumentError('file mode conflict'))
		__file = __iolib.fopen_4wr(buff1, buff2)
	elif ('r' in flags):
		if (('w' in flags) or ('a' in flags)):
			raise(ArgumentError('file mode conflict'))
		__file = __iolib.fopen_4rd(buff1, buff2)
	
	yield __file

	if ('r' in __flag):
		__iolib.fclose_4rd(__file)
	else:
		__iolib.fclose_4wr(__file)
	
def write(data:bytearray, blockSize:int, blockCount:int, file:c_voidp):
	global __iolib
	_type = c_ubyte * (blockSize * blockCount)
	buff = _type.from_buffer(data)
	
	start = time.time()
	written = __iolib.file_write(buff, blockSize, blockCount, file)
	end = time.time()
	elapsed = end - start
	return written, elapsed

def read(length:int, file:c_voidp):
	global __iolib
	_type_buff = c_ubyte * (length)
	buff = _type_buff()

	_type_ulongp = c_ulong * 1
	bytes_read_p = _type_ulongp()

	start = time.time()
	ret = __iolib.file_read(buff, length, bytes_read_p, file)
	end = time.time()
	elapsed = end - start
	return bytearray(buff), bytes_read_p[0], elapsed, 

def fclose4wr(file:c_voidp):
	return __iolib.fclose_4wr(file)

def fclose4rd(file:c_voidp):
	return __iolib.fclose_4rd(file)

def init_pattern(chunk_size:int, chunk_number:int, seed:int):
	__iolib.init_pattern(chunk_size, chunk_number, seed)

def free_buffer():
	__iolib.free_buffer()

def file_write_auto_pattern(fileName:str, sector_cnt:int, seed:int):
	fnameBuff = create_string_buffer(fileName.encode('utf-8'))

	res = __iolib.file_write_auto_pattern(fnameBuff, sector_cnt, seed)

	if (res.error_code != 0):
		if (res.error_code == 1):
			raise_error('Can not open file ' + fileName, myerror.file_error)

	return res.io_count, res.spend_time


def file_read_auto_pattern(fileName:str, sector_cnt:int, seed:int):
	fnameBuff = create_string_buffer(fileName.encode('utf-8'))

	res = __iolib.file_read_auto_pattern(fnameBuff, sector_cnt, seed)

	if (res.error_code != 0):
		if (res.error_code == 1):
			raise_error(msg='Can not open file ' + fileName, code = myerror.file_error)
		elif (res.error_code == 2):
			raise_error(msg='Can not read file ' + fileName, code = myerror.file_error)
		elif (res.error_code == 3):
			raise_error(msg='Pattern compare failed ' + fileName, code = myerror.pattern_error)

	return res.io_count, res.spend_time

def force_pat_error():
	__iolib.test_force_pattern_error()
	
