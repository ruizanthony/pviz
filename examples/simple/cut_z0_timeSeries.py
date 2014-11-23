#!/usr/bin/env pvbatch
from paraview.simple import *
import pviz
import sys
oviz = pviz.viz(sys.argv)            # instantiate viz object (and load data)
part = pviz.makeSlice( z = 0. )      # make slice
ResetCamera()                        # auto-adapt camera to part extent
for time in oviz.timeVector:         # loop over time steps
  oviz.updateTime(time)              # Update to current time
  for var in part.PointData:         # loop over node-centered data
      varName = var.GetName()        # get variable name
      oviz.colorPartByVarName(part,varName,barPosition = 'right')
      oviz.writeImage(varName)       # save image
