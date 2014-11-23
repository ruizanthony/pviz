#!/usr/bin/env pvbatch
from paraview.simple import *
import pviz
import sys
oviz=pviz.viz(sys.argv)            # instantiate viz object (and load data)
part=GetActiveSource()             # select active part
ResetCamera()                      # auto-adapt camera to part extent
for var in part.PointData:         # loop over node-centered data
    varName = var.GetName()        # get variable name
    oviz.colorPartByVarName(part,varName,barPosition = 'top')
    oviz.writeImage(varName)       # save image
