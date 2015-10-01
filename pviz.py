#!/usr/bin/env pvbatch
# =========================================
# PVIZ MAIN MODULE (http://pviz.net)
# Author: A. Ruiz  (http://ruizanthony.net)
# =========================================
#Copyright (c) 2014, Anthony Ruiz
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# =========================================
from paraview.simple import *
from math import cos, sin, pi
import sys
import os

# Some colors (constants of pviz module)
black    = [0.0,0.0,0.0]
white    = [1.0,1.0,1.0]
darkGrey = [0.1,0.1,0.1]
liteGrey = [0.9,0.9,0.9]
blue     = [0.0,0.3,1.0]
aqua     = [0.0,0.5,1.0]

# Main Class: viz
# Used to load your data and set default properties and filter
# put ``viz(sys.argv)`` to the top of your post-processing scripts
# see  $PVIZ/simpleExamples for examples
#   or 
class viz:
  def __init__(self,args):
    print 'Creating viz object using args: ',args
    paraview.simple._DisableFirstRenderCameraReset() # Prevent resetCamera
    self.parseOptions(args) # Extract filename, color, ... from command line options
    self.path=os.getcwd()   # Get current path

    # Get file base name and extension except if interactive session
    if not self.interactive: self.baseName, self.ext = os.path.splitext(self.fileName)

    # Load data if no state file is present
    if self.stateName == None:
      # loading data from the command line
      if not self.interactive: self.load()
      # GUI python shell: don't load the data, GetActiveSource instead
      else:                    self.loadInteractive()
    # If state file is present, load it
    else:
      self.loadMyState()
    # Create default bar attributes
    self.barProperties = barProperties(logscale = self.logscale)

  def load(self):
    fileName = self.fileName
    print "Loading %s ..." %(fileName)
    # Choose correct reader
    if self.ext == '.case':
      case = EnSightReader( CaseFileName=fileName )
      self.timeVector = case.TimestepValues.GetData()
    elif self.ext in ['.xdmf', '.xmf']:
      try:    # For paraview version < 4.4
        case = XDMFReader( FileName=fileName )
      except: # For paraview version 4.4
        case = XDMFReader( FileNames=[fileName])
      self.timeVector = case.TimestepValues
    elif self.ext == '.vtu':
      case = XMLUnstructuredGridReader( FileName=fileName )
      self.timeVector = case.TimestepValues.GetData()      
    elif self.ext == '.vtm' :
      case = XMLMultiBlockDataReader( FileName=fileName )
      self.timeVector = case.TimestepValues.GetData()      
    elif self.ext == '.vts' :
      case = XMLStructuredGridReader( FileName=fileName )
      self.timeVector = case.TimestepValues.GetData()      
    elif self.ext == '.pvd' :
      case = PVDReader( FileName=fileName )
      self.timeVector = case.TimestepValues.GetData()      
    elif self.ext == '.pvtu':
      case = XMLPartitionedUnstructuredGridReader( FileName=fileName )
      self.timeVector = case.TimestepValues.GetData()      
    else:
      print "unable to define a paraview reader for file type : ",self.ext
      sys.exit()

    # Readers are using different types of timeVector ... catch possible errrors
    try:
      if len(self.timeVector) == 0: self.timeVector = [ 0 ]
    except:
      self.timeVector = [ 0 ]

    # Ensure that timeVector is indeed a vector (enable looping over timeVector)
    try:    print "Number of time steps:",len(self.timeVector)
    except: self.timeVector = [ self.timeVector ]

    # Determine whether to show case or not (do not need to show case for 1D lines or histogram analysis)
    Show(case) # need to create representation properties before possibly calling mergeCleanD3point()
    if self.showcase == 0: hidePart()

    # If multiblock solutions, ensure that block interfaces are not visible
    if self.ext in ['.vts' , '.vtm', '.xmf' ,'.xdmf']:
      hidePart()
      case = mergeCleanD3() # This is an expensive macro (memory and CPU time), but it is necessary for clean cell2point
      # IBC specific to raptor
      ibcWallVarName='ibc_wall'
      if ibcWallVarName in case.CellData.keys():
        case = Threshold( Scalars=['CELLS', ibcWallVarName], ThresholdRange=[0.0, 0.1], AllScalars=1, UseContinuousCellRange=0 )
      if self.cell2point == 1:
        # Test if there is CellData, if so, transform it to PointData (linear variations of variables instead of piecewise constant)
        if len(case.CellData.values()) >= 1:
          print 'Transforming celldata to point data'
          case = makeCell2Point()

    self.view=GetRenderView()  # store view in the viz object
    setViewDefaults(self.view) # set default values for view (light, color, ...)

  def loadInteractive(self):
    self.baseName      = 'interactive'
    self.stateBaseName = 'interactive'
    self.timeVector = [ 0 ]
    self.view=GetRenderView()

  def loadMyState(self):
    stateName=self.stateName
    if not os.path.isfile(stateName): # Check if file exists
      print "state file not found"
      sys.exit()

    # As the state will be copied into the current directory, the basename is also the local state name
    localStateName=os.path.basename(stateName)
    # change the name of the local state file so that no problem arises with multithreading : mystate.pvsm -> mystate_solut.pvsm
    self.stateBaseName = localStateName[:-5] # Remove extension .pvsm
    localStateName = self.stateBaseName+"_"+self.baseName +".pvsm"

    # We need to update the xdmf solution file name before loading the state in batch mode
    # In GUI mode, pv asks if the solution name is correct
    command="sed -e 's/solut\.xdmf/"+self.fileName+"/g' "+stateName+" > " + localStateName
    print "substituting 'solut.xdmf' by "+self.fileName+" in "+localStateName
    os.system(command)

    # load state that points to correct solution
    servermanager.LoadState(localStateName)

    # By default, set view to the first view of the state file
    # if processing of multiple views is required, the user should
    # check restoreState for example on looping over views.
    views = GetRenderViews()
    self.view = views[0]
    SetActiveView(self.view)

    # V1: works but double try except is not pretty 
    #part=GetActiveSource()
    #for key in GetSources():
    #  part=FindSource(key[0])
    #  try:    self.timeVector = part.TimestepValues
    #  except: 
    #    try: self.timeVector = part.TimestepValues.GetData()
    #    except: pass

    #V2: I think the proxy id number is sorted by ascending numbers: smallest
    # number is the reader
    # ... not more compact, but only one level of try except
    partNames=[mytuple[0] for mytuple in GetSources().keys()]
    idNumbers=[mytuple[1] for mytuple in GetSources().keys()]
    idx=idNumbers.index(min(idNumbers))   # Find index of reader (min proxy number)
    readerPartName=partNames[idx]         # Get reader name
    readerPart=FindSource(readerPartName) # get part handle for reader
    try:    print readerPart.TimestepValues           # get time step (for xmf reader)
    except: print readerPart.TimestepValues.GetData() # get time step (for other readers)

    try:
      if len(self.timeVector) == 0:
        self.timeVector = [ 0 ]
    except:
      self.timeVector = [ 0 ]
    print 'Time Vector',self.timeVector

  # Generate Interactiviz. See http://ruizanthony.net/pviz/interactiviz for an
  # example
  # Rotate the scene present in view, around a given axis,
  # and store multiple still images to create a Matrix-like animation
  # (so called bullet-time animation)
  def bulletTimeAnimation(self,O,R,axis,nFrames=20,baseName=None,view=None):

      if baseName==None: baseName=self.stateBaseName+'_'+self.baseName
      if view    ==None: view    =self.view

      # This line is VERY important ... this store view into
      # active_objects (see paraview/simple.py module) and this is
      # what makes WriteImage and all the classical functions contained in
      # simple.py work !
      SetActiveView(view)

      # Camera view up has to be aligned with the rotation axis because
      # the axis that is up in the viz has to stay constant while rotating
      # one could also be more generic and use the CameraViewUp from the input
      # state and make a rotation around this axis ... it would be pretty cool
      # ... but ok for now on x,y,z axis, cool enough :)
      if axis == 'x':
        view.CameraViewUp = [1,0,0]
      if axis == 'y':
        view.CameraViewUp = [0,1,0]
      if axis == 'z':
        view.CameraViewUp = [0,0,1]

      view.CameraFocalPoint = O
      for n in range(nFrames):
        theta = float(n)*360./float(nFrames)
        view.CameraPosition = placePointAroundOrigin(O,R,theta,axis)
        #         mystate   _ sol_000120      _angle_     001           .png
        imageName=baseName+'_angle_'+str(n).zfill(3)+'.png'
        WriteImage(imageName, Magnification=self.quality)

  def parseOptions(self,args):
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-s', '--sol',         dest = 'sol',         help = 'Path to solution file.'              , default = None)
    parser.add_option('-q', '--quality',     dest = 'quality',     help = 'Magnification factor (image quality)', default = 1 )
    parser.add_option('-c', '--colorName',   dest = 'colorName',   help = 'Specify color scale'                 , default = "bgr")
    parser.add_option('-t', '--state',       dest = 'stateName',   help = 'Path to state file'                  , default = None)
    # On/Off True/False parameters
    parser.add_option('-i', '--interactive', dest = 'interactive', help = 'flag for interactive session'        , default = False, action = "store_true")
    # On/Off 1   /0     parameters
    parser.add_option('-l', '--logscale',    dest = 'logscale',    help = 'Use 1 for log scale'                 , default = 0)
    parser.add_option('-o', '--showcase'  ,  dest = 'showcase'   , help = 'show case (main part)'               , default = 1)
    parser.add_option('-p', '--cell2point',  dest = 'cell2point' , help = 'cell data to point data'             , default = 1)
    if len(args) == 1:
        parser.print_help()
        sys.exit(-1)
    else:
        (options, args) = parser.parse_args(args)
    self.colorName   = options.colorName
    self.logscale    = int(options.logscale)
    self.fileName    = options.sol
    if not self.fileName == None: self.fileName = self.fileName.rstrip() # remove possible newline character at the end
    self.quality     = int(options.quality)
    self.stateName   = options.stateName
    self.interactive = options.interactive
    self.cell2point  = int(options.cell2point)
    self.showcase    = int(options.showcase)
    print "colorName"   ,self.colorName
    print "logscale"    ,self.logscale
    print "FileName="   ,self.fileName
    print "quality="    ,self.quality
    print "stateName="  ,self.stateName
    print "interactive=",self.interactive
    print "cell2point=" ,self.cell2point
    print "showcase="   ,self.showcase

#   def updateCamera(self,x,y,z,ScreenRes):
  def updateCamera(self,position,focal):      
    # Camera position
    self.view.CameraPosition   = position
    self.view.CameraFocalPoint = focal
    self.view.CenterOfRotation = [position[0],position[1],-2*position[2]] # -2z to put it behind the camera

  def setScreenRes(self,ScreenRes): 
    self.view.ViewSize = ScreenRes # Render Window Size

  def updateBarProperties(self,varName,varRange=None,textColor=black):
    Title    = varName
    logscale = self.logscale    # logscale in viz instance
    # Check if 0 is contained in varRange ... if yes => linear scale
    if (not varRange==None) and (varRange[0]*varRange[1] <= 0): logscale=0
    self.barProperties.Title     = Title
    self.barProperties.varRange  = varRange
    self.barProperties.logscale  = logscale
    self.barProperties.textColor = textColor

  def updateLUT(self,part):
    varRange = self.barProperties.varRange

    # Black and white images
    if self.colorName=="black":
      # Create a "LookUpTable"<=>Legend info ( with min, max, and color scale
      # attribute )
      #  min white to max black
      rgbPoints = [varRange[0], 0.1, 0.1, 0.1, varRange[1], 0.9, 0.9, 0.9 ]
      lut = CreateLookupTable(RGBPoints=rgbPoints, ColorSpace="HSV",UseLogScale=self.barProperties.logscale)

    elif self.colorName=="black_invert":
      # Create a "LookUpTable"<=>Legend info ( with min, max, and color scale
      # attribute )
      #  min light grey to max black
      rgbPoints = [varRange[0], 0.9, 0.9, 0.9, varRange[1], 0.1, 0.1, 0.1 ]
      lut = CreateLookupTable(RGBPoints=rgbPoints, ColorSpace="HSV",UseLogScale=self.barProperties.logscale)

    elif self.colorName=="bgr": # Blue Green Red (ensight default)
      #lut=MakeBlueToRedLT(varRange[0],varRange[1]) # nice macro but cannot use logscale !
      colors=[]
      colors.append( [0.0,0.0,1.0] )
      colors.append( [1.0,0.0,0.0] )
      lut = self._makeLUT( varRange, colors, aColorSpace="HSV")

    elif self.colorName=="bwr": #Blue White Red  (paraview default)
      rgbPoints = [varRange[0], 0.23000000000000001, 0.29999999999999999, 0.754, varRange[1], 0.70599999999999996, 0.016, 0.14999999999999999 ]
      lut = CreateLookupTable(RGBPoints=rgbPoints, ColorSpace="Diverging",UseLogScale=self.barProperties.logscale)

    elif self.colorName=="hotMetal":
      colors=[]
      colors.append( [0.      ,0.        ,0.      ] )
      colors.append( [0.901961,0.        ,0.      ] )
      colors.append( [0.901961,0.901961  ,0.      ] )
      colors.append( [1.0     ,1.0       ,1.0     ] )
      lut = self._makeLUT( varRange, colors)

    elif self.colorName=="magma":
      colors=[]
      colors.append( [0.000000,1.000000,1.000000] )
      colors.append( [0.000000,0.585715,1.000000] )
      colors.append( [0.099999,0.000000,0.928570] )
      colors.append( [0.621432,0.000000,0.364290] )
      colors.append( [1.000000,0.257145,0.000000] )
      colors.append( [1.000000,0.757144,0.000000] )
      colors.append( [1.000000,0.985713,0.000000] )
      colors.append( [0.000000,0.000000,0.000000] )
      lut = self._makeLUT( varRange, colors)

    elif self.colorName=="magma_minWhite":

      colors=[]
      colors.append( [1.000000,1.000000,1.000000] )
      colors.append( [0.000000,1.000000,1.000000] )
      colors.append( [0.000000,0.585715,1.000000] )
      colors.append( [0.099999,0.000000,0.928570] )
      colors.append( [0.621432,0.000000,0.364290] )
      colors.append( [1.000000,0.257145,0.000000] )
      colors.append( [1.000000,0.757144,0.000000] )
      colors.append( [1.000000,0.985713,0.000000] )
      colors.append( [0.000000,0.000000,0.000000] )
      lut = self._makeLUT( varRange, colors)

# Palette from vorticity (or more generally for centered data +-
# Min: grey, Zero value: white, Max: black
    elif self.colorName=="bw_white0": # palette from paraview

      colors=[]
      colors.append( [0.6,0.6,0.6] )
      colors.append( [1.0,1.0,1.0] )
      colors.append( [0.1,0.1,0.1] )
      lut = self._makeLUT( varRange, colors)

# Min: white, Max: black
    elif self.colorName=="gray_banded":

      colors=[]
      colors.append( [0.990000,0.990000,0.990000] )
      colors.append( [0.690000,0.690000,0.690000] )
      colors.append( [0.860000,0.860000,0.860000] )
      colors.append( [0.560000,0.560000,0.560000] )
      colors.append( [0.730000,0.730000,0.730000] )
      colors.append( [0.440000,0.440000,0.440000] )
      colors.append( [0.600000,0.600000,0.600000] )
      colors.append( [0.310000,0.310000,0.310000] )
      colors.append( [0.470000,0.470000,0.470000] )
      colors.append( [0.180000,0.180000,0.180000] )
      colors.append( [0.340000,0.340000,0.340000] )
      colors.append( [0.050000,0.050000,0.050000] )
      colors.append( [0.200000,0.200000,0.200000] )
      lut = self._makeLUT( varRange, colors)

# Min: black, Max: white
    elif self.colorName=="gray_banded_invert":

      colors=[]
      colors.append( [0.200000,0.200000,0.200000] )
      colors.append( [0.050000,0.050000,0.050000] )
      colors.append( [0.340000,0.340000,0.340000] )
      colors.append( [0.180000,0.180000,0.180000] )
      colors.append( [0.470000,0.470000,0.470000] )
      colors.append( [0.310000,0.310000,0.310000] )
      colors.append( [0.600000,0.600000,0.600000] )
      colors.append( [0.440000,0.440000,0.440000] )
      colors.append( [0.730000,0.730000,0.730000] )
      colors.append( [0.560000,0.560000,0.560000] )
      colors.append( [0.860000,0.860000,0.860000] )
      colors.append( [0.690000,0.690000,0.690000] )
      colors.append( [0.990000,0.990000,0.990000] )
      lut = self._makeLUT( varRange, colors)

# Min: white, Max: black
    elif self.colorName=="BW16color": 

      colors=[]
      colors.append( [0.990000,0.990000,0.990000] )
      colors.append( [0.937500,0.937500,0.937500] )
      colors.append( [0.875000,0.875000,0.875000] )
      colors.append( [0.812500,0.812500,0.812500] )
      colors.append( [0.750000,0.750000,0.750000] )
      colors.append( [0.687500,0.687500,0.687500] )
      colors.append( [0.625000,0.625000,0.625000] )
      colors.append( [0.562500,0.562500,0.562500] )
      colors.append( [0.500000,0.500000,0.500000] )
      colors.append( [0.437500,0.437500,0.437500] )
      colors.append( [0.375000,0.375000,0.375000] )
      colors.append( [0.312500,0.312500,0.312500] )
      colors.append( [0.250000,0.250000,0.250000] )
      colors.append( [0.187500,0.187500,0.187500] )
      colors.append( [0.125000,0.125000,0.125000] )
      colors.append( [0.062500,0.062500,0.062500] )
      lut = self._makeLUT( varRange, colors)

    else:
      print "Unknown color palette:",self.colorName
      sys.exit()

    lut.NumberOfTableValues = self.barProperties.NumberOfTableValues

    # Use the LookUpTable to specify the min, max and coloring of the variable
    partRep = GetDisplayProperties(part)
    partRep.LookupTable = lut

    # Store it for later use
    self.barProperties.LookupTable = lut

  def putBar(self,bar=None):
    # If no scalar bar is specified, create one
    if bar==None:
      bar = CreateScalarBar( Orientation    = self.barProperties.Orientation,
                             Title          = self.barProperties.Title,
                             Position       = self.barProperties.Position,
                             Position2      = self.barProperties.Position2,
                             Enabled=1,
                             LabelFontFamily= self.barProperties.FontFamily,
                             LabelFontSize  = self.barProperties.TextSize,
                             LabelColor     = self.barProperties.textColor,
                             LookupTable    = self.barProperties.LookupTable,
                             TitleFontFamily= self.barProperties.FontFamily,
                             TitleFontSize  = self.barProperties.TitleSize,
                             TitleColor     = self.barProperties.textColor)
    self.view.Representations.append(bar) # add the scalar bar to the view
    return bar

  def removeBar(self,bar):
    self.view.Representations.remove(bar)

  def writeImage(self,tag):
    Render() # Render the scene before writing image
    # If only one time step, use the solution name for the snapshots
    if len(self.timeVector) == 1:
      imageName = self.path+"/"+tag+"_"+self.baseName+".png"
    # Else, multiple time steps: use _10000, _20000 ... zero padded on 9 digits
    else:
      stringNite = str( int(self.view.ViewTime) ).zfill(9) # zero padding
      imageName = self.path+"/"+tag+"_"+stringNite+".png"
    imageName=imageName.replace(" ","_") # Replace spaces by underscores
    print "Writing image ",imageName
    WriteImage(imageName, Magnification=self.quality )

  def updateCameraFromFile(self,cameraFileName):
    from xml.etree import ElementTree
    print "Parsing camera file ",cameraFileName
    doc = ElementTree.parse ( cameraFileName )
    Proxies=doc.find('Proxy')
    Properties=Proxies.findall('Property')

    for Property in Properties:
      # for example : Property.get("name") = CameraPosition
      PropertyName = Property.get("name")
      cameraCoor = [ ]
      for element in Property.findall('Element'):
        cameraCoor.append(element.get("value"))
      # For CameraViewAngle, only one parameter is needed
      if PropertyName == 'CameraViewAngle':
        exec "self.view."+PropertyName+" = "+str(cameraCoor[0])
      # For other properties 3 parameters are needed
      # (Note that the new parameters: CameraParallelScale and CameraParallelProjection
      #  are not handled by this method)
      elif PropertyName in ['CameraPosition',"CameraFocalPoint","CameraViewUp","CenterOfRotation"]:
        exec "self.view."+PropertyName+"= ["+str(cameraCoor[0])+","+str(cameraCoor[1])+","+cameraCoor[2]+"]"

  def colorPartByVarName(self,part,varName,barPosition=None,repType='Surface',varRange=None):
    print "Coloring a part by var:",varName," ..."
    partRep = GetDisplayProperties(part)
    partRep.Representation = repType
    partRep.ColorArrayName = varName

    # By default, varRange is the part min/max and bar title is varName
    if varRange == None:
      try:    varRange = part.PointData[varName].GetRange()
      except: varRange = part.CellData[varName].GetRange()

    # bar title name (=varName) and varRange
    self.updateBarProperties(varName,varRange)

    # Create and update lookup table (make a correspondance between colors and numerical values)
    self.updateLUT(part)

    if barPosition != None:
      try:    self.removeBar(self.bar) # Try to remove bar if present (not present at first call)
      except: pass
      self.barProperties.setPosition(barPosition) # Set bar to top, bot, left, or right
      self.bar = self.putBar()

  def updateTime(self,time):
    print 'Setting time to: ',time
    self.view.ViewTime = time

  # Private method _
  def _makeLUT( self, varRange, colors, aColorSpace="RGB" ):

    nlevels=len(colors)
    rgbPoints= [ ]

    # For each level, add an value and a color in the rgbPoints list
    for level in range(nlevels):
      # linear scale
      if self.barProperties.logscale == 0:
        value = varRange[0] + (varRange[1]-varRange[0] )*float(level)/(nlevels-1)
      # log scale
      else:
        value = exp( log(varRange[0]) + (log(varRange[1])-log(varRange[0]) )*float(level)/(nlevels-1) )
      rgbPoints.append( value )

      for color in colors[level]:
        rgbPoints.append( color )

    print "Using Logscale:",self.barProperties.logscale
    lut = CreateLookupTable(RGBPoints=rgbPoints, ColorSpace=aColorSpace,UseLogScale=self.barProperties.logscale)
    return lut

# Define a class of that contains all bar properties, for more convenient use
class barProperties:
  def __init__(self,Orientation = 'Horizontal',logscale=0,NumberOfTableValues=256):
    self.varRange = None
    self.logscale = logscale
    # By default, the text is Black and the background is white
    self.textColor=[ 0.0, 0.0, 0.0 ]
    self.Title    = None
    self.LookupTable = None
    self.Orientation = Orientation
    if Orientation == 'Horizontal': # Horizontal Bar
      self.Position  = [0.25, 0.15] # x,y of bottom left corner
      self.Position2 = [0.50, 0.25] # extent of bar
    elif Orientation == 'Vertical': # Vertical Bar
      self.Position  = [0.8, 0.1]
      self.Position2 = [0.1, 0.8]
    else:
	  print 'Error with bar orientation, should be Horizontal or Vertical'
    self.TitleSize = 16
    self.TextSize  = 16
    self.FontFamily="Times" # By default, the font is Times, which looks better than Arial
    self.NumberOfTableValues = NumberOfTableValues

  def setPosition(self,positionName):
    # Position:  x,y bottom left corner
    # Position2: x and y extent of bar
    if positionName == 'left':
      self.Orientation = 'Vertical'
      self.Position  = [0.175, 0.1]
      self.Position2 = [0.1  , 0.8]

    elif positionName == 'right':
      self.Orientation = 'Vertical'
      self.Position  = [0.825, 0.1]
      self.Position2 = [0.1  , 0.8]

    elif positionName == 'bot':
      self.Orientation = 'Horizontal'
      x = 0.15
      y = 0.10
      self.Position  = [x,y]
      # The bar is symmetric around 0.5
      xlength = 2.0*(0.5 - x)
      ylength = 0.25
      self.Position2 = [xlength, ylength]

    elif positionName == 'top':
      self.Orientation = 'Horizontal'
      x = 0.15
      y = 0.75
      self.Position  = [x,y]
      # The bar is symmetric around 0.5
      xlength = 2.0*(0.5 - x)
      ylength = 0.25
      self.Position2 = [xlength, ylength]

    elif positionName == 'manual':
      pass # user need to set orientation, Position, Position2

    else:
      print "Unknown bar position"
      sys.exit()

# ===============================================================
# PVIZ MACROS
# (Functions outside classes)
# ===============================================================
def setVisible(part):
    partRep = GetDisplayProperties(part)
    partRep.Visibility = 1

def setInvisible(part):
    partRep = GetDisplayProperties(part)
    partRep.Visibility = 0

def writeCSV(partFileName,dataType='PointData'):
  w = DataSetCSVWriter(FileName=partFileName)
  if   dataType=='PointData':
    w.FieldAssociation=0 # PointData
  elif dataType=='CellData':
    w.FieldAssociation=1 # CellData
  elif dataType=='FieldData':
    w.FieldAssociation=2 # FieldData
  w.UpdatePipeline()

# This method is closer to what the GUI does when you do File>save on a given part
def writeCSV_likeGUI(partFileName,dataType='PointData',Precision=5,UseScientificNotation=1):
  w = CreateWriter(partFileName)
  # Sometimes, creating a writing on a part do not allow for attribute FieldAssociation
  # This is the case for histogram filter => Use error handling
  try:    w.FieldAssociation = dataType
  except: pass
  w.Precision = Precision
  w.UseScientificNotation = UseScientificNotation
  w.UpdatePipeline()
  del(w)

def makeCalculator(functionString,outputVar,dataType='PointData'):
  oriVisibility = hidePart()
  aCalculator = Calculator()
  # 1: point_data, 2:cell_data, 5:field_data
  if   dataType == 'PointData': aCalculator.AttributeMode=1
  elif dataType == 'CellData':  aCalculator.AttributeMode=2
  aCalculator.ResultArrayName = outputVar
  aCalculator.Function        = functionString
  if oriVisibility == 1: Show() # only show children if parent was visible (if not, we're doing statistical analysis and do not need viz)
  return aCalculator

def makePythonCalculator(functionString, outputVar,dataType='PointData'):
  oriVisibility = hidePart()
  part = PythonCalculator( Expression=functionString,  ArrayName=outputVar, 
                           ArrayAssociation=dataType, CopyArrays=1 )
  if oriVisibility == 1: Show() # only show children if parent was visible (if not, we're doing statistical analysis and do not need viz)
  return part

# Compute gradphi from phi
def makeGradient(scalarName):
  oriVisibility = hidePart()
  aGradientOfUnstructuredDataSet = GradientOfUnstructuredDataSet()
  aGradientOfUnstructuredDataSet.ScalarArray     = ['POINTS',scalarName]
  aGradientOfUnstructuredDataSet.ResultArrayName = 'grad'+scalarName
  if oriVisibility == 1: Show() # only show children if parent was visible (if not, we're doing statistical analysis and do not need visu)
  return aGradientOfUnstructuredDataSet

def line(A,B,npoints,fileName,idelete=1):
  # the standard behavior of paraview is to set the active source to the
  # newly created filter ... we don't want that for lines 
  # in case multiple lines are created in a row (no sense in using a line as 
  # an input source for another line)
  # => The original active source is restored after the line is created
  oriParentPart = GetActiveSource()
  PlotOverLine1 = PlotOverLine( Source="High Resolution Line Source" )
  PlotOverLine1.Source.Point1 = A
  PlotOverLine1.Source.Point2 = B
  PlotOverLine1.Source.Resolution = npoints
  writeCSV(fileName)

  # Run pviz_pv2matlab on the fly (bash script that converts [Points:0,Point:1,Point:2] -> [x,y,z]
  # ... and all vectors with :0, :1, :2 into _x, _y, _z)
  os.system("pviz_pv2matlab " + fileName)

  # Delete cut by default
  if idelete==1: Delete(PlotOverLine1)
  else:          Show(PlotOverLine1)

  # Restore original active source for later postproc
  SetActiveSource(oriParentPart)
  if idelete==0: return PlotOverLine1

# point has never been tested (used resampleWithDataSet instead)
def point(A,pointFileName):

  # the standard behavior of paraview is to set the active source to the
  # newly created filter ... we don't want that for lines 
  # in case multiple lines are created in a row (no sense in using a line as 
  # an input source for another line)
  # => The original active source is restored after the line is created
  oriParentPart = GetActiveSource()
  ProbeLocation1 = ProbeLocation( guiName="ProbeLocation1", ProbeType="Fixed Radius Point Source" )
  ProbeLocation1.ProbeType.NumberOfPoints = 1
  ProbeLocation1.ProbeType.Radius = 0.0
  ProbeLocation1.ProbeType.Center = [A[0], A[1], A[2]]

  writeCSV(pointFileName)

  # Delete cut
  Delete(ProbeLocation1)

  # Restore original active source for later postproc
  SetActiveSource(oriParentPart)

def placePointAroundOrigin(O,R,theta,axis):

  xo = O[0]
  yo = O[1]
  zo = O[2]
  if axis=="z" :
    xb = xo + R*cos(pi/180.*theta)
    yb = yo + R*sin(pi/180.*theta)
    zb = zo
  if axis=="y":
    zb = zo + R*cos(pi/180.*theta)
    xb = xo + R*sin(pi/180.*theta)
    yb = yo
  if axis=="x":
    yb = yo + R*cos(pi/180.*theta)
    zb = zo + R*sin(pi/180.*theta)
    xb = xo
  B = [ xb , yb , zb ]
  return B

def radialCut(O,R,npoints,thetaBegin,thetaEnd,thetaStep,axis,baseName='cut_radial',idelete=1):

  rcutNumber  = 0
  theta      = thetaBegin
  while theta < thetaEnd:

    rcutNumber=rcutNumber+1
    B = placePointAroundOrigin(O,R,theta,axis)

    fileName="%s_%03d.txt" % (baseName,rcutNumber)
    line(O,B,npoints,fileName,idelete=idelete)
    theta = theta + thetaStep

def showPointList(pointListName,sphereRadius=0.1,sphereColor=[1,0,0]): # default red sphere

  nr=0
  if os.path.isfile(pointListName):
    pointListFile = open(pointListName, 'r')
    for line in pointListFile:
       nr=nr+1 # line number
       if nr>=2: # skip header
         line = line.rstrip() #  remove the end of line character
         words = line.split() # the default separator is space
         x = float(words[0])  # words[n] is a string, x is a float
         y = float(words[1])
         z = float(words[2])
         print x,y,z
         makeSphere(O=[x,y,z],sphereRadius=sphereRadius,sphereColor=sphereColor)
  else:
    print "The file "+pointListName+" is missing!"

def makeSphere(O,sphereRadius=0.1,sphereColor=[1,0,0]):
         oSphere = Sphere()
         oSphere.Center = O
         oSphere.Radius = sphereRadius
         sphereRep= Show()
         sphereRep.DiffuseColor=sphereColor
         return oSphere

def saveAllFields(fname=None,dataType='PointData',iBar=1):
# To be used within paraview GUI: color current part by all variables, rescale
# them with part min/max a save an image

  part   = GetActiveSource()
  DataRep= GetDisplayProperties(part)
  view   = GetRenderView()

  # Pd contains all the point data
  if   dataType=='PointData': pd = part.PointData
  elif dataType=='CellData' : pd = part.CellData
  else: print 'Error with dataType in saveAllFields, exiting ...'; sys.exit()
  print 'Values:',pd.values()
  for var in pd.values():
    var_name = var.GetName()
    DataRep.ColorArrayName = var_name   # Color By the variable
    var_range = pd[var_name].GetRange() # Get the min max of the variable
    # Create a "LookUpTable" <=> Legend info ( with min, max, and color scale attribute )
    lut=MakeBlueToRedLT(var_range[0],var_range[1])

    # Create a "Scalar Bar" <=> Printed Color Scale
    if iBar==1:
      bar = CreateScalarBar(LookupTable=lut, Title=var_name, LabelColor=black, TitleColor=black )
      view.Representations.append(bar) # Add the Color Scale to the View

    # Use the LookUpTable to specify the min, max and coloring of the variable
    DataRep.LookupTable = lut

    Render() # Apply
    fileName = var_name+".png"
    if not fname == None: fileName = fname+'_'+fileName
    WriteImage(fileName)

    # Remove the Scalar Bar before processing the other variables
    if iBar==1: view.Representations.remove(bar)

def makeSlice(x=None,y=None,z=None):
  ''' Cut the domain with a 2D plane'''
  oriVisibility = hidePart()
  if   x!=None:
    origin = [ x  , 0.0, 0.0 ]
    normal = [ 1.0, 0.0, 0.0 ]
  elif y!=None:
    origin = [ 0.0, y  , 0.0 ]
    normal = [ 0.0, 1.0, 0.0 ]
  elif z!=None:
    origin = [ 0.0, 0.0, z   ]
    normal = [ 0.0, 0.0, 1.0 ]
  aSlice = Slice( SliceType="Plane" )
  aSlice.SliceType.Origin =  origin
  aSlice.SliceType.Normal =  normal
  aSlice.SliceOffsetValues = [0.0]
  aSlice.SliceType = "Plane"
  if oriVisibility == 1: Show() # only show children if parent was visible (if not, we're doing statistical analysis and do not need viz)
  return aSlice

def makeClip(x=None,y=None,z=None,InsideOut=None,ClipType="Plane",Bounds=None):
  ''' Clip the domain with a 2D plane or a box '''
  # Hide parent
  oriVisibility=hidePart()
  if ClipType=="Plane":
    aClip = Clip( ClipType=ClipType )
    if InsideOut == None: InsideOut = 0 # Default value for plane, keeps everything beyond xi value
    if x!=None:
      origin = [ x  , 0.0, 0.0 ]
      normal = [ 1.0, 0.0, 0.0 ]
    elif y!=None:
      origin = [ 0.0, y  , 0.0 ]
      normal = [ 0.0, 1.0, 0.0 ]
    elif z!=None:
      origin = [ 0.0, 0.0, z   ]
      normal = [ 0.0, 0.0, 1.0 ]
    aClip.ClipType.Origin =  origin
    aClip.ClipType.Normal =  normal
    aClip.ClipType.Offset = 0.0
  elif ClipType=="Box":
    aClip = Clip( ClipType=ClipType )
    if InsideOut == None: InsideOut = 1 # Default value for clip, keeps everything within specified box
    if Bounds == None:
      print"when choosing Box clip, you need to specify bounds"
      print"...exiting"
      sys.exit()
    aClip.ClipType.Position = [x, y, z]
    aClip.ClipType.Bounds   = Bounds #[-deltax/2., deltax/2., -deltay/2., deltay/2., -deltaz/2., deltaz/2.]
    aClip.ClipType.Scale    = [1.0, 1.0, 1.0] # 100% of bounds
  elif ClipType=="BoxMinMax":
    aClip = Clip( ClipType="Box" )
    if InsideOut == None: InsideOut = 1 # Default value for clip, keeps everything within specified box
    if Bounds == None:
      print"when choosing BoxMinMax clip, you need to specify bounds"
      print"...exiting"
      sys.exit()
    [xmin,xmax,ymin,ymax,zmin,zmax] = Bounds
    x05= 0.5*(xmin+xmax)
    y05= 0.5*(ymin+ymax)
    z05= 0.5*(zmin+zmax)
    deltax= xmax-xmin
    deltay= ymax-ymin
    deltaz= zmax-zmin
    realBounds   = [-deltax/2., deltax/2., -deltay/2., deltay/2., -deltaz/2., deltaz/2.]
    aClip.ClipType.Position = [x05, y05, z05]
    aClip.ClipType.Bounds   = realBounds # the input bounds of this functions were not the real DeltaXYZ
    aClip.ClipType.Scale    = [1.0, 1.0, 1.0] # 100% of bounds
  aClip.InsideOut = InsideOut
  print 'oriVisibility',oriVisibility
  if oriVisibility == 1: Show() # only show children if parent was visible (if not, we're doing statistical analysis and do not need viz)
  return aClip

def makeContour(varName,isoValueArray,ColorArrayName=None,DiffuseColor=None,lineWidth=1.0):
   '''Create a surface for an isolevel of scalar'''
   oriVisibility=hidePart()
   aContour = Contour( PointMergeMethod="Uniform Binning" )
   aContour.ContourBy = ['POINTS', varName]
   aContour.Isosurfaces = isoValueArray
   Render()
   if oriVisibility == 1: 
     aContourRep = Show()
     if not ColorArrayName == None: aContourRep.ColorArrayName = ColorArrayName
     if not DiffuseColor   == None: aContourRep.DiffuseColor   = DiffuseColor
     aContourRep.LineWidth = lineWidth
   if oriVisibility == 1: Show() # only show children if parent was visible (if not, we're doing statistical analysis and do not need viz)      
   return aContour

def makeThreshold(varName,ThresholdRange,dataType='POINTS'):
  '''Only keep points within a range of a variable'''
  oriVisibility=hidePart()
  part = Threshold( Scalars=[dataType, varName], ThresholdRange=ThresholdRange, AllScalars=1, UseContinuousCellRange=0 )
  if oriVisibility == 1: Show() # only show children if parent was visible (if not, we're doing statistical analysis and do not need viz)
  return part

def makeCell2Point():
  oriVisibility = hidePart()
  part = CellDatatoPointData( PieceInvariant=0, PassCellData=0 )
  if oriVisibility == 1: Show() # only show children if parent was visible (if not, we're doing statistical analysis and do not need viz)
  return part

def hidePart(part=None):
  ''' This function hides the current part and returns ori visibility (which
  tells if the parent was originally visible or not)

  This function is similar to paraview.simple Hide function, except that it
  returns oriVisibility (instead of display properties).
  '''
  if part == None: parent = GetActiveSource() # if not part is given, get current part
  partRep = GetDisplayProperties(parent) # get representation properties
  oriVisibility = partRep.Visibility     # get visibility
  partRep.Visibility = 0                 # removes visibility
  return oriVisibility                   # return original visibility of part

def showPart(part=None):
  ''' This function shows the current part and returns ori visibility (which
  tells if the parent was originally visible or not)

  This function is similar to paraview.simple Show function, except that it
  returns oriVisibility (instead of display properties).
  '''
  if part == None: parent = GetActiveSource() # if not part is given, get current part
  partRep = GetDisplayProperties(parent) # get representation properties
  oriVisibility = partRep.Visibility     # get visibility
  partRep.Visibility = 1                 # make visible
  return oriVisibility                   # return original visibility of part

def calcRMS(dataType='PointData'):
  ''' transform var_2 into rms_var '''
  part = GetActiveSource()
  if dataType=='PointData':
    varList=part.PointData
  else:
    varList=part.CellData
  for var in varList:
    varname=var.GetName()
    # is varname == u_2
    if varname[-2:] == "_2": # _2
      var1  = varname[0:-2]  # u
      newvar="rms_"+var1     #rms_u
      # sqrt(abs(u_2 - u^2))
      functionString="sqrt(abs({0} - {1}^2))".format(varname,var1)
      makeCalculator(functionString,newvar,dataType=dataType)

def mergeCleanD3():
  oriVisibility = hidePart()
  MergeBlocks( MergePoints=1 )
  CleantoGrid()
  part=D3( BoundaryMode='Assign cells uniquely', MinimalMemory=0 ) # Data is redistributed to all procs
  if oriVisibility == 1: Show() # only show children if parent was visible (if not, we're doing statistical analysis and do not need viz)
  return part

def mergeCleanD3point():
  mergeCleanD3()
  part = makeCell2Point()
  return part

def visualFilter(ntimes=1,dataType='PointData'):
  '''multiple point2cell and cell2point for a visual filter effect'''
  oriVisibility = hidePart()
  if   dataType=='PointData':
    for n in range(ntimes):
      PointDatatoCellData()
      CellDatatoPointData()
  elif dataType=='CellData':
    for n in range(ntimes):
      CellDatatoPointData()
      PointDatatoCellData()
  if oriVisibility == 1: Show() # only show children if parent was visible (if not, we're doing statistical analysis and do not need viz)

def restoreState_1view(args):
  oviz = viz(args)                    # instantiate viz object (and load data with state)
  oviz.writeImage(oviz.stateBaseName) # save image with stateBaseName as a tag

def restoreState(args):
  oviz  = viz(args)     # instantiate viz object (and load data with state)
  saveAllViews(tag=oviz.stateBaseName,oviz=oviz)

def saveAllViews(tag=None,oviz=None):
  if oviz == None: oviz=iviz() # from the GUI you can call saveAllViews()
  views = GetRenderViews()  # Beware with ultiple views, scalar bars can be messed up
  nviews= len(views)
  print "Number of views: "+str(nviews)
  n=1
  for view in views:
      # This line is VERY important ... this store view into active_objects (see paraview/simple.py module) and this is
      # what makes WriteImage and all the classical functions contained in simple.py work!
      SetActiveView(view)

      tagview=tag
      if tag == None:  tagview= "view"+str(n)
      else:
        if nviews >= 2: tagview=tag+"_view"+str(n)
      oviz.writeImage(tagview) # save image with stateBaseName as a tag
      n=n+1

# This create a viz object in interactive mode from the GUI
def iviz():
  oviz=viz(['dummy.py','-i']) 
  return oviz

def setViewDefaults(view):

    # Set center of rotation and orientation axis invisible
    view.CenterAxesVisibility = 0
    view.OrientationAxesVisibility = 0

    # White Background
    view.Background=[1,1,1]
    # Put a spotLight
    view.UseLight = 1
    view.LightSwitch = 1
    view.LightIntensity = 0.3
    # View Resolution
#     view.ViewSize = [916,591]
    view.ViewSize = [900,600]
    view.UseOffscreenRenderingForScreenshots = 0
    Render()

print __name__
if __name__ == '__main__':
  if sys.argv[1] == 'restoreState_1view': restoreState_1view(sys.argv[1:]) #pass sys.argv[1:] to remove first item: 'pviz.py'
  if sys.argv[1] == 'restoreState':       restoreState(sys.argv[1:])

  #DEBUG
  #viz(sys.argv)
