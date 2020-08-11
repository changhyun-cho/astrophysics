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




  0.04
  '


fi

if [ "$MODEL" = "bbody" ]; then

  MODEL_VAR='model wabs*bbody


  0.01


  0.02


  0.03
  '

fi

if [ "$MODEL" = "powerlaw" ]; then

  MODEL_VAR='model wabs*powerlaw


  0.01


  0.02


  0.03
  '

fi

if [ "$MODEL" = "bbodyrad" ]; then

  MODEL_VAR='model wabs*bbodyrad


  0.01


  0.02


  0.03
  '

fi

if [ "$MODEL" = "diskbb+bbody" ]; then

  MODEL_VAR='model wabs*(diskbb+bbody)


  0.01

  0.01


  0.02

  0.02


  0.03

  0.03
  '

fi

if [ "$MODEL" = "gauss+powerlaw" ]; then

  MODEL_VAR='model wabs*(gauss+powerlaw)
  30
  6.4 -1

  0.01
  0.9
  0.01

  6.4 -1

  0.02

  0.02

  6.4 -1

  0.03

  0.03

  6.4 -1

  0.04

  0.04
  '

fi

if [ "$MODEL" = "gauss+powerlaw" ]; then

  MODEL_VAR='model wabs*(gauss+powerlaw)
  30
  6.4 -1

  0.01
  0.9
  0.01

  6.4 -1

  0.02

  0.02

  6.4 -1

  0.03

  0.03

  6.4 -1

  0.04

  0.04
  '

fi

if [ "$MODEL" = "tbabs*(gauss+powerlaw*highecut)*cyclabs" ]; then

  MODEL_VAR='model tbabs * (gauss + powerlaw * highecut) * cyclabs
  27
  6.4 -1
  0.01 -1
  0.01
  0.64
  0.01
  29
  21
  2.45
  30
  5 +1
  0 -1


  6.4 -1
  0.01 -1
  0.02

  0.02





  0 -1


  6.4 -1
  0.01 -1
  0.03

  0.03





  0 -1


  6.4 -1
  0.01 -1
  0 -1

  0.04





  0 -1

  '

fi

if [ "$MODEL" = "const*tbabs*(gauss+cutoffpl+cutoffpl)*cyclabs" ]; then

  MODEL_VAR='model const * tbabs * (gauss + cutoffpl + cutoffpl) * cyclabs
  1 -1
  30
  6.4 -1
  1
  10

  10
  0.01

  10
  0.03


  1 0
  0 -1

  2

  6.4 -1

  0.02









  0 -1

  3

  6.4 -1

  0.03









  0 -1

  4

  6.4 -1

  0 -1









  0 -1


  newpar 10 = 7
  '

fi
