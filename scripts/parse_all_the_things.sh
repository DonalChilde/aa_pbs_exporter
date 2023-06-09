#!/usr/bin/env bash

# Accepts Params
#   YEAR - the year to parse. Default 2023

declare -A DATA_DIRS
DATA_DIRS[2020]="11 12"
DATA_DIRS[2021]="01 02 03 04 05 06 07 08 09 10"
DATA_DIRS[2022]="01 02 03 04 05 06 07 08 09 10 11 12"
DATA_DIRS[2023]="01 03 03 04 05 06"

DATE_STRING="$(date -u "+%Y%m%dT%H%M%sZ")"
PATH_YEAR=${1:-"2023"}

IFS=' '
read -a MONTHS <<<"${DATA_DIRS[$PATH_YEAR]}"
for i in "${MONTHS[@]}"; do
    ./scripts/parse_to_tmp.sh ~/projects/aal-pbs-data-"$PATH_YEAR"/"$PATH_YEAR.$i"/extracted-text/ "$DATE_STRING"/"$PATH_YEAR.$i"
done
