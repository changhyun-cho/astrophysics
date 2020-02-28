#!/bin/bash

source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/env_SUZAKU.sh

REBIN="group 0 255 2
group 256 511 64
group 512 1023 32
group 1024 2047 64
group 2048 2559 128
group 2560 3071 256
group 3072 3583 256
group 3584 4095 256
"

for BURST in 0 1 2 3 4 5 6 7 8 ; do #0 1 2 3 4 5 6 7 8

	cd $SPEC_DIR/$BURST

	for INST in 0 1 3; do

		rm $SPEC_DIR/$BURST/xis${INST}_rebin.pha
		rm $SPEC_DIR/$BURST/back_xis${INST}_rebin.pha

		$GRAPPA <<EOF
xis${INST}.pha
xis${INST}_rebin.pha
$REBIN
exit
EOF

		$GRAPPA <<EOF
back_xis${INST}.pha
back_xis${INST}_rebin.pha
$REBIN
exit
EOF

	done

done

exit 0
