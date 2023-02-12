import FbxCommon
from fbx import *


def CreateScene(pSdkManager, pScene):
    # Create scene info
    lSceneInfo = FbxDocumentInfo.Create(pSdkManager, "SceneInfo")
    lSceneInfo.mTitle = "Test Scene"
    lSceneInfo.mAuthor = "fravolt"
    pScene.SetSceneInfo(lSceneInfo)

    lMeshNode = CreateMesh(pSdkManager, "Mesh")
    pScene.GetRootNode().AddChild(lMeshNode)

    return True


def CreateMesh(pSdkManager, pName):
    MeshControlPoints = (
        FbxVector4(-10, -10, 0), FbxVector4(10, -10, 0), FbxVector4(10, 10, 0), FbxVector4(-10, 10, 0),
    )

    lMesh = FbxMesh.Create(pSdkManager, pName)
    lMesh.InitControlPoints(4)
    for i in range(4):
        lMesh.SetControlPointAt(MeshControlPoints[i], i)

    lMesh.CreateLayer()
    lLayer: FbxLayer = lMesh.GetLayer(0)

    lLayerElementNormal = FbxLayerElementNormal.Create(lMesh, "")
    lLayerElementNormal.SetMappingMode(FbxLayerElement.eByPolygon)
    lLayerElementNormal.SetReferenceMode(FbxLayerElement.eIndexToDirect)

    lLayerElementNormal.GetDirectArray().Add(FbxVector4(0, 0, 1))
    lLayerElementNormal.GetIndexArray().Add(0)

    lLayer.SetNormals(lLayerElementNormal)

    # lMaterialElement:FbxGeometryElementMaterial = lMesh.CreateElementMaterial()
    # lMaterialElement

    lMaterialLayer = FbxLayerElementMaterial.Create(lMesh, "")
    lMaterialLayer.SetMappingMode(FbxLayerElement.eByPolygon)
    lMaterialLayer.SetReferenceMode(FbxLayerElement.eIndexToDirect)
    lLayer.SetMaterials(lMaterialLayer)

    # Create texture and material
    lUVDiffuseLayer = FbxLayerElementUV.Create(lMesh, "DiffuseUV")
    lUVDiffuseLayer.SetMappingMode(FbxLayerElement.eByPolygonVertex)
    lUVDiffuseLayer.SetReferenceMode(FbxLayerElement.eIndexToDirect)
    lLayer.SetUVs(lUVDiffuseLayer, FbxLayerElement.eTextureDiffuse)

    lUVDiffuseLayer.GetDirectArray().Add(FbxVector2(-11, 0))
    lUVDiffuseLayer.GetDirectArray().Add(FbxVector2(-10, 0))
    lUVDiffuseLayer.GetDirectArray().Add(FbxVector2(-10, 1))
    lUVDiffuseLayer.GetDirectArray().Add(FbxVector2(-11, 1))

    lUVDiffuseLayer.GetIndexArray().SetCount(4)

    lMesh.BeginPolygon(1)
    for i in range(4):
        lUVDiffuseLayer.GetIndexArray().SetAt(i, i)
        lMesh.AddPolygon(i)
    lMesh.EndPolygon()

    lNode = FbxNode.Create(pSdkManager, pName)
    lNode.SetNodeAttribute(lMesh)
    lNode.SetShadingMode(FbxNode.eTextureShading)

    lTexture = FbxFileTexture.Create(pSdkManager, "Diffuse Texture")
    lTexture.SetFileName("grss_tex.tiff")
    lTexture.SetMappingType(FbxTexture.eUV)
    lTexture.SetTextureUse(FbxTexture.eStandard)

    lMaterial = FbxSurfacePhong.Create(pSdkManager, 'my_material')
    lMaterial.Diffuse.ConnectSrcObject(lTexture)
    lNode.AddMaterial(lMaterial)

    lTexture2 = FbxFileTexture.Create(pSdkManager, "Diffuse Texture")
    lTexture2.SetFileName("Lfgrn_tex.tiff")
    lTexture2.SetMappingType(FbxTexture.eUV)
    lTexture2.SetTextureUse(FbxTexture.eStandard)

    lMaterial2 = FbxSurfacePhong.Create(pSdkManager, 'my_other_material')
    lMaterial2.Diffuse.ConnectSrcObject(lTexture2)
    lNode.AddMaterial(lMaterial2)

    return lNode


def main():
    (lSdkManager, lScene) = FbxCommon.InitializeSdkObjects()
    CreateScene(lSdkManager, lScene)

    FbxCommon.SaveScene(lSdkManager, lScene, 'test.fbx', 0, False)

if __name__ == '__main__':
    main()
