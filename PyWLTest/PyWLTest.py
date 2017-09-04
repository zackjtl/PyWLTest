import sys
import fiotest
import diskutil
import os
import random

from fileset import *
from filematrix import *
from ctypes import *
from IPC import *

ipc = IPC()

def create_communication(ipc:IPC):
	ipc.create_server_socket()
	ipc.start_check_thread()

def dotest():
	print("start test..\n")

	global ipc

	#產生跨行程溝通之連接；若程式不須與AP溝通則可註解這行
	create_communication(ipc)

	#若希望每次測試行為不同，請將下一行註解
	random.seed(0x1234567)		
	###
	root_seed = random.randint(0, 0xffffffff)	

	#初始化fileset模組seed，該模組seed會影響隨機產生之檔名和檔案大小
	sys.modules['fileset'].init(root_seed)

	#產生static fileset
	#此fileset未被指定seed，因此會以模組seed為基準來產生檔名和檔案大小
	capacity = int(diskutil.get_disk_size('K:\\')['total'] / 512)
	fs1 = fileset('k:\\', capacity * 0.02, 1024, 4096, Active.static)
	fs1.reset()

	#產生dynamic fileset
	#此fileset被指定固定的seed，因此產生之檔名和檔案大小與模組seed無關，而是每次測試都一樣
	fs2 = fileset('k:\\', capacity * 0.02, 1024, 4096, Active.dynamic, seed=0x20180121)
	fs2.reset()

	#filematrix的random seed只影響檔案內容pattern
	matrix = filematrix((fs1, fs2), Relationship.ordered, seed=root_seed)

	#開啟fileset的debug info
	fiotest.debug_info_en()

	#filematrix與fileset為測試行為的描述，而fio_test則為實際測試的執行者
	fio = fiotest.fio_test('K:\\', matrix, 0x12345678, IPC = ipc)
	print('delete all')
	fio.delete_all()
	print('write all')
	fio.write_all()
	print('read & compare all')
	fio.read_all()
	
	print('delete dynamic sets')
	fio.delete_dynamic()
	for i in range(100):	
		if (fio.terminated):
			print('terminated')
			break

		print('-------- loop', i, ' --------')
		print('write dynamic')
		fio.write_dynamic()
		print('read & compare dynamic')
		fio.read_dynamic()

		print('delete dynamic sets')
		fio.delete_dynamic()		
	
	#呼叫get_last_write_perf()與get_last_read_perf()可得到最近一次的performance量測值
	print('average write performance: ', fio.get_last_write_perf(), ' MB/s')
	print('average read performance: ', fio.get_last_read_perf(), ' MB/s')

if __name__ == '__main__':
	dotest()
else:
	pass