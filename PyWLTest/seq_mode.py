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
	#��l�Ʀ�{���q�T�s���A�Y��J��False�h���ϥΡA�Y�{�������PAP���q
	if (ipc == False):
		pass
	else:
		if (ipc == None):
			#����w��None�ɡA��ܦb���B�إ߷s��IPC
			ipc = IPC()			
			ipc.create_server_socket()
			ipc.start_terminate_check()
	return ipc


def execute(drive:str, minFile, maxFile, testPercent, loops:int, root_seed:int=None, ipc=None):
	""" 
	drive:	the target device to test
	minFile (unit:MB): minimum file size (for both fixed and partial)
	maxFile (unit:MB): maximum file size (for both fixed and partial)
	fixedPercent (unit: %): how many percentage of whole disk size for fixed data to write
	partialSize (unit: MB): partial test data size
	"""
	ipc = init_ipc(ipc)

	#root_seed���ͫ᭱��seed�F���w�@�ӱ`�ƥi�ϨC�����զ欰�@�P�F�Y�����w�h�ۤ�
	if (root_seed != None):
		random.seed(root_seed)

	#����3��seed�ѫ���ϥ�
	seeds = [random.randint(0, 0xffffffff) for i in range(4)]

	path = drive + ':\\'
	
	#���o�`�e�q
	capacity = int(diskutil.get_disk_size(path)['total'] / 512)

	#��l�ưѼ�
	minSectors = minFile * 2048
	maxSectors = maxFile * 2048	
	testSectors = (testPercent * capacity) / 100
	
	#����static�����ɮ׶��F���B��seed�v�T�ɮײ��ͪ��ɦW�P�j�p
	fs1 = fileset(path, testSectors, minSectors, maxSectors, 'static', seeds[0])

	#��J1��fileset���@�Ӵ��կx�}�A�ë��w�椬���Y��ordered (�`��)
	#���M�Ĥ@�ӰѼƥu��J�@���A�������[�W�r���A��ܬ��@��tuple
	matrix = filematrix((fs1, ), Relationship.ordered)

	#�W�z�Ҭ����զ欰���y�z�A���B�h�n�}�l��ڰ������
	tester = fio_test(path, matrix, seeds[2], ipc)
	
	prog = progress(0, 100)

	tester.delete_all()

	for i in range(loops):
		tester.write_all(sub_progress(prog, 0, 50))
		tester.read_all(sub_progress(prog, 50, 50))
		tester.delete_all()

		print('write performance: {} MB/s'.format(tester.get_last_write_perf()))
		print('read performance: {} MB/s'.format(tester.get_last_read_perf()))

		if (ipc.terminated):
			break