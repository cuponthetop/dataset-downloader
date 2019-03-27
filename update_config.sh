#!/usr/bin/env bash
#!/usr/bin/env bash

# Reset OPTIND
OPTIND=1

PART_IND=1
PART_NUM=1

# Argument Parsing
while getopts "i:n:" opt; do
    case "$opt" in
    n)  PART_NUM=$OPTARG
        sed -i 's/part_num=.*/part_num='${PART_NUM}'/' env/script.env;
        ;;
    i)  PART_IND=$OPTARG
        sed -i 's/part_idx=.*/part_idx='${PART_IND}'/' env/script.env;
        ;;
    esac
done