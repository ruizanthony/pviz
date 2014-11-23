.. include:: links.rst

.. _gettingStarted:

Getting Started 
================

PVIZ was mainly developed for batch-processing without the ParaView GUI. However, it is sometimes convenient to use PVIZ within GUI, which extends the capacities of ParaView with the macros defined in the PVIZ python module.

.. _gettingStarted_downloadAndInstall:

Download
--------

* `Download PVIZ`_
* Unzip it and place it into a convenient location. For instance ``~/workspace/PVIZ``

.. _gettingStarted_commandLine:

Command line mode (Unix and Mac Users only)
--------------------------------------

Insert these two lines in your ``~/.bashrc`` (don't forget to adjust ``~/workspace/PVIZ`` if necessary). 

.. code-block:: bash

   export PVIZ=~/workspace/PVIZ # PVIZ root directory
   source $PVIZ/bashrc_pviz.sh  # PVIZ env variables

.. _gettingStarted_GUI:

GUI mode
--------
* Open your solution file as usual (File/Open).
 
* Prepare your pipeline as usual (applying any needed filters, such as slices, contours).

* Open the python shell (Tools/Python Shell)

* Import PVIZ

::

  import sys; sys.path.append('/Users/ruiz/workspace/PVIZ'); # updates PYTHONPATH

  import pviz

Of course, you need to change ``'/Users/ruiz/workspace/PVIZ'``,  by the path to
where you placed the PVIZ root directory. 

Note that if you ran ParaView from a terminal, the ``PYTHONPATH`` environment
variable is transferred to ParaView. 
If you have sourced ``$PVIZ/bashrc_pviz.sh`` as explained in
:ref:`gettingStarted_commandLine`, you just need to type::

  import pviz     

* Use PVIZ. Some examples are given here: :ref:`interactiveMode`.


