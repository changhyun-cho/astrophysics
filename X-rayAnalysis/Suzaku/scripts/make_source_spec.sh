#!/bin/bash

source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/env_SUZAKU.sh

for BURST in 0 1 2 3 4 5 6 7 8; do #0 1 2 3 4 5 6 7 8

	cd $SPEC_DIR/$BURST

	for INST in 1; do

		rm $SPEC_DIR/$BURST/burst_${INST}.xcm

		$XSPEC <<EOF
data xis${INST}_rebin.pha
resp xis${INST}.rmf
arf xis${INST}.arf
backgrnd back_xis${INST}_rebin.pha
setplot energy
ignore **-1.0 12.0-**
statistic chi
model wabs*compTT

0 -1
1.46979
50 -1

2 -1

que no; fit ; renorm ; fit ; renorm ; fit ; renorm ; fit ; renorm ; fit
cpd /xs
iplot ldata ratio
rescale y 0.001 10
label top XIS$INST Specturm of the burst $BURST
hardcopy burst_${BURST}_xis${INST}_spec.ps/cps
quit
save all burst_${INST}
EOF

	$PS2PDF burst_${BURST}_xis${INST}_spec.ps

	done

  cp $SPEC_DIR/$BURST/*.pdf $RESULT_DIR/$BURST

done

exit 0

#rescale y 0.01 5
