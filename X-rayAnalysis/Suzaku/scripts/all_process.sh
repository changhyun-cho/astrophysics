#!/bin/bash

source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/env_SUZAKU.sh

#bash make_curve.sh
bash make_pha.sh
bash make_pha_back.sh
bash make_rmf_arf.sh
bash rebin_pha.sh
bash make_spec.sh

##bash make_pha_pin.sh
#you can find the background PHA on https://heasarc.gsfc.nasa.gov/FTP/suzaku/data/background/
##bash make_pha_back_pin.sh
##bash make_arf_pin.sh
#need to adjust the exposure time of background
##bash rebin_pha_pin.sh
#response file is in the caldb
##bash make_spec.sh
