#!/usr/bin/env pvbatch
try: paraview.simple
except: from paraview.simple import *
from numpy import linspace
import pviz
import sys
if __name__== '__vtkconsole__' : sys.argv=['dummy.py','-i','1'] # for interactive sessions only
oviz = pviz.viz(sys.argv)         # Instantiate a new visualisation
isocontour=FindSource('isoqcrit') # Find the part corresponding to the qcrit isocontour in state pipeline
qcritList=linspace(1.e7,1.e8,10)  # List of isovalues of explore, can also list directly values: [val1, val2, ...]
n=0
for qcrit in qcritList:
  isocontour.Isosurfaces = qcrit  # update isocontour value
  oviz.writeImage("{0}_nq_{1:03d}".format(oviz.stateBaseName,n)) # save image with state + nq stamp basename
  n=n+1
