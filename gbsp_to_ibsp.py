from bsp import GBSPChunk
from struct import pack
from main_quake import IBSP_TYPES
from full_test import convert_to_ibsp_full
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
        print('Usage: python gbsp_to_ibsp.py [filename.bsp]')

    path = sys.argv[1]
    gbsp = read_gbsp_file(path)

    # convert GBSP data to the correct IBSP data
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
