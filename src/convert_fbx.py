from math import ceil
import re
import FbxCommon
import sys

from fbx import *
from src.convert_fbx_face import get_and_append_face_fbx
from src.gbsp import GBSPChunk
from textures import write_bitmap


def convert_to_fbx(gbsp, out_path, folder_name, use_entity_chunk = False):
    print('Converting...')

    # To create texture_info, we need textures and texture_info from the gbsp data
    gbsp_models: GBSPChunk = gbsp[1]
    gbsp_tex: GBSPChunk = gbsp[18]
    gbsp_texdata: GBSPChunk = gbsp[19]
    gbsp_palettes: GBSPChunk = gbsp[23]

    (lSdkManager, lScene) = FbxCommon.InitializeSdkObjects()

    lSceneInfo = FbxDocumentInfo.Create(lSdkManager, "SceneInfo")
    lSceneInfo.mTitle = "Test Scene"
    lSceneInfo.mAuthor = "GBSPConverter"
    lSceneInfo.mComment = "https://www.github.com/frankvollebregt/GBSPConverter"
    lScene.SetSceneInfo(lSceneInfo)

    all_face_indices = set()

    print('Creating Textures...')
    materials = []
    tex_names = []
    for tex_index in range(gbsp_tex.elements):
        tex_offset = tex_index * gbsp_tex.size
        tex_bytes = gbsp_tex.bytes[tex_offset:tex_offset + gbsp_tex.size]
        tex_name = tex_bytes[0:32].decode('utf-8').rstrip('\x00')
        tex_width = int.from_bytes(tex_bytes[36:40], 'little')
        tex_height = int.from_bytes(tex_bytes[40:44], 'little')

        # Get data for the texture image
        tex_offset = int.from_bytes(tex_bytes[44:48], 'little')
        tex_palette_index = int.from_bytes(tex_bytes[48:52], 'little')

        # Get the texture data and palette, and write the image to a PNG image file
        tex_palette_offset = tex_palette_index * gbsp_palettes.size
        tex_palette_bytes = gbsp_palettes.bytes[tex_palette_offset:tex_palette_offset + gbsp_palettes.size]
        tex_data_bytes = gbsp_texdata.bytes[tex_offset:tex_offset + ceil(tex_width * tex_height * (85 / 64))]

        # Write the png image
        write_bitmap(my_bytes=tex_data_bytes, width=tex_width, height=tex_height, name=tex_name + '_tex',
                     palette=tex_palette_bytes, folder=folder_name)

        lTexture = FbxFileTexture.Create(lSdkManager, "")
        lTexture.SetFileName('{}_tex.png'.format(tex_name))
        lTexture.SetMappingType(FbxTexture.eUV)
        lTexture.SetTextureUse(FbxTexture.eStandard)

        lMaterial = FbxSurfacePhong.Create(lSdkManager, tex_name + '_mat')
        lMaterial.Diffuse.ConnectSrcObject(lTexture)
        lMaterial.SpecularFactor.Set(0)

        materials.append(lMaterial)
        tex_names.append(tex_name)

    entity_lines = []
    if use_entity_chunk is True:
        entities = str(gbsp[16].bytes, 'cp1252')
        entity_lines = entities.split('\n')

    motions = {}
    motion_lines = gbsp[24].bytes.decode('utf-8').split('\n')
    iterator = 1
    num_motions = int(motion_lines[iterator].split(' ')[1])

    for i in range(num_motions):
        iterator += 1
        model_number = int(motion_lines[iterator].split(' ')[1])
        current_line = motion_lines[iterator]
        while not 'PathArray' in current_line:
            iterator += 1
            current_line = motion_lines[iterator]

        iterator += 4
        rotations = [list(map(lambda x: float(x), motion_lines[iterator].split(' '))), list(map(lambda x: float(x), motion_lines[iterator+1].split(' ')))]
        iterator += 4
        translations = [list(map(lambda x: float(x), motion_lines[iterator].split(' '))), list(map(lambda x: float(x), motion_lines[iterator+1].split(' ')))]

        motions[model_number] = {
            'rotations': rotations,
            'translations': translations
        }
        iterator += 1
    print(motions)

    current_origin = [0.0, 0.0, 0.0]

    for model_index in range(gbsp_models.elements):

        if model_index == 0:
            continue

        if use_entity_chunk is True and entity_lines is not []:
            match = re.findall(r'(?<=%name%)[^a-z0-9_]*([a-z0-9_]+).*origin.*?(-{0,1}\d+\.\d+).*?(-{0,1}\d+\.\d+).*?(-{0,1}\d+\.\d+).*?(?<!%).*Model(?!%)\D*(\d+)', entity_lines[model_index])
            if len(match) > 0 and len(match[0]) == 5:
                model_name = match[0][0]
            elif len(match) > 0 and len(match[0]) == 4:
                model_name = 'model_{}'.format(match[0][3])
            elif model_index == 0:
                model_name = 'main_structure'
            else:
                model_name = 'model_{}'.format(model_index)

            if len(match) > 0:
                current_origin = [float(match[0][1]), float(match[0][2]), float(match[0][3])]
            else:
                current_origin = [0.0, 0.0, 0.0]
        else:
            model_name = 'model_{}'.format(model_index)

        print('handling model {}/{} ({})'.format(model_index+1, gbsp_models.elements, model_name))

        lMesh = FbxMesh.Create(lSdkManager, model_name)
        lMesh.CreateLayer()
        lLayer = lMesh.GetLayer(0)

        # Different variables are tracked while adding all values for this mesh
        vertex_array = []
        normal_array = []
        uv_array = []
        polygons = []

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
                vertex_array, normal_array, uv_array, polygons = get_and_append_face_fbx(gbsp, face_index, tex_names,
                                                                                         vertex_array, normal_array,
                                                                                         uv_array, polygons)
        else:
            print('empty object')

        # Add all vertices to the mesh
        lMesh.InitControlPoints(len(vertex_array))
        for i in range(len(vertex_array)):
            lMesh.SetControlPointAt(vertex_array[i], i)

        lLayerElementNormal = FbxLayerElementNormal.Create(lMesh, "")
        lLayerElementNormal.SetMappingMode(FbxLayerElement.eByPolygon)
        lLayerElementNormal.SetReferenceMode(FbxLayerElement.eIndexToDirect)

        for i in range(len(normal_array)):
            lLayerElementNormal.GetDirectArray().Add(normal_array[i])

        lMaterialLayer = FbxLayerElementMaterial.Create(lMesh, "")
        lMaterialLayer.SetMappingMode(FbxLayerElement.eByPolygon)
        lMaterialLayer.SetReferenceMode(FbxLayerElement.eIndexToDirect)
        lLayer.SetMaterials(lMaterialLayer)

        # TODO smartly add to the direct array for the materials

        lUVDiffuseLayer = FbxLayerElementUV.Create(lMesh, "DiffuseUV")
        lUVDiffuseLayer.SetMappingMode(FbxLayerElement.eByPolygonVertex)
        lUVDiffuseLayer.SetReferenceMode(FbxLayerElement.eIndexToDirect)
        lLayer.SetUVs(lUVDiffuseLayer, FbxLayerElement.eTextureDiffuse)

        for i in range(len(uv_array)):
            lUVDiffuseLayer.GetDirectArray().Add(uv_array[i])

        # Add all polygons to the mesh
        for polygon in polygons:
            # [texture_index, polygon_vertices, norm_index, uv_indices]
            lMesh.BeginPolygon(polygon[0])
            lLayerElementNormal.GetIndexArray().Add(polygon[2])
            for index in polygon[1]:
                lMesh.AddPolygon(index)
            lMesh.EndPolygon()

            for uv in polygon[3]:
                lUVDiffuseLayer.GetIndexArray().Add(uv)

        # Add and connect mesh node
        lMeshNode = FbxNode.Create(lSdkManager, model_name)

        for material in materials:
            lMeshNode.AddMaterial(material)

        if model_index in motions:
            motion = motions[model_index]

            animation_stack = FbxAnimStack.Create(lScene, "Animations")
            animation_layer = FbxAnimLayer.Create(lScene, model_name + "_animation")

            time = FbxTime()

            trans_x = lMeshNode.LclTranslation.GetCurve(animation_layer, "X", True)
            trans_y = lMeshNode.LclTranslation.GetCurve(animation_layer, "Y", True)
            trans_z = lMeshNode.LclTranslation.GetCurve(animation_layer, "Z", True)

            rot_x = lMeshNode.LclRotation.GetCurve(animation_layer, "X", True)
            rot_y = lMeshNode.LclRotation.GetCurve(animation_layer, "Y", True)
            rot_z = lMeshNode.LclRotation.GetCurve(animation_layer, "Z", True)

            # Handle translation
            trans_x.KeyModifyBegin()
            trans_y.KeyModifyBegin()
            trans_z.KeyModifyBegin()
            for keyframe in motion['translations']:
                time.SetSecondDouble(keyframe[0])
                x_index = trans_x.KeyAdd(time)[0]
                y_index = trans_y.KeyAdd(time)[0]
                z_index = trans_z.KeyAdd(time)[0]

                trans_x.KeySetValue(x_index, keyframe[1])
                trans_y.KeySetValue(y_index, keyframe[2])
                trans_z.KeySetValue(z_index, keyframe[3])
            trans_x.KeyModifyEnd()
            trans_y.KeyModifyEnd()
            trans_z.KeyModifyEnd()

            # Handle rotation
            lMeshNode.SetPivotState(FbxNode.eSourcePivot, FbxNode.ePivotActive)
            print(current_origin)
            lMeshNode.SetRotationPivot(FbxNode.eSourcePivot, FbxVector4(current_origin[0], current_origin[1], current_origin[2]))

            # TODO also handle rotation over the X and Z axes correctly
            rot_x.KeyModifyBegin()
            rot_y.KeyModifyBegin()
            rot_z.KeyModifyBegin()
            for keyframe in motion['rotations']:
                time.SetSecondDouble(keyframe[0])
                x_index = rot_x.KeyAdd(time)[0]
                y_index = rot_y.KeyAdd(time)[0]
                z_index = rot_z.KeyAdd(time)[0]

                fq = FbxQuaternion(keyframe[1], keyframe[2], keyframe[3], keyframe[4])

                mat = FbxAMatrix()
                mat.SetQ(fq)
                vec = mat.GetR()

                if 'knopdeur' in model_name:
                    print(vec)

                # rot_x.KeySetValue(x_index, vec[0])
                rot_y.KeySetValue(y_index, vec[1])
                # rot_z.KeySetValue(z_index, vec[2])

            rot_x.KeyModifyEnd()
            rot_y.KeyModifyEnd()
            rot_z.KeyModifyEnd()

            animation_stack.AddMember(animation_layer)

        lMeshNode.SetNodeAttribute(lMesh)
        lMeshNode.SetShadingMode(FbxNode.eTextureShading)
        lScene.GetRootNode().AddChild(lMeshNode)

    output_other_files(gbsp, out_path)

    print('Writing FBX file to {}'.format(out_path + '.fbx'))
    FbxCommon.SaveScene(lSdkManager, lScene, out_path + '.fbx', 0, True)


def output_other_files(gbsp, out_path):
    with open(out_path + '_motions.txt', 'wb') as motion_file:
        motion_file.write(gbsp[24].bytes)

    with open(out_path + '_models.bin', 'wb') as models_file:
        models_file.write(gbsp[1].bytes)

    entities = str(gbsp[16].bytes, 'cp1252')
    entity_lines = entities.split('\n')

    # for line in lines:
    #     print(re.findall(r'(?<=%name%)[^a-z0-9]*([a-z0-9]+).*(?<!%)Model(?!%)\D*(\d+)', line))
    #
    # entity_lines
    #
    # print(model_names)
    # for line in lines:
    #     if 'Model' in line:
    #         print('Model {}'.format(line[len(line)-1]))
    # with open(out_path + '_entities.txt', 'wb') as entities_file:
    #     entities_file.write(gbsp[16].bytes)
