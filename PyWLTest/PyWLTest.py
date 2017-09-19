import sys
import traceback

import partial_mode
import seq_mode

from IPC import *
#開啟fiotest模組的debug info
##fiotest.debug_info_en()

ipc = IPC()

def create_communication(ipc:IPC):
	ipc.create_server_socket()
	ipc.start_terminate_check()

def dotest():
	global ipc

	try:
		create_communication(ipc)
		#partial_mode.execute('D', 0.5, 2, 10, 50, 3000, 0x12345678, ipc)
		seq_mode.execute('K', 0.5, 5, 1.0, 3, 0x12345678, ipc)

	except BaseException as err:
		print("------------- error message ------------")
		print(str(err))
		print("------------- trace back info ----------")
		traceback.print_exc(file = sys.stdout)
		print("----------------------------------------")
		#raise(err)
		ipc.send_error_str(str(err))

	finally:
		ipc.sock.close()
		
if __name__ == '__main__':
	dotest()
else:
	pass