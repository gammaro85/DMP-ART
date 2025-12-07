"""
Test OCR setup and configuration
"""
import sys
import os
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 80)
print("OCR SETUP TEST")
print("=" * 80)

# Test 1: Check if pytesseract is installed
print("\n1. Checking pytesseract installation...")
try:
    import pytesseract
    print("✓ pytesseract is installed")

    # Check if Tesseract path is configured
    tesseract_cmd = pytesseract.pytesseract.tesseract_cmd
    print(f"   Tesseract command: {tesseract_cmd}")

    if tesseract_cmd and os.path.exists(tesseract_cmd):
        print("   ✓ Tesseract executable found")

        # Test Tesseract version
        try:
            version = pytesseract.get_tesseract_version()
            print(f"   ✓ Tesseract version: {version}")
        except Exception as e:
            print(f"   ✗ Error getting version: {e}")
    else:
        print("   ✗ Tesseract executable not found at configured path")

except ImportError as e:
    print(f"✗ pytesseract not installed: {e}")

# Test 2: Check if pdf2image is installed
print("\n2. Checking pdf2image installation...")
try:
    import pdf2image
    print("✓ pdf2image is installed")

    # Try to check for poppler
    try:
        # This will fail if poppler is not available
        from pdf2image.exceptions import PDFInfoNotInstalledError
        print("   Note: pdf2image requires poppler-utils")
        print("   Download from: https://github.com/oschwartz10612/poppler-windows/releases/")
        print("   Extract and add bin/ to PATH")
    except Exception:
        pass

except ImportError as e:
    print(f"✗ pdf2image not installed: {e}")

# Test 3: Check HAS_OCR in extractor
print("\n3. Checking DMP Extractor OCR support...")
try:
    from utils.extractor import HAS_OCR
    if HAS_OCR:
        print("✓ OCR is enabled in DMP Extractor")
    else:
        print("✗ OCR is not enabled (missing dependencies)")
except Exception as e:
    print(f"✗ Error checking extractor: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)

# Summary
print("\nSUMMARY:")
print("- If all tests passed, OCR is ready to use")
print("- If pdf2image test failed, you may need to install poppler manually")
print("- Try uploading your PDF to test the full workflow")
