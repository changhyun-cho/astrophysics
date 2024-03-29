#!/bin/bash

source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/env_SUZAKU.sh

for BURST in 0; do # 1 2 3 4 5 6 7 8
	cd $PHA_DIR/$BURST

	for INST in 0 1 3; do #0 1 3

		if [ $INST = 0 ]; then
			EVENTS='ae403044020xi0_0_3x3n090a_cl.evt.gz ae403044020xi0_0_5x5n090a_cl.evt.gz'
		elif [ $INST = 1 ]; then
			EVENTS='ae403044020xi1_0_3x3n101b_cl.evt.gz ae403044020xi1_0_5x5n101b_cl.evt.gz'
		elif [ $INST = 3 ]; then
			EVENTS='ae403044020xi3_0_3x3n092a_cl.evt.gz ae403044020xi3_0_5x5n092a_cl.evt.gz'
		fi

		$XSELECT <<EOF
proc
read event
$EVENT_DIR
$EVENTS
set xyname DETX DETY
filter region center.reg
filter phase 54837.07770217184 0.00793229 0.0-0.2
set binsize $BINSIZE
extract all
save all xis$INST
no
exit
no
EOF

	done

cp $PHA_DIR/$BURST/*.img $SPEC_DIR/$BURST/
cp $PHA_DIR/$BURST/*.pha $SPEC_DIR/$BURST/

done

exit 0
# ${TARGET}_pha_XIS$INST
# filter region center.reg
# filter time file burst_${BURST}.curs_gti
