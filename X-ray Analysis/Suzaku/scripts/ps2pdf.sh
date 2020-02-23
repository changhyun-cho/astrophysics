#!/bin/bash

source /Users/changhyun/suzaku/research/proc/scripts/env_SUZAKU.sh

for BURST in 0 1 2 3 4 5 6 7 8; do #1 2 3 4 5 6
	cd $RESULT_DIR/$BURST

  for FILE in `ls *.ps`; do #soft hard

			$PS2PDF $RESULT_DIR/$BURST/$FILE

  done

done

exit 0

# References
# https://heasarc.gsfc.nasa.gov/docs/xanadu/xronos/examples/lcurve.html
# https://heasarc.gsfc.nasa.gov/ftools/caldb/help/lcurve.txt
