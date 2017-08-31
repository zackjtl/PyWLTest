def make(size, mode='random', arg=0x123456aa):
	if (mode == 'random'):
		import random
		random.seed(arg)        
		ra = [random.randrange(0, 0xff) for x in range(size)]		
	elif (mode == 'fixed'):
		pat = arg.to_bytes(8, byteorder='little')[0]
		ra = [(x % 256) for x in range(size)]
		
	res = bytearray(ra)	
	return res