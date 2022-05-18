from math import ceil

from PIL import Image
from struct import pack
from os.path import exists


# write the bitmap with palette to get the texture BMP files
def write_bitmap(my_bytes: bytes, width, height, name, palette, folder):
    image = Image.frombytes("P", (width, height), my_bytes)
    image.putpalette(data=palette)
    if len(folder) > 0:
        folder = folder + '/'
    else:
        folder = ''

    if not exists(folder+name+'.png'):
        print('saving to {}'.format(folder + name + '.png'))
        image.save(folder+name + '.png')


# no longer in use, as we can extract the BMPs directly from the BSP data
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



