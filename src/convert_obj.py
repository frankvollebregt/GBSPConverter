from math import ceil

from src.convert_obj_face import get_and_append_face
from src.gbsp import GBSPChunk
from src.textures import write_bitmap


def convert_to_obj(gbsp, out_path, folder_name):
    print('Converting...')

    # To create texture_info, we need textures and texture_info from the gbsp data
    gbsp_models: GBSPChunk = gbsp[1]
    gbsp_faces: GBSPChunk = gbsp[11]
    gbsp_tex: GBSPChunk = gbsp[18]
    gbsp_texdata: GBSPChunk = gbsp[19]
    gbsp_palettes: GBSPChunk = gbsp[23]

    all_lines = ['# Generated with GBSPConverter\n', '# https://www.github.com/frankvollebregt/GBSPConverter\n\n',
                 'mtllib ' + out_path.split('/')[-1] + '.mtl\n']
    vert_lines = ['# verts\n']
    norm_lines = ['# vert normals\n']
    tex_lines = ['# vert textures\n']
    face_lines = []
    vert_counter = 1
    norm_counter = 1
    tex_counter = 1
    last_tex_name = ''

    vert_map = {}
    norm_map = {}

    all_face_indices = set()

    for model_index in range(gbsp_models.elements):
        model_index += 1

        model_name = 'model_{}'.format(model_index)

        face_lines += ['\n\n# the {} object\n'.format(model_name), 'o  {}\n'.format(model_name)]

        model_offset = model_index * gbsp_models.size
        model_bytes = gbsp_models.bytes[model_offset:model_offset + gbsp_models.size]

        face_indices = []

        first_face = int.from_bytes(model_bytes[44:48], 'little')
        num_faces = int.from_bytes(model_bytes[48:52], 'little')

        for i in range(num_faces):
            face_indices.append(first_face + i)

        if len(face_indices) > 0:
            all_face_indices.update(face_indices)

            # retrieve the faces
            for face_index in face_indices:
                vert_map, vert_counter, vert_lines, \
                norm_map, norm_counter, norm_lines, \
                tex_counter, tex_lines, \
                face_lines, last_tex_name = get_and_append_face(
                    face_index, gbsp,
                    vert_map, vert_counter, vert_lines,
                    norm_map, norm_counter, norm_lines,
                    tex_counter, tex_lines,
                    face_lines, last_tex_name, True
                )
        else:
            print('empty object')

    # Now go through the remaining faces and add them to the main object as required
    face_lines += ['\n\n# the main object\n', 'o  main_structure\n']
    for face_index in range(gbsp_faces.elements):
        if face_index not in all_face_indices:
            vert_map, vert_counter, vert_lines, \
            norm_map, norm_counter, norm_lines, \
            tex_counter, tex_lines, \
            face_lines, last_tex_name = get_and_append_face(
                face_index, gbsp,
                vert_map, vert_counter, vert_lines,
                norm_map, norm_counter, norm_lines,
                tex_counter, tex_lines,
                face_lines, last_tex_name, True
            )

    mtl_lines = ['# Generated with GBSPConverter\n', '# https://www.github.com/frankvollebregt/GBSPConverter\n']
    for tex_index in range(gbsp_tex.elements):
        tex_offset = tex_index * gbsp_tex.size
        tex_bytes = gbsp_tex.bytes[tex_offset:tex_offset + gbsp_tex.size]
        tex_name = tex_bytes[0:32].decode('utf-8').rstrip('\x00')
        tex_width = int.from_bytes(tex_bytes[36:40], 'little')
        tex_height = int.from_bytes(tex_bytes[40:44], 'little')

        # Get data for the texture image
        tex_offset = int.from_bytes(tex_bytes[44:48], 'little')
        tex_palette_index = int.from_bytes(tex_bytes[48:52], 'little')

        mtl_lines += [
            '\nnewmtl {}\n'.format(tex_name),
            'Ka 1.0 1.0 1.0\n',
            'Kd 1.0 1.0 1.0\n',
            'Ks 0.0 0.0 0.0\n',
            'illum 1\n',
            'Ns 0.0\n',
            'Tr alpha\n',
            'map_Kd {}.tiff\n'.format(tex_name)
        ]

        # Get the texture data and palette, and write the image to a PNG image file
        tex_palette_offset = tex_palette_index * gbsp_palettes.size
        tex_palette_bytes = gbsp_palettes.bytes[tex_palette_offset:tex_palette_offset + gbsp_palettes.size]
        tex_data_bytes = gbsp_texdata.bytes[tex_offset:tex_offset + ceil(tex_width * tex_height * (85 / 64))]

        # Write the png image
        write_bitmap(my_bytes=tex_data_bytes, width=tex_width, height=tex_height, name=tex_name,
                     palette=tex_palette_bytes, folder=folder_name)

    # write the obj file
    print('Writing OBJ file to {}'.format(out_path + '.obj'))
    obj_file = open(out_path + '.obj', 'w')
    obj_file.writelines(all_lines)
    obj_file.writelines(vert_lines)
    obj_file.writelines(norm_lines)
    obj_file.writelines(tex_lines)
    obj_file.writelines(face_lines)
    obj_file.close()

    # write the material file
    print('Writing MTL file to {}'.format(out_path + '.mtl'))
    mtl_file = open(out_path + '.mtl', 'w')
    mtl_file.writelines(mtl_lines)
    mtl_file.close()
