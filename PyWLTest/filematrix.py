import enum

from fileset import *
from errorcode import *

class Relationship(enum.Enum):
	ordered = 1
	crossed = 2
	random = 3

class filematrix(object):  
	"""a filematrix included one or more fileset that and descript the relative order between each fileset """	

	def __init__(self, filesets, relationship = Relationship.ordered, seed = 0x12345678):
		if type(filesets) != tuple:
			raise_error(TypeError, myerror.argument_error, "the second input argument filesets must be a tuple like (fs, ) or (fs1, fs2)")
					
		for item in filesets:
			if type(item) != fileset:
				raise_error(TypeError, myerror.argument_error, "the elements in the filesets tuple must be a fileset")

		self.filesets = filesets
		self.relationship = relationship
		self.seed = seed	 		
		self.total_sectors = 0
		self.total_files = 0
		self.total_dynamic_files = 0
		self.total_fs = 0
		self.total_dynamic_fs = 0		
		
		for fs in self.filesets:
			self.total_sectors += fs.total_sectors
			self.total_files += fs.total_files

			if (fs.mode is fsmode.dynamic):
				self.total_dynamic_fs += 1
				self.total_dynamic_files += fs.total_files
							 
		self.reset()		
	
	def reset(self, lock_static:bool=None): 		
		self.stack = []
		self.rand = random.Random(self.seed)   
		for i,fs in enumerate(self.filesets):
			fs.reset()
		self.reset_iter()
		self.done_counter = 0
		self.lock_static = lock_static

		#default is not set
		if (lock_static == None):
			self.lock_static = False

	def reset_iter(self):
		self.iter = iter(self.filesets)		
		self.current = None
		self.file_progress = 0
		#self.current = next(self.iter, None)

	def next_valid(self, round = False):
		if (self.done()):
			self.current = None
		else:		   
			self.current = next(self.iter, None)
			
			if (self.current is None):
				if (round):
					self.reset_iter()
					self.current = next(self.iter, None)
				else:
					self.current = None
					return

			while (self.current.done()):
				self.current = next(self.iter, None)
				if (self.current is None):
					if (round):
						self.reset_iter()		   
						self.current = next(self.iter, None) 
					else:
						self.current = None
						break

	def random_sel_fs(self, order):
		idx = 0
		for x in self.filesets:
			if not x.done():			   
				if idx == order:
					self.current = x
					return
				idx += 1
		# Must not come here
		assert(False)

	def select_fs(self):
		if self.relationship is Relationship.ordered:
			if self.current is None:
				self.next_valid(False)

			while (self.current.done()):			
				self.next_valid(False)
				
				if (self.current is None):
					raise_error(StopIteration, myerror.filematrix_error)

		elif self.relationship is Relationship.crossed:  
			self.next_valid(True)
			
			if (self.current is None):
				raise_error(StopIteration, myerror.filematrix_error)
		
		elif self.relationship is Relationship.random:  
			if (self.done()):
				raise_error(StopIteration, myerror.filematrix_error)
			else:				
				order = self.rand.randint(0, self.valid_cnt()-1)								
				self.random_sel_fs(order)					

	def next(self):	
		self.select_fs()		

		if (self.lock_static):
			if (self.current.mode is not fsmode.dynamic):
				self.current.next()

			while self.current.mode is not fsmode.dynamic:
				self.current.next()
				self.select_fs()
		
		self.file_progress += 1
		return self.current.next()

	def valid_cnt(self):
		counter = 0
		for fs in self.filesets:
			if not fs.done():
				counter += 1
		
		return counter

	def get_progress(self):
		if (self.lock_static):
			return (self.total_dynamic_files * self.file_progress) / 100.0

		return (self.total_files * self.file_progress) / 100.0

	def done(self):
		for fs in self.filesets:
			if not fs.done():
				return False
		
		return True						
			



