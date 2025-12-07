"""
PST to JSON Converter - Simplified Version
Provides multiple methods to convert PST files
"""

import os
import sys
import json

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def method1_manual_export():
    """Instructions for manual export from Outlook"""
    print("""
Method 1: Manual Export from Outlook (RECOMMENDED)
==================================================
1. Open Microsoft Outlook
2. File → Open & Export → Import/Export
3. Choose "Export to a file"
4. Select "Comma Separated Values" (CSV)
5. Select folders to export
6. Save as pzd.csv

Then convert CSV to JSON with:
   python csv_to_json.py pzd.csv pzd.json
""")

def method2_download_readpst():
    """Instructions to download readpst for Windows"""
    print("""
Method 2: Use readpst Tool
===========================
Download libpst for Windows from:
https://www.five-ten-sg.com/libpst/rn01re01.html

Or use Chocolatey:
   choco install pst-utils

Then run:
   readpst -r -o output_folder pzd/pzd.pst

This will extract emails to .eml files which can be processed.
""")

def method3_online_converter():
    """Instructions for online conversion"""
    print("""
Method 3: Online PST Converter
================================
Upload PST to online converter (use with caution for sensitive data):
- https://products.aspose.app/email/conversion/pst-to-mbox
- https://www.coolutils.com/online/PST-to-EML

Then convert the output format to JSON.
""")

def method4_python_pst_parser():
    """Create a basic PST structure parser"""
    print("""
Method 4: Basic PST Structure Info
====================================
I can create a script that reads basic PST file structure
(without full email content extraction).

This will show:
- File size and structure
- Folder organization
- Message counts
- Basic metadata

Would you like me to create this? (y/n): """, end='')

def main():
    pst_file = 'pzd/pzd.pst'

    print("=" * 70)
    print("PST to JSON Converter - Multiple Methods")
    print("=" * 70)
    print(f"\nTarget file: {pst_file}")

    if os.path.exists(pst_file):
        file_size = os.path.getsize(pst_file) / 1024 / 1024
        print(f"File size: {file_size:.1f} MB")
    else:
        print(f"✗ File not found: {pst_file}")
        return 1

    print("\nAvailable conversion methods:\n")

    method1_manual_export()
    print("\n" + "-" * 70)
    method2_download_readpst()
    print("\n" + "-" * 70)
    method3_online_converter()
    print("\n" + "-" * 70)
    method4_python_pst_parser()

    return 0

if __name__ == '__main__':
    sys.exit(main())
