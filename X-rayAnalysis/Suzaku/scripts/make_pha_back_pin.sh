#!/bin/bash

source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/env_SUZAKU.sh

for BURST in 0 1 2 3 4 5 6 7 8; do # 1 2 3 4 5 6 7 8
	cd $PHA_DIR/$BURST

	$XSELECT <<EOF
${TARGET}_pha_pin
read event
$HXD_EVENT_DIR
ae406076010_hxd_pinbgd.evt.gz
set binsize $BINSIZE
filter time file burst_${BURST}.curs_gti
extract all
save all back_hxd_pin
no
exit
no
EOF

cp $PHA_DIR/$BURST/back_hxd_pin.pha $SPEC_DIR/$BURST/

done

exit 0
