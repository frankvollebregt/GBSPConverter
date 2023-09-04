import sys

from convert_obj import convert_to_obj
from gbsp_to_ibsp import read_gbsp_file


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
