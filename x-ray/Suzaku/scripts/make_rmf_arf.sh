#!/bin/bash

source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/env_SUZAKU.sh

cd $SPEC_DIR/0

for INST in 0 1 3; do #0 1 3

	if [ $INST = 0 ]; then
		GTI_FILE='ae403044020xi0_0_3x3n090a_cl.evt.gz'
	elif [ $INST = 1 ]; then
		GTI_FILE='ae403044020xi1_0_3x3n101b_cl.evt.gz'
	elif [ $INST = 3 ]; then
		GTI_FILE='ae403044020xi3_0_3x3n092a_cl.evt.gz'
	fi

	$XISRMFGEN <<EOF
$SPEC_DIR/0/xis${INST}.img
$SPEC_DIR/0/xis${INST}.rmf
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

for BURST in 0 ; do

	cp $SPEC_DIR/0/*.rmf $SPEC_DIR/$BURST/
	cp $SPEC_DIR/0/*.arf $SPEC_DIR/$BURST/

done

exit 0
