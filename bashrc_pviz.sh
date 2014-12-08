#!/bin/bash
# =============================
# To use PVIZ, put this line in ~/.bashrc: source /path/to/pviz/bashrc_pviz.sh
# (The recommended /path/to/pviz is ~/workspace/PVIZ)
# =============================
# sets PVIZ to the directory containing bashrc_pviz.sh,
# for instance ~/workspace/PVIZ (/path/to/pviz in the above example)
export PVIZ=$( builtin cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

export PATH=$PVIZ/bin:$PATH                # various scripts (for instance pviz_pvsmPrepare)
export PATH=$PVIZ/examples/simple:$PATH    # pviz simple   scripts examples
export PATH=$PVIZ/examples/advanced:$PATH  # pviz advanced scripts examples
export PYTHONPATH=$PVIZ:$PYTHONPATH        # for importing pviz into python
export PATH=$PVIZ:$PATH                    # pviz.py can also be used as a script (not only module)
