#!/bin/bash

source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/env_SUZAKU.sh

for BURST in 0 1 2 3 4 5 6 7 8; do # 1 2 3 4 5 6 7 8
	cd $PHA_DIR/$BURST

	$XSELECT <<EOF
${TARGET}_pha_pin
read event
/Users/changhyun/suzaku/research/data/406076010/hxd/event_cl
ae406076010hxd_0_pinno_cl.evt.gz
set binsize $BINSIZE
filter time file burst_${BURST}.curs_gti
extract all
save all hxd_pin
no
exit
no
EOF

cp $PHA_DIR/$BURST/hxd_pin.pha $SPEC_DIR/$BURST/

done

exit 0
