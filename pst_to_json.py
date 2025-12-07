"""
PST to JSON Converter
Converts a Microsoft Outlook PST file to JSON format.
Uses readpst tool if available, otherwise attempts Python libraries.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def convert_with_readpst(pst_file, output_dir):
    """Try to use readpst command-line tool"""
    try:
        # Try to run readpst
        result = subprocess.run(
            ['readpst', '-r', '-o', output_dir, pst_file],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ Successfully extracted with readpst to {output_dir}")
            return True
        else:
            print(f"✗ readpst failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("✗ readpst tool not found")
        return False

def convert_with_outlook_com(pst_file, output_json):
    """Convert PST using Outlook COM API (Windows only)"""
    try:
        import win32com.client
        import pythoncom
    except ImportError:
        print("✗ pywin32 not available")
        return False

    print(f"Opening PST file with Outlook COM API: {pst_file}")

    # Get absolute path
    pst_file_abs = os.path.abspath(pst_file)

    try:
        # Initialize COM
        pythoncom.CoInitialize()

        # Create Outlook application object
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")

        # Add PST file to Outlook
        print("Adding PST to Outlook...")
        namespace.AddStore(pst_file_abs)

        data = {
            'file': os.path.basename(pst_file),
            'folders': [],
            'messages': []
        }

        # Find the PST store
        pst_store = None
        for store in namespace.Stores:
            if pst_file_abs.lower() in store.FilePath.lower():
                pst_store = store
                break

        if not pst_store:
            print("✗ Could not find PST store")
            return False

        print(f"✓ Found PST store: {pst_store.DisplayName}")

        # Process folders recursively
        def process_folder(folder, path=""):
            try:
                folder_name = folder.Name
                current_path = f"{path}/{folder_name}" if path else folder_name

                folder_info = {
                    'name': folder_name,
                    'path': current_path,
                    'num_items': folder.Items.Count
                }
                data['folders'].append(folder_info)

                print(f"Processing folder: {current_path} ({folder.Items.Count} items)")

                # Process messages (limit to first 1000 per folder to avoid memory issues)
                max_messages = min(folder.Items.Count, 1000)
                for i in range(1, max_messages + 1):
                    try:
                        item = folder.Items[i]
                        # Check if it's a mail item
                        if hasattr(item, 'Subject'):
                            msg_data = {
                                'folder': current_path,
                                'subject': item.Subject if hasattr(item, 'Subject') else '',
                                'sender': item.SenderName if hasattr(item, 'SenderName') else '',
                                'sent_on': str(item.SentOn) if hasattr(item, 'SentOn') else '',
                                'body': (item.Body[:500] + '...') if hasattr(item, 'Body') and item.Body and len(item.Body) > 500 else (item.Body if hasattr(item, 'Body') else '')
                            }
                            data['messages'].append(msg_data)
                    except Exception as e:
                        # Skip problematic items
                        pass

                # Process subfolders
                for subfolder in folder.Folders:
                    process_folder(subfolder, current_path)

            except Exception as e:
                print(f"Warning: Error processing folder {path}: {str(e)}")

        # Start processing from root folder
        root_folder = pst_store.GetRootFolder()
        process_folder(root_folder)

        # Remove PST from Outlook
        print("Removing PST from Outlook...")
        namespace.RemoveStore(root_folder)

        # Write JSON
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Successfully converted to {output_json}")
        print(f"  - Folders: {len(data['folders'])}")
        print(f"  - Messages: {len(data['messages'])}")

        pythoncom.CoUninitialize()
        return True

    except Exception as e:
        print(f"✗ Error with Outlook COM: {str(e)}")
        try:
            pythoncom.CoUninitialize()
        except:
            pass
        return False

def try_python_library(pst_file, output_json):
    """Try to use Python library to read PST"""
    print("\nAttempting to read PST with Python libraries...")

    # Try importing available libraries
    libraries_tried = []

    # Try Outlook COM (Windows only)
    if sys.platform == 'win32':
        try:
            import win32com.client
            libraries_tried.append("outlook_com")
            print("✓ Found Outlook COM (pywin32)")
            return convert_with_outlook_com(pst_file, output_json)
        except ImportError:
            print("✗ pywin32 not available")

    # Try pypff
    try:
        import pypff
        libraries_tried.append("pypff")
        print("✓ Found pypff library")
        return convert_with_pypff(pst_file, output_json)
    except ImportError:
        print("✗ pypff not available")

    # Try libratom
    try:
        from libratom.lib.pff import PffArchive
        libraries_tried.append("libratom")
        print("✓ Found libratom library")
        return convert_with_libratom(pst_file, output_json)
    except ImportError:
        print("✗ libratom not available")

    if not libraries_tried:
        print("\n✗ No suitable Python library found for PST processing.")
        print("\nTo install support for PST files, try:")
        print("  pip install pypff-python")
        print("  OR install readpst tool (part of libpst package)")
        return False

    return False

def convert_with_pypff(pst_file, output_json):
    """Convert PST using pypff library"""
    import pypff

    print(f"Opening PST file: {pst_file}")
    pst = pypff.file()
    pst.open(pst_file)

    root = pst.get_root_folder()
    data = {
        'file': os.path.basename(pst_file),
        'folders': [],
        'messages': []
    }

    def process_folder(folder, path=""):
        folder_info = {
            'name': folder.get_name(),
            'path': path,
            'num_sub_folders': folder.get_number_of_sub_folders(),
            'num_messages': folder.get_number_of_sub_messages()
        }
        data['folders'].append(folder_info)

        # Process messages
        for i in range(folder.get_number_of_sub_messages()):
            message = folder.get_sub_message(i)
            msg_data = {
                'folder': path,
                'subject': message.get_subject(),
                'sender': message.get_sender_name(),
                'recipients': message.get_recipients(),
                'delivery_time': str(message.get_delivery_time()),
                'body': message.get_plain_text_body()
            }
            data['messages'].append(msg_data)

        # Process subfolders
        for i in range(folder.get_number_of_sub_folders()):
            subfolder = folder.get_sub_folder(i)
            new_path = f"{path}/{subfolder.get_name()}" if path else subfolder.get_name()
            process_folder(subfolder, new_path)

    process_folder(root)
    pst.close()

    # Write JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Successfully converted to {output_json}")
    print(f"  - Folders: {len(data['folders'])}")
    print(f"  - Messages: {len(data['messages'])}")
    return True

def convert_with_libratom(pst_file, output_json):
    """Convert PST using libratom library"""
    from libratom.lib.pff import PffArchive

    print(f"Opening PST file: {pst_file}")

    data = {
        'file': os.path.basename(pst_file),
        'folders': [],
        'messages': []
    }

    with PffArchive(pst_file) as archive:
        for message in archive.messages():
            msg_data = {
                'subject': message.subject,
                'sender': message.sender_name,
                'delivery_time': str(message.delivery_time) if message.delivery_time else None,
                'body': message.plain_text_body
            }
            data['messages'].append(msg_data)

    # Write JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Successfully converted to {output_json}")
    print(f"  - Messages: {len(data['messages'])}")
    return True

def main():
    pst_file = 'pzd/pzd.pst'
    output_json = 'pzd/pzd.json'
    temp_output_dir = 'pzd/pst_extracted'

    if not os.path.exists(pst_file):
        print(f"✗ PST file not found: {pst_file}")
        return 1

    print(f"PST to JSON Converter")
    print(f"=" * 60)
    print(f"Input:  {pst_file} ({os.path.getsize(pst_file) / 1024 / 1024:.1f} MB)")
    print(f"Output: {output_json}")
    print(f"=" * 60)

    # Method 1: Try readpst command-line tool
    if convert_with_readpst(pst_file, temp_output_dir):
        print("\n✓ PST extracted using readpst tool")
        print(f"Check extracted files in: {temp_output_dir}")
        return 0

    # Method 2: Try Python libraries
    if try_python_library(pst_file, output_json):
        return 0

    print("\n" + "=" * 60)
    print("✗ Failed to convert PST file")
    print("\nPossible solutions:")
    print("1. Install readpst tool:")
    print("   - Windows: Download libpst from https://www.five-ten-sg.com/libpst/")
    print("   - Linux: sudo apt-get install pst-utils")
    print("   - macOS: brew install libpst")
    print("\n2. Install Python library:")
    print("   pip install pypff-python")
    print("\n3. Use online converter or Outlook to export data")
    return 1

if __name__ == '__main__':
    sys.exit(main())
