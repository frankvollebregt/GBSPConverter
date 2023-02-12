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


# return whether or not this image has any transparency in it (index 255 was used)
def has_transparency(my_bytes: bytes):
    for byte in my_bytes:
        if byte == 255:
            return True
    return False
