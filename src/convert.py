import struct
from math import ceil

from gbsp import GBSPChunk
from struct import pack

from obj_helpers import access_bit
from textures import write_bitmap


# Convert the map of GBSP chunk objects to a map of IBSP data
def convert_to_ibsp(gbsp, folder_name):
    print('Converting...')
    new_bsp = {}

    # To create texture_info, we need textures and texture_info from the gbsp data
    gbsp_tex_info: GBSPChunk = gbsp[17]
    gbsp_tex: GBSPChunk = gbsp[18]

    gbsp_faces: GBSPChunk = gbsp[11]
    gbsp_verts: GBSPChunk = gbsp[14]
    gbsp_vert_index: GBSPChunk = gbsp[13]
    gbsp_planes: GBSPChunk = gbsp[10]
    gbsp_texdata: GBSPChunk = gbsp[19]
    gbsp_palette: GBSPChunk = gbsp[23]

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

    print('convert nodes')
    gbsp_nodes = gbsp[2]
    ibsp_nodes = b''
    for index in range(gbsp_nodes.elements):
        offset = index * gbsp_nodes.size

        cur_bytes = gbsp_nodes.bytes[offset:offset + gbsp_nodes.size]
        front_child = cur_bytes[0:4]
        back_child = cur_bytes[4:8]
        num_faces = int.from_bytes(cur_bytes[8:12], 'little')
        first_face = int.from_bytes(cur_bytes[12:16], 'little')
        plane_num = cur_bytes[16:20]
        min_x, min_y, min_z = struct.unpack('fff', cur_bytes[20:32])
        max_x, max_y, max_z = struct.unpack('fff', cur_bytes[32:44])

        ibsp_nodes += plane_num + front_child + back_child
        ibsp_nodes += pack("<hhhhhh", int(min_x), int(min_y), int(min_z), int(max_x), int(max_y), int(max_z))
        ibsp_nodes += pack("<hh", first_face, num_faces)

    new_bsp['nodes'] = {
        'elements': gbsp_nodes.elements,
        'bytes': ibsp_nodes,
        'size': 28,
    }

    print('\'convert\' models')
    model_faces = []
    gbsp_models = gbsp[1]

    yellow_faces = []
    for index in range(gbsp_models.elements):
        offset = index * gbsp_models.size
        cur_bytes = gbsp_models.bytes[offset:offset + gbsp_models.size]

        first_face = int.from_bytes(cur_bytes[44:48], 'little')
        num_faces = int.from_bytes(cur_bytes[48:52], 'little')

        if num_faces < 1000:
            for i in range(num_faces + 1):
                # print('{} + {} = {}'.format(first_face, i, first_face + i))
                model_faces.append(first_face + i)

                if index == 44:
                    print('face should be yellow {}'.format(first_face + i))
                    yellow_faces.append(first_face + i)
        else:
            print('from face {} there\'s a whopping {} faces!'.format(first_face, num_faces))

    print('write motions to .mot file')
    gbsp_motions: GBSPChunk = gbsp[24]
    if len(folder_name) > 0:
        folder = folder_name + '/'
    else:
        folder = folder_name
    with open(folder + 'motions.mot', 'wb') as motion_file:
        motion_file.write(gbsp_motions.bytes)

    print('write entities to .txt file')
    gbsp_ents: GBSPChunk = gbsp[16]
    if len(folder_name) > 0:
        folder = folder_name + '/'
    else:
        folder = folder_name
    with open(folder + 'entities.txt', 'wb') as ent_file:
        ent_file.write(gbsp_ents.bytes)

    print('convert leafs')
    gbsp_leafs = gbsp[4]
    ibsp_leafs = b''
    invis_leaf_faces = []
    for index in range(gbsp_leafs.elements):
        offset = index * gbsp_leafs.size
        cur_bytes = gbsp_leafs.bytes[offset:offset + gbsp_leafs.size]

        contents = cur_bytes[0:4]
        # TODO somehow use the content to determine whether or not the faces in this leaf should be displayed
        content_bits = [access_bit(contents, i) for i in range(len(contents) * 8)]

        min_x, min_y, min_z = struct.unpack('fff', cur_bytes[4:16])
        max_x, max_y, max_z = struct.unpack('fff', cur_bytes[16:28])
        first_face = int.from_bytes(cur_bytes[28:32], 'little')
        num_faces = int.from_bytes(cur_bytes[32:36], 'little')
        first_portal = cur_bytes[36:40]
        num_portals = cur_bytes[40:44]
        cluster = cur_bytes[44:48]
        area = cur_bytes[48:52]
        first_side = cur_bytes[52:56]
        num_sides = cur_bytes[56:60]

        # if content_bits[0] != 1 and content_bits[1] != 1 and content_bits[6] != 1:
        # if content_bits[3] == 1:
        #     for i in range(num_faces + 1):
        #         print('{} + {} = {}'.format(first_face, i, first_face + i))
        #         invis_leaf_faces.append(first_face + i)

        ibsp_leafs += pack("<Ihh", 0, 0, 0)
        ibsp_leafs += pack("<hhhhhh", int(min_x), int(min_y), int(min_z), int(max_x), int(max_y), int(max_z))
        ibsp_leafs += pack("<HH", first_face, num_faces)
        ibsp_leafs += pack("<HH", 0, 0)

    new_bsp['leafs'] = {
        'elements': gbsp_leafs.elements,
        'bytes': ibsp_leafs,
        'size': 28,
    }

    print('convert leaf faces (1 to 1)')
    gbsp_leaf_faces = gbsp[12]
    ibsp_leaf_faces = b''
    invis_faces = []
    for index in range(gbsp_leaf_faces.elements):
        offset = index * gbsp_leaf_faces.size
        face_index = int.from_bytes(gbsp_leaf_faces.bytes[offset:offset + gbsp_leaf_faces.size], 'little', signed=True)
        if index in invis_leaf_faces:
            invis_faces.append(face_index)
        ibsp_leaf_faces += pack("<H", face_index)

    new_bsp['leaf_faces'] = {
        'elements': gbsp_leaf_faces.elements,
        'bytes': ibsp_leaf_faces,
        'size': 2,
    }

    print('converting faces and constructing edges')
    invis_texinfo = []
    for face_index in range(gbsp_faces.elements):
        # face_index = 0
        offset = face_index * gbsp_faces.size
        cur_bytes = gbsp_faces.bytes[offset:offset + gbsp_faces.size]

        # read info from the GBSP face
        first_vert_index = int.from_bytes(cur_bytes[0:4], 'little')
        num_verts = int.from_bytes(cur_bytes[4:8], 'little')
        plane = int.from_bytes(cur_bytes[8:12], 'little')
        plane_side = int.from_bytes(cur_bytes[12:16], 'little')
        tex_info = int.from_bytes(cur_bytes[16:20], 'little')

        # if face_index in yellow_faces:
        #     # replace texture with yellow
        #     print('making face {} yellow'.format(face_index))
        #     tex_info = 975

        # now that we know the index of the vertex, we can get the vertex indices and use those to create
        # the edges
        vert_index_indices = [first_vert_index + j for j in range(num_verts)]
        # TODO be smarter about this, to prevent duplicates?
        for index in range(len(vert_index_indices)):
            if index == 0:
                # first edge, store it to use in the face
                first_edge_index = int(len(all_edges) / 4)
            vert_index_a = gbsp_vert_index.bytes[4 * vert_index_indices[index]:4 * vert_index_indices[index] + 4]
            dest = (index + 1) % len(vert_index_indices)
            vert_index_b = gbsp_vert_index.bytes[4 * vert_index_indices[dest]:4 * vert_index_indices[dest] + 4]
            point_a = int.from_bytes(vert_index_a, 'little')
            point_b = int.from_bytes(vert_index_b, 'little')
            all_edges += pack("<hh", point_a, point_b)

        # Now store the face in the all_faces list
        all_faces += pack("<HHIHHII", plane, plane_side, first_edge_index, num_verts, tex_info, 0, 0)

    print('convert edges')
    num_edges = int(len(all_edges) / 4)
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

    print('convert texture info (with textures as well!)')
    texture_info = b''

    for index in range(gbsp_tex_info.elements):
        offset = index * gbsp_tex_info.size

        cur_bytes = gbsp_tex_info.bytes[offset:offset + gbsp_tex_info.size]
        u_x, u_y, u_z = struct.unpack('fff', cur_bytes[0:12])
        v_x, v_y, v_z = struct.unpack('fff', cur_bytes[12:24])
        u_offset = struct.unpack('f', cur_bytes[24:28])[0]
        v_offset = struct.unpack('f', cur_bytes[28:32])[0]
        u_scale = struct.unpack('f', cur_bytes[32:36])[0]
        v_scale = struct.unpack('f', cur_bytes[36:40])[0]
        tex_info_flags = cur_bytes[40:44]
        alpha = struct.unpack('f', cur_bytes[56:60])[0]
        texture = int.from_bytes(cur_bytes[60:64], 'little')

        # grab the texture name
        tex_bytes = gbsp_tex.bytes[texture * gbsp_tex.size:(texture + 1) * gbsp_tex.size]
        texture_name = tex_bytes[0:32]
        tex_flags = tex_bytes[32:36]
        tex_width = tex_bytes[36:40]
        tex_height = tex_bytes[40:44]
        tex_offset = int.from_bytes(tex_bytes[44:48], 'little')

        # read the correct palette for the texture
        tex_palette_index = int.from_bytes(tex_bytes[48:52], 'little')
        tex_palette = gbsp_palette.bytes[
                      gbsp_palette.size * tex_palette_index:gbsp_palette.size * (tex_palette_index + 1)]

        # write the texture bitmap file
        tex_bytes = gbsp_texdata.bytes[tex_offset:tex_offset + ceil(
            int.from_bytes(tex_width, 'little') * int.from_bytes(tex_height, 'little') * (85 / 64))]
        has_transparency = write_bitmap(my_bytes=tex_bytes, width=int.from_bytes(tex_width, 'little'),
                                        height=int.from_bytes(tex_height, 'little'),
                                        name=texture_name.decode('utf-8').rstrip('\x00'), palette=tex_palette,
                                        folder=folder_name)

        flag_bits = [access_bit(tex_info_flags, i) for i in range(len(tex_info_flags) * 8)]
        is_invisible = flag_bits[2] == 1 or (flag_bits[4] == 1 and not has_transparency)
        # bit at index 2 denotes empty (sky) throughout the level
        # bit at index 4 denotes portals/hitboxes
        # but also water throughout the level, and part of the tree canopy (for some reason)

        # replace the texture info with yellow texture info if the face is not visible
        # if not is_invisible:
        texture_info += pack('<fff', u_x / u_scale, u_y / u_scale, u_z / u_scale) + pack('<f', u_offset) + pack(
            '<fff', v_x / v_scale, v_y / v_scale, v_z / v_scale) + pack('<f', v_offset) + tex_info_flags + pack(
            "<I", 0)

        if texture_name.decode('utf-8').rstrip('\x00') == 'redP':
            print('---')
            print('u axis: {}, {}, {} (scale was {}, offset was {})'.format(u_x / u_scale, u_y / u_scale, u_z / u_scale, u_scale, u_offset))
            print('v axis: {}, {}, {} (scale was {},  offset was {})'.format(v_x / v_scale, v_y / v_scale, v_z / v_scale, v_scale, v_offset))

        texture_info += texture_name
        texture_info += pack("<I", 0)
        # else:
        #     with open('tex/ylw.bin', 'rb') as bin_file:
        #         tex_info_binary = bin_file.read()
        #         texture_info += tex_info_binary

    new_bsp['texture_info'] = {
        'elements': gbsp_tex_info.elements,
        'bytes': texture_info,
        'size': 76,
    }

    print('Conversion is done!')

    return new_bsp
