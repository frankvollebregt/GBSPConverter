from bsp import BSPChunk
from struct import pack


def convert_to_ibsp_single(bsp):
    print('Converting...')
    new_bsp = {}

    # To create texture_info, we need textures and texture_info from the gbsp data
    gbsp_tex_info: BSPChunk = bsp[17]
    gbsp_tex: BSPChunk = bsp[18]

    texture_info = b''

    gbsp_faces = bsp[11]
    gbsp_verts: BSPChunk = bsp[2]
    gbsp_planes: BSPChunk = bsp[10]

    # First, we read the faces to find out the vert index and number of verts
    # Then, we can use these verts to create edges between them
    all_edges = b''
    all_faces = b''

    print('gonna do face now')
    face_index = 0
    offset = face_index * gbsp_faces.size
    cur_bytes = gbsp_faces.bytes[offset:offset + gbsp_faces.size]

    # read info from the GBSP face
    first_vert = int.from_bytes(cur_bytes[0:4], 'little')
    num_verts = int.from_bytes(cur_bytes[4:8], 'little')
    plane = int.from_bytes(cur_bytes[8:12], 'little')
    tex_info = int.from_bytes(cur_bytes[16:20], 'little')

    print('num verts: {}'.format(num_verts))
    vert_bytes = gbsp_verts.bytes[gbsp_verts.size * first_vert:(first_vert + num_verts) * 12]

    new_bsp['vertices'] = {
        'elements': num_verts,
        'bytes': vert_bytes,
        'size': 12,
    }

    plane_bytes = gbsp_planes.bytes[gbsp_planes.size * plane:(plane + 1) * gbsp_planes.size]

    new_bsp['planes'] = {
        'elements': 1,
        'bytes': plane_bytes,
        'size': 20,
    }

    # now that we know the index of the vertex, we can get the vertex indices and use those to create
    # the edges
    vert_indices = [0 + j for j in range(num_verts)]
    for index in range(len(vert_indices)):
        if index == 0:
            # first edge, store it to use in the face
            first_edge_index = int(len(all_edges) / 4)
        point_a = vert_indices[index]
        b_index = (index+1) % len(vert_indices)
        point_b = vert_indices[b_index]

        all_edges += pack("<hh", point_a, point_b)

    # Now store the face in the all_faces list
    all_faces += pack("<HHIHHII", 0, 0, 0, num_verts, 0, 0, 0)



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
        'elements': 1,
        'bytes': all_faces,
        'size': 20,
    }

    print('tex info index {}'.format(tex_info))
    cur_bytes = gbsp_tex_info.bytes[gbsp_tex_info.size*tex_info:gbsp_tex_info.size*(tex_info+1)]
    u_axis = cur_bytes[0:12]
    v_axis = cur_bytes[12:24]
    u_offset = cur_bytes[24:28]
    v_offset = cur_bytes[28:32]

    # texture_info += u_axis + u_offset + v_axis + v_offset + pack("<II", 0, 0)
    texture_info += u_axis + pack("<f", 0) + v_axis + pack("<f", 0) + pack("<II", 0, 0)
    texture_info += "mytexture".encode('ascii')
    texture_info += b''.join([pack("<b", 0) for my_i in range(23)]) # pad the rest of the texture String with 0s
    texture_info += pack("<I", 0)

    # try to read it back
    my_text = texture_info[40:72].decode('ascii')
    print(my_text)

    f = open('../test/test_file.bin', 'wb')
    f.write(texture_info)
    f.close()

    print('Converted texture info!')
    new_bsp['texture_info'] = {
        'elements': 1,
        'bytes': texture_info,
        'size': 76,
    }

    print('Conversion is done!')
    return new_bsp