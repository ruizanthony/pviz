#!/usr/bin/env pvbatch
try: paraview.simple
except: from paraview.simple import *
from paraview_module import *

import sys

# __name__== "__main__" if batch. 
# If interactive, dont load the solution but do
# the rest of the postproc contained herein.
if __name__== '__vtkconsole__' :
  sys.argv = ['-i',1]
  #sys.argv = ['-s','dtms_ave_001600_full.xmf']

# Instantiate a new visualisation
oviz = visu(sys.argv)
# The state file has been loaded, and current view is the first one
isocontour=FindSource('isoqcrit')

# For Bullet Time
O= [ oviz.view.CameraPosition[0], oviz.view.CameraPosition[1], 0.0]
R= oviz.view.CameraPosition[2]
axis='y'

# Qcrit
qcritList=[0.5e10, 1e10, 2e10, 4e10, 6e10]
for n in range(len(qcritList)):
  isocontour.Isosurfaces = qcritList[n]
  #              mystate        _       sol_000120_nval_      001  (nangle will be added in bulletTimeAnimation)
  aBasename=oviz.stateBaseName+'_'+oviz.baseName+"_nval_"+str(n).zfill(3)
  oviz.bulletTimeAnimation(O,R,axis,baseName=aBasename,nFrames=20) # Save bullet time snapshots
