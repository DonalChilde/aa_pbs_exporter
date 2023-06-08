#!/usr/bin/env bash

# accepts params:
#   SOURCE_FILE - the source file to use
#   PATH_PREFIX - The path prefix to use in command. Optional

DATE_STRING="$(date -u "+%Y%m%dT%H%M%sZ")"

# Use DATE_STRING if no path prefix provided
PATH_PREFIX=${2:-"$DATE_STRING"}
SOURCE_FILE=$1

echo "$SOURCE - $FOO"
aa-pbs-exporter parse $SOURCE_FILE ~/tmp/aa-pbs-exporter/parsed_data/"$PATH_PREFIX"
