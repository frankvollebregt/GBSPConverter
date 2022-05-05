from bsp import BSPChunk
from struct import pack
from main_quake import IBSP_TYPES
from simple_test import convert_to_ibsp_single
from full_test import convert_to_ibsp_full


def convert_to_ibsp(bsp):
    print('Converting...')
    new_bsp = {}

    # To create texture_info, we need textures and texture_info from the gbsp data
    gbsp_tex_info: BSPChunk = bsp[17]
    gbsp_tex: BSPChunk = bsp[18]

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

    # planes and vertices can be copied 1-to-1
    # new_bsp['planes'] = bsp[10]
    # new_bsp['vertices'] = bsp[14]

    print('Conversion is done!')
    return new_bsp


def read_gbsp_chunk(f):
    gbsp_bytes = f.read(12)
    chunk = BSPChunk.from_bytes(gbsp_bytes)
    chunk.read_bytes(f)
    return chunk


if __name__ == '__main__':
    file = open('bsp/test.bsp', 'rb')

    chunks = []
    gbsp = {}

    current_chunk = read_gbsp_chunk(file)
    while current_chunk.type_string() != 'GBSP_CHUNK_END':
        chunks.append(current_chunk)
        gbsp[current_chunk.type] = current_chunk
        print(current_chunk)
        current_chunk = read_gbsp_chunk(file)

    file.close()
    print(gbsp)

    # convert GBSP data to the correct IBSP data
    # ibsp_data = convert_to_ibsp(gbsp)
    ibsp_data = convert_to_ibsp_full(gbsp)

    print("".join([key + ', ' for key, value in ibsp_data.items()]))

    out_file = open('bsp/test_quake.bsp', 'w+b')

    # first, write the header
    out_file.write(bytearray('IBSP', 'utf8'))            # identifier
    out_file.write(pack("<I", 38))     # version

    # then, write the lumps
    # keep track of where we can put the next one
    pointer = 160
    bytes_to_write = []
    for i in range(19):
        if IBSP_TYPES[i] == 'IBSP_PLANES':
            planes = ibsp_data['planes']
            out_file.write(pack("<II", pointer, planes['size'] * planes['elements']))
            pointer += planes['size'] * planes['elements']
            bytes_to_write.append(planes['bytes'])
            print("wrote {} bytes for planes".format(len(planes['bytes'])))
            print('length matches: {}'.format(len(planes['bytes']) == planes['size']*planes['elements']))
        elif IBSP_TYPES[i] == 'IBSP_VERTICES':
            verts = ibsp_data['vertices']
            out_file.write(pack("<II", pointer, verts['size'] * verts['elements']))
            pointer += verts['size'] * verts['elements']
            bytes_to_write.append(verts['bytes'])
            print("wrote {} bytes for verts".format(len(verts['bytes'])))
            print('length matches: {}'.format(len(verts['bytes']) == verts['size'] * verts['elements']))
        elif IBSP_TYPES[i] == 'IBSP_FACES':
            faces = ibsp_data['faces']
            out_file.write(pack("<II", pointer, faces['size'] * faces['elements']))
            pointer += faces['size'] * faces['elements']
            bytes_to_write.append(faces['bytes'])
            print("wrote {} bytes for faces".format(len(faces['bytes'])))
            print('length matches: {}'.format(len(faces['bytes']) == faces['size'] * faces['elements']))
        elif IBSP_TYPES[i] == 'IBSP_EDGES':
            edges = ibsp_data['edges']
            out_file.write(pack("<II", pointer, edges['size'] * edges['elements']))
            pointer += edges['size'] * edges['elements']
            bytes_to_write.append(edges['bytes'])
            print("wrote {} bytes for edges".format(len(edges['bytes'])))
            print('length matches: {}'.format(len(edges['bytes']) == edges['size'] * edges['elements']))
        elif IBSP_TYPES[i] == 'IBSP_FACE_EDGE_TABLE':
            face_edges = ibsp_data['face_edges']
            out_file.write(pack("<II", pointer, face_edges['size'] * face_edges['elements']))
            pointer += face_edges['size'] * face_edges['elements']
            bytes_to_write.append(face_edges['bytes'])
            print("wrote {} bytes for face_edges".format(len(face_edges['bytes'])))
            print('length matches: {}'.format(len(face_edges['bytes']) == face_edges['size'] * face_edges['elements']))
        elif IBSP_TYPES[i] == 'IBSP_TEXTURE_INFORMATION':
            texture_info = ibsp_data['texture_info']
            out_file.write(pack("<II", pointer, texture_info['size'] * texture_info['elements']))
            pointer += texture_info['size'] * texture_info['elements']
            bytes_to_write.append(texture_info['bytes'])
            print("wrote {} bytes for texture_info".format(len(texture_info['bytes'])))
            print('length matches: {}'.format(len(texture_info['bytes']) == texture_info['size'] * texture_info['elements']))
        else:
            # don't include this, keep offset and length 0
            out_file.write(pack("<II", 0, 0))

    # write plane
    for byte_group in bytes_to_write:
        out_file.write(byte_group)

    out_file.close()
