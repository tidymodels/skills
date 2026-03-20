#!/bin/bash

# Localize Shared Files Script
# Copies shared-references (including scripts/) into each skill's references/ folder
# This eliminates "../shared-references" paths that Claude treats as optional

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Go to parent directory (tidymodels/)
cd "$SCRIPT_DIR/.."

echo "========================================"
echo "Localizing Shared Files to Skills"
echo "========================================"
echo ""

# Define skills
SKILLS=(
    "add-yardstick-metric"
    "add-recipe-step"
)

# Copy shared files to each skill
for SKILL in "${SKILLS[@]}"; do
    echo "Processing: $SKILL"

    REFS_DIR="$SKILL/references"

    # Ensure references directory exists
    if [ ! -d "$REFS_DIR" ]; then
        echo "  ERROR: $REFS_DIR not found"
        continue
    fi

    # Copy shared-references files to references/
    echo "  Copying shared-references/*.md → $REFS_DIR/"
    cp -v shared-references/*.md "$REFS_DIR/"

    # Create scripts subdirectory
    SCRIPTS_DIR="$REFS_DIR/scripts"
    mkdir -p "$SCRIPTS_DIR"

    # Copy shared-references/scripts to references/scripts/
    echo "  Copying shared-references/scripts/* → $SCRIPTS_DIR/"
    cp -v shared-references/scripts/* "$SCRIPTS_DIR/"

    echo "  ✓ $SKILL complete"
    echo ""
done

echo "========================================"
echo "✓ Localization Complete"
echo "========================================"
echo ""
echo "Copied to each skill's references/ folder:"
echo "  - All shared-references/*.md files"
echo "  - All shared-references/scripts/* files (in scripts/ subdirectory)"
echo ""
echo "Next: Update paths in SKILL.md and references/*.md files"
