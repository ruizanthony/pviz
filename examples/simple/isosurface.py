#!/usr/bin/env pvbatch
from paraview.simple import *
import pviz
import sys
oviz = pviz.viz(sys.argv)    # instantiate viz object (and load data)
part = pviz.makeContour(varName='T_s',isoValueArray=[0.01],ColorArrayName='u_s')
ResetCamera()                # auto-adapt camera to part extent
oviz.writeImage('isoT_0p01') # save image
