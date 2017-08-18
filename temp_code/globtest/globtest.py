import random
counter = 1
 
name_gen_seed = 0x12345678
name_gen = random.Random(name_gen_seed)

def seed(rand_seed):
	global name_gen, name_gen_seed
	name_gen_seed = rand_seed
	name_gen.seed(name_gen_seed)
	

name_mask = []
name_array = []
prefix_mask = []
prefix_array = []

def reset():
	global name_mask, prefix_mask, name_array, prefix_array, name_gen_seed
	seed(name_gen_seed)
	name_mask = [0] * 10
	name_array = name_gen.sample(range(10000, 20000), 10)
	prefix_mask = [0] * 26
	prefix_array = [chr(x) for x in name_gen.sample(range(97, 123), 26)]

reset()

class c1:
	value = 0
	global name_mask, prefix_mask, name_array, prefix_array	
	prefix = ''
	
	
	def __init__(self):
		global counter
		print('counter = ' + str(counter))		
		value = counter
		counter = counter + 1
		print('counter# = ' + str(counter))	
		
		for idx, mask in enumerate(name_mask):
			#global name_mask, name_array
			if (mask == 0):
				self.name = str(name_array[idx])
				name_mask[idx] = 1
				print(idx, name_mask)
				break
				
		for idx, mask in enumerate(prefix_mask):
			#global prefix_mask, prefix_array
			if (mask == 0):
				self.prefix = prefix_array[idx]
				prefix_mask[idx] = 1
				print(idx, prefix_mask)
				break		