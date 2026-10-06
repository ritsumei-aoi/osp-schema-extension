#!/bin/sh
# Full reproduction of docs/issues/mathematical_proof.md.
# Run from inside scripts/ :   ./run_all.sh
set -e
cd "$(dirname "$0")"
mkdir -p ../artifacts

echo "### 1. basic structure checks"
python3 check_basic.py
echo
echo "### 2. main triviality analysis (n = 1,2,3)"
python3 analyze_triviality.py 3
echo
echo "### 3. scalar obstruction / 'up to scalar' clause"
python3 analyze_scalar_obstruction.py 3
echo
echo "### 4. kernel of delta = inner odd derivations"
python3 check_kernel.py
echo
echo "### 5. export JSON artifacts"
python3 export_artifacts.py 3
echo
echo "### 6. standalone re-verification from JSON only"
python3 verify_artifacts.py
