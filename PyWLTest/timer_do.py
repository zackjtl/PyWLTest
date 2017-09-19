import threading
import time

class mytimer:
	def __init__(self):
		self.thread = None
		self.func = None
		self.prev_time = 0
		self.interval = 0
		self.to_stop = False

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		if (self.thread != None):
			self.to_stop = True			

	def start(self, interval:float, func):
		self.func = func
		self.interval = interval
		self.thread = threading.Thread(target=self.caller, name = 'timer_caller')
		self.thread.daemon = True	
		self.to_stop = False
		self.thread.start()

	def caller(self):
		while (True):
			time.sleep(self.interval)
			self.func()
			if (self.to_stop):
				break
		
	def stop(self):
		if (self.thread != None):
			self.to_stop = True
