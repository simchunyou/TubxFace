#Check if the system path to scripts have been updated for the importing of modules
import sys
#sysPath = "/home/i7208422/Desktop/Innovations/InnovationsProject/scripts"
sysPath = "C:\Users\User\Documents\CY_Work_Documents\Bournemouth Year 3\Innovations\InnovationsProject2\scripts\TubxFace"
sysPathUpdated = 0
for path in sys.path:
    if path == sysPath:
        sysPathUpdated = 1
if sysPathUpdated == 0:
    sys.path.append(sysPath)

import LibraryGeneration
reload(LibraryGeneration)

import MayaImageReading
reload(MayaImageReading)

import ScanningImage
reload(ScanningImage)

import DeformLibrary
reload(DeformLibrary)

import CreateRelationships
reload (CreateRelationships)

LibraryGeneration.createShaders()

mesh = "Base_1x1_Mesh2"
relationshipList, Objects = LibraryGeneration.createMeshAndControl(mesh)

# User Input data. UI
dataEar1 = ["TubxEar_geo_1.vtx[47]",  "TubxEar_geo_1.vtx[7]", "TubxEar_geo_1.vtx[19]",  "TubxEar_geo_1.vtx[13]", "TubxEar_geo_1.vtx[53]"]
dataEar2 = ["TubxEar_geo_2.vtx[47]",  "TubxEar_geo_2.vtx[7]", "TubxEar_geo_2.vtx[19]",  "TubxEar_geo_2.vtx[11]", "TubxEar_geo_2.vtx[15]"]
dataGrp = [dataEar1, dataEar2]


LibraryGeneration.createDataMeshAndControl(dataGrp)

'''
Objects = LibraryGeneration.seperateMeshParts("Base_1x1_Mesh2")
LibraryGeneration.createProfileControl(Objects)
LibraryGeneration.createEyeControl("TubxEye_geo_1")
LibraryGeneration.createEyeControl("TubxEye_geo_2")
LibraryGeneration.createMouthControl("TubxMouth_geo_1")
LibraryGeneration.createForeheadControl("TubxForehead_geo_1")
LibraryGeneration.createNoseControl("TubxNose_geo_1", "TubxNoseBridge_geo_1")
LibraryGeneration.createMouthLoopControl("TubxMouthLoop_geo_1", "TubxNose_geo_1", "TubxMouth_geo_1")
LibraryGeneration.createNoseBridgeControl("TubxNoseBridge_geo_1", "TubxNose_geo_1",  "TubxForehead_geo_1" )
LibraryGeneration.createEarControl("TubxEar_geo_1.vtx[47]",  "TubxEar_geo_1.vtx[7]", "TubxEar_geo_1.vtx[19]",  "TubxEar_geo_1.vtx[13]", "TubxEar_geo_1.vtx[53]")
LibraryGeneration.createEarControl("TubxEar_geo_2.vtx[47]",  "TubxEar_geo_2.vtx[7]", "TubxEar_geo_2.vtx[19]",  "TubxEar_geo_2.vtx[11]", "TubxEar_geo_2.vtx[15]")
LibraryGeneration.createCheekControl("TubxCheek_geo_1")
LibraryGeneration.createCheekControl("TubxCheek_geo_2")
'''

basicFilter = "Image Files (*.png *.tiff);;PNG (*.png);;TIFF (*.tiff);;All Files (*.*)"
FrontImagePath = cmds.fileDialog2(caption = "Please select front image", fileFilter=basicFilter, fm=1)
SideImagePath = cmds.fileDialog2(caption = "Please select side image", fileFilter=basicFilter, fm=1)

MyImage = ScanningImage.ImageScan(str(FrontImagePath[0]), str(SideImagePath[0]))

LocatorGrp = MyImage.generateCoord()

DeformLibrary.deformGeoToImage(LocatorGrp)

reload(DeformLibrary)
DeformLibrary.cleanUpforEdit(LocatorGrp, Objects, relationshipList)


#Getting the directory path of the script
import os
import sys
ScriptDirectory = cmds.internalVar(userScriptDir = True)
sysPath = os.path.join(ScriptDirectory, 'TubxFace')

#Check if the system path to scripts have been updated for the importing of modules
#sysPath = "/home/i7208422/Desktop/Innovations/InnovationsProject/scripts"
#sysPath = "C:\Users\User\Documents\CY_Work_Documents\Bournemouth Year 3\Innovations\InnovationsProject2\scripts\TubxFace"
sysPathUpdated = 0
for path in sys.path:
  if path == sysPath:
    sysPathUpdated = 1
if sysPathUpdated == 0:
  sys.path.append(sysPath)

import TubxFaceUI
reload(TubxFaceUI)

UI = TubxFaceUI.showUI()

