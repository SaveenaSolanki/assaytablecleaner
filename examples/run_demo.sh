#!/usr/bin/env bash
# run_demo.sh — Demonstrate the assaytablecleaner CLI end-to-end.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "============================================"
echo " assaytablecleaner demo"
echo "============================================"
echo ""

# Install the package in development mode if not already installed
echo "[1/3] Installing assaytablecleaner (editable)..."
cd "$PROJECT_DIR"
pip install -e . 2>&1 | tail -1

echo ""
echo "[2/3] Running assay-clean on demo_input.csv..."
assay-clean clean \
    --input "$SCRIPT_DIR/demo_input.csv" \
    --out "$SCRIPT_DIR/demo_output.csv"

echo ""
echo "[3/3] Showing cleaned output..."
echo "----------------------------------------"
cat "$SCRIPT_DIR/demo_output.csv"
echo "----------------------------------------"
echo ""
echo "Demo complete. Output saved to: $SCRIPT_DIR/demo_output.csv"
