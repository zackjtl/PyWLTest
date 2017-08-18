import sys
def unload(name):		
	exec("del sys.modules[\'__main__\']." + name)
	exec("del sys.modules['" + name + "']")