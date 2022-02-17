#!/bin/bash

source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/env_SUZAKU.sh

for BURST in 0; do #0 1 2 3 4 5 6 7 8
	cd $PHA_DIR/$BURST

	$XSELECT <<EOF
${TARGET}_pha_pin
read event
$HXD_EVENT_DIR
ae403044020hxd_0_pinno_cl.evt.gz
set binsize $BINSIZE
filter phase 54837.07770217184 0.00793229 0.0-0.2
extract all
save all hxd_pin
no
exit
no
EOF

$HXDDTCOR $HXD_EVENT_DIR/ae403044020hxd_0_pse_cl.evt.gz hxd_pin.pha

cp $PHA_DIR/$BURST/hxd_pin.pha $SPEC_DIR/$BURST/

done

exit 0

# filter time file burst_${BURST}.curs_gti
