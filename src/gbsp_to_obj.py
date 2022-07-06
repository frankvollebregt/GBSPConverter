import sys

from convert_obj import convert_to_obj
from gbsp import GBSPChunk


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
        print('Usage: python gbsp_to_obj.py [(optional: output_filename.obj)]')
        exit(-1)

    path = sys.argv[1]
    gbsp = read_gbsp_file(path)

    out_path = path.split('.')[0]
    if len(sys.argv) >= 3:
        out_path = sys.argv[2].split('.')[0]

    # output to the correct folder
    if '/' in out_path:
        folder_name = out_path[:out_path.rindex('/')]
    else:
        folder_name = ''

    path = sys.argv[1]
    gbsp = read_gbsp_file(path)

    convert_to_obj(gbsp, out_path, folder_name)
