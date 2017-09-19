import sys
import traceback
import IPC

import partial_mode
import seq_mode

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
		#partial_mode.execute('D', 0.5, 2, 10, 50, 3000, 0x12345678, ipc)
		seq_mode.execute('D', 8, 8, 1, 3000, 0x12345678, ipc)

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