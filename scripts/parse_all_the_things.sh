#!/usr/bin/env bash

array_2020=(2020.11 2020.12)
array_2021=(2021.01 2021.02 2021.03 2021.04 2021.05 2021.06 2021.07 2021.08 2021.09 2021.10)
array_2022=(2022.01 2022.02 2022.03 2022.04 2022.05 2022.06 2022.07 2022.08 2022.09 2022.10 2022.11 2022.12)
array_2023=(2023.01 2023.03 2023.03 2023.04 2023.05 2023.06)

DATE_STRING="$(date -u "+%Y%m%dT%H%M%sZ")"
PATH_YEAR="2020"

for i in "${array_2020[@]}"; do
    aa-pbs-exporter parse ~/projects/aal-pbs-data-"$PATH_YEAR"/"$i"/extracted-text/ ~/tmp/pbs_packages/parsed_data/"$DATE_STRING"/"$i"
done
