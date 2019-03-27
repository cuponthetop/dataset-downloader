#!/usr/bin/env bash

# Remove CR
sed  $'s/\r//' -i /env/${SCRIPT_ENV}

export $(grep -v '^#' /env/${SCRIPT_ENV})

# Generate list of cmd arguments from env file
# and concatenate into single line
ARGS=$(grep -v -e '^#' -e '^\s' /env/${SCRIPT_ENV} | awk -F "=" '{print "--"$1" "$2}' | awk '{print}' ORS=' ')

echo "Starting script with $ARGS"

python /script/"${TARGET_SCRIPT}" ${ARGS}