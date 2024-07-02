#!/bin/bash

AHF=/home/cc6881/bin/AHF

TARGET=$1
DIR=$(dirname "$TARGET")/
FILE=$(basename "$TARGET")
MASS=$(echo "$FILE" | cut -d'.' -f1).$(echo "$FILE" | cut -d'.' -f2)
SNAP=$(echo "$FILE" | cut -d'.' -f3)
N_FILE=$(echo "$SNAP / 16" | bc)  # Perform the division and save the result to a variable

echo "Directory: $DIR"
echo "Mass: $MASS"
echo "Final snapshot number: $SNAP"
cd $DIR

for ((i=0; i<N_FILE; i++)); do
    INDEX=$(($i + 1))           # Increment i by 1 for correct file numbering
    INDEX_FORMAT=$(printf "%05d" $(($INDEX * 16)))  # Format number to 5 digits with leading zeros
    F_NAME="${DIR}${MASS}.${INDEX_FORMAT}"    # Construct FILE
    echo "$F_NAME"
    sed -i "s/SNAPSHOT/$F_NAME/" AHFinput.in > AHF.input
    cat AHF.input
    #$AHF AHF.input

done