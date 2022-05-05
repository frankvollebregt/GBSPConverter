# from bsp import HeaderLump
#
#
# def read_header_lump(f):
#     lump_bytes = f.read(16)
#     header_lump = HeaderLump.from_bytes(lump_bytes)
#     return header_lump
#
#
# if __name__ == '__main__':
#     file = open('valve.bsp', 'rb')
#
#     lumps = []
#
#     header = file.read(8)
#     ident = header[0:4]
#     version = int.from_bytes(header[4:8], 'little')
#
#     print("type: {}".format(ident))
#     print("version: {}".format(version))
#     # read lump dictionary
#
#     current_lump = read_header_lump(file)
#     while len(lumps) < 10:
#         lumps.append(current_lump)
#         print(current_lump)
#         current_lump = read_header_lump(file)
#
#     file.close()
