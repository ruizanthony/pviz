.. include:: links.rst
.. _interactiveMode:

GUI Mode
========

PVIZ provides a set of convenient functions that can ease post-processing within
the ParaView GUI. The ParaView GUI is great and very intuitive. PVIZ enables
you to take advantage of the Python Shell within the GUI and do hybrid
interactive/scripted postprocessing. Simple examples are provided here on how
to use PVIZ in interactive mode.

Have a look at the `interactive examples`_ in the git repository.

Setting your current directory
------------------------------

If you launched ParaView from the command line, your current directory 
is set to your current location (``$PWD``).

If you launched ParaView from your graphical environment (Mac, Windows, Linux), you
need to adjust your working directory (which is set by default to the installation 
directory of ParaView, for instance ``/Application/Paraview.app`` on Mac).
Use the ``os`` python module:

::

  import os; os.chdir('/Users/amruiz/temp')


Saving all views 
----------------

::

  pviz.saveAllViews()

NB: It's also possible to save all views into one image directly in the GUI
(Unticking `Save only selected view` in File/Save Screenshot). 

