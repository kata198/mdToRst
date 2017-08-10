#!/bin/bash

# Run this to regen the rest from md conversion for each of the "test" readmes.
#   You can then diff the rst to check for regressions or improvements

MAX_README_NUM=4

for i in `seq 1 1 ${MAX_README_NUM}`; do mdToRst "README_${i}.md" > "README_${i}.rst"; done

