# Identifies and describes the following block of data
class GBSPChunk:
    def __init__(self, type, size, elements, is_vbsp=False):
        self.type = type
        self.size = size
        self.elements = elements
        self.is_vbsp = is_vbsp
        self.bytes = None

    @classmethod
    def from_bytes(cls, bsp_bytes):
        type = int.from_bytes(bsp_bytes[0:4], 'little')
        size = int.from_bytes(bsp_bytes[4:8], 'little')
        elements = int.from_bytes(bsp_bytes[8:12], 'little')
        return cls(type, size, elements)

    def has_bytes(self):
        return self.bytes is not None

    def set_bytes(self, bytes):
        self.bytes = bytes

    def read_bytes(self, file):
        self.bytes = file.read(self.size * self.elements)

    def type_string(self):
        if self.type in GBSP_TYPES.keys():
            return GBSP_TYPES[self.type]
        else:
            return 'UNKNOWN'

    def __str__(self):
        return "BSPChunk(\n  type: {},\n  size: {},\n  elements: {},\n  bytes: {}\n)".format(self.type_string(), self.size, self.elements, len(self.bytes))


GBSP_TYPES = {
    0: "GBSP_CHUNK_HEADER",
    1: "GBSP_CHUNK_MODELS",
    2: "GBSP_CHUNK_NODES",
    3: "GBSP_CHUNK_BNODES",
    4: "GBSP_CHUNK_LEAFS",
    5: "GBSP_CHUNK_CLUSTERS",
    6: "GBSP_CHUNK_AREAS",
    7: "GBSP_CHUNK_AREA_PORTALS",
    8: "GBSP_CHUNK_LEAF_SIDES",
    9: "GBSP_CHUNK_PORTALS",
    10: "GBSP_CHUNK_PLANES",
    11: "GBSP_CHUNK_FACES",
    12: "GBSP_CHUNK_LEAF_FACES",
    13: "GBSP_CHUNK_VERT_INDEX",
    14: "GBSP_CHUNK_VERTS",
    15: "GBSP_CHUNK_RGB_VERTS",
    16: "GBSP_CHUNK_ENTDATA",
    17: "GBSP_CHUNK_TEXINFO",
    18: "GBSP_CHUNK_TEXTURES",
    19: "GBSP_CHUNK_TEXDATA",
    20: "GBSP_CHUNK_LIGHTDATA",
    21: "GBSP_CHUNK_VISDATA",
    22: "GBSP_CHUNK_SKYDATA",
    23: "GBSP_CHUNK_PALETTES",
    24: "GBSP_CHUNK_MOTIONS",
    0xffff: "GBSP_CHUNK_END",
}


class HeaderLump:
    def __init__(self, offset, length):
        self.offset = offset
        self.length = length
        self.type = 'UNKNOWN'

    @classmethod
    def from_bytes(cls, bsp_bytes):
        offset = int.from_bytes(bsp_bytes[0:4], 'little')
        length = int.from_bytes(bsp_bytes[4:8], 'little')

        return cls(offset, length)

    def set_type(self, type):
        self.type = type

    def __str__(self):
        return "HeaderLump(\n  offset: {},\n  length: {},\n  type: {}\n)".format(self.offset, self.length, self.type)
