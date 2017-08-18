from enum import Enum, auto

class TestStatus(Enum):
	DEL_ALL_FILES = auto()
	DEL_PARTIAL_FILES = auto()
	WRITE_DATA = auto()
	VERIFY_DATA = auto()
	VERIFY_FULL_DATA = auto()
	WRITE_FULL_STATIC_DATA = auto()
	WRITE_FULL_DYNAMIC_DATA = auto()
	WRITE_DYNAMIC_DATA = auto()
	VERIFY_DYNAMIC_DATA	= auto()


def set_test_status(status):	
	pass