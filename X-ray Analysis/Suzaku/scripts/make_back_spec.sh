#!/bin/bash

source /Users/changhyun/suzaku/research/proc/scripts/env_SUZAKU.sh

for BURST in 0 1 2 3 4 5 6 7 8; do #0 1 2 3 4 5 6 7 8

	cd $SPEC_DIR/$BURST

	for INST in 0 1 3; do

		rm $SPEC_DIR/$BURST/back_burst_${INST}.xcm

		$XSPEC <<EOF
data back_xis${INST}_rebin.pha
resp xis${INST}.rmf
arf xis${INST}.arf
setplot energy
ignore **-1.0 12.0-**
statistic chi
model wabs*bbody


5.0
que no; fit ; renorm ; fit ; renorm ; fit ; renorm ; fit ; renorm ; fit
cpd /xs
iplot ldata ratio
label top XIS$INST Specturm of the burst $BURST
hardcopy back_burst_${BURST}_xis${INST}_spec.ps/cps
quit
save all back_burst_${INST}
EOF

	$PS2PDF back_burst_${BURST}_xis${INST}_spec.ps

	done

  cp $SPEC_DIR/$BURST/*.pdf $RESULT_DIR/$BURST

done

exit 0

#rescale y 0.01 5
