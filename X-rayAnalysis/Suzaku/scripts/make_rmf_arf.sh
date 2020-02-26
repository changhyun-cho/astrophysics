#!/bin/bash

source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/env_SUZAKU.sh

for BURST in 0 1 2 3 4 5 6 7 8; do #0 1 2 3 4 5 6 7 8
	cd $SPEC_DIR/$BURST

	for INST in 0 1 3; do #0 1 3

		if [ $INST = 0 ]; then
			GTI_FILE='ae406076010xi0_0_3x3n090l_cl.evt.gz'
		elif [ $INST = 1 ]; then
			GTI_FILE='ae406076010xi1_0_3x3n131b_cl.evt.gz'
		elif [ $INST = 3 ]; then
			GTI_FILE='ae406076010xi3_0_3x3n092a_cl.evt.gz'
		fi

		$XISRMFGEN <<EOF
$SPEC_DIR/$BURST/xis${INST}.img
$SPEC_DIR/$BURST/xis${INST}.rmf
EOF

		$XISSIMARFGEN <<EOF
XIS$INST
DETXY
$POS_X
$POS_Y
1
DETREG
center.reg
xis${INST}.arf
NUM_PHOTON
100000
xis${INST}.pha
$MASK_DIR/ae_xi${INST}_calmask_20060731.fits
$GTI_DIR/$GTI_FILE
$ATT_DATA
xis${INST}.rmf
default
EOF

		#$XISARFGEN <<EOF
#xis${INST}.pha
#SKYXY
#$POS_X
#$POS_Y
#1
#SKYREG
#center.reg
#xis${INST}.arf
#$ATT_DATA
#xis${INST}.rmf
#EOF

	done

done

exit 0
