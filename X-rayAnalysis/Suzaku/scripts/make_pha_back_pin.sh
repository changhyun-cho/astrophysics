#!/bin/bash

source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/env_SUZAKU.sh

for BURST in 0; do #0 1 2 3 4 5 6 7 8
	cd $PHA_DIR/$BURST

	$XSELECT <<EOF
${TARGET}_pha_pin
read event
$HXD_EVENT_DIR
ae403044020_hxd_pinbgd.evt.gz
set binsize $BINSIZE
filter time file burst_${BURST}.curs_gti
extract all
save all back_hxd_pin
exit
no
EOF

$HXDDTCOR $HXD_EVENT_DIR/ae403044020hxd_0_pse_cl.evt.gz back_hxd_pin.pha

cp $PHA_DIR/$BURST/back_hxd_pin.pha $SPEC_DIR/$BURST/back_hxd_pin_expcor.pha
#cp $SPEC_DIR/$BURST/back_hxd_pin.pha $SPEC_DIR/$BURST/back_hxd_pin_expcor.pha

done

exit 0
