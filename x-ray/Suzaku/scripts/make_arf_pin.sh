#!/bin/bash

source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/env_SUZAKU.sh

for BURST in 0; do # 1 2 3 4 5 6 7 8
	cd $SPEC_DIR/$BURST
	rm hxd_pin.arf_pin.arf

	$HXDARFGEN <<EOF
hxd_pin.arf
64
17
CALDB
$ATT_DATA
CALDB
$POS_RA
$POS_DEC
hxd_pin.pha
EOF

done

exit 0
