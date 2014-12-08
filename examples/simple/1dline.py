#!/usr/bin/env pvbatch
from paraview.simple import *
import pviz
import sys
oviz = pviz.viz(sys.argv) # instantiate viz object (and load data)
pviz.line(A=[1.0,10.0,0.0],B=[9.0,10.0,0.0],npoints=100,
          fileName="line_"+oviz.baseName+".txt")
