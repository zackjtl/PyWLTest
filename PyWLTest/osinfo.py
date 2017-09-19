import platform
import os

def is_64Bit():
	ms = platform.machine()
	return platform.machine().endswith('64')

def is_32Bit():
	if (platform.machine().endswith('32') or platform.machine().endswith('x86')):
		return True
	return False
		

def is_windows():
	return os.name.startswith('nt')

def is_linux():
	return os.name.startswith('posix')

__thisdir = os.path.dirname(__file__)

libdir = ''

if (is_windows()):
	if (is_64Bit()):
		libdir = __thisdir + '\\lib\\Win64'
	elif (is_32Bit()):
		libdir = __thisdir + '\\lib\\Win32'
	else:
		raise(FileExistsError('unknown platform'))
elif (is_linux()):
	if (is_64Bit()):
		libdir = __thisdir + '\\lib\\Posix64'
	elif (is_64Bit()):
		libdir = __thisdir + '\\lib\\Posix64'
	else:
		raise(FileExistsError('unknown platform'))
else:
	raise(FileExistsError('unknown os'))

