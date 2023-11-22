import hashlib
import sys

h = hashlib.sha1()
for i in sys.argv[1:]:
    print(i)
    file = open(i, 'r')
    for line in file:
        h.update(line.encode('utf-8'))
    file.close()

hash_ = h.hexdigest()
print(hash_)
