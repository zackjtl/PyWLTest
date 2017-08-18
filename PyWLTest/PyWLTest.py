import name_gen as ng

ns = ng.name_set(6)

msg = []

for x in range(ns.max_count):
    msg.append(ns.Gen())

#print(msg)

ls_len = len(msg)
set_len = len(set(msg))

print("ls_len: ", ls_len)
print("set_len: ", set_len)