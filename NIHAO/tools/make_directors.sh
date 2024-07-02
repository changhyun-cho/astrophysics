#!/bin/bash

# Example usage: bash make_directors.sh /path/to/target/directory mass
# bash make_directors.sh /data/cc6881/movies/g2.71e12 g2.71e12

# Script configuration
HOME="/home/cc6881/scripts"
TARGET="$1"
FILE="$2"

# Clean up and prepare movie directories
rm -rf "${TARGET}/movie"
mkdir "${TARGET}/movie"
cd "${TARGET}/movie"
mkdir close closestar cosmo far farstar labeled metalclose metalfar dmclose dmfar dmcosmo closegas fargas cosmogas

# Copy files in a loop
cp "${HOME}/director" "${TARGET}/${FILE}.director"  # Fixed the missing closing quote here
cp "${HOME}/colortables.txt" "${TARGET}/colortables.txt"  # Fixed the missing closing quote here
for i in $(seq 2 10); do
    cp "${HOME}/director${i}" "${TARGET}/${FILE}.director${i}"
done

echo "Movie directories created successfully."
echo "Director Files copied successfully."
echo "Don't forget to make a photogenic file."
echo "And turn on the movie making options."
