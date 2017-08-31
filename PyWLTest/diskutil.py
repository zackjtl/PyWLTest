import os
import logging
import collections
import time
 	
def debug_info_en():
	logging.basicConfig(level=logging.INFO)

def delete_dir(path):
	logging.info('delete path: ' + path)
	if os.path.isdir(path) == False:
		raise("The input path to delete is not a directory")
	
	for root, dirs, files in os.walk(path, topdown=False):
		for name in files:
			os.remove(os.path.join(root, name))
			logging.info('remove file: ' + name)
			time.sleep(0.001)

		for name in dirs:
			accessible = True			
			if ((os.name == 'Linux') and (name[0] == '.')):
				accessible = False
			elif (os.name == 'nt'):
				if (name == 'System Volume Information'):
					accessible = False
				
			if (accessible):
				os.rmdir(os.path.join(root, name))
				logging.info('remove dir: ' + name)
			time.sleep(0.001)

#_ntuple_diskusage = collections.namedtuple('usage', 'total used free')

import ctypes
import sys
	  	
def get_disk_size(path):
	if (os.name != 'nt'):
		raise NotImplementedError("Only windows version was implemented")

	logging.info("get size info on windows for disk path")
	
	_, total, free = ctypes.c_ulonglong(), ctypes.c_ulonglong(), \
					   ctypes.c_ulonglong()
	if sys.version_info >= (3,) or isinstance(path, unicode):
		fun = ctypes.windll.kernel32.GetDiskFreeSpaceExW
	else:
		fun = ctypes.windll.kernel32.GetDiskFreeSpaceExA
	ret = fun(path, ctypes.byref(_), ctypes.byref(total), ctypes.byref(free))
	if ret == 0:
		raise ctypes.WinError()
	used = total.value - free.value

	return {'total': total.value, 'used' : used, 'free': free.value}


#disk_usage.__doc__ = __doc__

#if __name__ == '__main__':
#	print disk_usage(os.getcwd())