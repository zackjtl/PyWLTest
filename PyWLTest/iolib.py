import os
from contextlib import contextmanager
from ctypes import *
import time
import osinfo


__iolib=WinDLL(osinfo.libdir + '\\io.dll')

__file = None
__flag = None

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