"""Test script to debug PDF text extraction"""
import PyPDF2
import sys

pdf_path = "plan-zarzadzania-danymi.pdf"

print("=" * 80)
print("PDF TEXT EXTRACTION TEST")
print("=" * 80)

try:
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        print(f"\nTotal pages: {len(reader.pages)}")

        # Extract text from first page
        print("\n" + "=" * 80)
        print("FIRST PAGE TEXT:")
        print("=" * 80)
        page1_text = reader.pages[0].extract_text()
        print(page1_text)
        print("\n" + "=" * 80)

        # Check for start markers
        start_marks = [
            "DATA MANAGEMENT PLAN",
            "DATA MANAGEMENT PLAN [in English]",
            "PLAN ZARZĄDZANIA DANYMI",
        ]

        print("\nSTART MARKER DETECTION:")
        print("=" * 80)
        for mark in start_marks:
            if mark in page1_text:
                print(f"✓ Found: '{mark}'")
            else:
                print(f"✗ NOT Found: '{mark}'")

        # Extract all text
        print("\n" + "=" * 80)
        print("CHECKING ALL PAGES FOR MARKERS:")
        print("=" * 80)
        all_text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            all_text += page_text + "\n\n"

            for mark in start_marks:
                if mark in page_text:
                    print(f"Page {i+1}: Found '{mark}'")

        # Show first 500 chars of all_text
        print("\n" + "=" * 80)
        print("FIRST 500 CHARACTERS OF EXTRACTED TEXT:")
        print("=" * 80)
        print(all_text[:500])

except FileNotFoundError:
    print(f"ERROR: Could not find file '{pdf_path}'")
    print("Please make sure the PDF file is in the current directory.")
except Exception as e:
    import traceback
    print(f"ERROR: {str(e)}")
    print(traceback.format_exc())
