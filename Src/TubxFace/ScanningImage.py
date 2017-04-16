'''
This script scans the image for the various body parts
'''
from maya import cmds
import MayaImageReading
reload(MayaImageReading)

class ImageScan:
  """
  This class creates an object that takes in the front and side image and gets the 3D coordinates
  """
  def __init__(self, frontImagePath, sideImagePath):
    self.frontImage = MayaImageReading.MayaImage(frontImagePath)
    self.sideImage = MayaImageReading.MayaImage(sideImagePath)

  #The calling functions
  def generateCoord(self, resolutionList):
    """
    This function scans the image
    Args:
      resolutionList: The resolutionList contains points for the resolution of the control
                      resolutionList = [eye, mouth, mouthloop, nose, eyebrow, nosebridge]

    Returns: The scanned locators
    """
    locatorList = []

    print "Scanning Eye"
    self.getEyeCoord(locatorList, resolutionList[0])
    print "Got Eye Coord"
    print "Scanning NoseBridge"
    self.getNoseBridgeCoord(locatorList, resolutionList[5])
    print "Got NoseBridge Coord"
    print "Scanning Nose"
    self.getNoseCoord(locatorList, resolutionList[3])
    print "Got Nose Coord"
    print "Scanning Mouth"
    self.getMouthCoord(locatorList, resolutionList[1])
    print "Got Mouth Coord"
    print "Scanning MouthLoop"
    self.getMouthLoopCoord(locatorList, resolutionList[2])
    print "Got MouthLoop Coord"
    print "Scanning Eyebrow"
    self.getEyebrowCoord(locatorList, resolutionList[4])
    print "Got Eyebrow Coord"
    print "Scanning Ear"
    self.getEarCoord(locatorList)
    print "Got Ear Coord"
    print "Scanning SideProfile"
    self.getSideProfileCoord(locatorList)
    print "Got SideProfile Coord"

    print "Scanning FrontProfile"
    self.getFrontProfileCoord(locatorList)
    print "Got FrontProfile Coord"

    #Grouping locatorList
    cmds.select(locatorList)
    locatorGrp = cmds.group(name = "LocatorCoordGrp#")

    self.scaleToUnitVolume(locatorGrp)

    self.reverseName(locatorGrp)
    for locator in locatorList:
      if "SideProfile_Coord" in locator:
        cmds.move(0, locator, x=True, ws=True)
    return locatorGrp

  #The functions
  def getFrontCoord(self, colour, startCoord, rowDirection, columnDirection, arrangement, isLine, points):
    """
    This function scans the image for the front coordinate
    Args:
      colour: The colour to scan
      startCoord: The coordinate to start
      rowDirection: The row direction
      columnDirection: The column direction
      arrangement: How the scanned data should be arranged to have a common point
      isLine: Whether the scan data is supposed to be a line or a circle
      points: How many points makes up that object

    Returns: The list of coordinates for the front view

    """
    print "Doing Front"
    # We create a list to hold the front coordinates
    meshFrontLocation = []

    # We create a mechanism that triggers when there is infinite loop
    CountLoop = 0

    # Loop front view till no intended colour is detected
    while True:
      # Trigger mechanism when there is infinite loop
      CountLoop += 1
      if CountLoop > 10000:
        print "CountLoop is more then 10000, mechanism to prevent infinite loop during get3DCoord activated"
        break

      # Detect the colour pixel
      PixelDetected = self.frontImage.detectColourPixel(colour, startCoord, rowDirection, columnDirection)

      # If pixel is detected
      if len(PixelDetected) != 0:
        # traceLine(self, colour, StartCoord, rowScan, columnScan)
        CoordList, startCoord = self.frontImage.traceLine(colour, PixelDetected, rowDirection, columnDirection)
        # We rearrange to coordlist to a certain arrangement so we can get the same starting point in front and side
        CoordList = self.rearrange(CoordList, arrangement)

        # We check if it is a line or not. If it is a line, we half the coordinates
        if isLine == 1:
          CoordList = CoordList[:len(CoordList) / 2]
        # We then take note of a certain number of points in the CoordList


        stride = len(CoordList) / float(points)

        # We add the coordinates to the meshFrontLocation list
        #Safety mechanism for infinite loop
        loopTrigger = 0
        currentIndex = 0.0
        while loopTrigger < points:
          loopTrigger +=1
          if loopTrigger > 10000:
            print "Infinite loop in front coord scanning stride part!!"
            break
          i = int(currentIndex)
          meshFrontLocation.append([CoordList[i][0], CoordList[i][1]])
          currentIndex+=stride

      # If no pixel is detected
      else:
        break

    return meshFrontLocation

  def getSideCoord(self, colour, startCoord, rowDirection, columnDirection, arrangement, isLine):
    """
    This function scans the image for the side coordinate
    Args:
      colour: The colour to scan
      startCoord: The coordinate to start
      rowDirection: The row direction
      columnDirection: The column direction
      arrangement: How the scanned data should be arranged to have a common point
      isLine: Whether the scan data is supposed to be a line or a circle

    Returns: The list of coordinates for the side view

    """
    print "Doing Side"
    # We create a list to hold the side coordinates
    meshSideLocation = []

    # We create a mechanism that triggers when there is infinite loop
    CountLoop = 0

    # Loop side view till no intended colour is detected
    while True:
      # Trigger mechanism when there is infinite loop

      CountLoop += 1

      if CountLoop > 10000:
        print "CountLoop is more then 10000, mechanism to prevent infinite loop during get3DCoord activated"
        break

      # Detect the colour pixel
      PixelDetected = self.sideImage.detectColourPixel(colour, startCoord, rowDirection, columnDirection)

      # If pixel is detected
      if len(PixelDetected) != 0:
        # traceLine(self, colour, StartCoord, rowScan, columnScan)
        CoordList, startCoord = self.sideImage.traceLine(colour, PixelDetected, rowDirection, columnDirection)
        # We rearrange to coordlist to a certain arrangement so we can get the same starting point in front and side
        CoordList = self.rearrange(CoordList, arrangement)
        # We check if it is a line or not. If it is a line, we half the coordinates
        if isLine == 1:
          CoordList = CoordList[:len(CoordList) / 2]

        # We add the coordinates to the meshSideLocation list
        for i in range(0, len(CoordList)):
          meshSideLocation.append([CoordList[i][0], CoordList[i][1]])

      # If no pixel is detected
      else:
        break

    return meshSideLocation

  def get3DCoord(self, colour, startCoord, rowDirection, columnDirection, points, isLine = 1, arrangement = "LowestY"):
    """
    This function gets the 3D coordinates of a front and side view
    Args:
      colour: The colour to detect
      startCoord: The start coordinates of the scan
      rowDirection: The row direction
      columnDirection: The column direction
      points: The number of points to scan
      isLine: Whether we are scanning a circle or a line
      arrangement: How the data should be arranged to start from a common point

    Returns: The 3D coordinates

    """
    #We create a list to store the coordinates results

    meshFrontLocation = self.getFrontCoord(colour, startCoord, rowDirection, columnDirection, arrangement, isLine, points)
    print "mesh front location has %s points" % len(meshFrontLocation)

    #We check if any colour is detected in the front view first before we scan side view
    if len(meshFrontLocation) == 0:
      return

    #Reset the startCoord
    meshSideLocation = self.getSideCoord(colour, startCoord, rowDirection, columnDirection, arrangement, isLine)


    #We check if any colour is detected in the side view. If there is no colour, there is an error
    if len(meshSideLocation) == 0:
      print "Detected colour [%s, %s, %s] in front but not side. Please check" % (colour[0], colour[1], colour[2])
      return

    print "mesh side location has %s points" % len(meshSideLocation)

    #We now fix the offset between the front and the side location
    #We get the highest and lowest y value from the front location
    TempFront = meshFrontLocation
    FrontLowestY = self.rearrange(TempFront, "LowestY")[0][1]
    FrontHighestY = self.rearrange(TempFront, "HighestY")[0][1]
    TempSide = meshSideLocation
    SideLowestY = self.rearrange(TempSide, "LowestY")[0][1]
    SideHighestY = self.rearrange(TempSide, "HighestY")[0][1]

    #We then get the middle y for the 2 views and get the offset
    #We keep it to int as pixels doesn't exist as floats.
    FrontMiddleY = (FrontLowestY + FrontHighestY) / 2
    SideMiddleY = (SideLowestY + SideHighestY) / 2
    MidOffset = FrontMiddleY - SideMiddleY

    #We add the offset to the meshSideLocation
    for i in range(0, len(meshSideLocation)):
      meshSideLocation[i][1] += MidOffset

    #We check if the front y range is bigger then the side y range
    FrontRangeY = FrontHighestY - FrontLowestY
    SideRangeY = SideHighestY - SideLowestY
    if FrontRangeY > SideRangeY:
      cmds.warning("The side image for colour [%s, %s, %s] range is smaller then front image. Not enough data to calculate 3D values" % (colour[0], colour[1], colour[2]))
      cmds.warning("The range values are FrontRange: %s, SideRange: %s" % (FrontRangeY, SideRangeY))
      cmds.warning("The frontHighest Y is %s and the frontLowestY is %s" % (FrontHighestY, FrontLowestY))
      cmds.warning("The sideHighest Y is %s and the sideLowestY is %s" % (SideHighestY, SideLowestY))
      return

    #We then get the matching Y coordinates from the meshFrontLocation and the meshSideLocation
    mesh3DCoord = []

    for i in range(0, len(meshFrontLocation)):
      match = 0
      for j in range(0, len(meshSideLocation)):
        if meshFrontLocation[i][1] == meshSideLocation[j][1]:
          mesh3DCoord.append([meshFrontLocation[i][0], meshFrontLocation[i][1], meshSideLocation[j][0]])
          match = 1
          break
      if match==0:
        print "There is no match found for meshFrontLocation[i][1] = %s" % meshFrontLocation[i][1]
        print "Ensure your side view has more pixels then front"


    return mesh3DCoord

  def rearrange(self, list, type):
    """
    This function rearranges the data based on its type
    Args:
      list: The list to rearrange
      type: The factor to rearrange to

    Returns: The rearranged list

    """
    compare = 0
    index = 0
    if type == "LowestX":
      #Get the lowest X index
      for i in range(0, len(list)):
        # If its the first in the list, we store the value to compare
        if i == 0:
          compare = list[i][0]
          continue
        if list[i][0] < compare:
          compare = list[i][0]
          index = i
    elif type == "LowestY":
      #Get the lowest Y index
      for i in range(0, len(list)):
        # If its the first in the list, we store the value to compare
        if i == 0:
          compare = list[i][1]
          continue
        if list[i][1] < compare:
          compare = list[i][1]
          index = i
    elif type == "HighestX":
      #Get the highest X index
      for i in range(0, len(list)):
        # If its the first in the list, we store the value to compare
        if i == 0:
          compare = list[i][0]
          continue
        if list[i][0] > compare:
          compare = list[i][0]
          index = i
    elif type == "HighestY":
      #Get the highest Y index
      for i in range(0, len(list)):
        # If its the first in the list, we store the value to compare
        if i == 0:
          compare = list[i][1]
          continue
        if list[i][1] > compare:
          compare = list[i][1]
          index = i

    #We split the list into 2 with the index as the divider
    ListA = list[index:]
    ListB = list[:index]
    #We then combine the new list
    for i in ListB:
      ListA.append(i)
    return ListA

  def getEyeCoord(self, locatorList, points = 16):
    """
    This function gets the eye coordinates
    Args:
      locatorList: The list that stores all the locators generated
      points: The resolution points to detect
    """
    colour = [255,0,0]
    startCoord = [0,0]
    rowDirection = "DownUp"
    columnDirection = "LeftRight"
    #points = 16
    isLine = 0
    arrangement = "LowestY"

    Eye3DCoord = self.get3DCoord(colour, startCoord, rowDirection, columnDirection, points, isLine, arrangement)

    if not Eye3DCoord:
      print "No eyes were detected"
      return

    EyeSep3DCoord = []
    #As the eyes come with 16 points each, each other 16 points is another eye
    for p in range(0, len(Eye3DCoord), points):
      Eye = []
      for eyepoint in range(0,points):
        Eye.append(Eye3DCoord[p + eyepoint])
      EyeSep3DCoord.append(Eye)

    #We plot the eyes out using locators first
    for i in EyeSep3DCoord:
      for j in range(0,points):
        location = cmds.spaceLocator(n="Eye_Coord#")
        cmds.xform(location, t=[i[j][0],i[j][1],i[j][2]])
        locatorList.append(location[0])

  def getNoseBridgeCoord(self, locatorList, points = 4):
    """
    This function gets the nose bridge coordinates
    Args:
      locatorList: The list that stores all the locators generated
      points: The resolution points to detect
    """
    colour = [255,255,0]
    startCoord = [0,0]
    rowDirection = "LeftRight"
    columnDirection = "DownUp"
    #points = 4
    isLine = 1
    arrangement = "LowestY"

    NoseBridge3DCoord = self.get3DCoord(colour, startCoord, rowDirection, columnDirection, points, isLine, arrangement)

    if not NoseBridge3DCoord:
      print "No nosebridge were detected"
      return

    NoseBridgeSep3DCoord = []
    #As the nosebridge come with a certain number of points each, each other few points is another nosebridge
    for p in range(0, len(NoseBridge3DCoord), points):
      NoseBridge = []
      for nosebridgepoint in range(0,points):
        NoseBridge.append(NoseBridge3DCoord[p + nosebridgepoint])
      NoseBridgeSep3DCoord.append(NoseBridge)


    #We plot the nosebridge out using locators first
    for i in NoseBridgeSep3DCoord:
      for j in range(0,points):
        location = cmds.spaceLocator(n="NoseBridge_Coord#")
        cmds.xform(location, t=[i[j][0],i[j][1],i[j][2]])
        locatorList.append(location[0])

  def getNoseCoord(self, locatorList, points = 8):
    """
      This function gets the nose coordinates
      Args:
        locatorList: The list that stores all the locators generated
        points: The resolution points to detect
      """

    colour = [0, 255, 0]
    startCoord = [0, 0]
    rowDirection = "DownUp"
    columnDirection = "LeftRight"
    #points = 8
    isLine = 1
    arrangement = "HighestY"

    Nose3DCoord = self.get3DCoord(colour, startCoord, rowDirection, columnDirection, points, isLine, arrangement)

    if not Nose3DCoord:
      print "No nose was detected"
      return

    NoseSep3DCoord = []
    # As the nose come with 8 points each, each other 8 points is another nose
    for points in range(0, len(Nose3DCoord), 8):
      Nose = []
      for nosepoint in range(0, 8):
        Nose.append(Nose3DCoord[points + nosepoint])
      NoseSep3DCoord.append(Nose)

    # We plot the nose out using locators first
    for i in NoseSep3DCoord:
      for j in range(0, 8):
        location = cmds.spaceLocator(n="Nose_Coord#")
        cmds.xform(location, t=[i[j][0], i[j][1], i[j][2]])
        locatorList.append(location[0])

  def getMouthCoord(self, locatorList, points = 24):
    """
    This function gets the mouth coordinates
    Args:
      locatorList: The list that stores all the locators generated
      points: The resolution points to detect
    """

    colour = [0, 0, 255]
    startCoord = [0, 0]
    rowDirection = "LeftRight"
    columnDirection = "DownUp"
    #points = 24
    isLine = 0
    arrangement = "LowestY"

    Mouth3DCoord = self.get3DCoord(colour, startCoord, rowDirection, columnDirection, points, isLine, arrangement)

    if not Mouth3DCoord:
      print "No mouth was detected"
      return

    MouthSep3DCoord = []
    print len(Mouth3DCoord)
    # As the mouth come with 24 points each, each other 24 points is another mouth
    for p in range(0, len(Mouth3DCoord), points):
      Mouth = []
      for mouthpoint in range(0, points):
        Mouth.append(Mouth3DCoord[p + mouthpoint])
      MouthSep3DCoord.append(Mouth)

    # We plot the mouth out using locators first
    for i in MouthSep3DCoord:
      for j in range(0, points):
        location = cmds.spaceLocator(n="Mouth_Coord#")
        cmds.xform(location, t=[i[j][0], i[j][1], i[j][2]])
        locatorList.append(location[0])

  def getMouthLoopCoord(self, locatorList, points = 16):
    """
    This function gets the mouth loop coordinates
    Args:
      locatorList: The list that stores all the locators generated
      points: The resolution points to detect
    """

    colour = [255, 0, 255]
    startCoord = [0, 0]
    rowDirection = "LeftRight"
    columnDirection = "DownUp"
    #points = 16
    isLine = 1
    arrangement = "HighestY"

    MouthLoop3DCoord = self.get3DCoord(colour, startCoord, rowDirection, columnDirection, points, isLine, arrangement)

    if not MouthLoop3DCoord:
      print "No mouthLoop was detected"
      return

    MouthLoopSep3DCoord = []
    # As the mouthLoop come with 16 points each, each other 16 points is another mouthLoop
    for p in range(0, len(MouthLoop3DCoord), points):
      MouthLoop = []
      for mouthlooppoint in range(0, points):
        MouthLoop.append(MouthLoop3DCoord[p + mouthlooppoint])
      MouthLoopSep3DCoord.append(MouthLoop)

    # We plot the mouthLoop out using locators first
    for i in MouthLoopSep3DCoord:
      for j in range(0, points):
        location = cmds.spaceLocator(n="MouthLoop_Coord#")
        cmds.xform(location, t=[i[j][0], i[j][1], i[j][2]])
        locatorList.append(location[0])

  def getEyebrowCoord(self, locatorList, points = 16):
    """
    This function gets the eyebrow coordinates
    Args:
      locatorList: The list that stores all the locators generated
      points: The resolution points to detect
    """

    colour = [0, 255, 255]
    startCoord = [0, 0]
    rowDirection = "LeftRight"
    columnDirection = "DownUp"
    #points = 16
    isLine = 1
    arrangement = "LowestX"

    Eyebrow3DCoord = self.get3DCoord(colour, startCoord, rowDirection, columnDirection, points, isLine, arrangement)

    if not Eyebrow3DCoord:
      print "No eyebrow was detected"
      return

    EyebrowSep3DCoord = []
    # As the eyebrow come with 16 points each, each other 16 points is another eyebrow
    for p in range(0, len(Eyebrow3DCoord), points):
      Eyebrow = []
      for eyebrowpoint in range(0, points):
        Eyebrow.append(Eyebrow3DCoord[p + eyebrowpoint])
      EyebrowSep3DCoord.append(Eyebrow)

    # We plot the eyebrow out using locators first
    for i in EyebrowSep3DCoord:
      for j in range(0, points):
        location = cmds.spaceLocator(n="Eyebrow_Coord#")
        cmds.xform(location, t=[i[j][0], i[j][1], i[j][2]])
        locatorList.append(location[0])

  def getEarCoord(self, locatorList):
    """
    This function gets the ear coordinates
    Args:
      locatorList: The list that stores all the locators generated
    """

    colour = [178, 77, 0]
    startCoord = [0, 0]
    rowDirection = "LeftRight"
    columnDirection = "DownUp"
    points = 5
    isLine = 1
    arrangement = "HighestY"

    Ear3DCoord = self.get3DCoord(colour, startCoord, rowDirection, columnDirection, points, isLine, arrangement)

    if not Ear3DCoord:
      print "No ear was detected"
      return

    EarSep3DCoord = []
    # As the ear come with 5 points each, each other 5 points is another ear
    for p in range(0, len(Ear3DCoord), points):
      Ear = []
      for earpoint in range(0, points):
        Ear.append(Ear3DCoord[p + earpoint])
      EarSep3DCoord.append(Ear)

    # We plot the ear out using locators first
    for i in EarSep3DCoord:
      for j in range(0, points):
        location = cmds.spaceLocator(n="Ear_Coord#")
        cmds.xform(location, t=[i[j][0], i[j][1], i[j][2]])
        locatorList.append(location[0])

  def getSideProfileCoord(self, locatorList):
    """
    This function gets the side profile coordinates
    Args:
      locatorList: The list that stores all the locators generated
    """

    colour = [0,0,0]
    startCoord = [0,0]
    rowDirection = "LeftRight"
    columnDirection = "DownUp"
    arrangement = "LowestY"
    isLine = 0

    SideProfileCoord = self.getSideCoord(colour, startCoord, rowDirection, columnDirection, arrangement, isLine)
    if not SideProfileCoord:
      print "No Side Profile Coord detected"
      return

    RefinedSideProfileCoord = []
    #For the sake of checking, lets limit to 96 points
    points = 96
    # We then take note of a certain number of points in the SideProfileCoord
    # We add the coordinates to the meshFrontLocation list
    # Safety mechanism for infinite loop

    stride = len(SideProfileCoord) / float(points)
    loopTrigger = 0
    currentIndex = 0.0
    while loopTrigger < points:
      loopTrigger += 1
      if loopTrigger > 10000:
        print "Infinite loop in front coord scanning stride part of profile!!"
        break
      i = int(currentIndex)
      RefinedSideProfileCoord.append([SideProfileCoord[i][0], SideProfileCoord[i][1]])
      currentIndex += stride

    for i in RefinedSideProfileCoord:
        location = cmds.spaceLocator(n="SideProfile_Coord#")
        cmds.xform(location, t=[0, i[1], i[0]], ws=True)
        locatorList.append(location[0])

  def getFrontProfileCoord(self, locatorList):
    """
    This function gets the front profile coordinates
    Args:
      locatorList: The list that stores all the locators generated
    """

    colour = [0, 128, 128]
    startCoord = [0, 0]
    rowDirection = "LeftRight"
    columnDirection = "DownUp"
    points = 25
    isLine = 1
    arrangement = "LowestX"

    FrontProfile3DCoord = self.get3DCoord(colour, startCoord, rowDirection, columnDirection, points, isLine, arrangement)

    if not FrontProfile3DCoord:
      print "No front profile was detected"
      return

    FrontProfileSep3DCoord = []
    print len(FrontProfile3DCoord)
    # As the front profile come with 25 points each, each other 25 points is another front profile
    for p in range(0, len(FrontProfile3DCoord), points):
      FrontProfile = []
      for frontprofilepoint in range(0, points):
        FrontProfile.append(FrontProfile3DCoord[p + frontprofilepoint])
      FrontProfileSep3DCoord.append(FrontProfile)

    # We plot the front profile out using locators first
    for i in FrontProfileSep3DCoord:
      for j in range(0, points):
        location = cmds.spaceLocator(n="FrontProfile_Coord#")
        cmds.xform(location, t=[i[j][0], i[j][1], i[j][2]])
        locatorList.append(location[0])

  def scaleToUnitVolume(self, locatorGroup):
    """
    The function scales the locators to fit within a 1x1x1 volume
    Args:
      locatorGroup: The locator group to scale
    """
    BoundingBox = cmds.exactWorldBoundingBox(locatorGroup)
    xLength = BoundingBox[3] - BoundingBox[0]
    yLength = BoundingBox[4] - BoundingBox[1]
    zLength = BoundingBox[5] - BoundingBox[2]

    if xLength != 0 and yLength != 0 and zLength != 0:
      # Next we need to find the longest length and scale in down such that the
      # longest length fits within the unit Cube
      if xLength > yLength and xLength > zLength:
        scaleFactor = 1.0/xLength
      elif yLength > xLength and yLength > zLength:
        scaleFactor = 1.0 / yLength
      elif zLength > xLength and zLength > yLength:
        scaleFactor = 1.0 / zLength

    else:
      cmds.error("Division by zero. The scanned image is not 3D")
      return

    cmds.xform(locatorGroup, scale=[scaleFactor, scaleFactor, scaleFactor])
    cmds.select (locatorGroup)
    cmds.move(0, 0, 0, rpr=True, ws=True)

  def reverseName(self, locatorGroup):
    """
    As the deformation control points are from left to right and the mesh curves are from right to left in Maya,
    for convenience and clarity purposes, we are going to reverse the naming of the deformation points from
    right to left.
    Args:
      locatorGroup: The group with all the created locators

    """
    locatorList = cmds.listRelatives(locatorGroup)

    eyeLocators = []
    earLocators = []

    for i in locatorList:
      if "Eye_Coord" in i:
        eyeLocators.append(i)
      if "Ear_Coord" in i:
        earLocators.append(i)


    # We first check if there is more then one eye or not. If there is, we have to reorder
    points = 8
    TempRename = []
    if len(eyeLocators) > points:
      # We first rename all the eye locators to a default name to prevent name clashing
      for i in range(0, len(eyeLocators)):
        RenameObj = cmds.rename(eyeLocators[i], 'TempEyeCoord#')
        TempRename.append(RenameObj)

      # We reorder the eye from right to left
      for i in range((len(eyeLocators)/points)-1 , -1 , -1):
        for j in range(0, points):
          cmds.rename(TempRename[j + (i * points)], 'Eye_Coord#')

    # We then check if there is more then one ear or not. If there is, we have to reorder
    points = 5
    TempRename = []
    if len(earLocators) > points:
      # We first rename all the ear locators to a default name to prevent name clashing
      for i in range(0, len(earLocators)):
        RenameObj = cmds.rename(earLocators[i], 'TempEarCoord#')
        TempRename.append(RenameObj)

      # We reorder the ear from right to left
      for i in range((len(earLocators) / points) - 1, -1, -1):
        for j in range(0, points):
          cmds.rename(TempRename[j + (i * points)], 'Ear_Coord#')







