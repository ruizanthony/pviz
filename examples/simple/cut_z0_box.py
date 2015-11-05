#!/usr/bin/env pvbatch
from paraview.simple import *
import pviz
import sys
oviz = pviz.viz(sys.argv)          # instantiate viz object (and load data)
pviz.makeSlice( z = 0. )           # make slice
# Clip and zoom on a specific region around (x0,y0)
x0    =0.0
y0    =0.0
length=1.0
xmin=x0-length/2.; xmax= x0+length/2.
ymin=y0-length/2.; ymax= y0+length/2.
zmin=0.-length/2.; zmax= 0.+length/2.
part=pviz.makeClip(ClipType="BoxMinMax", Bounds=[xmin,xmax,ymin,ymax,zmin,zmax])
ResetCamera()                      # auto-adapt camera to part extent
for var in part.PointData:         # loop over node-centered data
    varName = var.GetName()        # get variable name
    oviz.colorPartByVarName(part,varName,barPosition = 'right')
    oviz.writeImage(varName)       # save image
