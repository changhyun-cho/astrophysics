#!/bin/bash

source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/total/env_SUZAKU_total.sh

bash copy_files_total.sh
#bash make_curve_total.sh
bash make_pha_total.sh
bash make_pha_back_total.sh
#bash make_rmf_arf.sh
bash rebin_pha_total.sh
bash make_spec_total.sh
