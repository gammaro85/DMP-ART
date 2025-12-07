"""
PST Structure Analyzer using olefile
Reads basic structure of PST file without full email extraction
"""

import os
import sys
import json
import olefile

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def analyze_pst_structure(pst_path):
    """Analyze PST file structure using olefile"""

    print(f"Analyzing PST structure: {pst_path}\n")

    if not olefile.isOleFile(pst_path):
        print("✗ This is not a valid OLE file (PST files use OLE format)")
        return None

    ole = olefile.OleFileIO(pst_path)

    data = {
        'file': os.path.basename(pst_path),
        'file_size_mb': round(os.path.getsize(pst_path) / 1024 / 1024, 2),
        'streams': [],
        'structure': {}
    }

    print("=" * 70)
    print("PST File Structure")
    print("=" * 70)

    # List all streams
    stream_list = ole.listdir()
    print(f"\nFound {len(stream_list)} streams/entries:\n")

    for i, stream_path in enumerate(stream_list, 1):
        stream_name = '/'.join(stream_path)

        try:
            stream_data = ole.openstream(stream_path)
            stream_size = stream_data.seek(0, 2)  # Seek to end to get size
            stream_data.seek(0)  # Reset to beginning

            # Read first 100 bytes as preview
            preview_bytes = stream_data.read(min(100, stream_size))

            stream_info = {
                'path': stream_name,
                'size_bytes': stream_size,
                'size_kb': round(stream_size / 1024, 2),
                'preview_hex': preview_bytes[:50].hex() if stream_size > 0 else ''
            }

            data['streams'].append(stream_info)

            print(f"{i}. {stream_name}")
            print(f"   Size: {stream_info['size_kb']} KB")

            if stream_size > 0 and len(preview_bytes) > 0:
                # Try to detect if it's text
                try:
                    preview_text = preview_bytes.decode('utf-8', errors='ignore')[:50]
                    if preview_text.strip():
                        print(f"   Preview: {preview_text}...")
                except:
                    print(f"   Hex: {preview_bytes[:20].hex()}...")

            print()

        except Exception as e:
            print(f"{i}. {stream_name}")
            print(f"   Error reading stream: {str(e)}\n")

    ole.close()

    print("=" * 70)
    print(f"\nTotal streams: {len(data['streams'])}")
    print(f"Total file size: {data['file_size_mb']} MB")

    return data

def save_to_json(data, output_path):
    """Save analysis results to JSON"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Analysis saved to: {output_path}")

def main():
    pst_file = 'pzd/pzd.pst'
    output_json = 'pzd/pzd_structure.json'

    if not os.path.exists(pst_file):
        print(f"✗ PST file not found: {pst_file}")
        return 1

    print("PST Structure Analyzer")
    print("=" * 70)
    print(f"Input:  {pst_file}")
    print(f"Output: {output_json}")
    print("=" * 70)
    print()

    try:
        data = analyze_pst_structure(pst_file)

        if data:
            save_to_json(data, output_json)

            print("\n" + "=" * 70)
            print("NOTE: This is a basic structure analysis.")
            print("For full email extraction, you need:")
            print("  1. Microsoft Outlook (export to CSV/EML)")
            print("  2. readpst tool (libpst package)")
            print("  3. Specialized PST processing libraries")
            print("=" * 70)

            return 0
        else:
            return 1

    except Exception as e:
        print(f"\n✗ Error analyzing PST: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
