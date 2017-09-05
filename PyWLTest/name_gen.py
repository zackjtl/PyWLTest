import random

class name_set:
	rand_seed = 0x12345678	
	
	def __init__(self, length, seed=0x12345678):
		self.rand_seed = seed
		self.length = length
		self.created = list()
		self.rand = random.Random(self.rand_seed)
		self.max_count = 36**length
		self.name = ''

		if (length == 1):
			self.samples = [chr(x) for x in self.rand.sample(range(97, 123), 26)]
		else:
			lower = 10**(length-1)
			upper = 10**(length) - 1

			if ((upper - lower) >= 200000):
				upper = lower + 200000

			temp = list(range(lower, upper))
			self.rand.shuffle(temp)

			#temp = self.rand.sample(range(lower, upper), min((upper-lower), 100000))
			self.samples = [str(x) for x in temp]

		self.max_count = len(self.samples)						
		self.used_flag = [0] * self.max_count

	def Gen(self):
		for i,value in enumerate(self.samples):
			return self.samples.pop()

		raise('Exceed used for all samples')