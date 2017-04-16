''' Deform Library
  This script creates the deformation relationship as well as deforms a mesh to
  its control points
'''

from maya import cmds
import math
import maya.mel as mel

import CreateRelationships
reload(CreateRelationships)

def reverseName(locatorGroup, name):
  """
  This functions reverse the locators in the opposite direction by renaming them to
  match the curves in Maya
  Args:
    locatorGroup: The group of locators to rename
    name: The name for the locators to be renamed to

  Returns: The list of the newly named locators
  """

  locatorList = cmds.listRelatives(locatorGroup)

  TempRename = []
  newLocatorList = []
  NumberList = []
  # We first rename all the locators to a default name to prevent name clashing
  # We also get the numerical digits the locators are
  for i in range(0, len(locatorList)):
    nameCoord = locatorList[i].rstrip('0123456789')
    numberCoord = locatorList[i][len(nameCoord):]
    NumberList.append(numberCoord)
    RenameObj = cmds.rename(locatorList[i], 'TempCoord#')
    TempRename.append(RenameObj)

  #We then reorder the locators in the reverse direction
  nameCount = 0
  for i in range(len(locatorList)- 1, -1, -1):
    newLocator = cmds.rename(TempRename[i], '%s%s' % (name, NumberList[nameCount]))
    newLocatorList.append(newLocator)
    nameCount+=1

  return newLocatorList

def getDistance(currentPos, deformPos):
  """
  This function gets the distance between the control position and the deform point
  Args:
    currentPos: The position of the control
    deformPos: The position of the deform point

  Returns: The distance calculated

  """
  distX = deformPos[0] - currentPos[0]
  distY = deformPos[1] - currentPos[1]
  distZ = deformPos[2] - currentPos[2]
  distance = distX*distX + distY*distY + distZ*distZ
  distance = math.sqrt(distance)
  return distance

def bubblesort(list, indexlist):
  """
  This function bubblesorts a list and alters a reference indexlist at the same time
  Args:
    list: The list to bubblesort the results with
    indexlist: The indexlist which gets bubblesorted according to the list
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

def getLocators(locatorGroup):
  """
  This function separates out the locators into its separate groups depending on which
  body part it represents
  Args:
    locatorGroup: The locator group to check and separate

  Returns: The separated locator lists
  """
  locatorList = cmds.listRelatives(locatorGroup)

  eyeLocators = []
  earLocators = []
  mouthLocators = []
  mouthLoopLocators = []
  noseLocators = []
  noseBridgeLocators = []
  eyebrowLocators = []
  sideLocators = []
  frontLocators = []

  for i in locatorList:
    if "Eye_Coord" in i:
      eyeLocators.append(i)
    if "Mouth_Coord" in i:
      mouthLocators.append(i)
    if "MouthLoop_Coord" in i:
      mouthLoopLocators.append(i)
    if "SideProfile_Coord" in i:
      sideLocators.append(i)
    if "FrontProfile_Coord" in i:
      frontLocators.append(i)
    if "Nose_Coord" in i:
      noseLocators.append(i)
    if "NoseBridge_Coord" in i:
      noseBridgeLocators.append(i)
    if "Eyebrow_Coord" in i:
      eyebrowLocators.append(i)
    if "Ear_Coord" in i:
      earLocators.append(i)


  return eyeLocators, earLocators, mouthLocators, mouthLoopLocators, noseLocators, noseBridgeLocators, eyebrowLocators, sideLocators, frontLocators

def grpLocators(points, index, coordName, coordGrpName):
  """
  This function group locators together
  Args:
    points: The number of points representing each group. This allow me to separate a group into
    2 parts if needed. For example if there are 2 eyes, each with 8 points. A 16 points input will
    let me know that there are 2 separate groups
    index: The current index I am checking for the correct locator to be added to the group
    coordName: The name of the coordinate to group
    coordGrpName: The name of the group of coordinates

  Returns: The group of coordinates

  """
  cmds.select(clear=True)
  for j in range(0, points):
    cmds.select("%s%s" % (coordName,str(j + index + 1)), add=True)
  CurrentGroup = cmds.group(n=coordGrpName)
  return CurrentGroup

def crossProduct (centerPoint, pointA, pointB):
  """
  The cross product between 2D vectors is used to check if a rotation is clockwise or anti-clockwise
  Args:
    centerPoint: The center point of the points to check. This represents the origin
    pointA: The point it start out
    pointB: The point it end up

  Returns: A boolean depending on whether it is clockwise or anti-clockwise.
  """

  # To check a circle direction, we use the cross product between the centerPoint to A and centerPoint to B
  a = centerPoint
  b = pointA
  c = pointB

  u = [(b[0] - a[0]), (b[1] - a[1]), (b[2] - a[2])]
  v = [(c[0] - a[0]), (c[1] - a[1]), (c[2] - a[2])]

  #CrossProduct = (u[1] * v[2] - u[2] * v[1]) + (u[2] * v[0] - u[0] * v[2]) + (u[0] * v[1] - u[1] * v[0])
  #print "3DCross is ", CrossProduct

  # We use the 2D Cross Product to get the clockwise or anti-clockwise direction
  CrossProduct = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
  #print "2DCross is ", CrossProduct

  if CrossProduct > 0:
    return 0
  elif CrossProduct < 0:
    return 1
  elif CrossProduct == 0:
    print "circular direction cross product is zero. Vectors are parallel"
    return

def checkCircularClockwise(CtrlCurve,DeformLocatorsGrp, points):
  """
  This function is a combination of various functions
  It takes in the ctrls and locators and check whether they are in the same direction using the
  crossProduct function. If they are not, it would reverse the deformation points using the
  reverseName function.
  Args:
    CtrlCurve: The control curve
    DeformLocatorsGrp: The deformation points
    points: The number of points that represents a body part

  Returns: A list of the corrected deform locators

  """
  # We first have to analyse the control curve
  controlPosList = []
  for i in range(0, points):
    ctrlPos = cmds.xform("%s.ep[%s]" % (CtrlCurve, i), q=True, t=True)
    controlPosList.append([i, ctrlPos])

  # We then get the middle X value of the curve
  cmds.xform(CtrlCurve, cp=True)
  middlePoint = cmds.xform(CtrlCurve, rp=True, q=True)

  # We check if the ctrl curve is moving clockwise or anti-clockwise
  CtrlClockwise = crossProduct(middlePoint, controlPosList[0][1], controlPosList[1][1])

  # We repeat the process for the DeformLocators
  # We first analyse the deform locators
  DeformLocators = cmds.listRelatives(DeformLocatorsGrp)
  # This is to get the name in case we have to reverse the direction of the controls
  nameCoord = DeformLocators[0].rstrip('0123456789')
  deformPosList = []
  for i in range(0, points):
    deformPos = cmds.xform(DeformLocators[i], q=True, t=True)
    deformPosList.append([i, deformPos])
  # We then get the middle X value of the locators
  cmds.xform(DeformLocatorsGrp, cp=True)
  middlePoint = cmds.xform(DeformLocatorsGrp, rp=True, q=True)

  # We check if the deform curve is moving clockwise or anti-clockwise
  DeformClockwise = crossProduct(middlePoint, deformPosList[0][1], deformPosList[1][1])

  print "CtrlClockwise is %s and DeformClockwise is %s" % (CtrlClockwise,DeformClockwise)


  # If the deform points are not in the same direction and the ctrl points, we reverse the deform
  if DeformClockwise != CtrlClockwise:
    print "Circle Control and deformation are going in opposite direction"
    print "Reversing Deformations"
    DeformLocators = reverseName(DeformLocatorsGrp, nameCoord)

  # After this stage, the deformation locators are in the correct direction. So we return the DeformationLocators
  return DeformLocators

def getCircularStartPoints(CtrlCurve,DeformLocatorsGrp, points):
  """
  This function gets a common start point between the control curve and deformation points
  for circular shapes
  Args:
    CtrlCurve: The control curve
    DeformLocatorsGrp: The deformation points
    points: The number of points that represents a body part

  Returns: The control start point, the deformation start point, the revised locator list

  """
  DeformLocators = cmds.listRelatives(DeformLocatorsGrp)
  print "Before ", CtrlCurve
  print DeformLocators
  # We first check and if necessary rearrange the deform locators to match the control curve direction
  DeformLocators = checkCircularClockwise(CtrlCurve, DeformLocatorsGrp, points)
  print "After ", CtrlCurve
  print DeformLocators

  # We then analyse the control curve
  controlPosList = []
  for i in range(0, points):
    ctrlPos = cmds.xform("%s.ep[%s]" % (CtrlCurve, i), q=True, t=True)
    controlPosList.append([i, ctrlPos])

  # We then get the middle X value of the curve
  cmds.xform(CtrlCurve, cp=True)
  middlePoint = cmds.xform(CtrlCurve, rp=True, q=True)
  midX = middlePoint[0]

  # Using the information we gathered from the ep pos, we find points closest to midX
  closestMidX = []
  closestMidIndex = []
  for i in range(0, points):
    distance = math.fabs(controlPosList[i][1][0] - midX)
    closestMidX.append(distance)
    closestMidIndex.append(controlPosList[i][0])
  bubblesort(closestMidX, closestMidIndex)

  # With the information we have, we find which points are above and which points are below
  YValueList = []
  YValueIndex = []
  for i in range(0, points / 2):
    YValueList.append(controlPosList[closestMidIndex[i]][1][1])
    YValueIndex.append(closestMidIndex[i])
  bubblesort(YValueList, YValueIndex)

  # Lastly, as we know its direction of movement, we compare the bottom 2 points to see which is further on the left
  if YValueIndex[0] == points - 1:
    controlStart = YValueIndex[0]
  elif YValueIndex[1] == points - 1:
    controlStart = YValueIndex[1]
  elif YValueIndex[0] < YValueIndex[1]:
    controlStart = YValueIndex[0]
  elif YValueIndex[1] < YValueIndex[0]:
    controlStart = YValueIndex[1]

  # We repeat the process for the DeformLocators
  # We first analyse the deform locators
  deformPosList = []
  for i in range(0, points):
    deformPos = cmds.xform(DeformLocators[i], q=True, t=True)
    deformPosList.append([i, deformPos])
  # We then get the middle X value of the locators
  cmds.xform(DeformLocatorsGrp, cp=True)
  middlePoint = cmds.xform(DeformLocatorsGrp, rp=True, q=True)
  midX = middlePoint[0]


  # Using the information we gathered from the locator pos, we find points closest to midX
  closestMidX = []
  closestMidIndex = []
  for i in range(0, points):
    distance = math.fabs(deformPosList[i][1][0] - midX)
    closestMidX.append(distance)
    closestMidIndex.append(deformPosList[i][0])
  bubblesort(closestMidX, closestMidIndex)
  # With the information we have, we find which points are above and which points are below
  YValueList = []
  YValueIndex = []
  for i in range(0, points / 2):
    YValueList.append(deformPosList[closestMidIndex[i]][1][1])
    YValueIndex.append(closestMidIndex[i])
  bubblesort(YValueList, YValueIndex)
  # Lastly, as we know it moves in an anti-clockwise fashion, we compare the bottom 2 locators to see which is further on the left
  if YValueIndex[0] == points - 1:
    deformStart = YValueIndex[0]
  elif YValueIndex[1] == points - 1:
    deformStart = YValueIndex[1]
  elif YValueIndex[0] < YValueIndex[1]:
    deformStart = YValueIndex[0]
  elif YValueIndex[1] < YValueIndex[0]:
    deformStart = YValueIndex[1]

  return controlStart, deformStart, DeformLocators

def deformEye(CtrlCurve, DeformLocatorsGrp, points):
  """
  This function deforms the eye
  Args:
    CtrlCurve: The control curve
    DeformLocatorsGrp: The deformation points
    points: the number of points to deform
  """

  #We get a reference point for the relationship between the control and the deformation
  #points = 16
  controlStart, deformStart, DeformLocators= getCircularStartPoints(CtrlCurve, DeformLocatorsGrp, points)

  #We now know which point is associated with which. We then deform the object
  #DeformLocators = cmds.listRelatives(DeformLocatorsGrp)
  count = -1
  loop = 0
  print DeformLocators
  while (count < points):
    #Create a prevention for infinity loop
    count+=1
    loop+=1
    if loop > 100:
      print "There is a coding error in the deform library deform Eye"
      break

    print "Control move from %s.ep[%s] to %s" % (CtrlCurve, controlStart, DeformLocators[deformStart])
    toMove = cmds.xform(DeformLocators[deformStart], q=True, t=True, ws=True)
    cmds.xform("%s.ep[%s]" % (CtrlCurve,controlStart), t = toMove, ws=True)

    controlStart +=1
    deformStart +=1
    if controlStart == points:
      controlStart = 0
    if deformStart == points:
      deformStart = 0

def deformEar(CtrlCurve, DeformLocatorsGrp):
  """
    This function deforms the ear
    Args:
      CtrlCurve: The control curve
      DeformLocatorsGrp: The deformation points
  """
  #We get a reference point for the relationship between the control and the deformation
  points = 5
  DeformLocators = matchVerticalLineDirection(points, CtrlCurve, DeformLocatorsGrp)

  # Since they are now in the same direction, we can easily get the start and end points
  controlStart = 0
  deformStart = 0
  # We now know which point is associated with which. We then deform the object
  loop = 0
  while controlStart < points:
    # Create a prevention for infinity loop
    loop += 1
    if loop > 100:
      print "There is a coding error in the deform library deform Ear"
      break

    toMove = cmds.xform(DeformLocators[deformStart], q=True, t=True, ws=True)
    cmds.xform("%s.ep[%s]" % (CtrlCurve, controlStart), t=toMove, ws=True)

    controlStart += 1
    deformStart += 1

def deformMouth(CtrlCurve, DeformLocatorsGrp, points):
  """
    This function deforms the mouth
    Args:
      CtrlCurve: The control curve
      DeformLocatorsGrp: The deformation points
      points: the number of points to deform
  """
  #We get a reference point for the relationship between the control and the deformation
  #points = 24
  controlStart, deformStart, DeformLocators = getCircularStartPoints(CtrlCurve, DeformLocatorsGrp, points)

  #We now know which point is associated with which. We then deform the object
  #DeformLocators = cmds.listRelatives(DeformLocatorsGrp)
  count = -1
  loop = 0
  while (count < points):
    #Create a prevention for infinity loop
    count+=1
    loop+=1
    if loop > 100:
      print "There is a coding error in the deform library deform Mouth"
      break

    toMove = cmds.xform(DeformLocators[deformStart], q=True, t=True, ws=True)
    cmds.xform("%s.ep[%s]" % (CtrlCurve,controlStart), t = toMove, ws=True)

    controlStart +=1
    deformStart +=1
    if controlStart == points:
      controlStart = 0
    if deformStart == points:
      deformStart = 0

def deformMouth2(CtrlCurve, DeformLocatorsGrp):
  """
    This function deforms the mouth.
    This function is not in used and was here to check between 2 different methods of deformation
    It remains here for me to switch between methods and compare as I am coding.
    Args:
      CtrlCurve: The control curve
      DeformLocatorsGrp: The deformation points
  """
  # The mouth curve deforms slightly differently
  # We get a list of all the available profile curves and match the points to the closest point in the profile deformation points
  ### Note: Try to pass by variable next time. For now, remember to add a clean up function
  points = 16
  DeformLocators = cmds.listRelatives(DeformLocatorsGrp)

  for ep in range(0,16):
    shortestDist = 99999
    transformPos = []
    deformToRemove = 0
    currentPos = cmds.xform("%s.ep[%s]" % (CtrlCurve, ep), t=True, q=True, ws=True)
    for deformPoint in DeformLocators:
      deformPos = cmds.xform(deformPoint, t=True, q=True, ws=True)
      distance = getDistance(currentPos, deformPos)
      if distance < shortestDist:
        shortestDist = distance
        transformPos = deformPos
        deformToRemove = deformPoint
    # Now we transform the ep to that position
    if not transformPos:
      cmds.error("No mouth was detected")
      return
    cmds.xform("%s.ep[%s]" % (CtrlCurve, ep), t=transformPos, ws=True)
    # We then remove that locator from the list. So that the same curve will not find the same point
    DeformLocators.remove(deformToRemove)

def deformMouthLoop(CtrlCurve, DeformLocatorsGrp, points):
  """
    This function deforms the mouth loop
    Args:
      CtrlCurve: The control curve
      DeformLocatorsGrp: The deformation points
      points: the number of points to deform
  """
  # We get a reference point for the relationship between the control and the deformation
  #points = 16
  # First we match the direction the control points and the deformation points are going
  DeformLocators = matchLineDirection(points, CtrlCurve, DeformLocatorsGrp)

  #Since they are now in the same direction, we can easily get the start and end points
  controlStart = 0
  deformStart = 0
  #We now know which point is associated with which. We then deform the object
  loop = 0
  while controlStart < points:
    # Create a prevention for infinity loop
    loop += 1
    if loop > 100:
      print "There is a coding error in the deform library deform MouthLoop"
      break

    toMove = cmds.xform(DeformLocators[deformStart], q=True, t=True, ws=True)
    cmds.xform("%s.ep[%s]" % (CtrlCurve, controlStart), t=toMove, ws=True)

    controlStart += 1
    deformStart += 1

def deformNose(CtrlCurve, DeformLocatorsGrp, points):
  """
    This function deforms the nose
    Args:
      CtrlCurve: The control curve
      DeformLocatorsGrp: The deformation points
      points: the number of points to deform
  """
  # We get a reference point for the relationship between the control and the deformation
  #points = 8
  # First we match the direction the control points and the deformation points are going
  DeformLocators = matchLineDirection(points, CtrlCurve, DeformLocatorsGrp)

  # Since they are now in the same direction, we can easily get the start and end points
  controlStart = 0
  deformStart = 0
  # We now know which point is associated with which. We then deform the object
  loop = 0
  while controlStart < points:
    # Create a prevention for infinity loop
    loop += 1
    if loop > 100:
      print "There is a coding error in the deform library deform Nose"
      break

    toMove = cmds.xform(DeformLocators[deformStart], q=True, t=True, ws=True)
    cmds.xform("%s.ep[%s]" % (CtrlCurve, controlStart), t=toMove, ws=True)

    controlStart += 1
    deformStart += 1

def deformNoseBridge(CtrlCurve, DeformLocatorsGrp, points):
  """
    This function deforms the noseBridge
    Args:
      CtrlCurve: The control curve
      DeformLocatorsGrp: The deformation points
      points: the number of points to deform
  """
  # We get a reference point for the relationship between the control and the deformation
  #points = 4
  # First we match the direction the control points and the deformation points are going
  DeformLocators = matchVerticalLineDirection(points, CtrlCurve, DeformLocatorsGrp)

  # Since they are now in the same direction, we can easily get the start and end points
  controlStart = 0
  deformStart = 0
  # We now know which point is associated with which. We then deform the object
  loop = 0
  while controlStart < points:
    # Create a prevention for infinity loop
    loop += 1
    if loop > 100:
      print "There is a coding error in the deform library deform NoseBridge"
      break

    toMove = cmds.xform(DeformLocators[deformStart], q=True, t=True, ws=True)
    cmds.xform("%s.ep[%s]" % (CtrlCurve, controlStart), t=toMove, ws=True)

    controlStart += 1
    deformStart += 1

def deformEyebrow(CtrlCurve, DeformLocatorsGrp, points):
  """
    This function deforms the eyebrow
    Args:
      CtrlCurve: The control curve
      DeformLocatorsGrp: The deformation points
      points: the number of points to deform
  """
  # We get a reference point for the relationship between the control and the deformation
  #points = 16
  # First we match the direction the control points and the deformation points are going
  DeformLocators = matchLineDirection(points, CtrlCurve, DeformLocatorsGrp)

  # Since they are now in the same direction, we can easily get the start and end points
  controlStart = 0
  deformStart = 0
  # We now know which point is associated with which. We then deform the object
  loop = 0
  while controlStart < points:
    # Create a prevention for infinity loop
    loop += 1
    if loop > 100:
      print "There is a coding error in the deform library deform Eyebrow"
      break

    # For the eyebrow control however, we would not want to move the middle bits and leave it to the
    # profile curve to move. This allows for more accurate deformations
    # We would also want a gradual transition. Thus we introduce the weight list
    # The weight list will be the t value for linear interpolation x = (t)(x1) + (1-t)(x2)
    # Where x1 is the deform position
    # x2 is the current position
    # t is the weight
    weightList = [1.0, 1.0, 1.0, 1.0, 0.7, 0.5, 0.3, 0.0,
                  0.0, 0.3, 0.5, 0.7, 1.0, 1.0, 1.0, 1.0]

    toMove = cmds.xform(DeformLocators[deformStart], q=True, t=True, ws=True)
    currentPos = cmds.xform("%s.ep[%s]" % (CtrlCurve, controlStart), q=True, t=True, ws=True)
    #using linear interpolation x = (t)(x1) + (1-t)(x2)
    t = weightList[controlStart]
    x1 = toMove
    x2 = currentPos

    linearMove = [(t*x1[0]) + ((1-t)*x2[0]), (t*x1[1]) + ((1-t)*x2[1]), (t*x1[2]) + ((1-t)*x2[2])]
    cmds.xform("%s.ep[%s]" % (CtrlCurve, controlStart), t=linearMove, ws=True)

    controlStart += 1
    deformStart += 1

def deformSideProfile(points = 4):
  """
  This function deforms the side profile
  Args:
    points: the number of points to deform
  """
  # The profile curve deforms slightly differently
  # We get a list of all the available profile curves and match the points to the closest point in the profile deformation points
  ### Note: Try to pass by variable next time. For now, remember to add a clean up function
  try:
    cmds.select("SideProfile_Coord*")
  except ValueError:
    return
  coordGrpName = "SideProfileCoordGrp#"
  # As there can only be one side profile
  CurrentGroup = cmds.group(n=coordGrpName)

  cmds.select("*_ProfileCurve")
  ProfileCurves = cmds.ls(sl=True)

  for curve in ProfileCurves:
    # Create a duplicate list of locators
    DeformLocators = cmds.listRelatives(CurrentGroup)
    # As each curve has 4 points by default, we go through each of them and find the closest deform point
    for ep in range(0, points):
      shortestDist = 99999
      transformPos = []
      deformToRemove = 0
      currentPos = cmds.xform("%s.ep[%s]" % (curve, ep), t=True, q=True, ws=True)
      for deformPoint in DeformLocators:
        deformPos = cmds.xform(deformPoint, t=True, q=True, ws=True)
        distance = getDistance(currentPos, deformPos)
        if distance < shortestDist:
          shortestDist = distance
          transformPos = deformPos
          deformToRemove = deformPoint
      # Now we transform the ep to that position
      if not transformPos:
        cmds.error("No profile position was detected")
        return
      cmds.xform("%s.ep[%s]" % (curve, ep), t=transformPos, ws=True)
      # We then remove that locator from the list. So that the same curve will not find the same point
      DeformLocators.remove(deformToRemove)

def deformFrontProfile(points = 6):
  """
  This function deforms the side profile
  Args:
    points: the number of points to deform
  """
  # The profile curve deforms slightly differently
  # We get a list of all the available profile curves and match the points to the closest point in the profile deformation points
  ### Note: Try to pass by variable next time. For now, remember to add a clean up function

  try:
    cmds.select("FrontProfile_Coord*")
  except ValueError:
    return

  coordGrpName = "FrontProfileCoordGrp#"
  # As there can only be one side profile
  CurrentGroup = cmds.group(n=coordGrpName)

  cmds.select("*_FtProfileCurve*")
  ProfileCurves = cmds.ls(sl=True)
  TempCurves = []
  for i in ProfileCurves:
    if "Base" not in str(i) and "Shape" not in str(i):
      TempCurves.append(i)

  ProfileCurves = TempCurves

  for curve in ProfileCurves:
    # Create a duplicate list of locators
    DeformLocators = cmds.listRelatives(CurrentGroup)
    # As each curve has 6 points by default, we go through each of them and find the closest deform point
    for ep in range(0, points):
      shortestDist = 99999
      transformPos = []
      deformToRemove = 0
      currentPos = cmds.xform("%s.ep[%s]" % (curve, ep), t=True, q=True, ws=True)
      for deformPoint in DeformLocators:
        deformPos = cmds.xform(deformPoint, t=True, q=True, ws=True)
        distance = getDistance(currentPos, deformPos)
        if distance < shortestDist:
          shortestDist = distance
          transformPos = deformPos
          deformToRemove = deformPoint
      # Now we transform the ep to that position
      if not transformPos:
        cmds.error("No profile position was detected")
        return
      #print "Transforming %s.ep[%s]" % (curve, ep)
      cmds.xform("%s.ep[%s]" % (curve, ep), t=transformPos, ws=True)
      # We then remove that locator from the list. So that the same curve will not find the same point
      DeformLocators.remove(deformToRemove)

def matchLineDirection(points, CtrlCurve, DeformLocatorsGrp):
  """
  This function matches a horizontal line direction to find a common point
  Args:
    points: The number of points that represents a line
    CtrlCurve: The control curves
    DeformLocatorsGrp: The deformation points

  Returns: The deformation locators

  """
  DeformLocators = cmds.listRelatives(DeformLocatorsGrp)
  # Since the ctrl curve is a line, we check if the index 0 of the ctrl curve and the last index is on the left or on the right
  ctrlPosStart = cmds.xform("%s.ep[0]" % CtrlCurve, q=True, t=True)
  ctrlPosEnd = cmds.xform("%s.ep[%s]" % (CtrlCurve, points - 1), q=True, t=True)
  ctrlClockwise = -1
  if ctrlPosStart[0] > ctrlPosEnd[0]:
    # The curve is clockwise
    ctrlClockwise = 1
  else:
    # The curve is anticlockwise
    ctrlClockwise = 0

  # We then do the same check for the deformation locators
  nameCoord = DeformLocators[0].rstrip('0123456789')
  deformPosStart = cmds.xform("%s1" % nameCoord, q=True, t=True)
  deformPosEnd = cmds.xform("%s%s" % (nameCoord,points), q=True, t=True)
  deformClockwise = -1
  if deformPosStart[0] > deformPosEnd[0]:
    # The curve is clockwise
    deformClockwise = 1
  else:
    # The curve is anticlockwise
    deformClockwise = 0

  # Now we know the direction of the deformations and controls
  # For ease, we reverse the deformation to match the curves if necessary
  if ctrlClockwise != deformClockwise:
    print "Control and deformation are going in opposite direction"
    print "Reversing Deformations"
    DeformLocators = reverseName(DeformLocatorsGrp, nameCoord)

  return DeformLocators

def matchVerticalLineDirection(points, CtrlCurve, DeformLocatorsGrp):
  """
  This function matches the direction of a vertical line
  Args:
    points: The number of points that represents a body part
    CtrlCurve: The control curve
    DeformLocatorsGrp: The deformation points

  Returns: The deformation locators

  """
  DeformLocators = cmds.listRelatives(DeformLocatorsGrp)
  # Since the ctrl curve is a line, we check if the index 0 of the ctrl curve and the index 16 is on top or bottom
  ctrlPosStart = cmds.xform("%s.ep[0]" % CtrlCurve, q=True, t=True)
  ctrlPosEnd = cmds.xform("%s.ep[%s]" % (CtrlCurve, points - 1), q=True, t=True)
  ctrlTop = -1
  if ctrlPosStart[1] > ctrlPosEnd[1]:
    # The curve start from top and goes to bottom
    ctrlTop = 1
  else:
    # The curve starts from bottom and goes to top
    ctrlTop = 0

  # We then do the same check for the deformation locators
  nameCoord = DeformLocators[0].rstrip('0123456789')
  startNum = DeformLocators[0][len(nameCoord):]
  print "startNum is %s" % startNum
  deformPosStart = cmds.xform("%s%s" % (nameCoord, startNum), q=True, t=True)
  deformPosEnd = cmds.xform("%s%s" % (nameCoord, (int(startNum) + points-1)), q=True, t=True)
  deformTop = -1
  if deformPosStart[1] > deformPosEnd[1]:
    # The deform points start from top and goes to bottom
    deformTop = 1
  else:
    # The deform points start from bottom and goes to top
    deformTop = 0

  # Now we know the direction of the deformations and controls
  # For ease, we reverse the deformation to match the curves if necessary
  if ctrlTop != deformTop:
    print "Control and deformation are going in opposite direction"
    print "Reversing Deformations"
    DeformLocators = reverseName(DeformLocatorsGrp, nameCoord)

  return DeformLocators

def cleanUpforEdit(locatorGroup, Objects, relationshipList):
  """
  This function is to clean up the mesh and average the inside vertices after deformation.
  This function is not used but is used as a check to compare the order of cleanup
  Args:
    locatorGroup: The locator group to delete
    Objects: The objects to clean up
    relationshipList: The relationship list to attach the child back to the parent

  """
  for i in Objects:
    CreateRelationships.averageInsideVertices(i)
    cmds.select(i)
    mel.eval('SculptGeometryToolOptions;')
    mel.eval('artPuttyCtx -e -opacity 1.0 `currentCtx`;')
    mel.eval('artPuttyCtx -e -clear `currentCtx`;')
    mel.eval('setToolTo $gMove;')
    cmds.delete(i, ch=True)

  cmds.delete(locatorGroup)
  #Need to give a better name
  cmds.select("*Curve*")
  cmds.delete()
  CreateRelationships.findRelationships(relationshipList)

def cleanUpforEdit2(locatorGroup, Objects, relationshipList, mesh):
  """
  This function is to clean up the mesh and average the inside vertices after deformation.
  Args:
    locatorGroup: The locator group to delete
    Objects: The objects to clean up
    relationshipList: The relationship list to attach the child back to the parent
    mesh: The initial mesh to delete
  """

  # We first delete the locators
  cmds.delete(locatorGroup)
  # We also delete the initial mesh
  cmds.delete(mesh)

  # We then delete the objects history so that the curves no longer influence the object
  for i in Objects:
    cmds.delete(i, ch=True)

  # Need to give a better name
  # We then delete the curves and combine the geometry based on the relationship
  cmds.select("*Curve*")
  cmds.delete()
  CreateRelationships.findRelationships(relationshipList)

  # We average out the vertices for each part
  for i in Objects:
    print "Smoothing ", i
    CreateRelationships.averageInsideVertices(i)
    cmds.select(i)
    mel.eval('SculptGeometryTool;')
    try:
      mel.eval('artPuttyCtx -e -mtm "relax" `currentCtx`;')
    except:
      pass
    mel.eval('artPuttyCtx -e -opacity 1.0 `currentCtx`;')
    mel.eval('artPuttyCtx -e -clear `currentCtx`;')
    mel.eval('setToolTo $gMove;')
    cmds.delete(i, ch=True)

  # We then combine the objects together and merge the matching vertices
  cmds.select(Objects)
  mesh = cmds.polyUnite(n = mesh, ch = 0)
  cmds.polyMergeVertex(mesh, d =  0.0001, am=True, ch = 0)

  # We finally do a quick smooth through the mesh vertices
  cmds.select(mesh)
  mel.eval('SculptGeometryTool;')
  mel.eval('artPuttyCtx -e -mtm "relax" `currentCtx`;')
  mel.eval('artPuttyCtx -e -opacity 1.0 `currentCtx`;')
  mel.eval('artPuttyCtx -e -clear `currentCtx`;')
  mel.eval('setToolTo $gMove;')

def matchCircleDirectionTest(locatorGroup):
  """
  This is a testing function to test if the checking of the circle direction is working
  It is not used anywhere in the program but served as a means for testing
  Args:
    locatorGroup: The locator group to seperate the locators
  """
  eyeLocators, earLocators, mouthLocators, mouthLoopLocators, noseLocators, \
  noseBridgeLocators, eyebrowLocators, sideLocators, frontLocators = getLocators(locatorGroup)

  count = 1
  points = 8
  coordName = "Eye_Coord"
  coordGrpName = "EyeCoordGrp#"
  curveName = "EyeCurve"
  for i in range(0, len(eyeLocators), points):
    CurrentGroup = grpLocators(points, i, coordName, coordGrpName)
    print "CurrentGroup initially is"
    print CurrentGroup
    deformEye("%s%s" % (curveName, count), CurrentGroup)
    count += 1

  """
  count = 1
  points = 16
  coordName = "Mouth_Coord"
  coordGrpName = "MouthCoordGrp#"
  curveName = "InnerMouthCurve"
  for i in range(0, len(mouthLocators), points):
    CurrentGroup = grpLocators(points, i, coordName, coordGrpName)
    deformMouth("%s%s" % (curveName, count), CurrentGroup)
    count += 1
  """

def deformGeoToImage(locatorGroup, resolutionList):
  """
  This function deforms the geometry to the image
  Args:
    locatorGroup: The locators of the 2D Scan points
    resolutionList: The resolutionList contains points for the resolution of the control
                      resolutionList = [eye, mouth, mouthloop, nose, eyebrow, nosebridge]

  """
  eyeLocators, earLocators, mouthLocators, mouthLoopLocators, noseLocators, \
  noseBridgeLocators, eyebrowLocators, sideLocators, frontLocators = getLocators(locatorGroup)

  count = 1
  points = resolutionList[0]
  coordName = "Eye_Coord"
  coordGrpName = "EyeCoordGrp#"
  curveName = "EyeCurve"
  for i in range(0, len(eyeLocators), points):
    CurrentGroup = grpLocators(points, i, coordName, coordGrpName)
    deformEye("%s%s" % (curveName,count), CurrentGroup, points)
    count+=1

  count = 1
  points = resolutionList[1]
  coordName = "Mouth_Coord"
  coordGrpName = "MouthCoordGrp#"
  curveName = "InnerMouthCurve"
  for i in range(0, len(mouthLocators), points):
    CurrentGroup = grpLocators(points, i, coordName, coordGrpName)
    deformMouth("%s%s" % (curveName,count), CurrentGroup, points)
    count+=1

  '''
  # This part of the function is used to compare between the deformMouth function and the
  # deformMouth2 function

  cmds.select(mouthLocators)
  CurrentGroup = cmds.group(n = coordGrpName)

  cmds.select("%s*" % curveName)
  selection = cmds.ls(sl=True)
  CtrlCurves = []
  for i in selection:
    if "BaseWire" not in i and "Shape" not in i:
      CtrlCurves.append(i)
  number = len(CtrlCurves)
  print CtrlCurves
  for i in range(0, number):
    deformMouth2("%s%s" % (curveName, count), CurrentGroup)
    count += 1
  '''

  count = 1
  points = resolutionList[2]
  coordName = "MouthLoop_Coord"
  coordGrpName = "MouthLoopCoordGrp#"
  curveName = "MouthLoopCurve"
  for i in range(0, len(mouthLoopLocators), points):
    CurrentGroup = grpLocators(points, i, coordName, coordGrpName)
    deformMouthLoop("%s%s" % (curveName, count), CurrentGroup, points)
    count += 1

  count = 1
  points = resolutionList[3]
  coordName = "Nose_Coord"
  coordGrpName = "NoseCoordGrp#"
  curveName = "NoseCurve"
  for i in range(0, len(noseLocators), points):
    CurrentGroup = grpLocators(points, i, coordName, coordGrpName)
    deformNose("%s%s" % (curveName, count), CurrentGroup, points)
    count += 1

  count = 1
  points = resolutionList[4]
  coordName = "Eyebrow_Coord"
  coordGrpName = "EyebrowCoordGrp#"
  curveName = "LowerForeheadCurve"
  for i in range(0, len(eyebrowLocators), points):
    CurrentGroup = grpLocators(points, i, coordName, coordGrpName)
    deformEyebrow("%s%s" % (curveName, count), CurrentGroup, points)
    count += 1

  count = 1
  points = 5
  coordName = "Ear_Coord"
  coordGrpName = "EarCoordGrp#"
  curveName = "EarCurve"
  for i in range(0, len(earLocators), points):
    CurrentGroup = grpLocators(points, i, coordName, coordGrpName)
    deformEar("%s%s" % (curveName, count), CurrentGroup)
    count += 1

  #The nose bridge is a unique case as the curves are seperated but the deformation points are not
  points = resolutionList[5]
  coordName = "NoseBridge_Coord"
  rtcount = 1
  lfcount = 1
  rtcoordGrpName = "NoseBridgeRtCoordGrp#"
  lfcoordGrpName = "NoseBridgeLfCoordGrp#"
  rtcurveName = "RtNoseBridgeCurve"
  lfcurveName = "LfNoseBridgeCurve"
  alternate = 0

  for i in range(0, len(noseBridgeLocators), points):
    if alternate%2 == 0:
      CurrentGroup = grpLocators(points, i, coordName, rtcoordGrpName)
      deformNoseBridge("%s%s" % (rtcurveName, rtcount), CurrentGroup, points)
      rtcount +=1

    elif alternate%2 == 1:
      CurrentGroup = grpLocators(points, i, coordName, lfcoordGrpName)
      deformNoseBridge("%s%s" % (lfcurveName, lfcount), CurrentGroup, points)
      lfcount+=1

    alternate+=1

  # The profile curve deforms slightly differently
  # We get a list of all the available profile curves and match the points to the closest point in the profile deformation points
  ### Note: Try to pass by variable next time. For now, remember to add a clean up function
  deformSideProfile()
  deformFrontProfile()


