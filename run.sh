#!/bin/sh
OUTPUT_DIR="output"
EXPECTED_DIR="expected"

mkdir $OUTPUT_DIR 2> /dev/null
rm $OUTPUT_DIR/* 2> /dev/null
python simulator.py

for output in "$OUTPUT_DIR"/*; do
    file=$(basename "$output")
    diff output "${EXPECTED_DIR}/$file"
done
