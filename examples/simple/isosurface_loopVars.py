#!/usr/bin/env pvbatch
from paraview.simple import *
import pviz
import sys
oviz = pviz.viz(sys.argv)   # instantiate viz object (and load data)
part = pviz.makeContour(varName='T_s',isoValueArray=[1.0],ColorArrayName='u_s')
ResetCamera()               # auto-adapt camera to part extent
for var in part.PointData:
    varName=var.GetName()
    varBar=oviz.colorPartByVarName(part,varName,barPosition='right')
    oviz.writeImage(varName+'_isoT_1p0') # save image
    oviz.removeBar(varBar)               # remove bar object
