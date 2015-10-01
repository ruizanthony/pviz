#!/usr/bin/env pvbatch
try: paraview.simple
except: from paraview.simple import *
import pviz
import sys

if __name__== '__vtkconsole__' : oviz=iviz() # for interactive sessions only
else: oviz = pviz.viz(sys.argv)   # Instantiate a new visualisation
isocontour=FindSource('isoqcrit') # Find the part named isoqcrit in state pipeline

# Bullet Time Inputs ----------------------------------------
O= [ oviz.view.CameraPosition[0], oviz.view.CameraPosition[1], 0.0] # center of rotation in z=0 plane
R= oviz.view.CameraPosition[2] # z-position is the radius of rotation around object
axis='y' # rotation axis
# -----------------------------------------------------------

qcritList=[1.0e7, 5.0e7, 1.0e8] # List of isovalues of explore 
for n in range(len(qcritList)):
  isocontour.Isosurfaces = qcritList[n]
  #              mystate_sol_000120_nval_001  (nangle will be added in bulletTimeAnimation)
  aBasename='{:s}_{:s}_nval_{:03d}'.format(oviz.stateBaseName,oviz.baseName,n)
  oviz.bulletTimeAnimation(O,R,axis,baseName=aBasename,nFrames=20) # Save bullet time snapshots
