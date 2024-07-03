#!/bin/bash

# Example usage: bash run_ahf.sh /path/to/target/directory/last_snapshot
# bash run_ahf.sh /data/cc6881/new_fb_test/bondi/g2.71e12/g2.71e12.01024
# Ensure the AHFinput.in is located in the target directory and insert the correct values for
# TIPSY_BOXSIZE, TIPSY_VUNIT, TIPSY_MUNIT manually.

AHF=/home/cc6881/bin/AHF

TARGET=$1
DIR=$(dirname "$TARGET")/
FILE=$(basename "$TARGET")
INTERVAL=16
MASS=$(echo "$FILE" | cut -d'.' -f1).$(echo "$FILE" | cut -d'.' -f2)
SNAP=$(echo "$FILE" | cut -d'.' -f3)
N_FILE=$(echo "$SNAP / $INTERVAL" | bc)  # Perform the division and save the result to a variable

echo "Directory: $DIR"
echo "Mass: $MASS"
echo "Final snapshot number: $SNAP"
cd $DIR

for ((i=0; i<N_FILE; i++)); do
    INDEX=$(($i + 1))           # Increment i by 1 for correct file numbering
    INDEX_FORMAT=$(printf "%05d" $(($INDEX * $INTERVAL)))  # Format number to 5 digits with leading zeros
    F_NAME="${DIR}${MASS}.${INDEX_FORMAT}"    # Construct FILE
    echo "$F_NAME"
    sed "s#SNAPSHOT#$F_NAME#" AHFinput.in > AHF.input
    $AHF AHF.input
done