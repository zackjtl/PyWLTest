# -*- coding: utf-8 -*-
import time
import progress
import enum
import ctypes
import sys
import random
import diskutil

from IPC import *
from fileset import *
from filematrix import *
from fiotest import *
from progress import *

def init_ipc(ipc):
	#初始化行程間通訊連接，若輸入為False則不使用，即程式不須與AP溝通
	if (ipc == False):
		pass
	else:
		if (ipc == None):
			#當指定為None時，表示在此處建立新的IPC
			ipc = IPC()			
			ipc.create_server_socket()
			ipc.start_terminate_check()
	return ipc


def execute(drive:str, minFile, maxFile, fixedPercent, partialSize, loops:int, root_seed:int=None, ipc=None):
	""" 
	drive:	the target device to test
	minFile (unit:MB): minimum file size (for both fixed and partial)
	maxFile (unit:MB): maximum file size (for both fixed and partial)
	fixedPercent (unit: %): how many percentage of whole disk size for fixed data to write
	partialSize (unit: MB): partial test data size
	"""
	ipc = init_ipc(ipc)

	#root_seed產生後面的seed；指定一個常數可使每次測試行為一致；若不指定則相反
	if (root_seed != None):
		random.seed(root_seed)

	#產生3個seed供後續使用
	seeds = [random.randint(0, 0xffffffff) for i in range(4)]

	path = drive + ':\\'
	
	#取得總容量
	capacity = int(diskutil.get_disk_size(path)['total'] / 512)

	#初始化參數
	minSectors = minFile * 2048
	maxSectors = maxFile * 2048	
	fixedSectors = (fixedPercent * capacity) / 100
	partialSectors = partialSize * 2048

	#產生static測試檔案集；此處的seed影響檔案產生的檔名與大小
	fs1 = fileset(path, fixedSectors, minSectors, maxSectors, 'static', seeds[0])

	#產生dynamic測試檔案集
	fs2 = fileset(path, partialSectors, minSectors, maxSectors, 'dynamic', seeds[1])

	#組合2個fileset為一個測試矩陣，並指定交互關係為ordered (循序)
	matrix = filematrix((fs1, fs2), Relationship.ordered)

	#上述皆為測試行為的描述，此處則要開始實際執行測試
	tester = fio_test(path, matrix, seeds[2], ipc)
	
	prog = progress(0, 100)

	tester.delete_all()
	tester.write_all(sub_progress(prog, 0, 50))
	tester.read_all(sub_progress(prog, 50, 50))
	tester.delete_dynamic()

	for i in range(loops):
		tester.write_dynamic(sub_progress(prog, 0, 50))
		tester.read_dynamic(sub_progress(prog, 50, 50))
		tester.delete_dynamic()

		print('write performance: {} MB/s'.format(tester.get_last_write_perf()))
		print('read performance: {} MB/s'.format(tester.get_last_read_perf()))

		if (ipc.terminated):
			break