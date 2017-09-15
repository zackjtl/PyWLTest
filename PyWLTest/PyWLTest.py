import sys
import os
import random
import traceback
import IPC
import fiotest

import partial_mode

#開啟fiotest模組的debug info
##fiotest.debug_info_en()

ipc = IPC.IPC()

def create_communication(ipc:IPC.IPC):
	if (ipc == False):
		return
	ipc.create_server_socket()
	ipc.start_terminate_check()

def dotest():
	global ipc

	try:
		create_communication(ipc)
		partial_mode.execute('K', 0.5, 2, 10, 50, 3000, 0x12345678, ipc)

	except BaseException as err:
		print("------------- error message ------------")
		print(str(err))
		print("------------- trace back info ----------")
		traceback.print_exc(file = sys.stdout)
		print("----------------------------------------")
		raise(err)
	finally:
		pass

if __name__ == '__main__':
	dotest()
else:
	pass