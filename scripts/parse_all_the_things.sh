#!/usr/bin/env bash

array=(2022.01 2022.02 2022.03 2022.04 2022.05 2022.06 2022.07 2022.08 2022.09 2022.10 2022.11 2022.12 2023.01 2023.03 2023.03 2023.04 2023.05 2023.06)

for i in "${array[@]}"; do
    # echo "$i"
    aa-pbs-exporter parse ~/Downloads/pbs_packages/"$i"/extracted-text/ ~/Downloads/pbs_packages/parsed_data/"$i"
done
