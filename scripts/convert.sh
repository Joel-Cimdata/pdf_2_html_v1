#!/bin/bash

# Find the first PDF file in the pdf_file_here folder
PDF_FILE=$(find ../pdf_file_here -maxdepth 1 -type f -name "*.pdf" | head -n 1)

if [ -z "$PDF_FILE" ]; then
  echo "❌ No PDF file found in the pdf_file_here folder."
  exit 1
fi

# All output goes inside the output folder
OUTPUT_DIR="../output"
INDEX_DIR="../output/index"
IMAGES_DIR="../output/images"
STYLE_DIR="../output/style"
OUTPUT_HTML="../output/index/index.html"

# Create all necessary directories inside output folder
echo "📁 Creating directories inside output folder..."
mkdir -p "$OUTPUT_DIR" && echo "  ✓ Created: $OUTPUT_DIR"
mkdir -p "$INDEX_DIR" && echo "  ✓ Created: $INDEX_DIR"
mkdir -p "$IMAGES_DIR" && echo "  ✓ Created: $IMAGES_DIR"
mkdir -p "$STYLE_DIR" && echo "  ✓ Created: $STYLE_DIR"

cd "$(dirname "$0")"

echo "🔄 Starting PDF conversion..."
(
source ../venv/bin/activate
python3 extract_pdf_to_html.py "$PDF_FILE" "$OUTPUT_HTML" "$IMAGES_DIR"
)

if [ $? -eq 0 ]; then
  echo "✅ Conversion complete: $OUTPUT_HTML"
  echo "📂 All output is in: $OUTPUT_DIR"
else
  echo "❌ Conversion failed"
  exit 1
fi