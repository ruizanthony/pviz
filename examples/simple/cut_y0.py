#!/usr/bin/env pvbatch
from paraview.simple import *
import pviz
import sys
oviz = pviz.viz(sys.argv)          # instantiate viz object (and load data)
part = pviz.makeSlice( y = 0. )    # make slice
oviz.view.CameraViewUp   = [0,0,1]
oviz.view.CameraPosition = [0,1,0]
ResetCamera()                      # auto-adapt camera to part extent
for var in part.PointData:         # loop over node-centered data
    varName = var.GetName()        # get variable name
    oviz.colorPartByVarName(part,varName,barPosition = 'right')
    oviz.writeImage(varName)       # save image
