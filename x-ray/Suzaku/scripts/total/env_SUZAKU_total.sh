#!/bin/bash

TARGET=406076010
POS_X=500.613
POS_Y=507.989
BINSIZE=8 #64 #2
MODEL='powerlaw' # compbb compTT powerlaw bbodyrad bbody diskbb+bbody diskbb

HOME=/Users/changhyun/suzaku/research/proc/$TARGET/total
PHA_DIR=$HOME/pha
CURVE_DIR=$HOME/lc
SPEC_DIR=$HOME/spec
RESULT_DIR=$HOME/result

DATA=/Users/changhyun/suzaku/research/data/$TARGET
EVENT_DIR=$DATA/xis/event_cl
GTI_DIR=$DATA/xis/event_cl
ATT_DATA=$DATA/auxil/ae${TARGET}.att.gz

CAL_DIR=/Users/changhyun/caldb/data/suzaku/xis
MASK_DIR=$CAL_DIR/bcf

HEASOFT=/Users/changhyun/heasoft-6.26.1/x86_64-apple-darwin19.0.0/bin/
XISSIMARFGEN=$HEASOFT/xissimarfgen
XISRMFGEN=$HEASOFT/xisrmfgen
XISARFGEN=$HEASOFT/xisarfgen
GRAPPA=$HEASOFT/grppha
LCURVE=$HEASOFT/lcurve
XSELECT=$HEASOFT/xselect
XSPEC=$HEASOFT/xspec
PS2PDF=/usr/local/bin/ps2pdf
