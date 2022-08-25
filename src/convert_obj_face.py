import struct
from src.gbsp import GBSPChunk
from src.obj_helpers import Vec3d, is_invisible, get_plane_size

PLANE_SIDE_FRONT = 0
PLANE_SIDE_BACK = 1


def get_and_append_face(face_index, gbsp,
                        vert_map, vert_counter, vert_lines,
                        norm_map, norm_counter, norm_lines,
                        tex_counter, tex_lines,
                        face_lines, last_tex_name, remove_invisible=False):

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
    norm = Vec3d(struct.unpack('fff', plane_bytes[0:12]))
    plane_type = int.from_bytes(plane_bytes[16:20], 'little')

    if plane_side == PLANE_SIDE_BACK:
        norm = norm.invert()

    # get this face's normal from the plane
    if signed_plane_index not in norm_map:
        norm_map[signed_plane_index] = norm_counter
        norm_counter += 1

        norm_lines.append('vn  {}  {}  {}\n'.format(norm.x, norm.y, norm.z))

    tex_info_index = int.from_bytes(face_bytes[16:20], 'little')
    tex_info_offset = tex_info_index * gbsp_tex_info.size
    tex_info_bytes = gbsp_tex_info.bytes[tex_info_offset:tex_info_offset + gbsp_tex_info.size]

    u_axis = Vec3d(struct.unpack('fff', tex_info_bytes[0:12]))
    v_axis = Vec3d(struct.unpack('fff', tex_info_bytes[12:24]))

    u_offset, v_offset, u_scale, v_scale = struct.unpack('ffff', tex_info_bytes[24:40])

    tex_index = int.from_bytes(tex_info_bytes[60:64], 'little')

    tex_offset = tex_index * gbsp_tex.size
    tex_bytes = gbsp_tex.bytes[tex_offset:tex_offset + gbsp_tex.size]
    tex_name = tex_bytes[0:32].decode('utf-8').rstrip('\x00')
    tex_width = int.from_bytes(tex_bytes[36:40], 'little')
    tex_height = int.from_bytes(tex_bytes[40:44], 'little')

    # Little detour for the texture of this face
    if is_invisible(gbsp, tex_info_index, tex_bytes) and remove_invisible:
        return vert_map, vert_counter, vert_lines, \
               norm_map, norm_counter, norm_lines, \
               tex_counter, tex_lines, \
               face_lines, last_tex_name

    face_def = ''
    if last_tex_name == tex_name:
        face_def += "f"
    else:
        face_def += "usemtl {}\nf".format(tex_name)

    for i in range(num_verts):
        vert_index_indices.append(first_vert_index + i)

    # retrieve the vertices via the vertex index
    vert_index_indices.reverse()
    for vert_index_index in vert_index_indices:
        vert_index_offset = vert_index_index * gbsp_vert_index.size
        vert_index_bytes = gbsp_vert_index.bytes[vert_index_offset:vert_index_offset + gbsp_vert_index.size]
        vert_index = int.from_bytes(vert_index_bytes, 'little')

        new_vert = vert_index not in vert_map

        if new_vert:
            vert_map[vert_index] = vert_counter
            vert_counter += 1

        # get the vert
        vert_offset = vert_index * gbsp_verts.size
        vert_bytes = gbsp_verts.bytes[vert_offset:vert_offset + gbsp_verts.size]
        vec = Vec3d(struct.unpack('fff', vert_bytes))

        # write the vertex
        if new_vert:
            vert_lines.append("v  {}  {}  {}\n".format(vec.x, vec.y, vec.z))

        u = vec.dot(u_axis)/u_scale/tex_width
        v = vec.dot(v_axis)/v_scale/tex_height

        u += u_offset/tex_width
        v += v_offset/tex_height

        # flip textures vertically
        v *= -1

        tex_lines.append('vt  {}  {}\n'.format(u, v))

        face_def += '  {}/{}/{}'.format(vert_map[vert_index], tex_counter, norm_map[signed_plane_index])

        tex_counter += 1

    # write the face
    face_def += '\n'

    face_lines.append(face_def)

    last_tex_name = tex_name

    return vert_map, vert_counter, vert_lines, \
           norm_map, norm_counter, norm_lines, \
           tex_counter, tex_lines, \
           face_lines, last_tex_name
