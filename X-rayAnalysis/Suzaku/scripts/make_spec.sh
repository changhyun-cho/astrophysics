#!/bin/bash

source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/env_SUZAKU.sh
source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/spec_models.sh

for BURST in 1 2 3 4 5 6 7 8; do #0 1 2 3 4 5 6 7 8

	cd $SPEC_DIR/$BURST
	rm $SPEC_DIR/$BURST/burst_$MODEL.xcm

	$XSPEC <<EOF
data 1:1 xis0_rebin.pha 2:2 xis1_rebin.pha 3:3 xis3_rebin.pha
resp 1 xis0.rmf 2 xis1.rmf 3 xis3.rmf
arf 1 xis0.arf 2 xis1.arf 3 xis3.arf
backgrnd 1:1 back_xis0_rebin.pha 2:2 back_xis1_rebin.pha 3:3 back_xis3_rebin.pha
setplot energy
ignore 1-3: **-1.0 12.0-**
statistic chi
$MODEL_VAR
que no; fit ; renorm ; fit ; renorm ; fit ; renorm ; fit ; renorm ; fit
cpd /xs
iplot ldata ratio
rescale y 0.05 7
label top Specturm of the burst $BURST using $MODEL fitting model
hardcopy burst_${BURST}_spec_${MODEL}.ps/cps
quit
save all burst_${MODEL}
EOF

	$PS2PDF burst_${BURST}_spec_${MODEL}.ps
  cp $SPEC_DIR/$BURST/burst_${BURST}_spec_${MODEL}.pdf $RESULT_DIR/$BURST

done

exit 0
#
