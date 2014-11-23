.. role:: bash(code)
   :language: bash
   :class: highlight

.. role:: py(code)
   :language: py
   :class: highlight

Quick Reference Guide
=====================

In this page, the main functions are listed  (slices, clips, isosurfaces, ...) 
and common usage examples are given.

makeSlice: Cut the domain with a 2D plane
-----------------------------------------

**Definition**::

  makeSlice(x=None,y=None,z=None)

**Examples**::

  makeSlice(x=0) # cut at x=0

::

  makeSlice(y=0) # cut at y=0

::

  makeSlice(z=5.2) # cut at z=5.2 ... easy right?

makeClip: Clip the domain with a 2D plane or a box
--------------------------------------------------

**Definition**::

  makeClip(x=None,y=None,z=None,InsideOut=0,ClipType="Plane",Bounds=None)

**Examples**::

With ``ClipType=="Plane"`` (default value) ::

  makeClip(x=0)             # keeps everything with x>=0

::

  makeClip(x=0,InsideOut=1) # keeps everything with x<=0

With ``ClipType=="BoxMinMax"`` ::

  [xmin,xmax,ymin,ymax,zmin,zmax] = [0.,1.,0.,1.,0.,1.]
  makeClip(ClipType="BoxMinMax", Bounds=[xmin,xmax,ymin,ymax,zmin,zmax])

With ``ClipType=="Box"`` (classical behavior in paraview)::
  
  [xmin,xmax,ymin,ymax,zmin,zmax] = [0.,1.,0.,1.,0.,1.] x05=
  0.5*(xmin+xmax) # position of box center y05= 0.5*(xmin+xmax) z05=
  0.5*(zmin+zmax) deltax= xmax-xmin    # extent of box deltay= ymax-ymin deltaz= zmax-zmin realBounds   = [-deltax/2., deltax/2., -deltay/2., deltay/2., -deltaz/2., deltaz/2.] aClip.ClipType.Position = [x05, y05, z05] aClip.ClipType.Bounds   = realBounds # paraview requires the real DeltaXYZ


makeContour: Create a surface for an isolevel of scalar
-------------------------------------------------------

**Definition**::

  makeContour(varName,isoValueArray,ColorArrayName=None,DiffuseColor=None,lineWidth=1.0)

**Examples**::

  #create isosurface T_s=0.01 and color it by the u_s field
  makeContour(varName='T_s',isoValueArray=[0.01],ColorArrayName='u_s')

::

  #create isosurface T_s=0.01 and color it in BLACK and increase the thickness
  of it
  makeContour(varName='T_s',isoValueArray=[0.01],DiffuseColor=[0,0,0],lineWidth=4.0)

makeThreshold: Only keep points within a range of a variable
------------------------------------------------------------

**Definition**::

  makeThreshold(varName,ThresholdRange,dataType='POINTS')

**Examples**:

The magnitude of a concentration gradient ``'magGradC'`` has been computed in a
given part. This snippet selects the points where the gradient of concentration
is within 10% and 100% of the maximum value. This enables to select region of
high concentration gradients::

  part=GetActiveSource() aVarName='magGradC' [minGrad,maxGrad] =
  part.PointData[aVarName].GetRange() # Get min max of grad in current part
  makeThreshold(varName=aVarName,ThresholdRange=[0.1*maxGrad,1.0*maxGrad])

makeCell2Point: CellDatatoPointData + oriVisibility handling
------------------------------------------------------------

**Definition**:: 

  makeCell2Point()

hidePart, showPart: visibility of a part 
----------------------------------------

hidePart and showPart hide/show at part and returns ori visibility (which tells
if the parent was originally visible or not) This function is similar to
paraview.simple Hide function, except that it returns oriVisibility (instead of
display properties).

When no part is given, the current part (Active Source) is chosen.

**Examples**::

  hidePart() 

::

  hidePart(part=partSlice)
 
::

  showPart(part=partClip)

calcRMS: transform var_2 into rms_var
-------------------------------------

When the solution is a time-averaged solution that contains u and u_2 for
instance, this function computes u_rms as ``u_rms = sqrt(abs(u_2 - u^2))``.

**Examples**::

  calcRMS() # by default dataType='PointData'

::

  calcRMS(dataType='CellData')

visualFilter: multiple point2cell and cell2point for a visual filter effect
---------------------------------------------------------------------------

For a smoother surface rendering before using makeContour, use this visual
filter.


**Examples**::

  visualFilter(ntimes=2) # by default, dataType='PointData'

::

  visualFilter(ntimes=1,dataType='CellData')





