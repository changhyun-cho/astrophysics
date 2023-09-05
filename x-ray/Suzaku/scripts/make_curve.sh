#!/bin/bash

source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/env_SUZAKU.sh

for BURST in 0; do #0 1 2 3 4 5 6 7 8

	cd $CURVE_DIR/$BURST

	for INST in 0; do #0 1 3

		if [ $INST = 0 ]; then
			EVENTS='ae403044020xi0_0_3x3n090a_cl.evt.gz ae403044020xi0_0_5x5n090a_cl.evt.gz'
		elif [ $INST = 1 ]; then
			EVENTS='ae403044020xi1_0_3x3n101b_cl.evt.gz ae403044020xi1_0_5x5n101b_cl.evt.gz'
		elif [ $INST = 3 ]; then
			EVENTS='ae403044020xi3_0_3x3n092a_cl.evt.gz ae403044020xi3_0_5x5n092a_cl.evt.gz'
		fi

    for TYPE in soft hard; do

			if [ $TYPE = soft ]; then
				ENERGY='274 1370'  # 1keV to 5keV
			elif [ $TYPE = hard ]; then
				ENERGY='1370 3288' # 5keV to 12keV
			fi

			$XSELECT <<EOF
suzaku_curve_${INST}_$TYPE
read event
$EVENT_DIR
$EVENTS
set xyname DETX DETY
set binsize $BINSIZE
filter region center.reg
filter time file burst_${BURST}.curs_gti
filter pha_cutoff $ENERGY
extract all
save all burst_${BURST}_xis${INST}_$TYPE
no
exit
no
EOF

		done

	done

	$LCURVE <<EOF
2
burst_${BURST}_xis0_soft.lc
burst_${BURST}_xis0_hard.lc
-
2055
INDEF
output
yes
/xw
2
la t
la g2 Count/sec (soft)
la g3 Count/sec (hard)
p
HArdcopy burst_${BURST}_xis0_lc.ps/ps
q
EOF

	$PS2PDF burst_${BURST}_xis0_lc.ps
	cp $CURVE_DIR/$BURST/*.pdf $RESULT_DIR/$BURST

done

exit 0
#INDEF
#$LCURVE nser=1 cfile1="burst_${BURST}_xis${INST}_${TYPE}.lc" window="-" dtnb=INDEF nbint=INDEF outfile=" " plot=yes plotdev="burst_${BURST}_xis${INST}_${TYPE}.ps/cps"<<EOF
#quit
#EOF
# References
# https://heasarc.gsfc.nasa.gov/docs/xanadu/xronos/examples/lcurve.html
# https://heasarc.gsfc.nasa.gov/ftools/caldb/help/lcurve.txt
#$PS2PDF $RESULT_DIR/$BURST/burst_${BURST}_xis${INST}_${TYPE}.ps
