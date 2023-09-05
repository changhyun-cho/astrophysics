#!/bin/bash

source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/total/env_SUZAKU_total.sh

for BURST in 1 2 3 4 5; do # 1 2 3 4 5 6 7 8

#	cp $HOME/test/center.reg $CURVE_DIR/$BURST/
	cp $HOME/test/center.reg $PHA_DIR/$BURST/
	cp $HOME/test/center.reg $SPEC_DIR/$BURST/

#  cp $HOME/test/back_center.reg $CURVE_DIR/$BURST/
	cp $HOME/test/back_center.reg $PHA_DIR/$BURST/
	cp $HOME/test/back_center.reg $SPEC_DIR/$BURST/

#	cp $HOME/test/burst_${BURST}.curs_gti $CURVE_DIR/$BURST/
	cp $HOME/test/total_${BURST}.curs_gti $PHA_DIR/$BURST/
  cp $HOME/test/total_${BURST}.curs_gti $SPEC_DIR/$BURST/

# cp $HOME/test/back_burst_${BURST}.curs_gti $CURVE_DIR/$BURST/
  #cp $HOME/test/back_burst_${BURST}.curs_gti $PHA_DIR/$BURST/
  #cp $HOME/test/back_burst_${BURST}.curs_gti $SPEC_DIR/$BURST/

	cp $HOME/test/*.rmf $SPEC_DIR/$BURST/
  cp $HOME/test/*.arf $SPEC_DIR/$BURST/


done

exit 0
