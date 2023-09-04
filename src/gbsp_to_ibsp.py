from gbsp import GBSPChunk
from struct import pack
from read_ibsp import IBSP_TYPES
from convert import convert_to_ibsp
import sys


# Read a GBSP header and bytes, and put them into a GBSPChunk object
def read_gbsp_chunk(f):
    gbsp_bytes = f.read(12)
    chunk = GBSPChunk.from_bytes(gbsp_bytes)
    chunk.read_bytes(f)
    return chunk


# Read the GBSP file, adding each chunk to a map
def read_gbsp_file(path):
    gbsp = {}
    file = open(path, 'rb')
    current_chunk = read_gbsp_chunk(file)
    while current_chunk.type_string() != 'GBSP_CHUNK_END':
        gbsp[current_chunk.type] = current_chunk
        current_chunk = read_gbsp_chunk(file)
    file.close()

    return gbsp


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python gbsp_to_ibsp.py [filename.bsp] [(optional: output_filename.bsp)]')
        exit(-1)

    path = sys.argv[1]
    gbsp = read_gbsp_file(path)

    print('# of motions: {} (of size {})'.format(gbsp[24].elements, gbsp[24].size))

    print('{}, {}, {}'.format(gbsp[23].elements, gbsp[23].size, gbsp[23].type))

    out_path = path.split('.')[0] + '_ibsp.' + path.split('.')[1]
    if len(sys.argv) >= 3:
        out_path = sys.argv[2]

    # output to the correct folder
    if '/' in out_path:
        folder_name = out_path[:out_path.rindex('/')]
    else:
        folder_name = ''

    # convert GBSP data to the correct IBSP data
    ibsp_data = convert_to_ibsp(gbsp, folder_name=folder_name)

    print("IBSP lumps to write: " + "".join([key + ', ' for key, value in ibsp_data.items()]))

    out_file = open(out_path, 'w+b')
    print('writing results to {}'.format(out_path))

    # first, write the header
    out_file.write(bytearray('IBSP', 'utf8'))            # identifier
    out_file.write(pack("<I", 38))     # version

    # then, write the lumps
    # keep track of the pointer where we can put the next one
    pointer = 160   # start after the header, which is always 160 bytes
    bytes_to_write = []
    for i in range(19):
        if IBSP_TYPES[i] == 'IBSP_PLANES':
            planes = ibsp_data['planes']
            out_file.write(pack("<II", pointer, planes['size'] * planes['elements']))
            pointer += planes['size'] * planes['elements']
            bytes_to_write.append(planes['bytes'])
            print("wrote {} planes ({} bytes)".format(planes['elements'], len(planes['bytes'])))
        elif IBSP_TYPES[i] == 'IBSP_VERTICES':
            verts = ibsp_data['vertices']
            out_file.write(pack("<II", pointer, verts['size'] * verts['elements']))
            pointer += verts['size'] * verts['elements']
            bytes_to_write.append(verts['bytes'])
            print("wrote {} verts ({} bytes)".format(verts['elements'], len(verts['bytes'])))
        elif IBSP_TYPES[i] == 'IBSP_FACES':
            faces = ibsp_data['faces']
            out_file.write(pack("<II", pointer, faces['size'] * faces['elements']))
            pointer += faces['size'] * faces['elements']
            bytes_to_write.append(faces['bytes'])
            print("wrote {} faces ({} bytes)".format(faces['elements'], len(faces['bytes'])))
        elif IBSP_TYPES[i] == 'IBSP_EDGES':
            edges = ibsp_data['edges']
            out_file.write(pack("<II", pointer, edges['size'] * edges['elements']))
            pointer += edges['size'] * edges['elements']
            bytes_to_write.append(edges['bytes'])
            print("wrote {} edges ({} bytes)".format(edges['elements'], len(edges['bytes'])))
        elif IBSP_TYPES[i] == 'IBSP_FACE_EDGE_TABLE':
            face_edges = ibsp_data['face_edges']
            out_file.write(pack("<II", pointer, face_edges['size'] * face_edges['elements']))
            pointer += face_edges['size'] * face_edges['elements']
            bytes_to_write.append(face_edges['bytes'])
            print("wrote {} face_edges ({} bytes)".format(face_edges['elements'], len(face_edges['bytes'])))
        elif IBSP_TYPES[i] == 'IBSP_TEXTURE_INFORMATION':
            texture_info = ibsp_data['texture_info']
            out_file.write(pack("<II", pointer, texture_info['size'] * texture_info['elements']))
            pointer += texture_info['size'] * texture_info['elements']
            bytes_to_write.append(texture_info['bytes'])
            print("wrote {} texture_info ({} bytes)".format(texture_info['elements'], len(texture_info['bytes'])))
        elif IBSP_TYPES[i] == 'IBSP_NODES':
            nodes = ibsp_data['nodes']
            out_file.write(pack("<II", pointer, nodes['size'] * nodes['elements']))
            pointer += nodes['size'] * nodes['elements']
            bytes_to_write.append(nodes['bytes'])
            print("wrote {} nodes ({} bytes)".format(nodes['elements'], len(nodes['bytes'])))
        elif IBSP_TYPES[i] == 'IBSP_LEAVES':
            leafs = ibsp_data['leafs']
            out_file.write(pack("<II", pointer, leafs['size'] * leafs['elements']))
            pointer += leafs['size'] * leafs['elements']
            bytes_to_write.append(leafs['bytes'])
            print("wrote {} leafs ({} bytes)".format(leafs['elements'], len(leafs['bytes'])))
        elif IBSP_TYPES[i] == 'IBSP_LEAF_FACE_TABLE':
            leaf_faces = ibsp_data['leaf_faces']
            out_file.write(pack("<II", pointer, leaf_faces['size'] * leaf_faces['elements']))
            pointer += leaf_faces['size'] * leaf_faces['elements']
            bytes_to_write.append(leaf_faces['bytes'])
            print("wrote {} leaf_faces ({} bytes)".format(leaf_faces['elements'], len(leaf_faces['bytes'])))
        else:
            # don't include this lump, set offset and length 0
            out_file.write(pack("<II", 0, 0))

    # write all the lump data
    for byte_group in bytes_to_write:
        out_file.write(byte_group)

    out_file.close()
