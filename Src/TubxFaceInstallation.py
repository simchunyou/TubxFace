'''
This script installs the TubxFace Button to the Maya Custom Shelf
'''

#Getting the directory path of the script
from maya import cmds
import os
import sys
ScriptDirectory = cmds.internalVar(userScriptDir = True)
sysPath = os.path.join(ScriptDirectory, 'TubxFace')
#Update the script Path if necessary
sysPathUpdated = 0
for path in sys.path:
    if path == sysPath:
        sysPathUpdated = 1
if sysPathUpdated == 0:
    sys.path.append(sysPath)
#Get the directory of the icon
iconPath = os.path.join(sysPath, 'TubxFaceIcon.png')

cmds.shelfButton(i1=iconPath, l = "TubxFaceTool", annotation = "TubxFaceTool", parent = "Custom", command = "from maya import cmds\nimport os\nimport sys\nScriptDirectory = cmds.internalVar(userScriptDir = True)\nsysPath = os.path.join(ScriptDirectory, 'TubxFace')\nsysPathUpdated = 0\nfor path in sys.path:\n    if path == sysPath:\n        sysPathUpdated = 1\nif sysPathUpdated == 0:\n    sys.path.append(sysPath)\nimport TubxFaceUI\nUI = TubxFaceUI.showUI()")
