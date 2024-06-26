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

for ((i=0; i<N_FILE; i++)); do
    INDEX=$(($i + 1))           # Increment i by 1 for correct file numbering
    INDEX_formatted=$(printf "%05d" $(($INDEX * 16)))  # Format number to 5 digits with leading zeros
    F_NAME="${DIR}${MASS}.${INDEX_formatted}"    # Construct FILE
    echo "$F_NAME"

    # If you have a command to process the files, replace the following line with that command
    # Example: ./process_simulation $F_NAME
done

# Under construction, I need to fill the input file first especially the TIPSY info.
while read snaps; do
    echo $galaxy/$snaps
    sed -e "s/GALAXY/$galaxy/g" AHF.input-template > AHF.input
    sed -i -e "s/SNAPSHOT/$snaps/g" AHF.input

    $AHF AHF.input

done < $current_folder/snapshots.txt