"""
Test on a real DMP file to check if section 5.2 is actually being skipped.
"""

import sys
import os
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

if __name__ != '__main__':
    raise unittest.SkipTest('Manual diagnostic script')

from utils.extractor_v2 import DMPExtractor
import json

# Ask user for file path
print("Enter path to a DMP file (PDF or DOCX) to test section 5.2 extraction:")
print("Or press Enter to skip this test.")
file_path = input("> ").strip().strip('"')

if not file_path or not os.path.exists(file_path):
    print("No valid file provided. Test skipped.")
    sys.exit(0)

print(f"\nProcessing: {file_path}")
print("="*80)

# Extract
extractor = DMPExtractor()
result = extractor.process_file(file_path, 'outputs')

if not result['success']:
    print(f"ERROR: {result['message']}")
    sys.exit(1)

print(f"Extraction successful: {result['message']}")
print(f"Cache ID: {result['cache_id']}")

# Load cache
cache_path = os.path.join('outputs', 'cache', f"cache_{result['cache_id']}.json")
with open(cache_path, 'r', encoding='utf-8') as f:
    cache = json.load(f)

# Check section 5 subsections
print("\n" + "="*80)
print("SECTION 5 EXTRACTION RESULTS")
print("="*80)

for sid in ['5.1', '5.2', '5.3', '5.4']:
    section = cache.get(sid, {})
    paras = section.get('paragraphs', [])
    print(f"\nSection {sid}: {len(paras)} paragraphs")
    print(f"Question: {section.get('question', 'N/A')}")

    if paras:
        print(f"First paragraph ({len(paras[0])} chars):")
        print(f"  {paras[0][:200]}")
        if len(paras) > 1:
            print(f"Last paragraph ({len(paras[-1])} chars):")
            print(f"  {paras[-1][:200]}")
    else:
        print("  [EMPTY]")

# Check for common keywords in 5.2
if cache.get('5.2', {}).get('paragraphs'):
    text_5_2 = ' '.join(cache['5.2']['paragraphs'])
    keywords = ['repozytorium', 'repository', 'archive', 'archiwum', 'preservation', 'przechowywanie']
    found_keywords = [kw for kw in keywords if kw.lower() in text_5_2.lower()]
    print(f"\n5.2 content contains keywords: {found_keywords}")
else:
    print("\n[WARNING] Section 5.2 is EMPTY - checking other sections for its content...")

    # Check if 5.2 content leaked into 5.1
    if cache.get('5.1', {}).get('paragraphs'):
        text_5_1 = ' '.join(cache['5.1']['paragraphs'])
        keywords_5_2 = ['długotrwałego przechowywania', 'long-term', 'preservation', 'repozytorium', 'repository']
        found_in_5_1 = [kw for kw in keywords_5_2 if kw.lower() in text_5_1.lower()]
        if found_in_5_1:
            print(f"  -> 5.2 keywords found in 5.1: {found_in_5_1}")
            print(f"  -> This suggests 5.2 anchor was not found, and its content merged into 5.1")

    # Check if it's in 5.3
    if cache.get('5.3', {}).get('paragraphs'):
        text_5_3 = ' '.join(cache['5.3']['paragraphs'])
        keywords_5_2 = ['długotrwałego przechowywania', 'long-term', 'preservation']
        found_in_5_3 = [kw for kw in keywords_5_2 if kw.lower() in text_5_3.lower()]
        if found_in_5_3:
            print(f"  -> 5.2 keywords found in 5.3: {found_in_5_3}")
