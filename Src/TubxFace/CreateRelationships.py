'''  CreateRelationships
  This python script creates a parent and child relationships between vertices.
  This allows child vertices to find their parents after deformations
'''

from maya import cmds

def createRelationships(RelationShipList, mainMesh, otherMesh):
  """
  This functions takes the main mesh and another mesh and compare matching vertices.
  If a vertex of the mainMesh is the same as the otherMesh, we add it to the RelationShipList
  The vertex of the mainMesh becomes the child
  Args:
    RelationShipList: The list to store all the vertex relationships
    mainMesh: The main mesh is the mesh we want to check matching vertex with
    otherMesh: The other mesh to check against the main mesh
  """

  # We first get a list of border edges the mainMesh has
  cmds.select(mainMesh)
  cmds.polySelectConstraint(m=3, t=0x8000, w=1)
  MainBorderEdges = cmds.ls(sl=True)
  MainBorderEdges = cmds.filterExpand(MainBorderEdges, ex=True, sm=32)
  cmds.polySelectConstraint(dis=True)

  # We then convert these edges to vertices
  MainBorderVert = cmds.polyListComponentConversion(fe=True, tv=True)
  MainBorderVert = cmds.filterExpand(MainBorderVert, ex=True, sm=31)

  # With the vertices that we got, we get the position they are in
  MainBorderPosition = []

  for vert in MainBorderVert:
    position = cmds.xform(vert, q=True, t=True, ws=True)
    #Remove Maya's annoying exponential which is basically 0
    if "e" in str(position[0]):
      position[0] = 0.0
    if "e" in str(position[1]):
      position[1] = 0.0
    if "e" in str(position[2]):
      position[2] = 0.0
    MainBorderPosition.append([vert, position])


  # We then get a list of the border edges of the other mesh
  cmds.select(otherMesh)
  cmds.polySelectConstraint(m=3, t=0x8000, w=1)
  OtherBorderEdges = cmds.ls(sl=True)
  OtherBorderEdges = cmds.filterExpand(OtherBorderEdges, ex=True, sm=32)
  cmds.polySelectConstraint(dis=True)

  # We then convert these edges to vertices
  OtherBorderVert = cmds.polyListComponentConversion(fe=True, tv=True)
  OtherBorderVert = cmds.filterExpand(OtherBorderVert, ex=True, sm=31)

  # With the vertices that we got, we get the position they are in
  OtherBorderPosition = []

  for vert in OtherBorderVert:
    position = cmds.xform(vert, q=True, t=True, ws=True)
    # Remove Maya's annoying exponential which is basically 0
    if "e" in str(position[0]):
      position[0] = 0.0
    if "e" in str(position[1]):
      position[1] = 0.0
    if "e" in str(position[2]):
      position[2] = 0.0
    OtherBorderPosition.append([vert, position])


  # We then compare the positions. If they match, we get the matching vertices and create a relationship
  MatchVertices = []
  for i in range(0, len(MainBorderPosition)):
    similar = 0
    for j in range(0, len(OtherBorderPosition)):
      if MainBorderPosition[i][1] == OtherBorderPosition[j][1]:
        if checkUniqueChild(RelationShipList, MainBorderPosition[i][0]) == 1:
          MatchVertices.append([MainBorderPosition[i][0], OtherBorderPosition[j][0]])

  for i in MatchVertices:
    RelationShipList.append(i)

def findRelationships(RelationShipList):
  """
  This function allows the child vertices to find the parent vertices
  Args:
    RelationShipList: The relationship list
  """
  for i in RelationShipList:
    getPos = cmds.xform(i[1], q=True, t=True, ws=True)
    cmds.xform(i[0], t=getPos, ws=True)

def checkUniqueChild(RelationShipList, child):
  """
  This function checks if the child vertex has been registered before in the relationship list
  Args:
    RelationShipList: The relationship list to check
    child: The child to check

  Returns: Returns 1 of unique and 0 if not.
  """
  if not RelationShipList:
    return 1
  for i in RelationShipList:
    if i[0] == child:
      return 0
  return 1

def meshRelationships(Objects):
  """
  This function checks through the objects in the scene and creates the relationship list
  Args:
    Objects: The mesh parts of the face mesh

  Returns: The relationship List

  """
  # Create some variables to be used to store objects
  foreheadVariable = []
  noseBridgeVariable = []
  noseVariable = []
  eyeVariable = []
  mouthLoopVariable = []
  mouthVariable = []
  cheekVariable = []
  chinVariable = []
  earVariable = []
  backHeadVariable = []
  lowerBackHeadVariable = []

  # Create the relationshipList
  relationshipList = []

  for forehead in Objects:
    if "TubxForehead_geo_" in forehead:
      foreheadVariable.append(forehead)

  for noseBridge in Objects:
    if "TubxNoseBridge_geo_" in noseBridge:
      noseBridgeVariable.append(noseBridge)
      for forehead in foreheadVariable:
        createRelationships(relationshipList, noseBridge, forehead)

  for eye in Objects:
    if "TubxEye_geo_" in eye:
      eyeVariable.append(eye)
      for forehead in foreheadVariable:
        createRelationships(relationshipList, eye, forehead)
      for noseBridge in noseBridgeVariable:
        createRelationships(relationshipList, eye, noseBridge)

  for nose in Objects:
    if "TubxNose_geo_" in nose:
      noseVariable.append(nose)
      for noseBridge in noseBridgeVariable:
        createRelationships(relationshipList, nose, noseBridge)

  for mouthLoop in Objects:
    if "TubxMouthLoop_geo_" in mouthLoop:
      mouthLoopVariable.append(mouthLoop)
      for nose in noseVariable:
        createRelationships(relationshipList, mouthLoop, nose)

  for mouth in Objects:
    if "TubxMouth_geo_" in mouth:
      mouthVariable.append(mouth)
      for mouthLoop in mouthLoopVariable:
        createRelationships(relationshipList, mouth, mouthLoop)

  for cheek in Objects:
    if "TubxCheek_geo_" in cheek:
      cheekVariable.append(cheek)
      for mouthLoop in mouthLoopVariable:
        createRelationships(relationshipList, cheek, mouthLoop)

  for chin in Objects:
    if "TubxChin_geo_" in chin:
      chinVariable.append(chin)
      for mouthLoop in mouthLoopVariable:
        createRelationships(relationshipList, chin, mouthLoop)
      for cheek in cheekVariable:
        createRelationships(relationshipList, chin, cheek)

  for ear in Objects:
    if "TubxEar_geo_" in ear:
      earVariable.append(ear)
      for forehead in foreheadVariable:
        createRelationships(relationshipList, ear, forehead)
      for cheek in cheekVariable:
        createRelationships(relationshipList, ear, cheek)

  for backhead in Objects:
    if "TubxBackHead_geo_" in backhead:
      backHeadVariable.append(backhead)
      for forehead in foreheadVariable:
        createRelationships(relationshipList, backhead, forehead)
      for ear in earVariable:
        createRelationships(relationshipList, backhead, ear)

  for lowerbackhead in Objects:
    if "TubxLowerBackHead_geo_" in lowerbackhead:
      lowerBackHeadVariable.append(lowerbackhead)
      for ear in earVariable:
        createRelationships(relationshipList, lowerbackhead, ear)
      for backhead in backHeadVariable:
        createRelationships(relationshipList, lowerbackhead, backhead)

  for default in Objects:
    for forehead in foreheadVariable:
      createRelationships(relationshipList, default, forehead)
    for noseBridge in noseBridgeVariable:
      createRelationships(relationshipList, default, noseBridge)
    for nose in noseVariable:
      createRelationships(relationshipList,default,nose)
    for eye in eyeVariable:
      createRelationships(relationshipList, default, eye)
    for mouthLoop in mouthLoopVariable:
      createRelationships(relationshipList, default, mouthLoop)
    for mouth in mouthVariable:
      createRelationships(relationshipList, default, mouth)
    for cheek in cheekVariable:
      createRelationships(relationshipList, default, cheek)
    for chin in chinVariable:
      createRelationships(relationshipList, default, chin)
    for ear in earVariable:
      createRelationships(relationshipList, default, ear)
    for backhead in backHeadVariable:
      createRelationships(relationshipList, default, backhead)
    for lowerbackhead in lowerBackHeadVariable:
      createRelationships(relationshipList, default, lowerbackhead)

  return relationshipList

def averageInsideVertices(mesh):
  """
  This function grabs the inside vertices of the mesh and average out the distance between
  Args:
    mesh: The mesh to average vertices
  """
  cmds.select(mesh)
  cmds.polySelectConstraint(m=3, t=0x0001, w=2)
  cmds.polySelectConstraint(dis=True)
  cmds.polyAverageVertex(i = 10, ch = 0)

