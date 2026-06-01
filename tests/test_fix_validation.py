"""
Validation test for MIN_FIRST_BLOCK = 0.60 fix.

This test ensures that:
1. False positive matches (3.1 matching 5.2 content) are prevented
2. Real anchors (with high scores) are still found correctly
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.extractor_v2 import AnchorMatcher, TextBlock, SECTION_ORDER
import json

# Load anchor configuration
config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'dmp_anchors.json')
with open(config_path, 'r', encoding='utf-8') as f:
    anchors_cfg = json.load(f)

# Test data: section 5 from user's report (with proper Polish characters)
test_text = """
5. Udostępnianie i długotrwałe przechowywanie danych

Sposób i termin udostępnienia danych. Ewentualne ograniczenia w udostępnianiu danych lub przyczyny embarga

The data set will be shared via MOST Wiedzy Open Research Catalog. If needed the part of the data will be published in scientific journals, which may also require raw data publication. Data will be systematically uploaded to the MOST Wiedzy repository in accordance with the publication dates of the articles that are derived from this data.

Only new data, generated during this project, will be published in the MOST Wiedzy repository.

Sposób wyboru danych przeznaczonych do przechowania oraz miejsce długotrwałego przechowywania danych (np. repozytorium lub archiwum danych)

The MOST Wiedzy Open Research Data Catalog will be the main data repository. The repository is CoreTrustSeal certified, which means that it has established good preservation and dissemination practices The data provided in the repository will fulfill FAIR requirements. During the research team meetings will discuss the gathered data and will decide on what part of research data is worth being included in repository and whether it is self-explanatory in its current form or will need an additional processing. Moreover, all data will be stored for at least 10 years after the project is finished and access to them will be possible only with the PI consent.

Metody lub narzędzia programowe umożliwiające dostęp do danych i korzystanie z danych

The shared data will be in open formats, so there will be no need for specialized software by recipients.

Sposób zapewniający stosowanie unikalnego i trwałego identyfikatora (np. cyfrowego identyfikatora obiektu (DOI)) dla każdego zestawu danych

The datasets provided in the repository will have the DOI assigned.
"""

# Convert to blocks
lines = [line.strip() for line in test_text.strip().split('\n') if line.strip()]
blocks = [TextBlock(text, False, False, 'paragraph', 0, False) for text in lines]

print("="*80)
print("TEST: MIN_FIRST_BLOCK = 0.60 Fix Validation")
print("="*80)

# Test boundary detection
matcher = AnchorMatcher(anchors_cfg.get('sections', {}))
boundaries = matcher.find_boundaries(blocks)

# Expected sections for this test data
expected_sections = ['5.1', '5.2', '5.3', '5.4']
found_sections = [sid for sid in expected_sections if sid in boundaries]
missing_sections = [sid for sid in expected_sections if sid not in boundaries]

# Check for false positives (3.1 should NOT be found in this text)
false_positives = [sid for sid in boundaries.keys() if not sid.startswith('5')]

print(f"\nExpected sections: {expected_sections}")
print(f"Found sections:    {found_sections}")
print(f"Missing sections:  {missing_sections if missing_sections else 'None'}")
print(f"False positives:   {false_positives if false_positives else 'None'}")

# Detailed results
print("\n" + "="*80)
print("BOUNDARY DETECTION DETAILS")
print("="*80)
for sid in SECTION_ORDER:
    if sid in boundaries:
        start_idx, win_size = boundaries[sid]
        print(f"{sid}: blocks {start_idx}-{start_idx+win_size-1} (window={win_size})")
        print(f"     Text: {blocks[start_idx].text[:70]}...")

# Validation
print("\n" + "="*80)
print("VALIDATION RESULTS")
print("="*80)

all_tests_passed = True

# Test 1: All section 5 subsections should be found
if len(found_sections) == len(expected_sections):
    print("[PASS] All section 5 subsections found")
else:
    print(f"[FAIL] Missing sections: {missing_sections}")
    all_tests_passed = False

# Test 2: No false positives (3.1, 3.2, etc. should NOT be found)
if not false_positives:
    print("[PASS] No false positives (3.1 not matched to 5.2 content)")
else:
    print(f"[FAIL] False positives detected: {false_positives}")
    all_tests_passed = False

# Test 3: Section 5.2 should be found and contain expected keywords
if '5.2' in boundaries:
    start_idx, _ = boundaries['5.2']
    # Check for either Polish or simplified characters
    if 'wyboru' in blocks[start_idx].text.lower() and ('przechow' in blocks[start_idx].text.lower()):
        print("[PASS] Section 5.2 anchor correctly identified")
    else:
        print(f"[FAIL] Section 5.2 anchor at wrong block: {blocks[start_idx].text[:50]}")
        all_tests_passed = False
else:
    print("[FAIL] Section 5.2 not found")
    all_tests_passed = False

print("\n" + "="*80)
if all_tests_passed:
    print("ALL TESTS PASSED")
    print("="*80)
    sys.exit(0)
else:
    print("SOME TESTS FAILED")
    print("="*80)
    sys.exit(1)
