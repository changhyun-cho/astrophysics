#!/bin/bash

source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/env_SUZAKU.sh

if [ "$MODEL" = "compTT" ]; then

  MODEL_VAR='model wabs*compTT

  0 -1
  1.5
  50 -1

  2 -1
  0.1






  0.2






  0.3
  '
elif [ "$MODEL" = "compbb" ]; then

  MODEL_VAR='model wabs*compbb


  50 -1

  0.01




  0.02




  0.03
  '

fi
