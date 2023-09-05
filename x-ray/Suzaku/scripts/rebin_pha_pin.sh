#!/bin/bash

source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/env_SUZAKU.sh

REBIN="group min 2"

for BURST in 0; do #0 1 2 3 4 5 6 7 8

	cd $SPEC_DIR/$BURST
	rm hxd_pin_rebin.pha
	rm back_hxd_pin_rebin.pha

	$GRAPPA <<EOF
hxd_pin.pha
hxd_pin_rebin.pha
$REBIN
exit
EOF

	$GRAPPA <<EOF
back_hxd_pin_expcor.pha
back_hxd_pin_rebin.pha
$REBIN
exit
EOF

done

exit 0
