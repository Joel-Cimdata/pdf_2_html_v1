PDF to HTML Converter
=====================

This project converts PDF files to HTML format with image extraction and text formatting.

SETUP INSTRUCTIONS
------------------

1. Create Virtual Environment:
   python3 -m venv venv

2. Activate Virtual Environment:
   source venv/bin/activate

3. Install Dependencies:
   pip install -r requirements.txt

USAGE
-----

1. Place your PDF file in the "pdf_file_here" folder
   - Only one PDF file should be in this folder
   - The script will process the first PDF it finds

2. Run the conversion script:
   cd scripts
   ./convert.sh

   Or if not executable:
   bash convert.sh

3. Output files will be created:
   - HTML file: index/index.html
   - Images: images/ folder
   - Additional output: output/ folder (with style subfolder)

PROJECT STRUCTURE
-----------------

pdf_2_html_v1/
├── scripts/
│   ├── convert.sh              # Main conversion script
│   └── extract_pdf_to_html.py  # Python extraction script
├── pdf_file_here/              # Place PDF files here
├── index/                      # HTML output folder (created by script)
├── images/                     # Extracted images folder (created by script)
├── output/                     # Additional output folder (created by script)
│   └── style/                  # CSS and styling files (created by script)
├── venv/                       # Virtual environment (create during setup)
├── requirements.txt            # Python dependencies
└── README.txt                  # This file

Note: Folders marked as "(created by script)" and "(create during setup)" 
will not exist in the repository and are generated when needed.

REQUIREMENTS
------------

- Python 3.6+
- Linux/Unix environment
- Bash shell

TROUBLESHOOTING
---------------

- If "Permission denied" error: chmod +x scripts/convert.sh
- If "No PDF found" error: Check pdf_file_here folder contains a PDF
- If Python errors: Make sure virtual environment is activated
- If missing packages: Run pip install -r requirements.txt

DEPENDENCIES
------------

- PyMuPDF: PDF processing
- beautifulsoup4: HTML manipulation
- Pillow: Image processing
- lxml: XML/HTML parsing
- html5lib: HTML5 parsing