#!/bin/bash

source /Users/changhyun/GitHub/astrophysics/X-rayAnalysis/Suzaku/scripts/env_SUZAKU_total.sh

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

if [ "$MODEL" = "diskbb" ]; then

  MODEL_VAR='model wabs*diskbb


  0.01


  0.02


  0.03
  '

fi
