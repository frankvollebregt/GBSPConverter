from gbsp import GBSPChunk
from struct import pack


# Convert the map of GBSP chunk objects to a map of IBSP data
def convert_to_ibsp(gbsp):
    print('Converting to IBSP...')
    new_bsp = {}

    # To create texture_info, we need textures and texture_info from the gbsp data
    gbsp_tex_info: GBSPChunk = gbsp[17]
    gbsp_tex: GBSPChunk = gbsp[18]

    gbsp_faces: GBSPChunk = gbsp[11]
    gbsp_verts: GBSPChunk = gbsp[14]
    gbsp_vert_index: GBSPChunk = gbsp[13]
    gbsp_planes: GBSPChunk = gbsp[10]

    # First, we read the faces to find out the vert index and number of verts
    # Then, we can use these verts to create edges between them
    all_edges = b''
    all_faces = b''

    print('convert all vertices (1 to 1)'.format(gbsp_verts.elements))
    new_bsp['vertices'] = {
        'elements': gbsp_verts.elements,
        'bytes': gbsp_verts.bytes,
        'size': 12,
    }

    print('convert all planes (1 to 1)')
    new_bsp['planes'] = {
        'elements': gbsp_planes.elements,
        'bytes': gbsp_planes.bytes,
        'size': 20,
    }

    print('converting faces and constructing edges')
    for face_index in range(gbsp_faces.elements):
        # face_index = 0
        offset = face_index * gbsp_faces.size
        cur_bytes = gbsp_faces.bytes[offset:offset + gbsp_faces.size]

        # read info from the GBSP face
        first_vert_index = int.from_bytes(cur_bytes[0:4], 'little')
        num_verts = int.from_bytes(cur_bytes[4:8], 'little')
        plane = int.from_bytes(cur_bytes[8:12], 'little')
        tex_info = int.from_bytes(cur_bytes[16:20], 'little')

        # now that we know the index of the vertex, we can get the vertex indices and use those to create
        # the edges
        vert_index_indices = [first_vert_index + j for j in range(num_verts)]
        # TODO be smarter about this, to prevent duplicates?
        for index in range(len(vert_index_indices)):
            if index == 0:
                # first edge, store it to use in the face
                first_edge_index = int(len(all_edges) / 4)
            vert_index_a = gbsp_vert_index.bytes[4*vert_index_indices[index]:4*vert_index_indices[index]+4]
            dest = (index+1) % len(vert_index_indices)
            vert_index_b = gbsp_vert_index.bytes[4*vert_index_indices[dest]:4*vert_index_indices[dest] + 4]
            point_a = int.from_bytes(vert_index_a, 'little')
            point_b = int.from_bytes(vert_index_b, 'little')
            all_edges += pack("<hh", point_a, point_b)

        # Now store the face in the all_faces list
        all_faces += pack("<HHIHHII", plane, 0, first_edge_index, num_verts, tex_info, 0, 0)


    print('convert edges')
    num_edges = int(len(all_edges)/4)
    new_bsp['edges'] = {
        'elements': num_edges,
        'bytes': all_edges,
        'size': 4,
    }

    # face edges, in our case, map 1 to 1 to the actual edges
    face_edges = b''
    for face_edge in range(num_edges):
        face_edges += pack("<I", face_edge)

    print('convert face edges (freebie)')
    new_bsp['face_edges'] = {
        'elements': num_edges,
        'bytes': face_edges,
        'size': 4,
    }

    print('convert faces')
    new_bsp['faces'] = {
        'elements': gbsp_faces.elements,
        'bytes': all_faces,
        'size': 20,
    }

    print('convert texture info (with hard-coded texture name)')
    texture_info = b''
    for index in range(gbsp_tex_info.elements):
        offset = index * gbsp_tex_info.size

        cur_bytes = gbsp_tex_info.bytes[offset:offset + gbsp_tex_info.size]
        u_axis = cur_bytes[0:12]
        v_axis = cur_bytes[12:24]
        u_offset = cur_bytes[24:28]
        v_offset = cur_bytes[28:32]

        # texture_info += u_axis + u_offset + v_axis + v_offset + pack("<II", 0, 0)
        texture_info += u_axis + u_offset + v_axis + v_offset + pack("<II", 0, 0)
        texture_info += b'mytexture'
        texture_info += b''.join([pack("<B", 0) for my_i in range(23)])  # pad the rest of the texture String with 0s
        texture_info += pack("<I", 0)

    new_bsp['texture_info'] = {
        'elements': gbsp_tex_info.elements,
        'bytes': texture_info,
        'size': 76,
    }

    print('Conversion is done!')
    return new_bsp


# Convert the map of GBSP chunk objects to a map of VBSP data
def convert_to_vbsp(gbsp):
    print('Converting to VBSP...')
    new_bsp = {}

    # To create texture_info, we need textures and texture_info from the gbsp data
    gbsp_tex_info: GBSPChunk = gbsp[17]
    gbsp_tex: GBSPChunk = gbsp[18]

    gbsp_faces: GBSPChunk = gbsp[11]
    gbsp_verts: GBSPChunk = gbsp[14]
    gbsp_vert_index: GBSPChunk = gbsp[13]
    gbsp_planes: GBSPChunk = gbsp[10]

    # First, we read the faces to find out the vert index and number of verts
    # Then, we can use these verts to create edges between them
    all_edges = b''
    all_faces = b''

    print('convert all vertices (1 to 1)'.format(gbsp_verts.elements))
    new_bsp['vertices'] = {
        'elements': gbsp_verts.elements,
        'bytes': gbsp_verts.bytes,
        'size': 12,
    }

    print('convert all planes (1 to 1)')
    new_bsp['planes'] = {
        'elements': gbsp_planes.elements,
        'bytes': gbsp_planes.bytes,
        'size': 20,
    }

    print('converting faces and constructing edges')
    for face_index in range(gbsp_faces.elements):
        offset = face_index * gbsp_faces.size
        cur_bytes = gbsp_faces.bytes[offset:offset + gbsp_faces.size]

        # read info from the GBSP face
        first_vert_index = int.from_bytes(cur_bytes[0:4], 'little')
        num_verts = int.from_bytes(cur_bytes[4:8], 'little')
        plane = int.from_bytes(cur_bytes[8:12], 'little')
        tex_info = int.from_bytes(cur_bytes[16:20], 'little')

        # now that we know the index of the vertex, we can get the vertex indices and use those to create
        # the edges
        vert_index_indices = [first_vert_index + j for j in range(num_verts)]
        # TODO be smarter about this, to prevent duplicates?
        for index in range(len(vert_index_indices)):
            if index == 0:
                # first edge, store it to use in the face
                first_edge_index = int(len(all_edges) / 4)
            vert_index_a = gbsp_vert_index.bytes[4*vert_index_indices[index]:4*vert_index_indices[index]+4]
            dest = (index+1) % len(vert_index_indices)
            vert_index_b = gbsp_vert_index.bytes[4*vert_index_indices[dest]:4*vert_index_indices[dest] + 4]
            point_a = int.from_bytes(vert_index_a, 'little')
            point_b = int.from_bytes(vert_index_b, 'little')
            all_edges += pack("<hh", point_a, point_b)

        # Now store the face in the all_faces list
        all_faces += pack("<HBBihh", plane, 0, 0, first_edge_index, num_verts, tex_info)
        all_faces += pack("<hhBBBBifiiiiiHHI", 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0, 0, 0, 0, 0, 0)

    print('convert edges')
    num_edges = int(len(all_edges)/4)
    new_bsp['edges'] = {
        'elements': num_edges,
        'bytes': all_edges,
        'size': 4,
    }

    # surface edges, in our naive case, map 1 to 1 to the actual edges
    surf_edges = b''
    for surf_edge in range(num_edges):
        surf_edges += pack("<i", surf_edge)

    print('convert surface edges (freebie)')
    new_bsp['surf_edges'] = {
        'elements': num_edges,
        'bytes': surf_edges,
        'size': 4,
    }

    print('convert faces')
    new_bsp['faces'] = {
        'elements': gbsp_faces.elements,
        'bytes': all_faces,
        'size': 56,
    }

    print('Conversion is done!')
    return new_bsp