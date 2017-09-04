class progress:
	def __init__(self, start:int, weight:float):
		self.start = start
		self.weight = weight
		self.current = 0

	def compute_position(self, partial: int):
		return self.start + ((partial * self.weight) / 100.0)

	def set_position(self, pos: int):
		self.current = pos

	def get_position(self):
		return self.parent.current

class sub_progress(progress):
	def __init__(self, parent:progress, start:int, weight:float):
		self.start = start
		self.weight = weight
		self.parent = parent

	def set_position(self, pos: float):
		self.parent.set_position(self.compute_position(pos))