#!/usr/bin/env pvbatch
try: paraview.simple
except: from paraview.simple import *
from numpy import linspace
import pviz
import sys
oviz = pviz.viz(sys.argv) # Reload state
#part = GetActiveSource() # for some reason, cannot access active source from pvsm :(
part = FindSource('loopvars') # instead set the part name that you want to loop vars on to: loopvars
SetActiveSource(part)

# for each pointdata vars in active source, color by var and save an image
# => you MUSTNOT CHANGE the title of scalar bar otherwise it
#    won't be able to identify which scalar bar to make visible
# iBar = 1 autoscales min/max of vars in part and adds a scalar bar
# iBar = 0 uses the var range and scalar bars already defined in state
pviz.saveAllFields(dataType='PointData', iBar =0, oviz=oviz)
