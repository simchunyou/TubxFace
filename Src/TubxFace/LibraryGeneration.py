'''
This script creates the processes for the library creation
It also contains function that creates control curves
'''

from maya import cmds
import maya.mel as mel
import math

import CreateRelationships
reload(CreateRelationships)

'''
User assigns regions for the face parts
This involves the process of clicking the faces and assigning the shader
'''

# Utility functions
def compareVector(Vertex1, Vertex2, Vector):
  """
  This function compares a vector with a known vector
  This was initially the way I used to create control curves to check if a vector is going up or right etc
  However, if a nose bridge were to slant outwards, the results will not be perfect.
  This is thus replaced with checking the other areas for matching vertex positions

  Args:
    Vertex1: The end point of the vector to check
    Vertex2: The start point of the vector to check
    Vector: The known vector

  Returns: The dot product between the vector and the known vector.
  """

  Pos1 = cmds.xform(Vertex1, t=True, q=True)
  Pos2 = cmds.xform(Vertex2, t=True, q=True)
  EdgeVector = [Pos1[0] - Pos2[0], Pos1[1] - Pos2[1], Pos1[2] - Pos2[2]]
  #Normalize
  mag = float(math.sqrt(EdgeVector[0]*EdgeVector[0] + EdgeVector[1]*EdgeVector[1] + EdgeVector[2]*EdgeVector[2]))
  EdgeVector = [EdgeVector[0]/float(mag), EdgeVector[1]/float(mag), EdgeVector[2]/float(mag)]
  #Dot product
  DotResult = math.fabs(EdgeVector[0]*Vector[0] + EdgeVector[1]*Vector[1] + EdgeVector[2]*Vector[2])
  return DotResult

def cleanUp(oldList):
  """
  This function cleans up the cmds.polyInfo command and extract useable information
  Args:
    oldList: The results of the polyInfo list

  Returns: a use-able list
  """
  newList = oldList[0].split()
  del newList[1]
  del newList[0]
  newerList = []
  for n in newList:
    newerList.append(int(n))
  return newerList

def splitNumberFromName(name):
  """
  This function extracts the id of a vertex/face/edge
  Args:
    name: The vertex/edge/face

  Returns: The id

  """
  # Split the number
  number = name.split('[')
  number = number[1].split(']')[0]
  return int(number)

def bubblesort(list, indexlist):
  """
  This function bubble sorts a list and together with it, the index list gets sorted as well
  Args:
    list: The list to sort
    indexlist: The list that follows the sorted list

  """
  for i in range(len(list)-1, 0, -1):
    for j in range(i):
      if list[j] > list[j+1]:
        temp = list[j]
        tempIndex = indexlist[j]
        list[j] = list[j+1]
        indexlist[j] = indexlist[j+1]
        list[j+1] = temp
        indexlist[j+1] = tempIndex

# The calling functions
def createShaders():
  """
  This function creates the shaders for the TubxFace tool
  """
  print "Creating Shaders"
  # Check for the list of current shaders
  CurrentShaders = cmds.ls(materials=True)

  # Create the Default Tubs Shader if it doesnt exist
  if not "TubxDefault" in CurrentShaders:
    cmds.shadingNode("lambert", n="TubxDefault", asShader=True)
    cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="TubxDefaultSG")
    cmds.connectAttr("TubxDefault.outColor", "TubxDefaultSG.surfaceShader")
    cmds.setAttr("TubxDefault.color", 1, 1, 1, type="double3")

  # Create the Eye Shader if it doesnt exist
  if not "TubxEye" in CurrentShaders:
    cmds.shadingNode("lambert", n="TubxEye", asShader=True)
    cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="TubxEyeSG")
    cmds.connectAttr("TubxEye.outColor", "TubxEyeSG.surfaceShader")
    cmds.setAttr("TubxEye.color", 1, 0, 0, type="double3")

  # Create the Nose Bridge Shader if it doesnt exist
  if not "TubxNoseBridge" in CurrentShaders:
    cmds.shadingNode("lambert", n="TubxNoseBridge", asShader=True)
    cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="TubxNoseBridgeSG")
    cmds.connectAttr("TubxNoseBridge.outColor", "TubxNoseBridgeSG.surfaceShader")
    cmds.setAttr("TubxNoseBridge.color", 1, 1, 0, type="double3")

  # Create the Nose Shader if it doesnt exist
  if not "TubxNose" in CurrentShaders:
    cmds.shadingNode("lambert", n="TubxNose", asShader=True)
    cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="TubxNoseSG")
    cmds.connectAttr("TubxNose.outColor", "TubxNoseSG.surfaceShader")
    cmds.setAttr("TubxNose.color", 0, 1, 0, type="double3")

  # Create the Mouth Shader if it doesnt exist
  if not "TubxMouth" in CurrentShaders:
    cmds.shadingNode("lambert", n="TubxMouth", asShader=True)
    cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="TubxMouthSG")
    cmds.connectAttr("TubxMouth.outColor", "TubxMouthSG.surfaceShader")
    cmds.setAttr("TubxMouth.color", 0, 0, 1, type="double3")

  # Create the Mouth Loop Shader if it doesnt exist
  if not "TubxMouthLoop" in CurrentShaders:
    cmds.shadingNode("lambert", n="TubxMouthLoop", asShader=True)
    cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="TubxMouthLoopSG")
    cmds.connectAttr("TubxMouthLoop.outColor", "TubxMouthLoopSG.surfaceShader")
    cmds.setAttr("TubxMouthLoop.color", 1, 0, 1, type="double3")

  # Create the Forehead Shader if it doesnt exist
  if not "TubxForehead" in CurrentShaders:
    cmds.shadingNode("lambert", n="TubxForehead", asShader=True)
    cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="TubxForeheadSG")
    cmds.connectAttr("TubxForehead.outColor", "TubxForeheadSG.surfaceShader")
    cmds.setAttr("TubxForehead.color", 0, 1, 1, type="double3")

  # Create the Ear Shader if it doesnt exist
  if not "TubxEar" in CurrentShaders:
    cmds.shadingNode("lambert", n="TubxEar", asShader=True)
    cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="TubxEarSG")
    cmds.connectAttr("TubxEar.outColor", "TubxEarSG.surfaceShader")
    cmds.setAttr("TubxEar.color", 0.7, 0.3, 0, type="double3")

  # Create the BackHead Shader if it doesnt exist
  if not "TubxBackHead" in CurrentShaders:
    cmds.shadingNode("lambert", n="TubxBackHead", asShader=True)
    cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="TubxBackHeadSG")
    cmds.connectAttr("TubxBackHead.outColor", "TubxBackHeadSG.surfaceShader")
    cmds.setAttr("TubxBackHead.color", 0.5, 1, 0.5, type="double3")

  # Create the LowerBackHead Shader if it doesnt exist
  if not "TubxLowerBackHead" in CurrentShaders:
    cmds.shadingNode("lambert", n="TubxLowerBackHead", asShader=True)
    cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="TubxLowerBackHeadSG")
    cmds.connectAttr("TubxLowerBackHead.outColor", "TubxLowerBackHeadSG.surfaceShader")
    cmds.setAttr("TubxLowerBackHead.color", 0.2, 0.5, 0.2, type="double3")

  # Create the Cheek Shader if it doesnt exist
  if not "TubxCheek" in CurrentShaders:
    cmds.shadingNode("lambert", n="TubxCheek", asShader=True)
    cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="TubxCheekSG")
    cmds.connectAttr("TubxCheek.outColor", "TubxCheekSG.surfaceShader")
    cmds.setAttr("TubxCheek.color", 0.5, 0.2, 0.5, type="double3")

  # Create the Chin Shader if it doesnt exist
  if not "TubxChin" in CurrentShaders:
    cmds.shadingNode("lambert", n="TubxChin", asShader=True)
    cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="TubxChinSG")
    cmds.connectAttr("TubxChin.outColor", "TubxChinSG.surfaceShader")
    cmds.setAttr("TubxChin.color", 0.2, 0.5, 0.5, type="double3")

def createMeshAndControl(mesh, resolutionList):
  """
  This function is a combination function. It separates the mesh into
  its parts and creates the controls
  Args:
    mesh: The mesh to separate
    resolutionList: The list that contains the ctrl point resolution

  Returns: The relationship list and the separated objects

  """
  # We first separate the mesh into the various parts
  Objects = seperateMeshParts(mesh)
  print "Objects Separated"

  # We establish the relationship
  relationshipList = CreateRelationships.meshRelationships(Objects)
  print "relationshipList Created"

  # We then begin to create the respective controls

  createProfileControl(Objects)
  print "Profile Ctrl Created"

  #Create some variables to be used to store objects
  mouthVariable, noseVariable, noseBridgeVariable, foreheadVariable = 0,0,0,0

  #The resolutionList contains points for the resolution of the control
  # resolutionList = [eye, mouth, mouthloop, nose, eyebrow, nosebridge]

  for forehead in Objects:
    if "TubxForehead_geo_" in forehead:
      createForeheadControl(forehead, resolutionList[4])
      foreheadVariable = forehead
  print "Forehead Ctrl Created"


  for eye in Objects:
    if "TubxEye_geo_" in eye:
      createEyeControl(eye, resolutionList[0])
  print "Eye Ctrl Created"

  for mouth in Objects:
    if "TubxMouth_geo_" in mouth:
      createMouthControl(mouth, resolutionList[1])
      mouthVariable = mouth
  print "Mouth Ctrl Created"


  #The nosebridge and nose is a little tricky as both needs to reference each other
  for noseBridge in Objects:
    if "TubxNoseBridge_geo_" in noseBridge:
      noseBridgeVariable = noseBridge

  for nose in Objects:
    if "TubxNose_geo_" in nose:
      createNoseControl(nose, noseBridgeVariable, resolutionList[3])
      noseVariable = nose
  print "Nose Ctrl Created"


  for noseBridge in Objects:
    if "TubxNoseBridge_geo_" in noseBridge:
      createNoseBridgeControl(noseBridge, noseVariable, foreheadVariable, resolutionList[5])
  print "Nosebridge Ctrl Created"


  for mouthLoop in Objects:
    if "TubxMouthLoop_geo_" in mouthLoop:
      createMouthLoopControl(mouthLoop, noseVariable, mouthVariable, resolutionList[2])
  print "MouthLoop Ctrl Created"

  for cheek in Objects:
    if "TubxCheek_geo_" in cheek:
      createCheekEdgeControl(cheek)
  print "Cheek Ctrl Created"

  for chin in Objects:
    if "TubxChin_geo_" in chin:
      createChinEdgeControl(chin)
  print "Chin Ctrl Created"



  return relationshipList, Objects

def createDataMeshAndControl(data):
  """
  This function creates the ear controls from the data input
  Args:
    data: The data of the ear

  """
  for index in range(0, len(data)):
    if not data[index]:
      continue
    objectData = data[index]
    objectName = objectData[0].split(".vtx")[0]

    if len(objectData) != 5:
      cmds.error("Not correct amount of data to create ear control")
      return
    createEarControl(objectName, objectData[0], objectData[1], objectData[2], objectData[3], objectData[4])

# The functions
def seperateMeshParts(mesh):
  """
  This function separates the mesh into its parts depending on the shader assigned
  Args:
    mesh: The mesh to work with

  Returns: The separated mesh parts
  """
  ShadingList = ['TubxEye', 'TubxNoseBridge', 'TubxNose', 'TubxMouth', 'TubxMouthLoop', 'TubxForehead',
                 'TubxEar', 'TubxBackHead', 'TubxLowerBackHead', 'TubxCheek', 'TubxChin', 'TubxDefault']

  ObjectList = []
  for shader in ShadingList:
    cmds.hyperShade(objects=shader)
    Selection = cmds.ls(sl=True)

    #Check if selection exists
    if not Selection:
      continue

    # We seperate out the mesh into its components
    cmds.polyChipOff(Selection)
    objects = cmds.polySeparate(mesh, n='Result', ch=False)

    # Unparent objects
    for i in range(0, len(objects)):
      cmds.parent(objects[i], w=True)

    # Delete the created group
    cmds.delete(mesh)

    # Renaming the geometry
    cmds.rename(objects[0], mesh)
    for i in range(1, len(objects)):
      createdGeo = cmds.rename(objects[i], '%s_%s_%s' % (shader,"geo",i))
      ObjectList.append(createdGeo)

  return ObjectList

def createEyeControl(mesh, spanNumber = 16):
  """
  This function creates the eye controls
  Args:
    mesh: The mesh to work with
  """
  # We grab the border edges
  cmds.select(mesh)
  cmds.polySelectConstraint(mode=3, t=0x8000, where=1)
  borderEdges = cmds.ls(sl=True)
  borderEdges = cmds.filterExpand(borderEdges, ex=True, sm=32)
  cmds.polySelectConstraint(dis=True)

  # As the eye has the inner and outer edge loops, we get the 2 separate edge loops
  EdgeLoops = []

  for i in borderEdges:
    # Split the number
    number = splitNumberFromName(i)
    # Select the number at a given edge loop
    selection = cmds.polySelect(eb=int(number), q=True)
    selection = [int(x) for x in selection]
    selection = list(set(selection))
    selection.sort()

    # Now we check if the number exist in the EdgeLoops list or not
    if selection in EdgeLoops:
      continue
    else:
      EdgeLoops.append(selection)
    # We then check if the number of edge loops detected is already 2
    if len(EdgeLoops) == 2:
      break

  BoundingVolume = []
  CurveName = []
  # We select the respective edge loops and convert them to curves
  for i in EdgeLoops:
    cmds.select(clear = True)
    for j in i:
      cmds.select("%s.e[%s]" % (mesh, j), add=True)
    CurveName.append(cmds.polyToCurve(n='EyeTempCurve', form=2, degree=1, ch=False))
    # We then check for the bounding volume
    bboxCurve = cmds.exactWorldBoundingBox()
    bboxCurve = [bboxCurve[3]- bboxCurve[0], bboxCurve[4]- bboxCurve[1], bboxCurve[5]- bboxCurve[2]]
    volume = bboxCurve[0] * bboxCurve[1] * bboxCurve[2]
    BoundingVolume.append(volume)

  # We compare the bounding boxes and delete the smaller one
  if BoundingVolume[0] > BoundingVolume[1]:
    cmds.delete(CurveName[0])
    CurrentCurve = cmds.rename(CurveName[1], "EyeCurve#")
  else:
    cmds.delete(CurveName[1])
    CurrentCurve =  cmds.rename(CurveName[0], "EyeCurve#")

  # We then rebuild the curve for standardise number of points
  #spanNumber = 16
  cmds.rebuildCurve(CurrentCurve, ch = False, rpo = True, end = True, kr = False, kep = True, s = spanNumber, d = 1)
  cmds.reverseCurve(CurrentCurve, ch = False, rpo = True)

  # We finally bind the respective mesh to the curves
  cmds.wire(mesh, w=[CurrentCurve], dds=[0,0.1])

def createNoseBridgeControl(mesh, noseMesh, foreheadMesh, spanNumber = 4):
  """
  This function creates the nose bridge control
  Args:
    mesh: The mesh to work with
    noseMesh: The nose mesh to check relationship with
    foreheadMesh: The forehead mesh to check relationship with
  """
  # We first get a list of border edges the NoseMesh has
  cmds.select(noseMesh)
  cmds.polySelectConstraint(m=3, t=0x8000, w=1)
  NoseBorderEdges = cmds.ls(sl=True)
  NoseBorderEdges = cmds.filterExpand(NoseBorderEdges, ex=True, sm=32)
  cmds.polySelectConstraint(dis=True)

  # With the edges that we got, we get the position they are in
  NoseBorderPosition = []
  for edge in NoseBorderEdges:
    transformations = cmds.xform(edge, q=True, t=True, ws=True)
    if "e" in str(transformations[0]):
      transformations[0] = 0.0
    if "e" in str(transformations[3]):
      transformations[3] = 0.0
    NoseBorderPosition.append(transformations)


  # We rearrange each position based on the lowest x in case the edge vector points a different way
  for i in range(0, len(NoseBorderPosition)):
    if (NoseBorderPosition[i][3] < NoseBorderPosition[i][0]):
      Temp0, Temp1, Temp2, Temp3, Temp4, Temp5 = [x for x in NoseBorderPosition[i]]
      NoseBorderPosition[i] = [Temp3, Temp4, Temp5, Temp0, Temp1, Temp2]

  # We then get a list of border edges the forehead has
  cmds.select(foreheadMesh)
  cmds.polySelectConstraint(m=3, t=0x8000, w=1)
  ForeheadBorderEdges = cmds.ls(sl=True)
  ForeheadBorderEdges = cmds.filterExpand(ForeheadBorderEdges, ex=True, sm=32)
  cmds.polySelectConstraint(dis=True)

  # With the edges that we got, we get the position they are in
  ForeheadBorderPosition = []
  for edge in ForeheadBorderEdges:
    transformations = cmds.xform(edge, q=True, t=True, ws=True)
    if "e" in str(transformations[0]):
      transformations[0] = 0.0
    if "e" in str(transformations[3]):
      transformations[3] = 0.0
    ForeheadBorderPosition.append(transformations)

  # We rearrange each position based on the lowest x in case the edge vector points a different way
  for i in range(0, len(ForeheadBorderPosition)):
    if (ForeheadBorderPosition[i][3] < ForeheadBorderPosition[i][0]):
      Temp0, Temp1, Temp2, Temp3, Temp4, Temp5 = [x for x in ForeheadBorderPosition[i]]
      ForeheadBorderPosition[i] = [Temp3, Temp4, Temp5, Temp0, Temp1, Temp2]

  # Lastly we get the border edge of the nosebridge mesh
  cmds.select(mesh)
  cmds.polySelectConstraint(m=3, t=0x8000, w=1)
  BorderEdges = cmds.ls(sl=True)
  BorderEdges = cmds.filterExpand(BorderEdges, ex=True, sm=32)
  cmds.polySelectConstraint(dis=True)

  # With the edges that we got, we get the position they are in
  BorderPosition = []
  for edge in BorderEdges:
    transformations = cmds.xform(edge, q=True, t=True, ws=True)
    if "e" in str(transformations[0]):
      transformations[0] = 0.0
    if "e" in str(transformations[3]):
      transformations[3] = 0.0
    BorderPosition.append([edge,transformations])

  # We rearrange each position based on the lowest x in case the edge vector points a different way
  for i in range(0, len(BorderPosition)):
    if (BorderPosition[i][1][3] < BorderPosition[i][1][0]):
      Temp0, Temp1, Temp2, Temp3, Temp4, Temp5 = [x for x in BorderPosition[i][1]]
      BorderPosition[i][1] = [Temp3, Temp4, Temp5, Temp0, Temp1, Temp2]

  # We compare the positions and remove matching ones
  LfOutsideEdges = []
  RtOutsideEdges = []
  for i in range(0, len(BorderPosition)):
    similar = 0
    for j in range(0, len(NoseBorderPosition)):
      if BorderPosition[i][1] == NoseBorderPosition[j]:
        similar = 1
        break
    if similar == 0:
      for j in range(0, len(ForeheadBorderPosition)):
        if BorderPosition[i][1] == ForeheadBorderPosition[j]:
          similar = 1
          break
    if similar == 0:
      #We then separate them into left and right side
      if BorderPosition[i][1][0] > 0 or BorderPosition[i][1][3] > 0:
        LfOutsideEdges.append(BorderPosition[i][0])
      else:
        RtOutsideEdges.append(BorderPosition[i][0])

  # We select the outside edges and create the curve
  cmds.select(LfOutsideEdges)
  LfNoseBridgeCurve = cmds.polyToCurve(n='LfNoseBridgeCurve#', form=2, degree=1, ch=False)
  cmds.select(RtOutsideEdges)
  RtNoseBridgeCurve = cmds.polyToCurve(n='RtNoseBridgeCurve#', form=2, degree=1, ch=False)

  # We then rebuild the curve for standardise number of points
  #spanNumber = 4
  cmds.rebuildCurve(LfNoseBridgeCurve, ch=False, rpo=True, end=True, kr=False, kep=True, s=spanNumber - 1, d=1)
  cmds.rebuildCurve(RtNoseBridgeCurve, ch=False, rpo=True, end=True, kr=False, kep=True, s=spanNumber - 1, d=1)

  # We finally bind the respective mesh to the curves
  cmds.wire(mesh, w=[RtNoseBridgeCurve[0], LfNoseBridgeCurve[0]], dds=[(0, 0.05),(1,0.05)])

def createNoseControl(mesh, noseBridgeMesh, spanNumber = 8):
  """
  This function creates the nose control
  Args:
    mesh: The mesh to work with
    noseBridgeMesh: The nose bridge mesh to check relationship with

  """
  #We first get a list of border edges the noseBridgeMesh has
  cmds.select(noseBridgeMesh)
  cmds.polySelectConstraint(m=3, t=0x8000, w=1)
  NoseBridgeBorderEdges = cmds.ls(sl=True)
  NoseBridgeBorderEdges = cmds.filterExpand(NoseBridgeBorderEdges, ex=True, sm=32)
  cmds.polySelectConstraint(dis=True)

  #With the edges that we got, we get the position they are in
  NoseBridgeBorderPosition = []
  for edge in NoseBridgeBorderEdges:
    transformations = cmds.xform(edge, q=True, t=True, ws=True)
    if "e" in str(transformations[0]):
      transformations[0] = 0.0
    if "e" in str(transformations[3]):
      transformations[3] = 0.0
    NoseBridgeBorderPosition.append(transformations)


  #We rearrange each position based on the lowest x in case the edge vector points a different way
  for i in range(0, len(NoseBridgeBorderPosition)):
    if (NoseBridgeBorderPosition[i][3] < NoseBridgeBorderPosition[i][0]):
      Temp0,Temp1,Temp2,Temp3,Temp4,Temp5 = [x for x in NoseBridgeBorderPosition[i]]
      NoseBridgeBorderPosition[i] = [Temp3,Temp4,Temp5,Temp0,Temp1,Temp2]

  #We then get a list of the border edges of the noseMesh
  cmds.select(mesh)
  cmds.polySelectConstraint(m=3, t=0x8000, w=1)
  BorderEdges = cmds.ls(sl=True)
  BorderEdges = cmds.filterExpand(BorderEdges, ex=True, sm=32)
  cmds.polySelectConstraint(dis=True)

  #With the edges that we got, we get the position they are in
  NoseBorderPosition = []
  for edge in BorderEdges:
    transformations = cmds.xform(edge, q=True, t=True, ws=True)
    if "e" in str(transformations[0]):
      transformations[0] = 0.0
    if "e" in str(transformations[3]):
      transformations[3] = 0.0
    NoseBorderPosition.append([edge,transformations])

  # We rearrange each position based on the lowest x in case the edge vector points a different way
  for i in range(0, len(NoseBorderPosition)):
    if (NoseBorderPosition[i][1][3] < NoseBorderPosition[i][1][0]):
      Temp0, Temp1, Temp2, Temp3, Temp4, Temp5 = [x for x in NoseBorderPosition[i][1]]
      NoseBorderPosition[i][1] = [Temp3, Temp4, Temp5, Temp0, Temp1, Temp2]


  #We then compare the positions and remove matching ones
  NoseOutsideEdges = []
  for i in range(0,len(NoseBorderPosition)):
    similar = 0
    for j in range(0,len(NoseBridgeBorderPosition)):
      if NoseBorderPosition[i][1] == NoseBridgeBorderPosition[j]:
        similar = 1
        break
    if similar == 0:
      NoseOutsideEdges.append(NoseBorderPosition[i][0])


  #We select the outside edges and create the curve
  cmds.select(NoseOutsideEdges)
  CurrentCurve = cmds.polyToCurve(n='NoseCurve#', form=2, degree=1, ch=False)

  # We then rebuild the curve for standardise number of points
  #spanNumber = 8
  cmds.rebuildCurve(CurrentCurve, ch=False, rpo=True, end=True, kr=False, kep=True, s=spanNumber-1, d=1)

  # We finally bind the respective mesh to the curves
  cmds.wire(mesh, w=CurrentCurve, dds=[0, 0.05])

def createMouthControl(mesh, spanNumber = 24):
  """
  This function creates the mouth control
  Args:
    mesh: The mesh to work with

  """
  # We grab the border edges
  cmds.select(mesh)
  cmds.polySelectConstraint(mode=3, t=0x8000, where=1)
  borderEdges = cmds.ls(sl=True)
  borderEdges = cmds.filterExpand(borderEdges, ex=True, sm=32)
  cmds.polySelectConstraint(dis=True)

  # As the mouth has the inner and outer edge loops, we get the 2 separate edge loops
  EdgeLoops = []

  for i in borderEdges:
    # Split the number
    number = splitNumberFromName(i)
    # Select the number at a given edge loop
    selection = cmds.polySelect(eb=int(number), q=True)
    selection = [int(x) for x in selection]
    selection = list(set(selection))
    selection.sort()

    # Now we check if the number exist in the EdgeLoops list or not
    if selection in EdgeLoops:
      continue
    else:
      EdgeLoops.append(selection)
    # We then check if the number of edge loops detected is already 2
    if len(EdgeLoops) == 2:
      break

  BoundingVolume = []
  CurveName = []
  # We select the respective edge loops and convert them to curves
  for i in EdgeLoops:
    cmds.select(clear=True)
    for j in i:
      cmds.select("%s.e[%s]" % (mesh, j), add=True)
    CurveName.append(cmds.polyToCurve(n='MouthTempCurve', form=2, degree=1, ch=False))
    # We then check for the bounding volume
    bboxCurve = cmds.exactWorldBoundingBox()
    bboxCurve = [bboxCurve[3] - bboxCurve[0], bboxCurve[4] - bboxCurve[1], bboxCurve[5] - bboxCurve[2]]
    volume = bboxCurve[0] * bboxCurve[1] * bboxCurve[2]
    BoundingVolume.append(volume)

  # We compare the bounding volume and assign the name accordingly
  if BoundingVolume[0] > BoundingVolume[1]:
    #OuterCurve = cmds.rename(CurveName[0], "OuterMouthCurve#")
    cmds.delete(CurveName[0])
    InnerCurve = cmds.rename(CurveName[1], "InnerMouthCurve#")
  else:
    #OuterCurve = cmds.rename(CurveName[1], "OuterMouthCurve#")
    cmds.delete(CurveName[1])
    InnerCurve = cmds.rename(CurveName[0], "InnerMouthCurve#")

  # We then rebuild the curve for standardise number of points
  #spanNumber = 24
  #cmds.rebuildCurve(OuterCurve, ch=False, rpo=True, end=True, kr=False, kep=True, s=spanNumber, d=1)
  cmds.rebuildCurve(InnerCurve, ch=False, rpo=True, end=True, kr=False, kep=True, s=spanNumber, d=1)
  cmds.reverseCurve(InnerCurve, ch=False, rpo=True)

  # We finally bind the respective mesh to the curves
  #cmds.wire(mesh, w=[OuterCurve, InnerCurve], dds=[(0, 0.05),(1,0.07)])
  cmds.wire(mesh, w=InnerCurve, dds=[0, 0.05])

def createMouthLoopControl(mesh, noseMesh, mouthMesh, spanNumber = 16):
  """
  This function creates the mouth loop control
  Args:
    mesh: The mesh to work with
    noseMesh: The nose mesh to compare relationship
    mouthMesh: The mouth mesh to compare relationship
  """
  # We first get a list of border edges the NoseMesh has
  cmds.select(noseMesh)
  cmds.polySelectConstraint(m=3, t=0x8000, w=1)
  NoseBorderEdges = cmds.ls(sl=True)
  NoseBorderEdges = cmds.filterExpand(NoseBorderEdges, ex=True, sm=32)
  cmds.polySelectConstraint(dis=True)

  # With the edges that we got, we get the position they are in
  NoseBorderPosition = [cmds.xform(edge, q=True, t=True, ws=True) for edge in NoseBorderEdges]

  # We rearrange each position based on the lowest x in case the edge vector points a different way
  for i in range(0, len(NoseBorderPosition)):
    if (NoseBorderPosition[i][3] < NoseBorderPosition[i][0]):
      Temp0, Temp1, Temp2, Temp3, Temp4, Temp5 = [x for x in NoseBorderPosition[i]]
      NoseBorderPosition[i] = [Temp3, Temp4, Temp5, Temp0, Temp1, Temp2]

  # We then get a list of border edges the mouthMesh has
  cmds.select(mouthMesh)
  cmds.polySelectConstraint(m=3, t=0x8000, w=1)
  MouthBorderEdges = cmds.ls(sl=True)
  MouthBorderEdges = cmds.filterExpand(MouthBorderEdges, ex=True, sm=32)
  cmds.polySelectConstraint(dis=True)

  # With the edges that we got, we get the position they are in
  MouthBorderPosition = [cmds.xform(edge, q=True, t=True, ws=True) for edge in MouthBorderEdges]

  # We rearrange each position based on the lowest x in case the edge vector points a different way
  for i in range(0, len(MouthBorderPosition)):
    if (MouthBorderPosition[i][3] < MouthBorderPosition[i][0]):
      Temp0, Temp1, Temp2, Temp3, Temp4, Temp5 = [x for x in MouthBorderPosition[i]]
      MouthBorderPosition[i] = [Temp3, Temp4, Temp5, Temp0, Temp1, Temp2]

  #Lastly we get the border edge of the mouth loop mesh
  cmds.select(mesh)
  cmds.polySelectConstraint(m=3, t=0x8000, w=1)
  BorderEdges = cmds.ls(sl=True)
  BorderEdges = cmds.filterExpand(BorderEdges, ex=True, sm=32)
  cmds.polySelectConstraint(dis=True)

  # With the edges that we got, we get the position they are in
  BorderPosition = [[edge, cmds.xform(edge, q=True, t=True, ws=True)] for edge in BorderEdges]

  # We rearrange each position based on the lowest x in case the edge vector points a different way
  for i in range(0, len(BorderPosition)):
    if (BorderPosition[i][1][3] < BorderPosition[i][1][0]):
      Temp0, Temp1, Temp2, Temp3, Temp4, Temp5 = [x for x in BorderPosition[i][1]]
      BorderPosition[i][1] = [Temp3, Temp4, Temp5, Temp0, Temp1, Temp2]

  # We compare the positions and remove matching ones
  OutsideEdges = []
  for i in range(0, len(BorderPosition)):
    similar = 0
    for j in range(0, len(NoseBorderPosition)):
      if BorderPosition[i][1] == NoseBorderPosition[j]:
        similar = 1
        break
    if similar == 0:
      for j in range(0, len(MouthBorderPosition)):
        if BorderPosition[i][1] == MouthBorderPosition[j]:
          similar = 1
          break
    if similar == 0:
      OutsideEdges.append(BorderPosition[i][0])

  # We select the outside edges and create the curve
  cmds.select(OutsideEdges)
  CurrentCurve = cmds.polyToCurve(n='MouthLoopCurve#', form=2, degree=1, ch=False)

  # We then rebuild the curve for standardise number of points
  #spanNumber = 16
  cmds.rebuildCurve(CurrentCurve, ch=False, rpo=True, end=True, kr=False, kep=True, s=spanNumber-1, d=1)

  # We finally bind the respective mesh to the curves
  cmds.wire(mesh, w=CurrentCurve, dds=[0, 0.05])

def createForeheadControl(mesh, spanNumberEyebrow = 16):
  """
  This function creates the forehead control
  Args:
    mesh: The mesh to work with
  """
  # We grab the border edges
  cmds.select(mesh)
  cmds.polySelectConstraint(mode=3, t=0x8000, where=1)
  borderEdges = cmds.ls(sl=True)
  borderEdges = cmds.filterExpand(borderEdges, ex=True, sm=32)
  cmds.polySelectConstraint(dis=True)

  CornerVertices = []
  # We find the corner vertices. Those are vertices with only 2 connecting edges
  for i in borderEdges:
    cmds.select(i)
    # First we convert the Edges into the 2 vertices
    EdgeVert = cmds.polyListComponentConversion(fe=True, tv=True)
    EdgeVert = cmds.filterExpand(EdgeVert, ex=True, sm=31)
    # We then check from the 2 vertices their respective connecting edges
    # The corner vertices will only have 2 connecting edges while the rest has 3
    cmds.select(EdgeVert[0])
    VertEdge = cleanUp(cmds.polyInfo(ve=True))
    if len(VertEdge) == 2:
      CornerVertices.append(EdgeVert[0])
    cmds.select(EdgeVert[1])
    VertEdge = cleanUp(cmds.polyInfo(ve=True))
    if len(VertEdge) == 2:
      CornerVertices.append(EdgeVert[1])

  CornerVertices = list(set(CornerVertices))
  if (len(CornerVertices) > 4):
    cmds.warning("There are more then 4 corners at the forehead")
    return

  # Now we simply identify where the vertices are
  LfSide = []
  RtSide = []
  for i in CornerVertices:
    transformation = cmds.xform(i, q=True, t=True)
    if transformation[0] < 0:
      RtSide.append([i, transformation])
    if transformation[0] > 0:
      LfSide.append([i, transformation])

  if LfSide[0][1][2] < LfSide[1][1][2]:
    BackLf = splitNumberFromName(LfSide[0][0])
    FrontLf = splitNumberFromName(LfSide[1][0])
  else:
    BackLf = splitNumberFromName(LfSide[1][0])
    FrontLf = splitNumberFromName(LfSide[0][0])

  if RtSide[0][1][2] < RtSide[1][1][2]:
    BackRt = splitNumberFromName(RtSide[0][0])
    FrontRt = splitNumberFromName(RtSide[1][0])
  else:
    BackRt = splitNumberFromName(RtSide[1][0])
    FrontRt = splitNumberFromName(RtSide[0][0])

  #Lastly, we connect these vertices by finding the shortest path between and create the controls
  cmds.select(clear=True)
  cmds.polySelect(mesh, sep = [FrontRt, FrontLf])
  CurrentCurve = cmds.polyToCurve(n='LowerForeheadCurve#', form=2, degree=1, ch=False)

  # We then rebuild the curve for standardise number of points
  #spanNumberEyebrow = 16
  cmds.rebuildCurve(CurrentCurve, ch=False, rpo=True, end=True, kr=False, kep=True, s=spanNumberEyebrow - 1, d=1)

  # We finally bind the respective mesh to the curves
  cmds.wire(mesh, w=CurrentCurve, dds=[0, 0.2])

  cmds.select(clear=True)
  cmds.polySelect(mesh, sep=[BackRt, BackLf])
  CurrentCurve = cmds.polyToCurve(n='UpperForeheadCurve_FtProfileCurve#', form=2, degree=1, ch=False)

  # We then rebuild the curve for standardise number of points
  spanNumber = 6
  cmds.rebuildCurve(CurrentCurve, ch=False, rpo=True, end=True, kr=False, kep=True, s=spanNumber - 1, d=1)

  # We finally bind the respective mesh to the curves
  cmds.wire(mesh, w=CurrentCurve, dds=[0, 0.2])

  """
  #This was meant to create controls for the side of the forehead, however, I found out I do not need it for now
  cmds.select(clear=True)
  cmds.polySelect(mesh, sep=[FrontLf, BackLf])
  cmds.polyToCurve(n='LfForeheadCurve#', form=2, degree=1, ch=False)

  cmds.select(clear=True)
  cmds.polySelect(mesh, sep=[FrontRt, BackRt])
  cmds.polyToCurve(n='RtForeheadCurve#', form=2, degree=1, ch=False)
  """

def createEarControl(mesh, startEar, upperEar, midEar, lowerEar, endEar):
  """
  This function creates the ear control
  Args:
    mesh: The mesh to work with
    startEar: The position of the top of the ear
    upperEar: The position of the upperEar
    midEar: The position of the middle ear
    lowerEar: The position of the lower ear
    endEar: The end position of the ear

  """

  #We get the position of the start, mid and end Ear
  startPos = cmds.xform(startEar, q=True, t=True)
  upperPos = cmds.xform(upperEar, q=True, t=True)
  midPos = cmds.xform(midEar, q=True, t=True)
  lowerPos = cmds.xform(lowerEar, q=True, t=True)
  endPos = cmds.xform(endEar, q=True, t=True)

  #We then form a curve with those positions as cv points
  CurrentCurve = cmds.curve(n="EarCurve#", d=1, p=(startPos,upperPos,midPos, lowerPos, endPos))

  # We then rebuild the curve for standardise number of points
  spanNumber = 5
  cmds.rebuildCurve(CurrentCurve, ch=False, rpo=True, end=True, kr=False, kep=True, s=spanNumber - 1, d=1)

  # We finally bind the respective mesh to the curves
  cmds.wire(mesh, w=CurrentCurve, dds=[0, 0.1])

def createCheekEdgeControl(mesh, spanNumber = 6):
  """
  This function creates a control at the edge of the cheek to create the front profile
  Args:
    mesh: The mesh to work with

  """
  # We grab the border edges
  cmds.select(mesh)
  cmds.polySelectConstraint(mode=3, t=0x8000, where=1)
  borderEdges = cmds.ls(sl=True)
  borderEdges = cmds.filterExpand(borderEdges, ex=True, sm=32)
  cmds.polySelectConstraint(dis=True)

  CornerVertices = []
  # We find the corner vertices. Those are vertices with only 2 connecting edges
  for i in borderEdges:
    cmds.select(i)
    # First we convert the Edges into the 2 vertices
    EdgeVert = cmds.polyListComponentConversion(fe=True, tv=True)
    EdgeVert = cmds.filterExpand(EdgeVert, ex=True, sm=31)
    # We then check from the 2 vertices their respective connecting edges
    # The corner vertices will only have 2 connecting edges while the rest has 3
    cmds.select(EdgeVert[0])
    VertEdge = cleanUp(cmds.polyInfo(ve=True))
    if len(VertEdge) == 2:
      CornerVertices.append(EdgeVert[0])
    cmds.select(EdgeVert[1])
    VertEdge = cleanUp(cmds.polyInfo(ve=True))
    if len(VertEdge) == 2:
      CornerVertices.append(EdgeVert[1])

  CornerVertices = list(set(CornerVertices))

  if (len(CornerVertices) > 4):
    cmds.warning("There are more then 4 corners at the cheek")
    return

  # Now we simply identify where the vertices are
  # We get the z axis of the corner vertices and we get the 2 lowest z axis
  ZAxes = []
  for i in CornerVertices:
    transformation = cmds.xform(i, q=True, t=True)
    ZAxes.append(transformation[2])

  bubblesort(ZAxes, CornerVertices)

  # With that, we grab the back corner vertices and create the control curve
  # We connect these vertices by finding the shortest path between and create the controls
  vertexNoA = CornerVertices[0].split(".vtx[")[1]
  vertexNoA = int(vertexNoA.split("]")[0])
  vertexNoB = CornerVertices[1].split(".vtx[")[1]
  vertexNoB = int(vertexNoB.split("]")[0])

  cmds.select(clear=True)
  cmds.polySelect(mesh, sep=[vertexNoA, vertexNoB])
  CurrentCurve = cmds.polyToCurve(n='Cheek_FtProfileCurve#', form=2, degree=1, ch=False)

  # We then rebuild the curve for standardise number of points
  spanNumber = 6
  cmds.rebuildCurve(CurrentCurve, ch=False, rpo=True, end=True, kr=False, kep=True, s=spanNumber - 1, d=1)

  # We finally bind the respective mesh to the curves
  cmds.wire(mesh, w=CurrentCurve, dds=[0, 0.2])

def createChinEdgeControl(mesh, spanNumber = 6):
  """
  This function creates a control for the edge of the chin. It is used for the front profile
  Args:
    mesh: The mesh to work with

  """
  # We grab the border edges
  cmds.select(mesh)
  cmds.polySelectConstraint(mode=3, t=0x8000, where=1)
  borderEdges = cmds.ls(sl=True)
  borderEdges = cmds.filterExpand(borderEdges, ex=True, sm=32)
  cmds.polySelectConstraint(dis=True)

  CornerVertices = []
  # We find the corner vertices. Those are vertices with only 2 connecting edges
  for i in borderEdges:
    cmds.select(i)
    # First we convert the Edges into the 2 vertices
    EdgeVert = cmds.polyListComponentConversion(fe=True, tv=True)
    EdgeVert = cmds.filterExpand(EdgeVert, ex=True, sm=31)
    # We then check from the 2 vertices their respective connecting edges
    # The corner vertices will only have 2 connecting edges while the rest has 3
    cmds.select(EdgeVert[0])
    VertEdge = cleanUp(cmds.polyInfo(ve=True))
    if len(VertEdge) == 2:
      CornerVertices.append(EdgeVert[0])
    cmds.select(EdgeVert[1])
    VertEdge = cleanUp(cmds.polyInfo(ve=True))
    if len(VertEdge) == 2:
      CornerVertices.append(EdgeVert[1])

  CornerVertices = list(set(CornerVertices))

  if (len(CornerVertices) > 4):
    cmds.warning("There are more then 4 corners at the chin")
    return

  # Now we simply identify where the vertices are
  # We get the z axis of the corner vertices and we get the 2 lowest z axis
  ZAxes = []
  for i in CornerVertices:
    transformation = cmds.xform(i, q=True, t=True)
    ZAxes.append(transformation[2])

  bubblesort(ZAxes, CornerVertices)

  # With that, we grab the back corner vertices and create the control curve
  # We connect these vertices by finding the shortest path between and create the controls
  vertexNoA = CornerVertices[0].split(".vtx[")[1]
  vertexNoA = int(vertexNoA.split("]")[0])
  vertexNoB = CornerVertices[1].split(".vtx[")[1]
  vertexNoB = int(vertexNoB.split("]")[0])

  cmds.select(clear=True)
  cmds.polySelect(mesh, sep=[vertexNoA, vertexNoB])
  CurrentCurve = cmds.polyToCurve(n='Chin_FtProfileCurve#', form=2, degree=1, ch=False)

  # We then rebuild the curve for standardise number of points
  spanNumber = 6
  cmds.rebuildCurve(CurrentCurve, ch=False, rpo=True, end=True, kr=False, kep=True, s=spanNumber - 1, d=1)

  # We finally bind the respective mesh to the curves
  cmds.wire(mesh, w=CurrentCurve, dds=[0, 0.2])

def createCheekControl(mesh):
  """
  This is use as a soft selection handle for the cheek to adjust its roundness.
  It is not included in the current script but it is there as I am still developing the tool
  It would be used in the future
  Args:
    mesh: The mesh to work on
  """
  # Check if a softMod*Handle was created before hand. If it has, we know the newly created node name is different
  try:
    cmds.select("softMod*Handle")
    foundHandles = cmds.ls(sl=True)
  except:
    foundHandles = []

  # Create the new softMod Handle
  cmds.select(mesh)
  mel.eval('performSoftMod( 0, 1, 0, { float(0.0), float(0.0), float(0.0) } );')
  cmds.setToolTo("Move")

  # Select the newly created softMod Handle and rename accordingly
  cmds.select("softMod*Handle")
  newHandles = cmds.ls(sl=True)

  unique = list(set(newHandles).difference(foundHandles))

  if len(unique) > 1:
    cmds.error("More then one handle was created")
    return
  cmds.rename(unique[0], "CheekControlHandle#")

def createProfileControl(meshList, spanNumber = 4):
  """
  This function creates the profile controls for the mesh
  Args:
    meshList: The list of mesh to check if it is part of the side profile
  """
  for mesh in meshList:
    cmds.select(mesh)
    NumberOfEdges = cmds.polyEvaluate(edge = True)
    CenterEdge = []

    for i in range(0, NumberOfEdges):
      transformations = cmds.xform("%s.e[%s]" % (mesh, i), q=True, t=True, ws=True)
      if "e" in str(transformations[0]):
        transformations[0] = 0.0
      if "e" in str(transformations[3]):
        transformations[3] = 0.0

      if float("%.7f" % transformations[0]) == 0 and float("%.7f" % transformations[3]) == 0:
        CenterEdge.append("%s.e[%s]" % (mesh, i))

    # If there are no middle edges in the geo
    if len(CenterEdge) == 0:
      continue
    else:
      cmds.select(CenterEdge)
      CenterEdges = cmds.ls(sl=True)
      CenterEdges = cmds.filterExpand(CenterEdges, ex=True, sm=32)
      UniqueVertex = []
      for edge in CenterEdges:
        #Now we have to check if the edges are connected or not
        cmds.select(edge)
        VerticesSelected = cmds.polyListComponentConversion(fe = True, tv = True)
        VerticesSelected = cmds.filterExpand(VerticesSelected, ex=True, sm=31)
        for vertex in VerticesSelected:
          UniqueVertex.append(vertex)

      Elements = list(set(UniqueVertex))
      Unique = []
      for element in Elements:
        repeat = UniqueVertex.count(element)
        if repeat == 1:
          Unique.append(element)

      #Unique has the number of vertices that are not joined by other edges
      #If it is more then 2, that means there is a hole in the geometry
      if len(Unique) == 2:
        cmds.select(clear = True)
        for edge in CenterEdges:
          cmds.select(edge, add=True)
        CurrentCurve = cmds.polyToCurve(n='%s_ProfileCurve' % mesh, form=2, degree=1, ch=False)
        # We then rebuild the curve for standardise number of points
        spanNumber = 4
        cmds.rebuildCurve(CurrentCurve, ch=False, rpo=True, end=True, kr=False, kep=True, s=spanNumber - 1, d=1)

        # We finally bind the respective mesh to the curves
        if "TubxMouth_geo" in mesh:
          cmds.wire(mesh, w=CurrentCurve, dds=[0, 0.1])
        else:
          cmds.wire(mesh, w=CurrentCurve, dds=[0, 0.2])

      elif len(Unique) > 2:
        #There is a hole in between, so we have to create the profile curve slightly different
        littleCurve = []
        for edge in CenterEdges:
          cmds.select(edge)
          littleCurve.append(cmds.polyToCurve(n='tempProfileCurve' , form=2, degree=1, ch=False)[0])

        cmds.select(littleCurve)
        CurrentCurve = cmds.attachCurve(n='%s_ProfileCurve' % mesh, rpo=0, m=1, ch=False)

        # We then rebuild the curve for standardise number of points
        spanNumber = 4
        cmds.rebuildCurve(CurrentCurve, ch=False, rpo=True, end=True, kr=False, kep=True, s=spanNumber - 1, d=1)

        # We finally bind the respective mesh to the curves
        if "TubxMouth_geo" in mesh:
          cmds.wire(mesh, w=CurrentCurve, dds=[0, 0.1])
        else:
          cmds.wire(mesh, w=CurrentCurve, dds=[0, 0.2])

        #Cleanup
        cmds.delete(littleCurve)






