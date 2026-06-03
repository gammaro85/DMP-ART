"""
test_v2_vs_v3_comparison.py — Compare extractor_v2 vs extractor_v3_separated

Tests the difference between:
- v2: Clean DURING slicing (per-section)
- v3: Slice FIRST, clean LATER (batch)

Expected outcome: IDENTICAL cleaned results, but v3 provides RAW slices for debugging
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.extractor_v2 import DMPExtractor as DMPExtractorV2
from utils.extractor_v3_separated import DMPExtractorSeparated as DMPExtractorV3


def compare_extractors(test_file_path: str):
    """
    Run both extractors on the same file and compare results.

    Args:
        test_file_path: Path to DMP file (PDF or DOCX)
    """
    print("=" * 80)
    print("COMPARISON: extractor_v2 vs extractor_v3_separated")
    print("=" * 80)
    print(f"\nTest file: {test_file_path}")
    print(f"File exists: {os.path.exists(test_file_path)}")

    if not os.path.exists(test_file_path):
        print(f"\n[ERROR] File not found: {test_file_path}")
        return

    # Create temporary output directories
    with tempfile.TemporaryDirectory() as tmpdir:

        # ─────────────────────────────────────────────────────────────────
        # RUN V2 (original - clean during slicing)
        # ─────────────────────────────────────────────────────────────────
        print("\n" + "-" * 80)
        print("[V2] RUNNING V2 (original: clean during slicing)")
        print("-" * 80)

        extractor_v2 = DMPExtractorV2()
        result_v2 = extractor_v2.process_file(test_file_path, tmpdir)

        print(f"\nV2 Result: {result_v2.get('success')}")
        print(f"V2 Message: {result_v2.get('message')}")

        cache_v2 = None
        if result_v2['success']:
            cache_id_v2 = result_v2['cache_id']
            cache_path_v2 = os.path.join(tmpdir, 'cache', f'cache_{cache_id_v2}.json')
            with open(cache_path_v2, encoding='utf-8') as f:
                cache_v2 = json.load(f)
            print(f"V2 Cache keys: {list(cache_v2.keys())}")

        # ─────────────────────────────────────────────────────────────────
        # RUN V3 (separated - slice first, clean later)
        # ─────────────────────────────────────────────────────────────────
        print("\n" + "-" * 80)
        print("[V3] RUNNING V3 (separated: slice first, clean later)")
        print("-" * 80)

        extractor_v3 = DMPExtractorV3(save_raw_slices=True)  # Enable RAW export
        result_v3 = extractor_v3.process_file(test_file_path, tmpdir)

        print(f"\nV3 Result: {result_v3.get('success')}")
        print(f"V3 Message: {result_v3.get('message')}")

        cache_v3 = None
        if result_v3['success']:
            cache_id_v3 = result_v3['cache_id']
            cache_path_v3 = os.path.join(tmpdir, 'cache', f'cache_{cache_id_v3}.json')
            with open(cache_path_v3, encoding='utf-8') as f:
                cache_v3 = json.load(f)
            print(f"V3 Cache keys: {list(cache_v3.keys())}")

        # ─────────────────────────────────────────────────────────────────
        # COMPARE RESULTS
        # ─────────────────────────────────────────────────────────────────
        print("\n" + "=" * 80)
        print("[RESULTS] COMPARISON RESULTS")
        print("=" * 80)

        if not cache_v2 or not cache_v3:
            print("\n[FAIL] Cannot compare - one or both extractors failed")
            return

        # Compare cleaned paragraphs (should be IDENTICAL)
        print("\n1. CLEANED PARAGRAPHS (should be identical):")
        print("-" * 80)

        all_match = True
        from utils.extractor_v2 import SECTION_ORDER

        for sid in SECTION_ORDER:
            para_v2 = cache_v2.get(sid, {}).get('paragraphs', [])
            para_v3 = cache_v3.get(sid, {}).get('paragraphs', [])

            if para_v2 == para_v3:
                status = "[OK] MATCH"
            else:
                status = "[FAIL] DIFFER"
                all_match = False

            print(f"{sid}: {status} (v2: {len(para_v2)} lines, v3: {len(para_v3)} lines)")

            # Show diff if different
            if para_v2 != para_v3:
                print(f"  V2 paragraphs: {para_v2[:2]}")  # First 2 lines
                print(f"  V3 paragraphs: {para_v3[:2]}")

        if all_match:
            print("\n[OK] ALL SECTIONS MATCH - Cleaning produces identical results!")
        else:
            print("\n[WARN] SOME SECTIONS DIFFER - Investigate!")

        # Check V3-specific features (RAW slices)
        print("\n2. V3 RAW SLICES (debugging feature):")
        print("-" * 80)

        if '_raw_sections' in cache_v3:
            raw_sections = cache_v3['_raw_sections']
            print(f"[OK] V3 exported {len(raw_sections)} raw sections for debugging")

            # Show example raw vs cleaned for section 1.1
            if '1.1' in raw_sections and '1.1' in cache_v3:
                print("\nExample: Section 1.1")
                print("  RAW (before cleaning):")
                for i, line in enumerate(raw_sections['1.1'][:3]):
                    print(f"    [{i}] {line[:80]}")

                print("\n  CLEANED (after cleaning):")
                for i, line in enumerate(cache_v3['1.1']['paragraphs'][:3]):
                    print(f"    [{i}] {line[:80]}")
        else:
            print("[FAIL] V3 did not export raw sections (save_raw_slices=False?)")

        # Check if sections have raw_blocks field
        print("\n3. PER-SECTION RAW BLOCKS (debugging feature):")
        print("-" * 80)

        sections_with_raw = [
            sid for sid in SECTION_ORDER
            if 'raw_blocks' in cache_v3.get(sid, {})
        ]

        if sections_with_raw:
            print(f"[OK] V3 includes raw_blocks in {len(sections_with_raw)} sections")
            print(f"   Sections: {sections_with_raw[:5]}")
        else:
            print("[FAIL] V3 does not include per-section raw_blocks")

        # Memory comparison (rough estimate)
        print("\n4. CACHE SIZE COMPARISON:")
        print("-" * 80)

        size_v2 = len(json.dumps(cache_v2, ensure_ascii=False))
        size_v3 = len(json.dumps(cache_v3, ensure_ascii=False))

        print(f"V2 cache size: {size_v2:,} bytes")
        print(f"V3 cache size: {size_v3:,} bytes (with raw data)")
        print(f"Difference: +{size_v3 - size_v2:,} bytes ({(size_v3/size_v2 - 1)*100:.1f}% larger)")

        print("\n" + "=" * 80)
        print("DONE")
        print("=" * 80)


def main():
    """Run comparison on test file or user-provided file."""

    if len(sys.argv) > 1:
        # Use file from command line
        test_file = sys.argv[1]
    else:
        # Look for test file in fixtures
        fixtures_dir = Path(__file__).parent / 'fixtures'

        # Try to find any DMP PDF/DOCX in fixtures
        candidates = list(fixtures_dir.glob('*.pdf')) + list(fixtures_dir.glob('*.docx'))

        if candidates:
            test_file = str(candidates[0])
            print(f"Using test file from fixtures: {test_file}")
        else:
            print("No test files found in fixtures/")
            print("Usage: python test_v2_vs_v3_comparison.py <path_to_dmp_file>")
            print("\nOr place a DMP file in tests/fixtures/")
            return

    compare_extractors(test_file)


if __name__ == '__main__':
    main()
