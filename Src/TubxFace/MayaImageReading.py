'''
This script allows the creation of a maya image
'''
import maya.OpenMaya as om

class MayaImage:
  """
  This class allows the reading of image as well as the querying of image data
  """
  def __init__(self, filename):
    # Create an MImage Object
    self.image = om.MImage()
    # Read from file. MImage should handle errors for us
    self.image.readFromFile(filename)
    # To access pointers, we have to use MScriptUtil helpers
    # MImage is only a wrapper to the C++ module
    imageWidth = om.MScriptUtil()
    imageHeight = om.MScriptUtil()

    # Create an unsigned int pointer for width and height
    WidthPtr = imageWidth.asUintPtr()
    HeightPtr = imageHeight.asUintPtr()

    # We get the size of the image and the return value is an address which we store in the ptr
    self.image.getSize(WidthPtr,HeightPtr)

    # We then get the values from the pointers
    self.m_width=imageWidth.getUint(WidthPtr)
    self.m_height = imageHeight.getUint(HeightPtr)

    # Grab and store the pixel data
    self.PixelPtr = self.image.pixels()

    # We create an empty MScriptUtil and a pointer to the function
    # getUcharArrayItem for speed when accessing the information in PixelPtr when needed
    scriptUtil = om.MScriptUtil()
    self.getUcharArrayItem = scriptUtil.getUcharArrayItem

  def getPixel(self, x, y):
    """
    Get the pixel at coordinates X,Y
    Args:
      x: The X Coordinate
      y: The Y Coordinate

    Returns: The RGBA values of the pixel

    """
    #Check the bounds to make sure we are still within the image
    if x<0 or x>self.m_width:
      print "Error x out of bounds\n"
      return
    if y < 0 or y > self.m_height:
      print "Error y out of bounds\n"
      return

    #Calculate the index of the pixel
    index = (y * self.m_width * 4) + x * 4
    #Finally we grab the pixels
    red = self.getUcharArrayItem(self.PixelPtr, index)
    green = self.getUcharArrayItem(self.PixelPtr, index+1)
    blue = self.getUcharArrayItem(self.PixelPtr, index+2)
    alpha = self.getUcharArrayItem(self.PixelPtr, index+3)

    return red,green,blue,alpha

  def getRGB(self, x, y):
    """
    Get the RGB values of a pixel at coordinates x and y
    Args:
      x: the X coordinate
      y: the Y coordinate

    Returns: The r,g,b values

    """
    r,g,b,a = self.getPixel(x,y)
    return r,g,b

  def width(self):
    """
    Get the width of the image
    Returns: The width of the image

    """
    return self.m_width

  def height(self):
    """
    Get the height of the image
    Returns: The height of the image
    """

    return self.m_height

  def detectHColourLoop(self, yStart, yEnd, yIncrement, xStart, xEnd, xIncrement, resetRow, colour):
    """
    This function scans the image if its row direction is horizontal
    Args:
      yStart: The start of the y coordinate
      yEnd: The end of the y coordinate
      yIncrement: How much to increment Y
      xStart: The start of the x coordinate
      xEnd: The end of the x coordinate
      xIncrement: How much to increment X
      resetRow: In the case we are starting from a middle of a row, when we move to the next row, it is the width of the image
      colour: The colour to detect

    Returns: The coordinates of the detected pixel

    """

    # We create some variables that we will used during the scanning
    # If the pixel colour is detected, Endloop = 1 and we break the scan
    Endloop = 0
    # The x and y coordinates of the detected pixel
    DetectedX, DetectedY = -1, -1
    # If we are starting from the middle of an image, once we go to the next column,
    # we have to reset the row value. This variable is to check if we have reached the next column or not
    FirstTrace = -1

    for y in range(yStart, yEnd, yIncrement):
      FirstTrace += 1
      if FirstTrace > 0:
        xStart = resetRow
      for x in range(xStart, xEnd, xIncrement):
        r, g, b, a = self.getPixel(x, y)
        # If pixel is detected, store the value and break
        if r == colour[0] and g == colour[1] and b == colour[2]:
          DetectedX = x
          DetectedY = y
          Endloop = 1
        if Endloop == 1:
          break
      if Endloop == 1:
        break

    return DetectedX, DetectedY

  def detectVColourLoop(self, xStart, xEnd, xIncrement, yStart, yEnd, yIncrement, resetRow, colour):
    """
      This function scans the image if its row direction is vertical
      Args:
        xStart: The start of the x coordinate
        xEnd: The end of the x coordinate
        xIncrement: How much to increment X
        yStart: The start of the y coordinate
        yEnd: The end of the y coordinate
        yIncrement: How much to increment Y
        resetRow: In the case we are starting from a middle of a row, when we move to the next row, it is the height of the image
        colour: The colour to detect

      Returns: The coordinates of the detected pixel

      """
    # We create some variables that we will used during the scanning
    # If the pixel colour is detected, Endloop = 1 and we break the scan
    Endloop = 0
    # The x and y coordinates of the detected pixel
    DetectedX, DetectedY = -1, -1
    # If we are starting from the middle of an image, once we go to the next column,
    # we have to reset the row value. This variable is to check if we have reached the next column or not
    FirstTrace = -1

    for x in range(xStart, xEnd, xIncrement):
      FirstTrace += 1
      if FirstTrace > 0:
        yStart = resetRow
      for y in range(yStart, yEnd, yIncrement):
        r, g, b, a = self.getPixel(x, y)
        # If pixel is detected, store the value and break
        if r == colour[0] and g == colour[1] and b == colour[2]:
          DetectedX = x
          DetectedY = y
          Endloop = 1
        if Endloop == 1:
          break
      if Endloop == 1:
        break

    return DetectedX, DetectedY

  def detectColourPixel(self, colour, StartCoord, rowDirection, columnDirection):
    """
    Get the coordinates of a pixel with the intended colour
    Args:
      colour: The intended colour to detect
      StartCoord: The starting coordinates to scan from
      rowDirection: The row direction of the scan
      columnDirection: The column direction of the scan

    Returns: The coordinates of the detected pixel

    """

    #We split the start coordinates for easy reference
    xStart = StartCoord[0]
    yStart = StartCoord[1]
    DetectedX, DetectedY = -1,-1

    #We now scan based on the rows and columns specified
    if rowDirection == "LeftRight":
      if columnDirection == "DownUp":
        resetRow = 0
        DetectedX, DetectedY = self.detectHColourLoop(yStart, self.m_height, +1, xStart, self.m_width, +1, resetRow, colour)

      elif columnDirection == "UpDown":
        resetRow = 0
        DetectedX, DetectedY = self.detectHColourLoop(yStart, -1, -1, xStart, self.m_width, +1, resetRow, colour)

    elif rowDirection == "RightLeft":
      if columnDirection == "DownUp":
        resetRow = self.m_width
        DetectedX, DetectedY = self.detectHColourLoop(yStart, self.m_height, +1, xStart, -1, -1, resetRow, colour)
      if columnDirection == "UpDown":
        resetRow = self.m_width
        DetectedX, DetectedY = self.detectHColourLoop(yStart, -1, -1, xStart, -1, -1, resetRow, colour)

    elif rowDirection == "UpDown":
      if columnDirection == "LeftRight":
        resetRow = self.m_height
        DetectedX, DetectedY = self.detectVColourLoop(xStart, self.m_width, +1, yStart, -1, -1, resetRow, colour)
      elif columnDirection == "RightLeft":
        resetRow = self.m_height
        DetectedX, DetectedY = self.detectVColourLoop(xStart, -1, -1, yStart, -1, -1, resetRow, colour)

    elif rowDirection == "DownUp":
      if columnDirection == "LeftRight":
        resetRow = 0
        DetectedX, DetectedY = self.detectVColourLoop(xStart, self.m_width, +1, yStart, self.m_height, +1, resetRow, colour)
      elif columnDirection == "RightLeft":
        resetRow = 0
        DetectedX, DetectedY = self.detectVColourLoop(xStart, -1, -1, yStart, self.m_height, +1, resetRow, colour)


    if DetectedX == -1 and DetectedY == -1:
      # No pixel detected
      PixelCoordinates = []
      return PixelCoordinates
    else:
      PixelCoordinates = [DetectedX,DetectedY]
      return PixelCoordinates

  def getLastMostPixel(self, TraceX, TraceY, rowScan, columnScan, LastMostPixel):
    """
    This function get the last most pixel depending on the direction of the scan for the scanning stage to continue after
    the tracing stage
    Args:
      TraceX: The current X trace
      TraceY: The current Y trace
      rowScan: The row scan direction
      columnScan: The column scan direction
      LastMostPixel: The starting pixel

    Returns: The last most pixel

    """
    if rowScan == "LeftRight":
      if columnScan == "DownUp":
        if LastMostPixel[1] < TraceY:
          LastMostPixel = [TraceX, TraceY]
        elif LastMostPixel[1] == TraceY:
          if LastMostPixel[0] < TraceX:
            LastMostPixel = [TraceX, TraceY]

      elif columnScan == "UpDown":
        if LastMostPixel[1] > TraceY:
          LastMostPixel = [TraceX, TraceY]
        elif LastMostPixel[1] == TraceY:
          if LastMostPixel[0] < TraceX:
            LastMostPixel = [TraceX, TraceY]

    elif rowScan == "RightLeft":
      if columnScan == "DownUp":
        if LastMostPixel[1] < TraceY:
          LastMostPixel = [TraceX, TraceY]
        elif LastMostPixel[1] == TraceY:
          if LastMostPixel[0] > TraceX:
            LastMostPixel = [TraceX, TraceY]
      if columnScan == "UpDown":
        if LastMostPixel[1] > TraceY:
          LastMostPixel = [TraceX, TraceY]
        elif LastMostPixel[1] == TraceY:
          if LastMostPixel[0] > TraceX:
            LastMostPixel = [TraceX, TraceY]

    elif rowScan == "UpDown":
      if columnScan == "LeftRight":
        if LastMostPixel[0] < TraceX:
          LastMostPixel = [TraceX, TraceY]
        elif LastMostPixel[0] == TraceX:
          if LastMostPixel[1] > TraceY:
            LastMostPixel = [TraceX, TraceY]

      elif columnScan == "RightLeft":
        if LastMostPixel[0] > TraceX:
          LastMostPixel = [TraceX, TraceY]
        elif LastMostPixel[0] == TraceX:
          if LastMostPixel[1] > TraceY:
            LastMostPixel = [TraceX, TraceY]

    elif rowScan == "DownUp":
      if columnScan == "LeftRight":
        if LastMostPixel[0] < TraceX:
          LastMostPixel = [TraceX, TraceY]
        elif LastMostPixel[0] == TraceX:
          if LastMostPixel[1] < TraceY:
            LastMostPixel = [TraceX, TraceY]

      elif columnScan == "RightLeft":
        if LastMostPixel[0] > TraceX:
          LastMostPixel = [TraceX, TraceY]
        elif LastMostPixel[0] == TraceX:
          if LastMostPixel[1] < TraceY:
            LastMostPixel = [TraceX, TraceY]

    return LastMostPixel

  def checkValidMovement(self, LastMovement, CurrentMovement):
    """
    This function checks if a movement during tracing is valid. It is to prevent infinite loops
    However, with the new implementation of moore-neightbours algorithm, this is not used
    Args:
      LastMovement: The last movement during the trace
      CurrentMovement: The current movement during the trace

    Returns: A boolean value determining if a movement is valid or not

    """
    if LastMovement == 0 and CurrentMovement == 4:
      print "During tracing, pixel last Movement goes bottom and next movement goes top. Redundant so skip"
      return 0
    elif LastMovement == 1 and CurrentMovement == 5:
      print "During tracing, pixel last Movement goes bottom right and next movement goes top left. Redundant so skip"
      return 0
    elif LastMovement == 2 and CurrentMovement == 6:
      print "During tracing, pixel last Movement goes right and next movement goes left. Redundant so skip"
      return 0
    elif LastMovement == 3 and CurrentMovement == 7:
      print "During tracing, pixel last Movement goes bottom top right and next movement goes bottom left. Redundant so skip"
      return 0
    elif LastMovement == 4 and CurrentMovement == 0:
      print "During tracing, pixel last Movement goes top and next movement goes bottom. Redundant so skip"
      return 0
    elif LastMovement == 5 and CurrentMovement == 1:
      print "During tracing, pixel last Movement goes top left and next movement goes bottom right. Redundant so skip"
      return 0
    elif LastMovement == 6 and CurrentMovement == 2:
      print "During tracing, pixel last Movement goes left and next movement goes right. Redundant so skip"
      return 0
    elif LastMovement == 7 and CurrentMovement == 3:
      print "During tracing, pixel last Movement goes bottom bottom left and next movement goes top right. Redundant so skip"
      return 0
    return 1

  def traceLine2(self, colour, StartCoord, rowScan, columnScan):
    """
    This function traces the pixel shape.
    This function is depricated and is not used. Instead, traceLine which implements moore-neighbours algorithm is used
    Args:
      colour: The colour to trace
      StartCoord: The starting coordinate of the trace
      rowScan: The row direction
      columnScan: The column direction

    Returns: The scanned list as well as the last most pixel to continue scanning

    """
    # Split and get the coordinates
    TraceX = StartCoord[0]
    TraceY = StartCoord[1]

    # This list "LastMostPixel" stores the pixel to continue detection scanning after tracing
    LastMostPixel = StartCoord
    # This is to check if it is the first action of tracing. This is because the loop will break when we arrive
    # back to the starting coordinates
    FirstAction = 1
    # This list stores the coordinates of the detected pixels
    CoordinateList = []

    #Last movement is a variable to check how the pixel last moved. This is to prevent any forward backward movement
    #during the trace which would result in an infinite loop
    LastMovement = 0


    # This is to provide a mechanism to prevent infinite loop
    CountLoop = 0

    while(True):
      CountLoop += 1
      if CountLoop > 10000:
        print "CountLoop is more then 10000, mechanism to prevent infinite loop during tracing activated"
        break

      #We check if we have arrived back to the starting pixel
      if TraceX == StartCoord[0] and TraceY == StartCoord[1] and FirstAction != 1:
        break

      #Once we first enter the loop, we set FirstAction to 0 as the next loop would not be the first action
      FirstAction = 0

      #Check pixel to see if it is the intended colour. If it is not, break
      r,g,b = self.getRGB(TraceX, TraceY)
      if r!=colour[0] and g!=colour[1] and b!=colour[2]:
        break

      #We register the coordinates since it is of the intended colour
      #########################################
      CoordinateList.append([TraceX-(self.m_width/2),TraceY-(self.m_height/2)])
      #CoordinateList.append([TraceX, self.m_height-TraceY])
      #########################################


      #Register last most pixel based on the direction of the scan to find the next starting pixel
      LastMostPixel = self.getLastMostPixel(TraceX, TraceY, rowScan, columnScan, LastMostPixel)

      #Now we check where to move
      #We create a few lists to guide pixel movement
      ColourPixelList = []
      MoveXList = [0, 1, 1, 1, 0, -1, -1, -1]
      MoveYList = [-1, -1, 0, 1, 1, 1, 0, -1]

      #We check the neighbouring pixels starting from the bottom in an anti clockwise fashion
      #Bottom (b)
      rb,gb,bb = self.getRGB(TraceX, TraceY-1)
      ColourPixelList.append([rb,gb,bb])
      #Bottom Right (br)
      rbr, gbr, bbr = self.getRGB(TraceX + 1, TraceY - 1)
      ColourPixelList.append([rbr, gbr, bbr])
      #Right (r)
      rr, gr, br = self.getRGB(TraceX + 1, TraceY)
      ColourPixelList.append([rr, gr, br])
      #Top Right (tr)
      rtr, gtr, btr = self.getRGB(TraceX + 1, TraceY + 1)
      ColourPixelList.append([rtr, gtr, btr])
      #Top (t)
      rt, gt, bt = self.getRGB(TraceX, TraceY + 1)
      ColourPixelList.append([rt, gt, bt])
      #Top Left (tl)
      rtl, gtl, btl = self.getRGB(TraceX - 1, TraceY + 1)
      ColourPixelList.append([rtl, gtl, btl])
      #Left (l)
      rl, gl, bl = self.getRGB(TraceX - 1, TraceY)
      ColourPixelList.append([rl, gl, bl])
      #Bottom Left(bl)
      rbl, gbl, bbl = self.getRGB(TraceX - 1, TraceY - 1)
      ColourPixelList.append([rbl, gbl, bbl])

      #Next we determine where to move
      hasMoved = 0
      #If former element is some other colour and next element is the colour we are tracing, we move.
      for i in range(1, 8):
        if ColourPixelList[i - 1] != [colour[0], colour[1], colour[2]] and ColourPixelList[i] == [colour[0], colour[1], colour[2]]:
          # This means previous cell was some other colour and the next cell is the colour we are tracing
          # We check the last movement call, if it is just going backwards, we continue
          ValidMovement = self.checkValidMovement(LastMovement, i)
          if ValidMovement == 1:
            TraceX += MoveXList[i]
            TraceY += MoveYList[i]
            hasMoved = 1
            LastMovement = i
            break

      if ColourPixelList[7] != [colour[0], colour[1], colour[2]] and ColourPixelList[0] == [colour[0], colour[1], colour[2]] and hasMoved == 0:
        TraceX += MoveXList[0]
        TraceY += MoveYList[0]
        LastMovement = 0
        hasMoved = 1

      if hasMoved == 0:
        print "Pixel has not moved"
        print "TraceX and TraceY is at [%s,%s]" % (TraceX, TraceY)
        print "Photoshop Coordinates is TraceX and TraceY is at [%s,%s]" % (TraceX, self.m_height - TraceY)
        break

    if CountLoop>10000:
      print "Coordinate list len before is : ", len(CoordinateList)
      #If CountLoop is more then 10000, that means something went wrong. The pixel may be looping
      #Around and around and was unable to get back to the starting position.
      #In this case, we remove the repeated elements to refine the list
      unique = []
      for i in CoordinateList:
        if i not in unique:
          unique.append(i)

      CoordinateList = unique
      print "Coordinate list len after is : ", len(CoordinateList)

    # We then add one to to LastMostPixel depending on direction of scanning
    if rowScan == "LeftRight":
        LastMostPixel[0] += 1

    elif rowScan == "RightLeft":
        LastMostPixel[0] -=1

    elif rowScan == "UpDown":
        LastMostPixel[1] -=1

    elif rowScan == "DownUp":
      LastMostPixel[1] += 1

    return CoordinateList, LastMostPixel

  def traceLine(self, colour, StartCoord, rowScan, columnScan):
    """
    This function traces the pixel shape.
    It uses moore-neighbour tracing algorithm
    Args:
      colour: The colour to trace
      StartCoord: The starting coordinate of the trace
      rowScan: The row direction
      columnScan: The column direction

    Returns: The scanned list as well as the last most pixel to continue scanning

    """
    # Moore-Neighbour tracing algorithm

    # Split and get the coordinates
    TraceX = StartCoord[0]
    TraceY = StartCoord[1]

    # This list "LastMostPixel" stores the pixel to continue detection scanning after tracing
    LastMostPixel = StartCoord
    # This is to check if it is the first action of tracing. This is because the loop will break when we arrive
    # back to the starting coordinates
    FirstAction = 1
    # This list stores the coordinates of the detected pixels
    CoordinateList = []

    #Last movement is a variable to check how the pixel last moved.
    #Using the new algorithm, last movement has to be taken into account and would be used to start the check for neighbour pixels
    if rowScan == "LeftRight":
      LastMovement = 'R'

    elif rowScan == "DownUp":
      LastMovement = 'U'

    elif rowScan == "RightLeft":
      LastMovement = 'L'

    elif rowScan == "UpDown":
      LastMovement = 'D'


    # This is to provide a mechanism to prevent infinite loop
    CountLoop = 0

    while(True):
      CountLoop += 1
      if CountLoop > 10000:
        print "CountLoop is more then 10000, mechanism to prevent infinite loop during tracing activated"
        break

      #We check if we have arrived back to the starting pixel
      if TraceX == StartCoord[0] and TraceY == StartCoord[1] and FirstAction != 1:
        break

      #Once we first enter the loop, we set FirstAction to 0 as the next loop would not be the first action
      FirstAction = 0

      #Check pixel to see if it is the intended colour. If it is not, break
      r,g,b = self.getRGB(TraceX, TraceY)
      if r!=colour[0] and g!=colour[1] and b!=colour[2]:
        break

      #We register the coordinates since it is of the intended colour
      #########################################
      CoordinateList.append([TraceX-(self.m_width/2),TraceY-(self.m_height/2)])
      #CoordinateList.append([TraceX, self.m_height-TraceY])
      #########################################


      #Register last most pixel based on the direction of the scan to find the next starting pixel
      LastMostPixel = self.getLastMostPixel(TraceX, TraceY, rowScan, columnScan, LastMostPixel)

      #Using Moore-Neighbour tracing algorithm, we create a few lists to guide pixel movement
      ColourPixelList = []
      MoveXList = [0, 1, 1, 1, 0, -1, -1, -1]
      MoveYList = [-1, -1, 0, 1, 1, 1, 0, -1]
      #This is the direction I came from
      MoveDirection = ["R", "R", "U", "U", "L", "L", "D", "D"]
      #This is the index to start the movement
      MoveDict = {"R" : 6, "U" : 0, "L" : 2, "D" : 4}


      #We check the neighbouring pixels starting from the bottom in an anti clockwise fashion
      #Bottom (b)
      rb,gb,bb = self.getRGB(TraceX, TraceY-1)
      ColourPixelList.append([rb,gb,bb])
      #Bottom Right (br)
      rbr, gbr, bbr = self.getRGB(TraceX + 1, TraceY - 1)
      ColourPixelList.append([rbr, gbr, bbr])
      #Right (r)
      rr, gr, br = self.getRGB(TraceX + 1, TraceY)
      ColourPixelList.append([rr, gr, br])
      #Top Right (tr)
      rtr, gtr, btr = self.getRGB(TraceX + 1, TraceY + 1)
      ColourPixelList.append([rtr, gtr, btr])
      #Top (t)
      rt, gt, bt = self.getRGB(TraceX, TraceY + 1)
      ColourPixelList.append([rt, gt, bt])
      #Top Left (tl)
      rtl, gtl, btl = self.getRGB(TraceX - 1, TraceY + 1)
      ColourPixelList.append([rtl, gtl, btl])
      #Left (l)
      rl, gl, bl = self.getRGB(TraceX - 1, TraceY)
      ColourPixelList.append([rl, gl, bl])
      #Bottom Left(bl)
      rbl, gbl, bbl = self.getRGB(TraceX - 1, TraceY - 1)
      ColourPixelList.append([rbl, gbl, bbl])

      #Next we determine where to move
      hasMoved = 0
      index = MoveDict[LastMovement]

      for i in range(0,8):
        if ColourPixelList[index] == [colour[0], colour[1], colour[2]]:
          #This means we move to the cell
          TraceX += MoveXList[index]
          TraceY += MoveYList[index]
          hasMoved = 1
          #We then update the last movement
          LastMovement = MoveDirection[index]
          break
        else:
          index+=1
          if index == 8:
            index = 0

      if hasMoved == 0:
        print "Pixel has not moved"
        print "TraceX and TraceY is at [%s,%s]" % (TraceX, TraceY)
        print "Photoshop Coordinates is TraceX and TraceY is at [%s,%s]" % (TraceX, self.m_height - TraceY)
        break

    if CountLoop>10000:
      print "Coordinate list len before is : ", len(CoordinateList)
      #If CountLoop is more then 10000, that means something went wrong. The pixel may be looping
      #Around and around and was unable to get back to the starting position.
      #In this case, we remove the repeated elements to refine the list
      unique = []
      for i in CoordinateList:
        if i not in unique:
          unique.append(i)

      CoordinateList = unique
      print "Coordinate list len after is : ", len(CoordinateList)

    # We then add one to to LastMostPixel depending on direction of scanning
    if rowScan == "LeftRight":
        LastMostPixel[0] += 1

    elif rowScan == "RightLeft":
        LastMostPixel[0] -=1

    elif rowScan == "UpDown":
        LastMostPixel[1] -=1

    elif rowScan == "DownUp":
      LastMostPixel[1] += 1

    return CoordinateList, LastMostPixel





