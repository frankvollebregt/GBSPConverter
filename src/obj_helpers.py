import math
import struct
import sys

from src.gbsp import GBSPChunk


# Simple vector class
# for cleaner dot product code and vector storage
class Vec3d:
    def __init__(self, tuple):
        self.x = tuple[0]
        self.y = tuple[1]
        self.z = tuple[2]

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def invert(self):
        self.x *= -1
        self.y *= -1
        self.z *= -1

    def get_norm(self):
        # calculate length
        length = self.get_length()
        return Vec3d((self.x / length, self.y / length, self.z / length))

    def get_scaled(self, scale):
        return Vec3d((self.x * scale, self.y * scale, self.z * scale))

    def get_length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def __str__(self):
        return 'Vec3d({}, {}, {})'.format(self.x, self.y, self.z)


# Get the size of this plane in world coordinates
def get_plane_size(gbsp, indices, u_axis: Vec3d, v_axis: Vec3d, u_scale, v_scale):
    gbsp_vert_index: GBSPChunk = gbsp[13]
    gbsp_verts: GBSPChunk = gbsp[14]

    min_u = math.inf
    max_u = -math.inf
    min_v = math.inf
    max_v = -math.inf

    for vert_index_index in indices:
        vert_index_offset = vert_index_index * gbsp_vert_index.size
        vert_index_bytes = gbsp_vert_index.bytes[vert_index_offset:vert_index_offset + gbsp_vert_index.size]
        vert_index = int.from_bytes(vert_index_bytes, 'little')

        # get the vert
        vert_offset = vert_index * gbsp_verts.size
        vert_bytes = gbsp_verts.bytes[vert_offset:vert_offset + gbsp_verts.size]
        vec = Vec3d(struct.unpack('fff', vert_bytes))

        vec_dot_u = vec.dot(u_axis.get_scaled(u_scale))
        vec_dot_v = vec.dot(v_axis.get_scaled(v_scale))

        if vec_dot_u < min_u:
            min_u = vec_dot_u
        if vec_dot_u > max_u:
            max_u = vec_dot_u
        if vec_dot_v < min_v:
            min_v = vec_dot_v
        if vec_dot_v > max_v:
            max_v = vec_dot_v

    u_size = max_u - min_u
    v_size = max_v - min_v

    if u_size == 0:
        u_size = sys.float_info.epsilon
    if v_size == 0:
        v_size = sys.float_info.epsilon

    return u_size, v_size


def is_invisible(gbsp, tex_info_index):
    gbsp_tex_info: GBSPChunk = gbsp[17]
    gbsp_texdata: GBSPChunk = gbsp[18]

    tex_info_offset = tex_info_index * gbsp_tex_info.size
    tex_info_bytes = gbsp_tex_info.bytes[tex_info_offset:tex_info_offset + gbsp_tex_info.size]
    tex_width = int.from_bytes(tex_info_bytes[36:40], 'little')
    tex_height = int.from_bytes(tex_info_bytes[40:44], 'little')
    texture_offset = int.from_bytes(tex_info_bytes[44:48], 'little')

    tex_data_bytes = gbsp_texdata.bytes[texture_offset:texture_offset + math.ceil(tex_width * tex_height * (85 / 64))]

    has_transparency = False
    for byte in tex_data_bytes:
        if byte == 255:
            has_transparency = True

    # We only need the flags
    tex_info_flags = tex_info_bytes[40:44]
    flag_bits = [access_bit(tex_info_flags, i) for i in range(len(tex_info_flags) * 8)]

    return (flag_bits[2] == 1 or flag_bits[4] == 1) and not has_transparency


# Thanks SO! https://stackoverflow.com/a/43787831/15469537
def access_bit(data, num):
    base = int(num // 8)
    shift = int(num % 8)
    return (data[base] >> shift) & 0x1

