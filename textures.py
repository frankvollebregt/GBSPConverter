from math import ceil

from PIL import Image
from struct import pack


def write_bitmap(bytes, width, height, name):
    if name == 'snd00':
        with open('tex/testfile.bin', 'wb') as binfile:
            binfile.write(bytes)
    # print('Creating image {} of size {}x{}'.format(name, width, height))
    image = Image.frombytes("RGB", (width, height), bytes)
    image.save('tex/'+name + '.png')


def write_wal(bytes, width, height, name: bytes, folder):
    with open(folder+'/'+name.decode('utf-8').rstrip('\x00')+'.wal', 'wb') as wal_file:
        wal_file.write(name)
        wal_file.write(width)
        wal_file.write(height)

        # mipmap level offsets
        w = int.from_bytes(width, 'little')
        h = int.from_bytes(height, 'little')
        wal_file.write(pack("<iiii", 100, ceil(100 + w*h), ceil(100 + w*h + w/2*h/2), ceil(100+ w*h + w/2*h/4 + w/2*h/4)))
        # no next name
        wal_file.write(b''.join([pack("<B", 0) for my_i in range(32)]))
        wal_file.write(pack("<III", 0, 0, 0))

        # body
        wal_file.write(bytes)



