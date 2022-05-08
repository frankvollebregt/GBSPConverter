from gbsp import GBSPChunk
from struct import pack
from read_ibsp import IBSP_TYPES
from convert import convert_to_vbsp
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
        print('Usage: python gbsp_to_vbsp.py [filename.bsp] [(optional: output_filename.bsp)]')
        exit(-1)

    path = sys.argv[1]
    gbsp = read_gbsp_file(path)

    print('Warning! The output of this converter is not tested yet!')

    # convert GBSP data to the correct IBSP data
    vbsp_data = convert_to_vbsp(gbsp)

    print("VBSP lumps to write: " + "".join([key + ', ' for key, value in vbsp_data.items()]))

    out_path = path.split('.')[0] + '_vbsp.' + path.split('.')[1]
    if len(sys.argv) >= 3:
        out_path = sys.argv[2]

    out_file = open(out_path, 'w+b')
    print('writing results to {}'.format(out_path))

    # first, write the header
    out_file.write(bytearray('VBSP', 'utf8'))            # identifier
    out_file.write(pack("<I", 20))     # version

    # then, write the lumps
    # keep track of the pointer where we can put the next one
    pointer = 1036   # start after the header, which is always 1036 bytes
    bytes_to_write = []
    for i in range(64):
        if i == 1:  # planes
            planes = vbsp_data['planes']
            out_file.write(pack("<iiiI", pointer, planes['size'] * planes['elements'], 0, 0))
            pointer += planes['size'] * planes['elements']
            bytes_to_write.append(planes['bytes'])
            print("wrote {} planes ({} bytes)".format(planes['elements'], len(planes['bytes'])))
        elif i == 3:
            verts = vbsp_data['vertices']
            out_file.write(pack("<iiiI", pointer, verts['size'] * verts['elements'], 0, 0))
            pointer += verts['size'] * verts['elements']
            bytes_to_write.append(verts['bytes'])
            print("wrote {} verts ({} bytes)".format(verts['elements'], len(verts['bytes'])))
        elif i == 7:
            faces = vbsp_data['faces']
            out_file.write(pack("<iiiI", pointer, faces['size'] * faces['elements'], 0, 0))
            pointer += faces['size'] * faces['elements']
            bytes_to_write.append(faces['bytes'])
            print("wrote {} faces ({} bytes)".format(faces['elements'], len(faces['bytes'])))
        elif i == 12:
            edges = vbsp_data['edges']
            out_file.write(pack("<iiiI", pointer, edges['size'] * edges['elements'], 0, 0))
            pointer += edges['size'] * edges['elements']
            bytes_to_write.append(edges['bytes'])
            print("wrote {} edges ({} bytes)".format(edges['elements'], len(edges['bytes'])))
        elif i == 13:
            surf_edges = vbsp_data['surf_edges']
            out_file.write(pack("<iiiI", pointer, surf_edges['size'] * surf_edges['elements'], 0, 0))
            pointer += surf_edges['size'] * surf_edges['elements']
            bytes_to_write.append(surf_edges['bytes'])
            print("wrote {} face_edges ({} bytes)".format(surf_edges['elements'], len(surf_edges['bytes'])))
        else:
            # don't include this lump, set offset and length 0
            out_file.write(pack("<iiiI", 0, 0, 0, 0))

    # map version is always 1
    out_file.write(pack("<I", 1))

    # write all the lump data
    for byte_group in bytes_to_write:
        out_file.write(byte_group)

    out_file.close()
