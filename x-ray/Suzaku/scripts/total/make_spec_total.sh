#!/bin/bash

source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/total/env_SUZAKU_total.sh
source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/total/spec_models_total.sh

for BURST in 1 2 3 4 5; do #0 1 2 3 4 5 6 7 8

	cd $SPEC_DIR/$BURST
	rm $SPEC_DIR/$BURST/total_$MODEL.xcm

	$XSPEC <<EOF
data 1:1 xis0_rebin.pha 2:2 xis1_rebin.pha 3:3 xis3_rebin.pha
resp 1 xis0.rmf 2 xis1.rmf 3 xis3.rmf
arf 1 xis0.arf 2 xis1.arf 3 xis3.arf
backgrnd 1:1 back_xis0_rebin.pha 2:2 back_xis1_rebin.pha 3:3 back_xis3_rebin.pha
setplot energy
ignore 1-3: **-1.0 1.7-1.9 2.2-2.4 12.0-**
statistic chi
$MODEL_VAR
que no; fit ; renorm ; fit ; renorm ; fit ; renorm ; fit ; renorm ; fit
cpd /xs
iplot ldata delchi
rescale y 0.01 4
label top Specturm using $MODEL fitting model
hardcopy total_${BURST}_spec_${MODEL}.ps/cps
quit
save all total_${MODEL}
EOF

	$PS2PDF total_${BURST}_spec_${MODEL}.ps
  mv $SPEC_DIR/$BURST/total_${BURST}_spec_${MODEL}.pdf $RESULT_DIR/$BURST

done

exit 0

# ignore 1-3: **-1.0 1.7-1.9 2.2-2.4 12.0-**
# ignore 1-3: **-1.0 12.0-**

# if [ "$BURST" == "0" ] || [ "$BURST" == "0" ]; then
