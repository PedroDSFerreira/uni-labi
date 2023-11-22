import hashlib
import sys

h = hashlib.sha1()
for i in sys.argv[1:]:
    print(i)
    file = open(i, 'rb')
    buffer = file.read(512)

    # len(buffer) == 0 --> End-of-file reached
    # len(buffer) > 0 --> buffer has len(buffer) bytes
    while len(buffer):
        h.update(buffer)
        buffer = file.read(512)
    file.close()

hash_ = h.hexdigest()
print(hash_)
