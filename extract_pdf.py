#!/usr/bin/env python3
"""Script to extract text from PDF and identify columns"""

try:
    import pdfplumber

    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    try:
        import PyPDF2

        HAS_PYPDF2 = True
    except ImportError:
        HAS_PYPDF2 = False


def extract_with_pdfplumber(pdf_path):
    """Extract text using pdfplumber"""
    with pdfplumber.open(pdf_path) as pdf:
        # Get first few pages to identify structure
        for i, page in enumerate(pdf.pages[:5]):
            print(f"\n=== Page {i+1} ===")
            text = page.extract_text()
            if text:
                print(text[:2000])  # First 2000 chars

            # Try to extract tables
            tables = page.extract_tables()
            if tables:
                print(f"\nFound {len(tables)} table(s) on page {i+1}")
                for j, table in enumerate(tables[:2]):  # First 2 tables
                    print(f"\n--- Table {j+1} ---")
                    if table and len(table) > 0:
                        # Print header row
                        if len(table) > 0:
                            print("Headers:", table[0])
                        # Print first few data rows
                        for row in table[1:6]:
                            print(row)


def extract_with_pypdf2(pdf_path):
    """Extract text using PyPDF2"""
    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for i, page in enumerate(pdf_reader.pages[:5]):
            print(f"\n=== Page {i+1} ===")
            text = page.extract_text()
            if text:
                print(text[:2000])  # First 2000 chars


if __name__ == "__main__":
    pdf_path = "data/33-Constituency-Wise-Detailed-Result.pdf"

    if HAS_PDFPLUMBER:
        print("Using pdfplumber...")
        extract_with_pdfplumber(pdf_path)
    elif HAS_PYPDF2:
        print("Using PyPDF2...")
        extract_with_pypdf2(pdf_path)
    else:
        print("No PDF library available. Please install pdfplumber or PyPDF2")
        print("Try: pip install pdfplumber --break-system-packages")
