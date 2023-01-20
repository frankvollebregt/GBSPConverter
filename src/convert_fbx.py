from math import ceil

from src.convert_fbx_face import get_and_append_face_fbx
from src.gbsp import GBSPChunk
import FbxCommon
from fbx import *
from textures import write_bitmap


def convert_to_fbx(gbsp, out_path, folder_name):
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
        write_bitmap(my_bytes=tex_data_bytes, width=tex_width, height=tex_height, name=tex_name+'_tex',
                     palette=tex_palette_bytes, folder=folder_name)

        lTexture = FbxFileTexture.Create(lSdkManager, "")
        lTexture.SetFileName('{}_tex.tiff'.format(tex_name))
        lTexture.SetMappingType(FbxTexture.eUV)
        lTexture.SetTextureUse(FbxTexture.eStandard)

        lMaterial = FbxSurfacePhong.Create(lSdkManager, tex_name+'_mat')
        lMaterial.Diffuse.ConnectSrcObject(lTexture)

        materials.append(lMaterial)
        tex_names.append(tex_name)

    for model_index in range(gbsp_models.elements):
        model_index += 1

        print('handling model {}/{}'.format(model_index, gbsp_models.elements))

        # if model_index != 20:
        #     continue

        model_name = 'model_{}'.format(model_index)

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
                vertex_array, normal_array, uv_array, polygons = get_and_append_face_fbx(gbsp, face_index, tex_names, vertex_array, normal_array, uv_array, polygons)
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
            lMesh.BeginPolygon(polygon.texture_index)
            lLayerElementNormal.GetIndexArray().Add(polygon.normal_index)
            for index in polygon.vert_indices:
                lMesh.AddPolygon(index)
            lMesh.EndPolygon()

            for uv in polygon.uvs:
                lUVDiffuseLayer.GetIndexArray().Add(uv)

        # Add and connect mesh node
        lMeshNode = FbxNode.Create(lSdkManager, model_name)
        lMeshNode.SetNodeAttribute(lMesh)

        for material in materials:
            lMeshNode.AddMaterial(material)

        lScene.GetRootNode().AddChild(lMeshNode)

    model_name = 'main_structure'

    lMesh = FbxMesh.Create(lSdkManager, model_name)
    lMesh.CreateLayer()
    lLayer = lMesh.GetLayer(0)

    # Different variables are tracked while adding all values for this mesh
    vertex_array = []
    normal_array = []
    uv_array = []
    polygons = []

    model_offset = 0
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
                                                                                     uv_array, polygons, True)
    else:
        print('empty object')

    # Add all vertices to the mesh
    lMesh.InitControlPoints(len(vertex_array))
    for i in range(len(vertex_array)):
        lMesh.SetControlPointAt(vertex_array[i], i)

    lLayerElementNormal = FbxLayerElementNormal.Create(lMesh, "LayerNormal")
    lLayerElementNormal.SetMappingMode(FbxLayerElement.eByPolygon)
    lLayerElementNormal.SetReferenceMode(FbxLayerElement.eIndexToDirect)

    for i in range(len(normal_array)):
        lLayerElementNormal.GetDirectArray().Add(normal_array[i])

    lMaterialLayer = FbxLayerElementMaterial.Create(lMesh, "LayerMaterial")
    lMaterialLayer.SetMappingMode(FbxLayerElement.eByPolygon)
    lMaterialLayer.SetReferenceMode(FbxLayerElement.eIndexToDirect)
    lLayer.SetMaterials(lMaterialLayer)

    # TODO smartly add to the direct array for the materials

    lUVDiffuseLayer = FbxLayerElementUV.Create(lMesh, "LayerUV")
    lUVDiffuseLayer.SetMappingMode(FbxLayerElement.eByPolygonVertex)
    lUVDiffuseLayer.SetReferenceMode(FbxLayerElement.eIndexToDirect)
    lLayer.SetUVs(lUVDiffuseLayer, FbxLayerElement.eTextureDiffuse)

    for i in range(len(uv_array)):
        lUVDiffuseLayer.GetDirectArray().Add(uv_array[i])

    # Add all polygons to the mesh
    for polygon in polygons:
        lMesh.BeginPolygon(polygon.texture_index)
        lLayerElementNormal.GetIndexArray().Add(polygon.normal_index)
        for index in polygon.vert_indices:
            lMesh.AddPolygon(index)
        lMesh.EndPolygon()

        for uv in polygon.uvs:
            lUVDiffuseLayer.GetIndexArray().Add(uv)

    # Add and connect mesh node
    lMeshNode = FbxNode.Create(lSdkManager, model_name)
    lMeshNode.SetNodeAttribute(lMesh)

    for material in materials:
        lMeshNode.AddMaterial(material)

    lScene.GetRootNode().AddChild(lMeshNode)

    print('Writing FBX file to {}'.format(out_path + '.fbx'))
    FbxCommon.SaveScene(lSdkManager, lScene, out_path+'.fbx', 0, True)
