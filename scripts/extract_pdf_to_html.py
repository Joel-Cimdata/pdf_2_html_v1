import sys
import os
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from PIL import Image
import re
from collections import Counter
from difflib import SequenceMatcher

# Args: input.pdf output.html images_folder
pdf_path = sys.argv[1]
output_html = sys.argv[2]
images_folder = sys.argv[3]

# Open PDF
doc = fitz.open(pdf_path)

# Prepare HTML structure (CSS path updated since index and style are both in output folder)
html = BeautifulSoup("""
<!DOCTYPE html>
<html lang="de">
  <head>
    <meta charset="utf-8">
    <title>TourName</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" type="text/css" href="../style/styles-canua-2024.css" />
  </head>
  <body></body>
</html>
""", "html.parser")
body = html.body

in_infobox = False
infobox_div = None

# Parameters for header/footer detection
top_x_percent = 0.09  # Top 9% of the page
bottom_x_percent = 0.02  # Bottom 2% of the page


# === Step 1: Detect repeating header/footer text ===
header_lines = []
footer_lines = []


for page in doc:  # Loop through all pages
    blocks = page.get_text("blocks")
    page_height = page.rect.height

    for block in blocks:
        if not isinstance(block[4], str):
            continue
        text = block[4].strip()
        y0 = block[1]
        if not text or len(text) > 150:
            continue
        if y0 < page_height * top_x_percent:
            header_lines.append(text)
        elif y0 > page_height * (1 - bottom_x_percent):
            footer_lines.append(text)

# Combine all header and footer lines into a set to exclude them later
excluded_text = set(header_lines + footer_lines)

print("Excluding headers/footers:", excluded_text)


# === Step 2: Loop through pages ===
image_counter = 1

for page in doc:
    blocks = page.get_text("blocks")

    # Separate blocks into two columns based on their x-coordinates
    left_column = []
    right_column = []
    column_threshold = page.rect.width / 2  # Divide page width into two columns

    for block in blocks:
        x0 = block[0]  # x-coordinate of the block's top-left corner
        if x0 < column_threshold:
            left_column.append(block)
        else:
            right_column.append(block)

    # Sort each column top-to-bottom, left-to-right
    left_column.sort(key=lambda b: (b[1], b[0]))
    right_column.sort(key=lambda b: (b[1], b[0]))

    # Combine the columns: process left column first, then right column
    sorted_blocks = left_column + right_column

    used_block_indices = set()
    text_blocks = list(sorted_blocks)  # keep original order

    # === Step 3: Extract images and captions ===
    for img_index, img in enumerate(page.get_images(full=True)):
        xref = img[0]
        pix = fitz.Pixmap(doc, xref)

        if pix.colorspace.n != 3:
            pix = fitz.Pixmap(fitz.csRGB, pix)

        # Skip images under 100px wide
        if pix.width < 100:
            continue

        # Resize images over 1000px wide to 950px while maintaining aspect ratio
        if pix.width > 1001:
            scale_factor = 1000 / pix.width
            new_width = 1000
            new_height = int(pix.height * scale_factor)
            img_data = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_data = img_data.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            img_data = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        img_filename = f"image_{image_counter}.jpg"
        img_path = os.path.join(images_folder, img_filename)

        # Save image as JPEG
        #img_data = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_data.save(img_path, "JPEG", quality=50)

        # Try to find a short nearby text as caption
        caption_text = None
        for idx, block in enumerate(text_blocks):
            if idx in used_block_indices:
                continue
            text = block[4].strip() if isinstance(block[4], str) else ""
            if not text or len(text) > 150 or text in excluded_text:
                continue
            if re.match(r"^[A-ZÄÖÜ]", text):  # likely sentence start
                caption_text = text
                used_block_indices.add(idx)
                break

        # Wrap image in <div class="image"> with caption
        div = html.new_tag("div", attrs={"class": "image"})
        img_tag = html.new_tag("img", src=f"../images/{img_filename}")
        caption = html.new_tag("p", attrs={"class": "caption"})
        caption.string = caption_text or f"Bild {image_counter}"

        div.append(img_tag)
        div.append(caption)
        body.append(div)

        image_counter += 1

    # === Step 4: Add cleaned text blocks ===
    for idx, block in enumerate(text_blocks):
        if idx in used_block_indices:
            continue

        text_raw = block[4]
        if not isinstance(text_raw, str):
            continue
        text_raw = text_raw.strip()
        if not text_raw or text_raw in excluded_text:
            continue

        # Clean hyphenation and line breaks
        text = re.sub(r"-\n", "", text_raw)
        text = re.sub(r"\n", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            continue

        # Start infobox
        if text.startswith("KURZ-INFO"):
            in_infobox = True
            infobox_div = html.new_tag("div", attrs={"class": "blockquote156"})

            # Split first sentence (title) from the rest
            parts = re.split(r"(\bKURZ-INFO[^\.\n]*)", text, maxsplit=1)
            title = parts[1].strip() if len(parts) > 1 else text.strip()
            remaining = parts[2].strip() if len(parts) > 2 else ""

            # Add <h4> title
            h4 = html.new_tag("h4", attrs={"class": "h4-1"})
            h4.string = "🛶 " + title
            infobox_div.append(h4)

            # If there's more content in the same block, keep it as a paragraph
            if remaining:
                p = html.new_tag("p", attrs={"class": "noindentx"})
                p.string = remaining
                infobox_div.append(p)

            continue

        # Handle text inside infobox
        if in_infobox:
            if re.match(r"^[A-ZÄÖÜa-z0-9 ,\-]{2,30}:$", text):
                p = html.new_tag("p", attrs={"class": "noindent"})
                strong = html.new_tag("strong")
                span = html.new_tag("span", attrs={"class": "color4"})
                span.string = text.rstrip(":").strip()
                strong.append(span)
                p.append(strong)
                infobox_div.append(p)
            else:
                p = html.new_tag("p", attrs={"class": "noindentx"})
                p.string = text
                infobox_div.append(p)
            continue

        # Normal body paragraph
        p = html.new_tag("p", attrs={"class": "noindent"})
        p.string = text
        body.append(p)

        # === Finalize infobox if it was still open
    if in_infobox and infobox_div:
        body.append(infobox_div)
        in_infobox = False
        infobox_div = None

# === Step 5: Write final HTML ===
with open(output_html, "w", encoding="utf-8") as f:
    # Use the 'html5lib' parser for proper formatting
    formatted_html = BeautifulSoup(str(html), "html5lib").prettify()
    f.write(formatted_html)