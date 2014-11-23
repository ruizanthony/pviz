#!/usr/bin/env pvbatch
from paraview.simple import *
import pviz
import sys
oviz = pviz.viz(sys.argv)   # instantiate viz object (and load data)
bulletTimeAnimation(O=[0,0,0],R=10,axis='z',nFrames=20)