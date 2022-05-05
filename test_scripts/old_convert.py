from bsp import GBSPChunk
from struct import pack


def convert_to_ibsp(bsp):
    print('Converting...')
    new_bsp = {}

    # To create texture_info, we need textures and texture_info from the gbsp data
    gbsp_tex_info: GBSPChunk = bsp[17]
    gbsp_tex: GBSPChunk = bsp[18]

    # todo, use this to determine the actual texture names, and use the offset from the info

    texture_info = b''
    for index in range(gbsp_tex_info.elements):
        offset = index * gbsp_tex_info.size

        cur_bytes = gbsp_tex_info.bytes[offset:offset+gbsp_tex_info.size]
        u_axis = cur_bytes[0:12]
        v_axis = cur_bytes[12:24]
        u_offset = cur_bytes[24:28]
        v_offset = cur_bytes[28:32]

        # texture_info += u_axis + u_offset + v_axis + v_offset + pack("<II", 0, 0)
        texture_info += u_axis + pack("<f", 0) + v_axis + pack("<f", 0) + pack("<II", 0, 0)
        texture_info += b'mytexture'
        texture_info += b''.join([pack("<B", 0) for my_i in range(23)]) # pad the rest of the texture String with 0s
        texture_info += pack("<I", 0)

    print('Converted texture info!')
    new_bsp['texture_info'] = {
        'elements': gbsp_tex_info.elements,
        'bytes': texture_info,
        'size': 76,
    }

    gbsp_faces = bsp[11]

    # First, we read the faces to find out the vert index and number of verts
    # Then, we can use these verts to create edges between them
    all_edges = b''
    all_faces = b''

    print('gonna do faces now')
    for face_index in range(gbsp_faces.elements):
        offset = face_index * gbsp_faces.size
        cur_bytes = gbsp_faces.bytes[offset:offset + gbsp_faces.size]

        # read info from the GBSP face
        first_vert = int.from_bytes(cur_bytes[0:4], 'little')
        num_verts = int.from_bytes(cur_bytes[4:8], 'little')
        plane = int.from_bytes(cur_bytes[8:12], 'little')
        tex_info = int.from_bytes(cur_bytes[16:20], 'little')

        first_edge_index = -1

        # now that we know the index of the vertex, we can get the vertex indices and use those to create
        # the edges
        vert_indices = [first_vert + j for j in range(num_verts)]
        for index in range(len(vert_indices)):
            if index == 0:
                # first edge, store it to use in the face
                first_edge_index = int(len(all_edges) / 4)
            point_a = vert_indices[index]
            b_index = (index+1) % len(vert_indices)
            point_b = vert_indices[b_index]

            all_edges += pack("<hh", point_a, point_b)

        # Now store the face in the all_faces list
        all_faces += pack("<HHIHHBI", plane, 0, first_edge_index, num_verts, tex_info, 0, 0)



    num_edges = int(len(all_edges)/4)
    new_bsp['edges'] = {
        'elements': num_edges,
        'bytes': all_edges,
        'size': 4,
    }
    print('Added edges')

    # face edges, in our case, map 1 to 1 to the actual edges
    face_edges = b''
    for face_edge in range(num_edges):
        face_edges += pack("<I", face_edge)

    new_bsp['face_edges'] = {
        'elements': num_edges,
        'bytes': face_edges,
        'size': 4,
    }
    print('Added face edges')

    new_bsp['faces'] = {
        'elements': gbsp_faces.elements,
        'bytes': all_faces,
        'size': 20,
    }

    print('Conversion is done!')
    return new_bsp