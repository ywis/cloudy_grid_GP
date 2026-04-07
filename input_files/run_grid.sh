#!/bin/bash
# Batch run script for Cloudy PDR grid
# Total models: 169
# Usage: cd input_files && bash run_grid.sh
# Requires: Cloudy v17.02 installed and 'cloudy.exe' in PATH

NPROC=${1:-4}  # Number of parallel processes (default: 4)

echo "Running ${NPROC} parallel Cloudy processes..."
echo "Total models: 169"

run_model() {
    local model=$1
    echo "Running $model ..."
    cloudy.exe -r $model
}
export -f run_model

# Generate model list and run in parallel
ls *.in | sed 's/.in$//' | xargs -P $NPROC -I {} bash -c 'run_model "{}"'

echo "Grid complete."
