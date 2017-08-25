import random
import logging

#the module scope static variables

def init(seed):
    """initial the module scope static variables """
    global prefix_idx, path_names
    global module_seed, module_rand
    print('fileset module initialized with random seed:', seed)
    prefix_idx = 97
    path_names = 10000000
    module_seed = seed
    module_rand = random.Random(module_seed)

def debug_info_en():
	logging.basicConfig(level=logging.INFO)

init(1234)

import enum

class Active(enum.Enum):
    static =1
    dynamic = 2

class file_parameter:
    """ the parameters descript a single file to access on the target disk (read or write) """
    def __init__(self, folder, name, size, rand_seed):
        self.path = folder + '\\' + name
        self.folder = folder
        self.name = name
        self.size = int(size)
        self.rand_seed = rand_seed

class fileset(object):
    path = ''

    """fileset is the unit of a set of files to write into the testing device. 
    A fileset have its own folder and an unique filename prefix as the difference with the others. """
    def __init__(self, root, total_sectors, min_sectors=4, max_sectors=1024, active = Active.static, rand_seed=None):
        global prefix_idx, path_names
        global module_rand
        self.total_sectors = total_sectors
        self.min_sectors = min_sectors
        self.max_sectors = max_sectors               
        self.max_files_per_layer = 128   
        self.filenumber_offset = 100000        
        self.active = active
        
        if (rand_seed is None):
            self.rand_seed = module_rand.randint(0, 0xffffffff)
        else:
            self.rand_seed = rand_seed                   

        if (prefix_idx > 122):
            raise(StopIteration('out of iteration to create fileset'))

        self.prefix = chr(prefix_idx)
        
        if (self.active == Active.static):
            self.path = root + 'st' + str(path_names) + self.prefix
        else:
            self.path = root + 'dy' + str(path_names) + self.prefix
        prefix_idx = prefix_idx + 1
        path_names = path_names + 1

        self.reset()

    def reset(self):
        """ iterator go back to the head of the fileset"""
        self.current_depth = 0
        self.current_filenumber = 0
        self.current_folder = self.path
        self.current_sectors = 0
        self.rand = random.Random(self.rand_seed)
        
    def next(self):
        """ get next file path of the fileset. """
        if (self.current_filenumber >= self.max_files_per_layer):
            self.current_depth += 1
            self.current_folder += '\\' + str(self.current_depth)
            self.current_filenumber = 0
        
        """ make file parameters """
        name = self.prefix + str(self.current_filenumber + self.filenumber_offset)
        size = self.rand.randrange(self.min_sectors, self.max_sectors + 1)

        if ((self.current_sectors + size) > self.total_sectors):
            size = self.total_sectors - self.current_sectors

        self.current_sectors += size        
        self.current_filenumber += 1
        fp = file_parameter(self.current_folder, name, size, self.rand.randint(0, 0xffffffff))
        
        return fp

    def done(self):
        """ to check is the iterator the end of the fileset """
        if self.current_sectors >= self.total_sectors: 
            return True
        else:
            return False
        pass