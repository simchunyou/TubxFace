'''
This script allows the user to export and import required data for the library
'''

from maya import cmds
import os
import json

'''
#This are just testing directory paths and thus are commented out

#At this moment, lets put the files in the current project directory.
#USERWORKSPACEDIR = cmds.workspace(q=True, rd=True)
#This variable is not used but is left here just in case I want to switch the exporting of data to
#The main maya folder
#USERAPPDIR = cmds.internalVar(userAppDir = True)
# Use os specific seperator to join directory name together
#DIRECTORY = os.path.join(USERWORKSPACEDIR, 'TubxFaceLibrary')
#print DIRECTORY
'''

def createDirectory(directory):
  """
  This function creates a directory to store our library if one does not exist
  Args:
    directory: The directory of the current user workspace
  """

  print directory
  if not os.path.exists(directory):
    #If directory does not exist, make this directory
    print "Making Directory"
    USERWORKSPACEDIR = cmds.workspace(q=True, rd=True)
    DIRECTORY = os.path.join(USERWORKSPACEDIR, 'TubxFaceLibrary')
    os.mkdir(DIRECTORY)

class TubxLibrary(dict):
  """
  This class inherits from a dictionary. Thus it is a dictionary class.
  This class allows the saving and loading of library files to extend TUBXFace or use the tool.
  """
  def __init__(self):
    """
    This function creates the directory path
    """
    USERWORKSPACEDIR = cmds.workspace(q=True, rd=True)
    self.DIRECTORY = os.path.join(USERWORKSPACEDIR, 'TubxFaceLibrary')
    print self.DIRECTORY
    # To make sure there is a directory that exists
    createDirectory(self.DIRECTORY)

  def save(self, name, activeMesh, **info):
    """
    The function saves out the required data
    Args:
      name: The name to save out to
      activeMesh: The mesh to save out and be used for the library
      **info: Any extra information to save out to in the JSON file

    """
    directory = self.DIRECTORY
    #To make sure there is a directory to save to

    createDirectory(directory)

    #Create path to save to
    path = os.path.join(directory, "%s.ma" % name)
    userInfoPath = os.path.join(directory, "%s.json" % name)

    # We create an info dictionary to store the information of a particular file.
    # The **info parameter allows extra information to be added to the info dictionary by
    # adding extra parameters when calling the save function.

    # We add some default information to the info dictionary.
    info['name'] = name
    info['path'] = path

    # Now we save out the files.
    # ---------------------------------
    # We first save out the .ma file
    cmds.select(activeMesh)
    cmds.file(rename=path)
    if cmds.ls(sl=True):
      cmds.file(force = True, type="mayaAscii", exportSelected = True)
    else:
      print "No objects to save as nothing is selected. No mesh is active"
      return

    # Now we save out a screenshot
    # We also add this to the info dictionary
    info['screenshot'] = self.saveScreenshot(name)

    # Now we save out the .json file
    # This means open a file in the path as f, write in it, and dump the info dictionary in here
    with open(userInfoPath, 'w') as f:
      json.dump(info, f, indent=4)

    #Updating the dictionary every time we save
    self[name] = info

  def find(self):
    directory = self.DIRECTORY
    self.clear()
    if not os.path.exists(directory):
      print "The directory does not exist"
      return

    #List the directory
    allFiles = os.listdir(directory)

    #Seperate and list only the .ma files
    mayaFiles = [f for f in allFiles if f.endswith(".ma")]

    for maFiles in mayaFiles:
      # Split the extension from the file names
      name, ext = os.path.splitext(maFiles)
      # as now maFiles only give the name of the ma files, but we need the full directory, we join them
      mayaFilePath = os.path.join(directory, maFiles)

      # We then find the corresponding json file
      jsonFile = '%s.json' % name
      if jsonFile in allFiles:
        jsonPath = os.path.join(directory, jsonFile)

        # Now we read the json file
        with open(jsonPath, 'r') as f:
          info = json.load(f)

      else:
        print "No json file found, %s is not a complete Tubx file" % name
        continue

      # We then find the corresponding jpg file
      screenshot = "%s.jpg" % name
      if screenshot in allFiles:
        screenshotPath = os.path.join(directory, screenshot)
        info["screenshot"] = screenshotPath

      else:
        print "No screenshot file found, %s is not a complete Tubx file" % name
        continue


      # Now we store it as a dictionary, since the class is inherited from a dictionary
      self[name] = info

  def load(self, name):
    """
    This function loads the mesh from the library
    Args:
      name: The name of the library mesh
    """
    self.find()
    mayaFile = "%s.ma" % name
    directory = self.DIRECTORY
    loadingPath = os.path.join(directory, mayaFile)
    #loadingPath = self[name]['path']
    print "Loading Path is ", loadingPath
    cmds.file(loadingPath, i =True, usingNamespaces = False)

  def loadExtraData(self, name):
    """
    This function loads the information from the JSON file
    Args:
      name: The name of the library

    Returns: the data from the json file

    """
    directory = self.DIRECTORY
    allFiles = os.listdir(directory)
    jsonFile = "%s.json" % name
    if jsonFile in allFiles:
      jsonPath = os.path.join(directory, jsonFile)

      # Now we read the json file
      with open(jsonPath, 'r') as f:
        info = json.load(f)

    dataGrp = []
    #We check if ear data exists and appends to dataGrp
    if 'earData' not in info:
      print "NO EXTRA EAR INFO"

    else:
      earData = (info['earData'])
      for i in range(0, len(earData), 5):
        individualEar = []
        for j in range(0, 5):
          if earData[i+j] == "" :
            break
          else:
            individualEar.append(earData[i+j])
        if individualEar:
          print "individual ear is ", individualEar
          dataGrp.append(individualEar)
          print "dataGrp is ", dataGrp


    return dataGrp

  def saveScreenshot(self, name):
    """
    This function saves a screenshot of the library mesh
    Args:
      name: The name of the file to be saved

    Returns: The path to the screenshot

    """
    directory = self.DIRECTORY
    screenshotPath = os.path.join(directory, "%s.jpg" % name)
    cmds.viewFit()
    #We deselect the mesh so we can screenshot it prettier
    cmds.select(clear=True)
    #Save as jpeg
    cmds.setAttr('defaultRenderGlobals.imageFormat', 8)
    cmds.playblast(completeFilename = screenshotPath, forceOverwrite = True, format = 'image',
                   width = 200, height = 200, showOrnaments = False, startTime = 1, endTime = 1,
                   viewer = False)

    return screenshotPath