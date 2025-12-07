"""
Test OCR configuration in extractor
"""
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 80)
print("TESTING EXTRACTOR OCR CONFIGURATION")
print("=" * 80)

# Import the extractor module (this will run the OCR configuration code)
from utils.extractor import HAS_OCR, DMPExtractor

print(f"\n HAS_OCR: {HAS_OCR}")

if HAS_OCR:
    import pytesseract
    import os

    tesseract_cmd = pytesseract.pytesseract.tesseract_cmd
    print(f"pytesseract.tesseract_cmd: {tesseract_cmd}")

    # Check if the configured path exists
    if os.path.exists(str(tesseract_cmd)):
        print(f"✓ Tesseract executable found at: {tesseract_cmd}")

        # Try to get version
        try:
            version = pytesseract.get_tesseract_version()
            print(f"✓ Tesseract version: {version}")
            print("\n✓✓✓ OCR IS READY TO USE! ✓✓✓")
        except Exception as e:
            print(f"✗ Error getting Tesseract version: {e}")
    else:
        print(f"✗ Tesseract executable not found at: {tesseract_cmd}")
        print("\nTrying manual configuration...")

        # Try manual paths
        manual_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
        ]

        for path in manual_paths:
            if os.path.exists(path):
                print(f"✓ Found Tesseract at: {path}")
                pytesseract.pytesseract.tesseract_cmd = path

                try:
                    version = pytesseract.get_tesseract_version()
                    print(f"✓ Version: {version}")
                    print(f"\n✓✓✓ OCR IS READY (manually configured)! ✓✓✓")
                    break
                except Exception as e:
                    print(f"✗ Error: {e}")
else:
    print("✗ OCR dependencies not available")

print("\n" + "=" * 80)
