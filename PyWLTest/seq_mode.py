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
from errorcode import *

def execute(devName:str, minFile, maxFile, testPercent, loops:int, root_seed:int=None, ipc=None):
	""" 
	drive:	the target device to test
	minFile (unit:MB): minimum file size (for both fixed and partial)
	maxFile (unit:MB): maximum file size (for both fixed and partial)
	testPercent (unit: %): how many percentage of whole disk size for fixed data to write
	loops : how many cycle to test
	ipc: the communication object
	"""
	if (ipc==None):
		ipc=IPC() #create an empty IPC which do nothing
		
	root_path = devName + ':\\'	

	capacity = int(diskutil.get_disk_size(root_path)['total'] / 512)

	minSectors = minFile * 2048
	maxSectors = maxFile * 2048	
	testSectors = (testPercent * capacity) / 100
	
	prog = progress(0, 100)

	total_prog = 0.0
	total_weight = 100.0/loops

	if (root_seed != None):		
		cycle_seed = root_seed

	for i in range(loops):
		random.seed(cycle_seed)
		seeds = [random.randint(0, 0xffffffff) for i in range(2)]

		fs1 = fileset(root_path, testSectors, minSectors, maxSectors, 'static', seeds[0])
		matrix = filematrix((fs1, ), Relationship.ordered)

		with fio_test(devName, matrix, seeds[1], ipc) as tester:				
			try:							
				tester.delete_all()
				tester.write_all(sub_progress(prog, 0, 50))		
				tester.read_all(sub_progress(prog, 50, 50))				

				print('write performance: {} MB/s'.format(tester.get_last_write_perf()))
				print('read performance: {} MB/s'.format(tester.get_last_read_perf()))			

				total_prog += total_weight					
				ipc.send_total_progress(total_prog)			
				ipc.send_sub_progress(100)	

				tester.read_smart()

				cycle_seed = random.randint(0, 0xffffffff)

				if (ipc.terminated):
					break
			except BaseException as exp:
				msg = exp.args[0]
				exp.args = (msg + ', Cycle seed = 0x{:08X}'.format(tester.seed), )
				raise exp

	ipc.send_status('Done')	
	ipc.send_total_progress(100)
			
