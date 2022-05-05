from bsp import BSPChunk
from struct import pack
from main_quake import IBSP_TYPES


def read_gbsp_chunk(f):
    gbsp_bytes = f.read(12)
    chunk = BSPChunk.from_bytes(gbsp_bytes)
    chunk.read_bytes(f)
    return chunk


if __name__ == '__main__':
    # file = open('test.bsp', 'rb')
    #
    # chunks = []
    # gbsp = {}
    #
    # current_chunk = read_gbsp_chunk(file)
    # while current_chunk.type_string() != 'GBSP_CHUNK_END':
    #     chunks.append(current_chunk)
    #     gbsp[current_chunk.type] = current_chunk
    #     print(current_chunk)
    #     current_chunk = read_gbsp_chunk(file)
    #
    # file.close()
    #
    # print(gbsp)

    out_file = open('bsp/test_quake_single.bsp', 'wb')

    # first, write the header
    out_file.write(b'IBSP')            # identifier
    out_file.write(pack("<I", 38))     # version

    # then, write the lumps
    # keep track of where we can put the next one
    pointer = 160
    bytes_to_write = []
    for i in range(19):
        if IBSP_TYPES[i] == 'IBSP_PLANES':
            planes_file = open('test/plane.bin', 'rb')
            planes = planes_file.read()
            out_file.write(pack("<II", pointer, 20*1))
            pointer += 20*1
            bytes_to_write.append(planes)
        elif IBSP_TYPES[i] == 'IBSP_VERTICES':
            verts_file = open('test/verts.bin', 'rb')
            verts = verts_file.read()
            out_file.write(pack("<II", pointer, 12*3))
            pointer += 12*3
            bytes_to_write.append(verts)
        elif IBSP_TYPES[i] == 'IBSP_FACES':
            faces_file = open('test/face.bin', 'rb')
            faces = faces_file.read()
            out_file.write(pack("<II", pointer, 20 * 1))
            pointer += 20 * 1
            bytes_to_write.append(faces)
        elif IBSP_TYPES[i] == 'IBSP_EDGES':
            edge_file = open('test/edge.bin', 'rb')
            edges = edge_file.read()
            out_file.write(pack("<II", pointer, 4 * 3))
            pointer += 4 * 3
            bytes_to_write.append(edges)
        elif IBSP_TYPES[i] == 'IBSP_FACE_EDGE_TABLE':
            face_edge_file = open('test/face_edge.bin', 'rb')
            face_edges = face_edge_file.read()
            out_file.write(pack("<II", pointer, 4 * 3))
            pointer += 4 * 3
            bytes_to_write.append(face_edges)
        elif IBSP_TYPES[i] == 'IBSP_TEXTURE_INFORMATION':
            texture_file = open('test/tex.bin', 'rb')
            textures = texture_file.read()
            out_file.write(pack("<II", pointer, 76 * 1))
            pointer += 76 * 1
            bytes_to_write.append(textures)
        else:
            # don't include this, keep offset and length 0
            out_file.write(pack("<II", 0, 0))

    # write plane
    for byte_group in bytes_to_write:
        out_file.write(byte_group)

    out_file.close()
