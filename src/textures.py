from PIL import Image
from os.path import exists
import numpy as np


# write the bitmap with palette to get the texture BMP files
def write_bitmap(my_bytes: bytes, width, height, name, palette, folder):
    # Manipulate the palette to replace the last color with (hopefully) an otherwise unused color
    palette = palette[0:-3] + bytes([15, 234, 123])

    image = Image.frombytes("P", (width, height), my_bytes)
    image.putpalette(data=palette)
    last_b, last_g, last_r = palette[-1], palette[-2], palette[-3]

    if len(folder) > 0:
        folder = folder + '/'
    else:
        folder = ''

    image = image.convert('RGBA')

    data = np.array(image)
    red, green, blue, alpha = data.T
    with_last = (red == last_r) & (blue == last_b) & (green == last_g)
    data[...][with_last.T] = (0, 0, 0, 0)

    image = Image.fromarray(data)

    if not exists(folder+name+'.png') or True:
        image.save(folder+name + '.png')

    # return whether or not this image had any transparency in it (index 255 was used)
    for byte in my_bytes:
        if byte == 255:
            return True
    return False


# no longer in use, as we can extract the BMPs directly from the BSP data
# def write_wal(bytes, width, height, name: bytes, folder):
#     with open(folder+'/'+name.decode('utf-8').rstrip('\x00')+'.wal', 'wb') as wal_file:
#         wal_file.write(name)
#         wal_file.write(width)
#         wal_file.write(height)
#
#         # mipmap level offsets
#         w = int.from_bytes(width, 'little')
#         h = int.from_bytes(height, 'little')
#         wal_file.write(pack("<iiii", 100, ceil(100 + w*h), ceil(100 + w*h + w/2*h/2), ceil(100+ w*h + w/2*h/4 + w/2*h/4)))
#         # no next name
#         wal_file.write(b''.join([pack("<B", 0) for my_i in range(32)]))
#         wal_file.write(pack("<III", 0, 0, 0))
#
#         # body
#         wal_file.write(bytes)



