#-*-coding:utf-8-*-

from simpleenum import make_enum
import enum

class myerror(enum.Enum):
	dir_error = 1
	file_error = 2
	pattern_error = 3
	fileset_error = 4
	filematrix_error = 5
	argument_error = 6
	diskutil_error = 7
	coding_error = 0xce

def make_error(base:BaseException, code, msg:str='', digits:int=4):
	class ErrorCode(base):
		"""description of class"""
		def __init__(self, code:int, msg:str, digits:int):
			super(ErrorCode, self).__init__(msg)
			self.code = code
			self.msg = '[{:0{}x}] '.format(code, digits) +  msg	

	if (issubclass(type(code), enum.Enum)):
		error = ErrorCode(code.value, msg, digits)						
	elif (type(code) == int):
		error = ErrorCode(code, msg, digits)
	
	return error
			
def raise_error(base:BaseException, code, msg:str='', digits:int=4):
	raise(make_error(base, code, msg, digits))