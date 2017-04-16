'''
This script builds the UI for TubxFace
'''

import ExportingData
reload(ExportingData)
import LibraryGeneration
reload(LibraryGeneration)
import ScanningImage
reload(ScanningImage)
import DeformLibrary
reload(DeformLibrary)
import CreateRelationships
reload(CreateRelationships)

from maya import cmds
from functools import partial
import maya.mel as mel
import os

# This abstraction is used in the future to make it compatible with Maya 2016 and below and Maya 2017
# from Qt import QtWidgets, QtCore, QtGui
from PySide import QtCore, QtGui
# When i see a """!""", this means QtGui is correct when using Qt abstraction layer
# If I don't see """!""", this means to change QtGui to QtWidgets

class TubxFaceUI(QtGui.QDialog):
  """
  This class creates the UI using pyQT
  """
  # Constructor
  def __init__(self):
    # Find the parent class (QDialog) and refer it to self. We then call QDialog's init method
    # It is the same as QtWidgets.QDialog.__init__(self)
    super(TubxFaceUI, self).__init__()

    self.setWindowTitle('TubxFaceUI')
    self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    #Create the file import export class
    self.Tubxlibrary = ExportingData.TubxLibrary()
    #Build the UI
    self.buildUI()
    #Populate the library
    self.populateUI()

  def buildUI(self):
    """
    This function builds the UI
    """
    MainLayout = QtGui.QVBoxLayout(self)


    #Get the directory to load the banner
    SCRIPTDIR = cmds.internalVar(userScriptDir = True)
    # Use os specific seperator to join directory name together
    banner_directory = os.path.join(SCRIPTDIR, 'TubxFace', 'TubxFaceBanner.jpg')
    BannerLabel = QtGui.QLabel()
    BannerPic = QtGui.QPixmap(banner_directory)
    BannerLabel.setPixmap(BannerPic)
    BannerLabel.setScaledContents(True)
    #BannerLabel.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
    MainLayout.addWidget(BannerLabel)

    TabLayoutWidget = QtGui.QTabWidget()
    MainLayout.addWidget(TabLayoutWidget)

    self.createLibraryTabWidget = QtGui.QWidget()
    TabLayoutWidget.addTab(self.createLibraryTabWidget, "Create Section")
    self.createLibraryUI()

    self.deformLibraryTabWidget = QtGui.QWidget()
    TabLayoutWidget.addTab(self.deformLibraryTabWidget, "Deform Section")
    self.deformLibraryUI()

  def populateUI(self):
    """
    This function populates the library
    """
    #Clear list widget content
    self.listScreenshotWidget.clear()

    self.Tubxlibrary.find()

    for name, info in self.Tubxlibrary.items():
      TubxGeo = QtGui.QListWidgetItem(name)
      self.listScreenshotWidget.addItem(TubxGeo)

      screenshot = info.get('screenshot')
      if screenshot:
        """!"""
        icon = QtGui.QIcon(screenshot)
        TubxGeo.setIcon(icon)

  def createLibraryUI(self):
    """
    This function creates the UI for the createLibrary section
    """
    layout = QtGui.QVBoxLayout()

    createWidget = QtGui.QWidget()
    createLayout = QtGui.QHBoxLayout(createWidget)
    layout.addWidget(createWidget)

    labelSelectLibraryMesh = QtGui.QLabel("Use mesh as library")
    createLayout.addWidget(labelSelectLibraryMesh)

    useMeshButton = QtGui.QPushButton("Use this mesh as Library")
    useMeshButton.clicked.connect(self.useLibraryMesh)
    createLayout.addWidget(useMeshButton)

    labelDefiningMeshParts = QtGui.QLabel("Defining Mesh Parts")
    layout.addWidget(labelDefiningMeshParts)

    # Create buttons for assigning mesh parts
    ShadingList = ['TubxEye', 'TubxNoseBridge', 'TubxNose', 'TubxMouth', 'TubxMouthLoop', 'TubxForehead',
                   'TubxEar', 'TubxBackHead', 'TubxLowerBackHead', 'TubxCheek', 'TubxChin', 'TubxDefault']

    for i in range (0,len(ShadingList)):
      currentMesh = QtGui.QPushButton(ShadingList[i])
      currentMesh.clicked.connect(partial(self.assignPartsShader,ShadingList[i]))
      layout.addWidget(currentMesh)

    labelExtraInfo = QtGui.QLabel("Assigning Extra Info")
    layout.addWidget(labelExtraInfo)

    widgetExtraInfo = QtGui.QWidget()
    self.layoutExtraInfo = QtGui.QGridLayout(widgetExtraInfo)
    layout.addWidget(widgetExtraInfo)


    # Populate the grid extra info layout
    EarLabels = ["Top Ear" , "Upper Ear" , "Mid Ear", "Lower Ear", "Bot Ear"]
    for i in range(0, len(EarLabels)):
      labelEarParts = QtGui.QLabel(EarLabels[i])
      self.layoutExtraInfo.addWidget(labelEarParts,0,i+1)

    self.earLabelList = []

    for i in range(0,2):
      labelCurrentEar = QtGui.QLabel("Ear%s" % i)
      self.layoutExtraInfo.addWidget(labelCurrentEar, i+1, 0)
      eachEarLabelList = []
      for j in range(0, len(EarLabels)):
        EarVertexLine = QtGui.QLineEdit()
        #Append to a list so we have access to the widget
        eachEarLabelList.append(EarVertexLine)
        self.layoutExtraInfo.addWidget(EarVertexLine, i+1, j+1)
      self.earLabelList.append(eachEarLabelList)
      buttonEarExtraInfo = QtGui.QPushButton("SelectEarData")
      buttonEarExtraInfo.clicked.connect(self.assignEarData)

      self.layoutExtraInfo.addWidget(buttonEarExtraInfo, i+1, len(EarLabels)+1)

    # Save to library
    saveWidget = QtGui.QWidget()
    saveLayout = QtGui.QHBoxLayout(saveWidget)
    layout.addWidget(saveWidget)

    self.lineSaveName = QtGui.QLineEdit()
    saveLayout.addWidget(self.lineSaveName)

    SaveButton = QtGui.QPushButton("Create Library")
    SaveButton.clicked.connect(self.saveLibrary)
    saveLayout.addWidget(SaveButton)


    self.createLibraryTabWidget.setLayout(layout)

  def deformLibraryUI(self):
    """
    This function creates the UI for the deform library function
    """
    layout = QtGui.QVBoxLayout()

    self.FrontImagePath = ""
    self.SideImagePath = ""

    #Let screeshot icon size be 128 pixels
    screenShotSize = 80
    #Set buffer between screen shots to 12 pixels
    buffersize = 12
    self.listScreenshotWidget = QtGui.QListWidget()
    self.listScreenshotWidget.setViewMode(QtGui.QListWidget.IconMode)
    self.listScreenshotWidget.setIconSize(QtCore.QSize(screenShotSize, screenShotSize))
    self.listScreenshotWidget.setResizeMode(QtGui.QListWidget.Adjust)
    self.listScreenshotWidget.setGridSize(QtCore.QSize(screenShotSize+buffersize, screenShotSize+buffersize))
    layout.addWidget(self.listScreenshotWidget)

    #Add a refresh button to refresh the listScreenshotWidget
    refreshButton = QtGui.QPushButton("Refresh")
    refreshButton.clicked.connect(self.populateUI)
    layout.addWidget(refreshButton)

    #Add the front and side image input
    imageInputWidget = QtGui.QWidget()
    imageInputLayout = QtGui.QGridLayout(imageInputWidget)
    layout.addWidget(imageInputWidget)

    imageInputLabel = QtGui.QLabel("User Orthographic images")
    imageInputLayout.addWidget(imageInputLabel,0,0)

    frontInputLabel = QtGui.QLabel("Front view")
    imageInputLayout.addWidget(frontInputLabel,1,0)

    self.lineFront = QtGui.QLineEdit()
    imageInputLayout.addWidget(self.lineFront,1,1)

    loadFrontButton = QtGui.QPushButton("Select Front")
    loadFrontButton.clicked.connect(self.selectFrontView)
    imageInputLayout.addWidget(loadFrontButton,1,2)


    sideInputLabel = QtGui.QLabel("Side view")
    imageInputLayout.addWidget(sideInputLabel,2,0)

    self.lineSide = QtGui.QLineEdit()
    imageInputLayout.addWidget(self.lineSide, 2,1)

    loadSideButton = QtGui.QPushButton("Select Side")
    loadSideButton.clicked.connect(self.selectSideView)
    imageInputLayout.addWidget(loadSideButton,2,2)

    #Add an option to change the resolution of the scans and deformers
    resolutionLabel = QtGui.QLabel("Resolution")
    resolutionLabel.setStyleSheet("font-weight: bold; font-size: 15px;")
    layout.addWidget(resolutionLabel)

    resolutionWidget = QtGui.QWidget()
    resolutionLayout = QtGui.QGridLayout(resolutionWidget)
    layout.addWidget(resolutionWidget)

    eyeResolutionLabel = QtGui.QLabel("Eye")
    resolutionLayout.addWidget(eyeResolutionLabel,0,0)
    self.eyeResolutionWidget = QtGui.QSpinBox()
    self.eyeResolutionWidget.setRange(8,96)
    self.eyeResolutionWidget.setValue(16)
    self.eyeResolutionWidget.setSingleStep(8)
    resolutionLayout.addWidget(self.eyeResolutionWidget,1,0)

    mouthResolutionLabel = QtGui.QLabel("Mouth")
    resolutionLayout.addWidget(mouthResolutionLabel, 0, 1)
    self.mouthResolutionWidget = QtGui.QSpinBox()
    self.mouthResolutionWidget.setRange(8, 96)
    self.mouthResolutionWidget.setValue(24)
    self.mouthResolutionWidget.setSingleStep(8)
    resolutionLayout.addWidget(self.mouthResolutionWidget, 1, 1)

    mouthLoopResolutionLabel = QtGui.QLabel("Mouth Loop")
    resolutionLayout.addWidget(mouthLoopResolutionLabel, 0, 2)
    self.mouthLoopResolutionWidget = QtGui.QSpinBox()
    self.mouthLoopResolutionWidget.setRange(8, 96)
    self.mouthLoopResolutionWidget.setValue(16)
    self.mouthLoopResolutionWidget.setSingleStep(8)
    resolutionLayout.addWidget(self.mouthLoopResolutionWidget, 1, 2)

    noseResolutionLabel = QtGui.QLabel("Nose")
    resolutionLayout.addWidget(noseResolutionLabel, 2, 0)
    self.noseResolutionWidget = QtGui.QSpinBox()
    self.noseResolutionWidget.setRange(4, 96)
    self.noseResolutionWidget.setValue(8)
    self.noseResolutionWidget.setSingleStep(4)
    resolutionLayout.addWidget(self.noseResolutionWidget, 3, 0)

    eyebrowResolutionLabel = QtGui.QLabel("Eyebrow")
    resolutionLayout.addWidget(eyebrowResolutionLabel, 2, 1)
    self.eyebrowResolutionWidget = QtGui.QSpinBox()
    self.eyebrowResolutionWidget.setRange(8, 96)
    self.eyebrowResolutionWidget.setValue(16)
    self.eyebrowResolutionWidget.setSingleStep(8)
    resolutionLayout.addWidget(self.eyebrowResolutionWidget, 3, 1)

    nosebridgeResolutionLabel = QtGui.QLabel("NoseBridge")
    resolutionLayout.addWidget(nosebridgeResolutionLabel, 2, 2)
    self.nosebridgeResolutionWidget = QtGui.QSpinBox()
    self.nosebridgeResolutionWidget.setRange(4, 96)
    self.nosebridgeResolutionWidget.setValue(4)
    self.nosebridgeResolutionWidget.setSingleStep(4)
    resolutionLayout.addWidget(self.nosebridgeResolutionWidget, 3, 2)


    #Add an option to allow you to see the scan first to correct any errors in calculations before edit stage
    DeformationLabel = QtGui.QLabel("Deformation instructions")
    DeformationLabel.setStyleSheet("font-weight: bold; font-size: 15px;")
    DeformationInstructions = QtGui.QLabel ("If user wants to inspect scan, check the checkbox and click generate mesh.")
    DeformationInstructions2 = QtGui.QLabel("After inspecting and editing, click on the PROCEED TO DEFORM button.")
    DeformationInstructions3 = QtGui.QLabel("If not, just uncheck the checkbox and click generate mesh.")
    layout.addWidget(DeformationLabel)
    layout.addWidget(DeformationInstructions)
    layout.addWidget(DeformationInstructions2)
    layout.addWidget(DeformationInstructions3)

    checkScanWidget = QtGui.QWidget()
    checkScanLayout = QtGui.QHBoxLayout(checkScanWidget)
    layout.addWidget(checkScanWidget)

    self.checkBeforeCleanUp = QtGui.QCheckBox("Inspect Scan First before Deformation")
    self.checkBeforeCleanUp.setChecked(1)
    checkScanLayout.addWidget(self.checkBeforeCleanUp)

    self.proceedToCleanUp = QtGui.QPushButton("Proceed to deform")
    self.proceedToCleanUp.clicked.connect(self.deformGeometry)
    checkScanLayout.addWidget(self.proceedToCleanUp)

    #Add the generate mesh button
    GenerateMeshButton = QtGui.QPushButton("Generate Mesh")
    GenerateMeshButton.clicked.connect(self.generateGeometry)
    layout.addWidget(GenerateMeshButton)

    #Add the edit mode
    editGeoWidget = QtGui.QWidget()
    editGeoLayout = QtGui.QGridLayout(editGeoWidget)
    layout.addWidget(editGeoWidget)

    editLabel = QtGui.QLabel("Edit Section")
    editLabel.setStyleSheet("font-weight: bold; font-size: 15px;")
    editGeoLayout.addWidget(editLabel,0,0)

    #Add the various modes of edit
    self.paintEditCheckbox = QtGui.QCheckBox("Paint Mode")
    self.paintEditCheckbox.setChecked(1)
    self.paintEditCheckbox.toggled.connect(self.toggledPaintEdit)
    editGeoLayout.addWidget(self.paintEditCheckbox, 1,0)

    self.controlEditCheckbox = QtGui.QCheckBox("Control Mode")
    self.controlEditCheckbox.setChecked(0)
    self.controlEditCheckbox.toggled.connect(self.toggledCtrlEdit)
    editGeoLayout.addWidget(self.controlEditCheckbox, 1,1)

    #Add the finish button for final cleanup of scene
    finishButton = QtGui.QPushButton("Finalise")
    finishButton.clicked.connect(self.finaliseCleanUp)
    layout.addWidget(finishButton)


    self.deformLibraryTabWidget.setLayout(layout)

  def useLibraryMesh(self):
    """
    This function allows the user to select a mesh for the library creation
    """
    #When the button is clicked, first we get a duplicate of the mesh
    selectedMesh = cmds.ls(sl=True)
    if not selectedMesh:
      #This means nothing is selected. So don't do anything
      return

    self.workMesh = cmds.duplicate(n ='TubxLibraryMesh', rr=True)
    #We we isolate the object
    cmds.select(self.workMesh)
    cmds.isolateSelect('modelPanel4', state=1)
    cmds.select(self.workMesh)
    cmds.isolateSelect('modelPanel4', addSelected = True)

    #We create the shaders
    LibraryGeneration.createShaders()

    #Finally, we assign the default shader to the workMesh
    cmds.sets(self.workMesh, edit = True, forceElement = 'TubxDefaultSG')

    #We also enable tracking selection so we can get the order of selection for the ear vertex
    self.TrackingStatus = cmds.selectPref(q=True, trackSelectionOrder=True)
    cmds.selectPref(trackSelectionOrder = True)

  def assignPartsShader(self, shader):
    """
    This function allows the shader to be assigned to the selected faces
    Args:
      shader: The shader to be assigned
    """
    #We assign the shader to the selected faces
    Selection = cmds.ls(sl=True)
    if not Selection:
      return
    cmds.sets(Selection,edit=True, forceElement = "%sSG" % shader)

  def assignEarData(self):
    """
    This function allows the user to specify where the ear data is
    """
    #We query the currently selected vertices
    SelectedVertex = cmds.ls(orderedSelection=True)
    SelectedVertex = cmds.filterExpand(SelectedVertex, ex=True, sm=31)
    if len(SelectedVertex) > 5:
      print "Too many vertex selected. Only 5 needed"
      return

    elif len(SelectedVertex) < 5:
      print "Too little vertex selected. 5 Needed"
      return

    #Get button location
    button = self.sender()
    idx = self.layoutExtraInfo.indexOf(button)
    location = self.layoutExtraInfo.getItemPosition(idx)

    """
    print location
    print "Button", button, "at row/col", location[:2]
    """

    #Update the text in the line edit accordingly to which button was clicked
    for i in range(0, len(SelectedVertex)):
      self.earLabelList[location[0] - 1][i].setText(SelectedVertex[i])

  def saveLibrary(self):
    """
    This function allows the user to save a library
    """
    #Get save name
    name = self.lineSaveName.text()

    #Rename mesh
    self.workMesh = cmds.rename(self.workMesh, name)

    #Resize mesh to a 1x1x1 bounding volume
    cmds.makeIdentity(self.workMesh, apply=True)
    BoundingBox = cmds.exactWorldBoundingBox(self.workMesh)
    xLength = BoundingBox[3] - BoundingBox[0]
    yLength = BoundingBox[4] - BoundingBox[1]
    zLength = BoundingBox[5] - BoundingBox[2]

    if xLength != 0 and yLength != 0 and zLength != 0:
      # Next we need to find the longest length and scale in down such that the
      # longest length fits within the unit Cube
      if xLength > yLength and xLength > zLength:
        scaleFactor = 1.0 / xLength
      elif yLength > xLength and yLength > zLength:
        scaleFactor = 1.0 / yLength
      elif zLength > xLength and zLength > yLength:
        scaleFactor = 1.0 / zLength

    else:
      cmds.error("Division by zero. The library geo is not 3D")
      return

    cmds.xform(self.workMesh, scale=[scaleFactor, scaleFactor, scaleFactor])
    cmds.select(self.workMesh)
    cmds.move(0, 0, 0, rpr=True, ws=True)
    cmds.makeIdentity(self.workMesh, apply=True)

    #Get ear data
    ExtraData = []
    for i in range(0,2):
      for j in range(0,5):
        currentName = self.earLabelList[i][j].text()
        if not currentName:
          break
        splitName = currentName.split(".vtx")
        if splitName[0] != name:
          currentName = "%s.vtx%s" % (name, splitName[1])

        ExtraData.append(currentName)

    if not name.strip():
      cmds.warning("Name has not been given. Please give a name")
      return

    #Call the save function
    self.Tubxlibrary.save(name, self.workMesh, earData = ExtraData)

    #Clean Up
    cmds.select(self.workMesh)
    cmds.delete()
    self.workMesh = ""
    cmds.isolateSelect('modelPanel4', state=0)
    ShadingList = ['TubxEye', 'TubxNoseBridge', 'TubxNose', 'TubxMouth', 'TubxMouthLoop', 'TubxForehead',
                   'TubxEar', 'TubxBackHead', 'TubxLowerBackHead', 'TubxCheek', 'TubxChin', 'TubxDefault']
    cmds.select(ShadingList)
    cmds.delete()
    cmds.isolateSelect('modelPanel4', state=0)
    #We also turn back the tracking selection to what it was
    cmds.selectPref(trackSelectionOrder=self.TrackingStatus)

  def selectFrontView(self):
    """
    This function allows the user to select a front view image
    """
    basicFilter = "Image Files (*.png *.tiff);;PNG (*.png);;TIFF (*.tiff);;All Files (*.*)"
    self.hide()
    self.FrontImagePath = cmds.fileDialog2(caption="Please select front image", fileFilter=basicFilter, fm=1)
    self.lineFront.setText(str(self.FrontImagePath[0]))
    self.show()

  def selectSideView(self):
    """
    This function allows the user to select a side view image
    """
    basicFilter = "Image Files (*.png *.tiff);;PNG (*.png);;TIFF (*.tiff);;All Files (*.*)"
    self.hide()
    self.SideImagePath = cmds.fileDialog2(caption="Please select side image", fileFilter=basicFilter, fm=1)
    self.lineSide.setText(str(self.SideImagePath[0]))
    self.show()

  def generateGeometry(self):
    """
    This function allows the user to load the mesh and scan the points and create the locators
    """
    currentTubxItem = self.listScreenshotWidget.currentItem()
    currentFrontImage = self.lineFront.text()
    currentSideImage = self.lineSide.text()

    if not currentTubxItem or not currentFrontImage or not currentSideImage:
      return

    #We first load the geometry back in with the shaders
    self.mesh = currentTubxItem.text()
    self.Tubxlibrary.load(self.mesh)

    #We then recreate shaders in the case where shaders was missing from the import. This is to prevent valueError
    LibraryGeneration.createShaders()

    #We get the list for resolution
    eyeRes = self.eyeResolutionWidget.value()
    mouthRes = self.mouthResolutionWidget.value()
    mouthLoopRes = self.mouthLoopResolutionWidget.value()
    noseRes = self.noseResolutionWidget.value()
    eyebrowRes = self.eyebrowResolutionWidget.value()
    noseBridgeRes = self.nosebridgeResolutionWidget.value()

    self.ResolutionList = [eyeRes,mouthRes,mouthLoopRes,noseRes,eyebrowRes,noseBridgeRes]

    #We then separate the head out and create the controls and relationships
    self.relationshipList, self.Objects = LibraryGeneration.createMeshAndControl(self.mesh, self.ResolutionList)

    #We now get the additional data from the json file and create the extra controls
    dataGrp = self.Tubxlibrary.loadExtraData(self.mesh)
    LibraryGeneration.createDataMeshAndControl(dataGrp)

    #Now we load the image data and convert it into 3D coordinates
    MyImage = ScanningImage.ImageScan(currentFrontImage, currentSideImage)
    self.LocatorGrp = MyImage.generateCoord(self.ResolutionList)

    #We then check if the checkbox of whether the user wants to take a look at the scan is checked
    CheckScan = self.checkBeforeCleanUp.checkState()
    if not CheckScan:
      #This means the user do not want to check
      self.deformGeometry()

    if CheckScan:
      cmds.modelEditor('modelPanel4', e=True, nurbsCurves=False, polymeshes=False)
      cmds.select(self.LocatorGrp, hi=True)
      locators = cmds.ls(sl=True)
      for i in range(1, len(locators)):
        cmds.setAttr("%s.localScaleX" % locators[i], 10)
        cmds.setAttr("%s.localScaleY" % locators[i], 10)
        cmds.setAttr("%s.localScaleZ" % locators[i], 10)

  def deformGeometry(self):
    """
    This function deforms the geometry with the following steps
        1) We first separate the mesh into parts.
        2) We then create the controls and BIND IT TO THE PARTS
        2) We then deform the controls and it moves the parts
        4) We then find the vertex relationships and join them together
        5) We then average out the vertex in each part.
    """
    cmds.modelEditor('modelPanel4', e=True, nurbsCurves=True, polymeshes=True)
    #DeformLibrary.matchCircleDirectionTest(self.LocatorGrp)
    DeformLibrary.deformGeoToImage(self.LocatorGrp, self.ResolutionList)
    DeformLibrary.cleanUpforEdit2(self.LocatorGrp, self.Objects, self.relationshipList, self.mesh)
    self.Objects = []
    self.relationshipList = []

  def toggledPaintEdit(self):
    """
    This function is run when the user toggles paint edit
    """
    #We check its current status and the other control status first
    selfStatus = self.paintEditCheckbox.checkState()
    #If selfStatus is on, we switch other status off
    if selfStatus:
      if self.controlEditCheckbox.checkState():
        self.controlEditCheckbox.setChecked(0)
        self.createPaintEdit()
        self.deleteCtrlEdit()

    #If selfStatus is off, we switch other status on
    elif not selfStatus:
      if not self.controlEditCheckbox.checkState():
        self.controlEditCheckbox.setChecked(1)
        self.deletePaintEdit()
        self.createCtrlEdit()

  def toggledCtrlEdit(self):
    """
    This function is run when the user toggle ctrl edit
    """
    #We check its current status and the other control status first
    selfStatus = self.controlEditCheckbox.checkState()
    #If selfStatus is on, we switch other status off
    if selfStatus:
      if self.paintEditCheckbox.checkState():
        self.paintEditCheckbox.setChecked(0)
        self.createCtrlEdit()
        self.deletePaintEdit()

    #If selfStatus is off, we switch other status on
    elif not selfStatus:
      if not self.paintEditCheckbox.checkState():
        self.paintEditCheckbox.setChecked(1)
        self.deleteCtrlEdit()
        self.createPaintEdit()

  def createCtrlEdit(self):
    """
    This allows the user to manually manipulate curves during edit stage
    """
    print self.mesh
    self.relationshipList, self.Objects = LibraryGeneration.createMeshAndControl(self.mesh, self.ResolutionList)
    cmds.delete(self.mesh)

    #We now create the control edit window
    self.editWindowID = "editControls"
    if cmds.window(self.editWindowID, exists=True):
      cmds.deleteUI(self.editWindowID)

    window = cmds.window(self.editWindowID, title = "edit controls")
    cmds.paneLayout()
    editModelPanel = cmds.modelPanel()
    cmds.modelEditor(editModelPanel, e=True, allObjects=False)
    cmds.modelEditor(editModelPanel, e=True, nurbsCurves=True, controlVertices = True)
    cmds.showWindow(window)

  def deleteCtrlEdit(self):
    """
    This function is run when we exit ctrl edit stage
    """
    # We delete the objects history so that the curves no longer influence the object
    for i in self.Objects:
      #print "Smoothing ", i
      #CreateRelationships.averageInsideVertices(i)
      cmds.select(i)
      mel.eval('SculptGeometryTool;')
      mel.eval('artPuttyCtx -e -mtm "relax" `currentCtx`;')
      mel.eval('artPuttyCtx -e -opacity 0.3 `currentCtx`;')
      mel.eval('artPuttyCtx -e -clear `currentCtx`;')
      mel.eval('setToolTo $gMove;')
      cmds.delete(i, ch=True)

    # Need to give a better name
    # We then delete the curves and combine the geometry based on the relationship
    cmds.select("*Curve*")
    cmds.delete()
    CreateRelationships.findRelationships(self.relationshipList)

    # We combine the objects together and merge the matching vertices
    cmds.select(self.Objects)
    mesh = cmds.polyUnite(n=self.mesh, ch=0)
    cmds.polyMergeVertex(self.mesh, d=0.0001, am=True, ch=0)

    #We reset the relationshiplist and object
    self.Objects = []
    self.relationshipList = []

    #We delete the edit window
    if cmds.window(self.editWindowID, exists=True):
      cmds.deleteUI(self.editWindowID)

  def createPaintEdit(self):
    """
    This allow the user to use the maya art context to edit
    """
    mel.eval('SculptGeometryToolOptions;')

  def deletePaintEdit(self):
    """
    This function is run when we exit paint edit
    """
    mel.eval('setToolTo $gMove;')

  def finaliseCleanUp(self):
    """
    This function is run to clean up the maya file and exit the tool
    """
    # Clean Up
    #We check current edit status. If it is on, we set it to off
    paintEdit = self.paintEditCheckbox.checkState()
    ctrlEdit = self.controlEditCheckbox.checkState()
    if paintEdit:
      self.deletePaintEdit()
    if ctrlEdit:
      self.deleteCtrlEdit()

    #Set object to default lambert
    cmds.select(self.mesh)
    Selection = cmds.ls(sl=True)
    cmds.sets(Selection, edit=True, forceElement="initialShadingGroup")

    #Delete shaders
    ShadingList = ['TubxEye', 'TubxNoseBridge', 'TubxNose', 'TubxMouth', 'TubxMouthLoop', 'TubxForehead',
                   'TubxEar', 'TubxBackHead', 'TubxLowerBackHead', 'TubxCheek', 'TubxChin', 'TubxDefault']
    cmds.select(ShadingList)
    cmds.delete()

    #Set self.mesh to a # name in order to prevent any naming error
    cmds.rename(self.mesh, "%s#" % self.mesh)
    self.mesh= ""
    self.ResolutionList = []

    #Finally, we close the UI
    self.close()


def showUI():
  """
  This function creates the UI
  Returns: The UI
  """
  UI = TubxFaceUI()
  UI.show()
  return UI
