#!/bin/bash

# Find the first PDF file in the pdf_file_here folder
PDF_FILE=$(find ../pdf_file_here -maxdepth 1 -type f -name "*.pdf" | head -n 1)

if [ -z "$PDF_FILE" ]; then
  echo "❌ No PDF file found in the pdf_file_here folder."
  exit 1
fi

OUTPUT_HTML="../index/index.html"
IMAGES_DIR="../images"
INDEX_DIR="../index"
OUTPUT_DIR="../output"
STYLE_DIR="../output/style"

# Create all necessary directories
mkdir -p "$IMAGES_DIR"
mkdir -p "$INDEX_DIR"
mkdir -p "$OUTPUT_DIR"
mkdir -p "$STYLE_DIR"

cd "$(dirname "$0")"

(
source ../venv/bin/activate
python3 extract_pdf_to_html.py "$PDF_FILE" "$OUTPUT_HTML" "$IMAGES_DIR"
)

echo "✅ Conversion complete: $OUTPUT_HTML"