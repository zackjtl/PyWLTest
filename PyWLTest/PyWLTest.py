from fileset import *
from filematrix import *

import sys

org_stdout = sys.stdout

log = open(r'pythonlog.txt', 'w')
sys.stdout = log
sys.modules['fileset'].init(0x12345677)

capacity = 67108864
fs1 = fileset('k:\\', capacity * 0.0005, 4, 1024, Active.static)
fs1.reset()

fs2 = fileset('k:\\', capacity * 0.0005, 4, 1024, Active.dynamic)
fs2.reset()

fs3 = fileset('k:\\', capacity * 0.0005, 4, 1024, Active.dynamic)
fs3.reset()

"""
while(fs1.done() == False):
    fp = fs1.next()
    print('path:', fp.path, ', size: ', fp.size, ', seed: ', fp.rand_seed)

while(fs2.done() == False):
    fp = fs2.next()
    print('path:', fp.path, ', size: ', fp.size, ', seed: ', fp.rand_seed)

while(fs3.done() == False):
    fp = fs3.next()
    print('path:', fp.path, ', size: ', fp.size, ', seed: ', fp.rand_seed)
"""

fmt = filematrix((fs1, fs2, fs3), Relationship.crossed)

while not fmt.done():
    fp = fmt.next()
    #print('path: ', fp.path)
    print('path:', fp.path, ', size: ', fp.size, ', seed: ', fp.rand_seed)

print('\n=========== Dynamic ==========\n')

fmt.reset()

while not fmt.done():
    fp = fmt.next_dynamic()
    #print('path: ', fp.path)
    print('path:', fp.path, ', size: ', fp.size, ', seed: ', fp.rand_seed)




"""
fs1 = fileset('k:\\', capacity * 0.6, 4, 1024, Active.dynamic, 0x12345678)
fs2 = fileset('k:\\', capacity * 0.4, 4, 1024, Active.dynamic,0x12345678)

print(fs1.prefix);
print(fs1.path); 
print(fs2.prefix);
print(fs2.path);

ftx1 = filematrix((fs1, fs2), Relationship.sequential, 0x12345678)
"""

sys.stdout = org_stdout