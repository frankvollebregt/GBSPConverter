import struct

# from convert_fbx import Polygon
from fbx import *

from src.gbsp import GBSPChunk
from src.obj_helpers import Vec3d, is_invisible, get_plane_size

PLANE_SIDE_FRONT = 0
PLANE_SIDE_BACK = 1


# def get_and_append_face_fbx(gbsp, face_index, vertices, polygons, texture_names, remove_invisible=False):
#
#     # Get the data chunks from the GBSP file
#     gbsp_planes: GBSPChunk = gbsp[10]
#     gbsp_faces: GBSPChunk = gbsp[11]
#     gbsp_vert_index: GBSPChunk = gbsp[13]
#     gbsp_verts: GBSPChunk = gbsp[14]
#     gbsp_tex_info: GBSPChunk = gbsp[17]
#     gbsp_tex: GBSPChunk = gbsp[18]
#
#     face_offset = face_index * gbsp_faces.size
#     face_bytes = gbsp_faces.bytes[face_offset:face_offset + gbsp_faces.size]
#
#     # array to store the indices of the vertices in the vert_index chunk
#     vert_index_indices = []
#
#     first_vert_index = int.from_bytes(face_bytes[0:4], 'little')
#     num_verts = int.from_bytes(face_bytes[4:8], 'little')
#     plane_index = int.from_bytes(face_bytes[8:12], 'little')
#     plane_side = int.from_bytes(face_bytes[12:16], 'little')
#     signed_plane_index = plane_index if plane_side == 1 else -plane_index
#
#     plane_offset = plane_index * gbsp_planes.size
#     plane_bytes = gbsp_planes.bytes[plane_offset:plane_offset + gbsp_planes.size]
#     norm = Vec3d(struct.unpack('fff', plane_bytes[0:12]))
#     plane_type = int.from_bytes(plane_bytes[16:20], 'little')
#
#     if plane_side == PLANE_SIDE_BACK:
#         norm = norm.invert()
#
#     # get this face's normal from the plane
#     # if signed_plane_index not in norm_map:
#     #     norm_map[signed_plane_index] = norm_counter
#     #     norm_counter += 1
#     #
#     #     norm_lines.append('vn  {}  {}  {}\n'.format(norm.x, norm.y, norm.z))
#
#     tex_info_index = int.from_bytes(face_bytes[16:20], 'little')
#     tex_info_offset = tex_info_index * gbsp_tex_info.size
#     tex_info_bytes = gbsp_tex_info.bytes[tex_info_offset:tex_info_offset + gbsp_tex_info.size]
#
#     u_axis = Vec3d(struct.unpack('fff', tex_info_bytes[0:12]))
#     v_axis = Vec3d(struct.unpack('fff', tex_info_bytes[12:24]))
#
#     u_offset, v_offset, u_scale, v_scale = struct.unpack('ffff', tex_info_bytes[24:40])
#
#     tex_index = int.from_bytes(tex_info_bytes[60:64], 'little')
#
#     tex_offset = tex_index * gbsp_tex.size
#     tex_bytes = gbsp_tex.bytes[tex_offset:tex_offset + gbsp_tex.size]
#     tex_name = tex_bytes[0:32].decode('utf-8').rstrip('\x00')
#     tex_width = int.from_bytes(tex_bytes[36:40], 'little')
#     tex_height = int.from_bytes(tex_bytes[40:44], 'little')
#
#     # Little detour for the texture of this face
#     if is_invisible(gbsp, tex_info_index, tex_bytes) and remove_invisible:
#         return vertices, polygons, texture_names
#
#     # face_def = ''
#     # if last_tex_name == tex_name:
#     #     face_def += "f"
#     # else:
#     #     face_def += "usemtl {}\nf".format(tex_name)
#
#     for i in range(num_verts):
#         vert_index_indices.append(first_vert_index + i)
#
#     # retrieve the vertices via the vertex index
#     vert_index_indices.reverse()
#
#     polygon = []
#     for vert_index_index in vert_index_indices:
#         vert_index_offset = vert_index_index * gbsp_vert_index.size
#         vert_index_bytes = gbsp_vert_index.bytes[vert_index_offset:vert_index_offset + gbsp_vert_index.size]
#         vert_index = int.from_bytes(vert_index_bytes, 'little')
#
#         # new_vert = vert_index not in vert_map
#         #
#         # if new_vert:
#         #     vert_map[vert_index] = vert_counter
#         #     vert_counter += 1
#
#         # get the vert
#         vert_offset = vert_index * gbsp_verts.size
#         vert_bytes = gbsp_verts.bytes[vert_offset:vert_offset + gbsp_verts.size]
#         vec = Vec3d(struct.unpack('fff', vert_bytes))
#
#         # write the vertex
#         if vec not in vertices:
#             vertices.append(vec)
#             # vert_lines.append("v  {}  {}  {}\n".format(vec.x, vec.y, vec.z))
#
#         u = vec.dot(u_axis)/u_scale/tex_width
#         v = vec.dot(v_axis)/v_scale/tex_height
#
#         u += u_offset/tex_width
#         v += v_offset/tex_height
#
#         # flip textures vertically
#         v *= -1
#
#         fbx_vert_index = vertices.index(vec)
#         polygon.append(fbx_vert_index)
#         # tex_lines.append('vt  {}  {}\n'.format(u, v))
#
#         # face_def += '  {}/{}/{}'.format(vert_map[vert_index], tex_counter, norm_map[signed_plane_index])
#
#         # tex_counter += 1
#
#     polygons.append(polygon)
#     texture_names.append(tex_name)
#
#     return vertices, polygons, texture_names
#     # write the face
#     # face_def += '\n'
#
#     # face_lines.append(face_def)
#
#     # last_tex_name = tex_name
#
#     # return vert_map, vert_counter, vert_lines, \
#     #        norm_map, norm_counter, norm_lines, \
#     #        tex_counter, tex_lines, \
#     #        face_lines, last_tex_name


def get_and_append_face_fbx(gbsp, face_index, tex_names, vertex_array, normal_array, uv_array, polygons, remove_invisible=True):
    # Get the data chunks from the GBSP file
    gbsp_planes: GBSPChunk = gbsp[10]
    gbsp_faces: GBSPChunk = gbsp[11]
    gbsp_vert_index: GBSPChunk = gbsp[13]
    gbsp_verts: GBSPChunk = gbsp[14]
    gbsp_tex_info: GBSPChunk = gbsp[17]
    gbsp_tex: GBSPChunk = gbsp[18]

    face_offset = face_index * gbsp_faces.size
    face_bytes = gbsp_faces.bytes[face_offset:face_offset + gbsp_faces.size]

    # array to store the indices of the vertices in the vert_index chunk
    vert_index_indices = []

    first_vert_index = int.from_bytes(face_bytes[0:4], 'little')
    num_verts = int.from_bytes(face_bytes[4:8], 'little')
    plane_index = int.from_bytes(face_bytes[8:12], 'little')
    plane_side = int.from_bytes(face_bytes[12:16], 'little')
    signed_plane_index = plane_index if plane_side == 1 else -plane_index

    plane_offset = plane_index * gbsp_planes.size
    plane_bytes = gbsp_planes.bytes[plane_offset:plane_offset + gbsp_planes.size]
    norm = FbxVector4(struct.unpack('f', plane_bytes[0:4])[0], struct.unpack('f', plane_bytes[4:8])[0], struct.unpack('f', plane_bytes[8:12])[0])
    plane_type = int.from_bytes(plane_bytes[16:20], 'little')

    if plane_side == PLANE_SIDE_FRONT:
        norm = FbxVector4(-1*struct.unpack('f', plane_bytes[0:4])[0], -1*struct.unpack('f', plane_bytes[4:8])[0], -1*struct.unpack('f', plane_bytes[8:12])[0])

    # Add normal to the array (if needed)
    if norm not in normal_array:
        normal_array.append(norm)

    norm_index = normal_array.index(norm)

    tex_info_index = int.from_bytes(face_bytes[16:20], 'little')
    tex_info_offset = tex_info_index * gbsp_tex_info.size
    tex_info_bytes = gbsp_tex_info.bytes[tex_info_offset:tex_info_offset + gbsp_tex_info.size]

    tex_info_flags = tex_info_bytes[40:44]
    flag_bits = [access_bit(tex_info_flags, i) for i in range(len(tex_info_flags) * 8)]

    u_axis = Vec3d(struct.unpack('fff', tex_info_bytes[0:12]))
    v_axis = Vec3d(struct.unpack('fff', tex_info_bytes[12:24]))

    u_offset, v_offset, u_scale, v_scale = struct.unpack('ffff', tex_info_bytes[24:40])

    tex_index = int.from_bytes(tex_info_bytes[60:64], 'little')

    tex_offset = tex_index * gbsp_tex.size
    tex_bytes = gbsp_tex.bytes[tex_offset:tex_offset + gbsp_tex.size]
    tex_name = tex_bytes[0:32].decode('utf-8').rstrip('\x00')
    tex_width = int.from_bytes(tex_bytes[36:40], 'little')
    tex_height = int.from_bytes(tex_bytes[40:44], 'little')

    texture_index = tex_names.index(tex_name)

    # Little detour for the texture of this face
    if remove_invisible and flag_bits[2] == 1:
        return vertex_array, normal_array, uv_array, polygons

    for i in range(num_verts):
        vert_index_indices.append(first_vert_index + i)

    # retrieve the vertices via the vertex index
    vert_index_indices.reverse()

    polygon_vertices = []
    uv_indices = []
    for vert_index_index in vert_index_indices:
        vert_index_offset = vert_index_index * gbsp_vert_index.size
        vert_index_bytes = gbsp_vert_index.bytes[vert_index_offset:vert_index_offset + gbsp_vert_index.size]
        vert_index = int.from_bytes(vert_index_bytes, 'little')

        # get the vert
        vert_offset = vert_index * gbsp_verts.size
        vert_bytes = gbsp_verts.bytes[vert_offset:vert_offset + gbsp_verts.size]
        vec = Vec3d(struct.unpack('fff', vert_bytes))

        # write the vertex
        if FbxVector4(vec.x, vec.y, vec.z) not in vertex_array:
            vertex_array.append(FbxVector4(vec.x, vec.y, vec.z))

        polygon_vertices.append(vertex_array.index(FbxVector4(vec.x, vec.y, vec.z)))

        u = vec.dot(u_axis) / u_scale / tex_width
        v = vec.dot(v_axis) / v_scale / tex_height

        u += u_offset / tex_width
        v += v_offset / tex_height

        # flip textures vertically
        v *= -1

        if FbxVector2(u, v) not in uv_array:
            uv_array.append(FbxVector2(u, v))

        uv_indices.append(uv_array.index(FbxVector2(u, v)))

    polygons.append([texture_index, polygon_vertices, norm_index, uv_indices])

    return vertex_array, normal_array, uv_array, polygons


# class Polygon:
#     def __init__(self, texture_index, vert_indices, normal_index, uvs):
#         self.texture_index = texture_index
#         self.vert_indices = vert_indices
#         self.normal_index = normal_index
#         self.uvs = uvs
#
#     def __str__(self):
#         return "Polygon:\n  texture_index: {},\n  vert_indices: {},\n  normal_index: {},\n  uvs: {}\n".format(self.texture_index, self.vert_indices, self.normal_index, self.uvs)

# Thanks SO! https://stackoverflow.com/a/43787831/15469537
def access_bit(data, num):
    base = int(num // 8)
    shift = int(num % 8)
    return (data[base] >> shift) & 0x1