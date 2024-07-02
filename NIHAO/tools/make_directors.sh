#!/bin/bash

# Script configuration
HOME="/home/cc6881/scripts"
TARGET="$1"

# Clean up and prepare movie directories
rm -rf "${TARGET}/movie"
mkdir "${TARGET}/movie"
cd "${TARGET}/movie"
mkdir close closestar cosmo far farstar labeled metalclose metalfar dmclose dmfar dmcosmo closegas fargas cosmogas

# Define the file variable - adjust this according to what it should be
file="$2"

# Print the file name for debugging
echo "$file"

# Copy files in a loop
cp "${HOME}/director" "${TARGET}/${file}.director
for i in $(seq 2 10); do
    cp "${HOME}/director${i}" "${TARGET}/${file}.director${i}"
done

echo "Files copied successfully."
