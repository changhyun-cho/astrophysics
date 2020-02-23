#!/bin/bash

source /Users/changhyun/suzaku/research/proc/scripts/env_SUZAKU.sh

for BURST in 0 1 2 3 4 5 6 7 8; do # 1 2 3 4 5 6 7 8

#	cp $HOME/test/center.reg $CURVE_DIR/$BURST/
#	cp $HOME/test/center.reg $PHA_DIR/$BURST/
#	cp $HOME/test/center.reg $SPEC_DIR/$BURST/

#	cp $HOME/test/burst_${BURST}.curs_gti $CURVE_DIR/$BURST/
#	cp $HOME/test/burst_${BURST}.curs_gti $PHA_DIR/$BURST/
# cp $HOME/test/burst_${BURST}.curs_gti $SPEC_DIR/$BURST/

	#cp $HOME/test/back_burst_${BURST}.curs_gti $CURVE_DIR/$BURST/
	#cp $HOME/test/back_burst_${BURST}.curs_gti $PHA_DIR/$BURST/
  #cp $HOME/test/back_burst_${BURST}.curs_gti $SPEC_DIR/$BURST/


done

exit 0
