#!/bin/bash

source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/total/env_SUZAKU_total.sh

for BURST in 1 2 3 4 5; do # 1 2 3 4 5 6 7 8
	cd $PHA_DIR/$BURST

	for INST in 0 1 3; do #0 1 3

		if [ $INST = 0 ]; then
			EVENTS='ae406076010xi0_0_3x3n090l_cl.evt.gz ae406076010xi0_0_5x5n090l_cl.evt.gz'
		elif [ $INST = 1 ]; then
			EVENTS='ae406076010xi1_0_3x3n131b_cl.evt.gz ae406076010xi1_0_5x5n131b_cl.evt.gz'
		elif [ $INST = 3 ]; then
			EVENTS='ae406076010xi3_0_3x3n092a_cl.evt.gz ae406076010xi3_0_5x5n092a_cl.evt.gz'
		fi

		$XSELECT <<EOF
${TARGET}_pha_back_XIS$INST
read event
$EVENT_DIR
$EVENTS
set xyname DETX DETY
set binsize $BINSIZE
filter region back_center.reg
filter time file total_${BURST}.curs_gti
extract all

















m
save all back_xis$INST
no
exit
no
EOF

	done

  cp $PHA_DIR/$BURST/*.pha $SPEC_DIR/$BURST/

done

exit 0
