#!/bin/bash
# put these two lines in your ~/.bashrc
# =============================
# export PVIZ=/path/to/pviz/ # directory containing bashrc_pviz.sh, for instance ~/workspace/PVIZ
# source $PVIZ/bashrc_pviz.sh
# =============================
export PATH=$PVIZ/bin:$PATH               # various scripts (for instance pviz_pvsmPrepare)
export PATH=$PVIZ/simpleExamples:$PATH    # pviz simple   scripts examples
export PATH=$PVIZ/advancedExamples:$PATH  # pviz advanced scripts examples
export PYTHONPATH=$PVIZ:$PYTHONPATH       # for importing pviz into python
export PATH=$PVIZ:$PATH                   # pviz.py can also be used as a script (not only module)
