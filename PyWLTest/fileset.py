import random

#the module scope static variables
module_seed = 0
module_rand = random.Random(0)
prefix = 97
path_names = 10000000

def init(seed):
    """initial the module scope static variables """
    global module_rand, module_seed
    global prefix, path_names
    prefix = 97
    path_names = []

import enum

class Active(enum):
    static =1
    dynamic = 2

class fileset(object):
    """fileset is the unit of a set of files to write into the testing device. 
    A fileset have its own folder and an unique filename prefix as the difference with the others. """
    def __init__(self, root, active, min_sectors=4, max_sectors=1024, rand_seed=0x12345678):
        global module_rand
        global prefix, path_names
        self.min_sectors = min_sectors
        self.min_sectors = max_sectors
        self.rand_seed = rand_seed
        self.rand = random.Random(rand_seed)

        if (prefix > 122):
            raise(StopIteration('out of iteration to create fileset'))

        self.prefix = chr(prefix)
        
        if (active == Active.static):
            self.path = root + 'static' + str(path_names) + self.prefix
        else:
            self.path = root + 'dynamic' + str(path_names) + self.prefix
        ++prefix
        ++path_names

