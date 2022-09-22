from src.gbsp import HeaderLump
import sys

IBSP_TYPES = {
    0: "IBSP_ENTITIES",
    1: "IBSP_PLANES",
    2: "IBSP_VERTICES",
    3: "IBSP_VISIBILITY",
    4: "IBSP_NODES",
    5: "IBSP_TEXTURE_INFORMATION",
    6: "IBSP_FACES",
    7: "IBSP_LIGHTMAPS",
    8: "IBSP_LEAVES",
    9: "IBSP_LEAF_FACE_TABLE",
    10: "IBSP_LEAF_BRUSH_TABLE",
    11: "IBSP_EDGES",
    12: "IBSP_FACE_EDGE_TABLE",
    13: "MODELS",
    14: "BRUSHES",
    15: "BRUSH_SIDES",
    16: "POP",
    17: "AREAS",
    18: "AREA_PORTALS"
}


# Read IBSP header lump
def read_header_lump(f, i):
    lump_bytes = f.read(8)
    header_lump = HeaderLump.from_bytes(lump_bytes)
    header_lump.set_type(IBSP_TYPES[i])
    return header_lump


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python read_ibsp.py [filename.bsp]')
        exit(-1)

    path = sys.argv[1]
    file = open(path, 'rb')

    lumps = []

    header = file.read(8)
    ident = header[0:4]
    version = int.from_bytes(header[4:8], 'little')

    print("type: {}".format(ident))
    print("version: {}".format(version))

    # read lump dictionary
    for i in range(19):
        current_lump = read_header_lump(file, i)
        lumps.append(current_lump)
        if current_lump.length > 0:
            print(current_lump)

    file.close()

