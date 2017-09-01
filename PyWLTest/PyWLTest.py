import sys
import fiotest
import diskutil
import os

from fileset import *
from filematrix import *
from ctypes import *

def dotest():
	print("start test..\n")

	#org_stdout = sys.stdout

	#log = open(r'pythonlog.txt', 'w')
	#sys.stdout = log
	sys.modules['fileset'].init(0x12345677)

	capacity = int(diskutil.get_disk_size('K:\\')['total'] / 512)
	fs1 = fileset('k:\\', capacity * 0.02, 1024, 4096, Active.static)
	fs1.reset()

	fs2 = fileset('k:\\', capacity * 0.02, 1024, 4096, Active.dynamic)
	fs2.reset()

	fmt = filematrix((fs1, fs2), Relationship.ordered)

	fiotest.debug_info_en()

	fio = fiotest.fio_test('K:\\', fmt, 0x12345678)
	print('delete all')
	fio.delete_all()
	print('write all')
	fio.write_all()
	print('read & compare all')
	fio.read_all()
	"""
	print('delete dynamic sets')
	fio.delete_dynamic()
	for i in range(100):
		print('-------- loop', i, ' --------')
		print('write dynamic')
		fio.write_dynamic()
		print('read & compare dynamic')
		fio.read_dynamic()

		print('delete dynamic sets')
		fio.delete_dynamic()		
	"""
	#sys.stdout = org_stdout

	print('average write performance: ', fio.get_last_write_perf(), ' MB/s')
	print('average read performance: ', fio.get_last_read_perf(), ' MB/s')

if __name__ == '__main__':
	dotest()
else:
	pass