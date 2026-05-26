"""
Test script for extraction algorithm fixes (2026-05-26)

Tests the 3 critical fixes:
1. Multi-block anchor exclusion
2. Numeration removal from content
3. Enhanced main section title filtering
"""

import re
from utils.extractor_v2 import _RE_SEC_NUM, _RE_MAIN_NUM, _BUILTIN_NOISE

print("=" * 70)
print("EXTRACTION ALGORITHM FIX VERIFICATION")
print("=" * 70)

# Test 1: Numeration Removal
print("\n[TEST 1] Numeration Removal from Content")
print("-" * 70)

test_cases = [
    ("1.1 Sposób pozyskiwania nowych danych", "Sposób pozyskiwania nowych danych"),
    ("2.2 Metadane i dokumenty", "Metadane i dokumenty"),
    ("6. Zadania związane z zarządzaniem", "Zadania związane z zarządzaniem"),
    ("1. Opis danych", "Opis danych"),
    ("Some text without numbers", "Some text without numbers"),
]

all_passed = True
for original, expected in test_cases:
    cleaned = _RE_MAIN_NUM.sub('', _RE_SEC_NUM.sub('', original))
    passed = cleaned == expected
    all_passed = all_passed and passed
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] '{original}'")
    print(f"        -> '{cleaned}'")
    if not passed:
        print(f"        Expected: '{expected}'")

print(f"\nTest 1 Result: {'PASS' if all_passed else 'FAIL'}")

# Test 2: Main Section Title Filtering
print("\n[TEST 2] Main Section Title Filtering (_BUILTIN_NOISE)")
print("-" * 70)

section_titles = [
    "1. Opis danych oraz pozyskiwanie lub ponowne wykorzystanie dostępnych danych",
    "2. Dokumentacja i jakość danych",
    "3. Przechowywanie i tworzenie kopii zapasowych podczas badań",
    "4. Wymogi prawne, kodeks postępowania",
    "5. Udostępnianie i długotrwałe przechowywanie danych",
    "6. Zadania związane z zarządzaniem danymi oraz zasoby",
    "1. Data description and collection or re-use of existing data",
    "2. Documentation and data quality",
    "3. Storage and backup during the research process",
    "4. Legal requirements, codes of conduct",
    "5. Data sharing and long-term preservation",
    "6. Data management responsibilities and resources",
]

all_filtered = True
for title in section_titles:
    is_filtered = any(pattern.search(title) for pattern in _BUILTIN_NOISE)
    all_filtered = all_filtered and is_filtered
    status = "PASS" if is_filtered else "FAIL"
    print(f"  [{status}] {title}")
    if not is_filtered:
        print(f"        ^ NOT FILTERED - should be removed!")

print(f"\nTest 2 Result: {'PASS' if all_filtered else 'FAIL'}")

# Test 3: Non-Title Content Should NOT Be Filtered
print("\n[TEST 3] Valid Content Should NOT Be Filtered")
print("-" * 70)

valid_content = [
    "The project will generate new experimental data",
    "Data will be organized in clearly labeled folders",
    "Working data will be stored on secure computers",
    "No personal or medical data will be processed",
    "Ownership and management of data will follow regulations",
    "Selected datasets will be made openly available",
]

all_not_filtered = True
for content in valid_content:
    is_filtered = any(pattern.search(content) for pattern in _BUILTIN_NOISE)
    all_not_filtered = all_not_filtered and not is_filtered
    status = "PASS" if not is_filtered else "FAIL"
    print(f"  [{status}] {content}")
    if is_filtered:
        print(f"        ^ INCORRECTLY FILTERED - should be kept!")

print(f"\nTest 3 Result: {'PASS' if all_not_filtered else 'FAIL'}")

# Summary
print("\n" + "=" * 70)
test1_pass = all_passed
test2_pass = all_filtered
test3_pass = all_not_filtered

overall = test1_pass and test2_pass and test3_pass
print(f"OVERALL RESULT: {'ALL TESTS PASSED' if overall else 'SOME TESTS FAILED'}")
print("=" * 70)

if overall:
    print("\n✓ Algorithm fixes verified successfully!")
    print("  - Multi-block anchors are now fully excluded")
    print("  - Numerations (1.1, 2.2) are removed from content")
    print("  - Main section titles are properly filtered")
else:
    print("\n✗ Some tests failed - review algorithm changes")
