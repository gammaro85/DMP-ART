"""
Test script for enhanced scanned PDF detection
"""
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from utils.extractor import DMPExtractor

def test_garbled_text_detection():
    """Test if garbled text is detected correctly"""

    # Simulate garbled text extraction (like from the user's PDF)
    garbled_text = "ϭ͘KƉŝƐĚĂŶǇĐŚŽƌĂǌƉŽǌǇƐŬŝǁĂŶŝĞůƵďƉŽŶŽǁŶĞǁǇŬŽƌǌǇƐƚĂŶŝĞĚŽƐƚħƉŶǇĐŚĚĂŶǇĐŚ" * 10

    # Count ASCII chars
    ascii_chars = sum(1 for c in garbled_text if 32 <= ord(c) <= 126)
    ascii_ratio = ascii_chars / len(garbled_text) if len(garbled_text) > 0 else 0

    print("=" * 80)
    print("GARBLED TEXT DETECTION TEST")
    print("=" * 80)
    print(f"\nText sample: {garbled_text[:100]}...")
    print(f"Total characters: {len(garbled_text)}")
    print(f"ASCII characters: {ascii_chars}")
    print(f"ASCII ratio: {ascii_ratio:.1%}")
    print(f"\nWould be detected as garbled: {ascii_ratio < 0.5 and len(garbled_text) > 100}")

    # Test with normal text
    normal_text = "PLAN ZARZĄDZANIA DANYMI 1. Opis danych oraz pozyskiwanie danych" * 10
    ascii_chars_normal = sum(1 for c in normal_text if 32 <= ord(c) <= 126)
    ascii_ratio_normal = ascii_chars_normal / len(normal_text) if len(normal_text) > 0 else 0

    print("\n" + "=" * 80)
    print("NORMAL TEXT TEST")
    print("=" * 80)
    print(f"\nText sample: {normal_text[:100]}...")
    print(f"Total characters: {len(normal_text)}")
    print(f"ASCII characters: {ascii_chars_normal}")
    print(f"ASCII ratio: {ascii_ratio_normal:.1%}")
    print(f"\nWould be detected as garbled: {ascii_ratio_normal < 0.5 and len(normal_text) > 100}")

    # Test word detection
    print("\n" + "=" * 80)
    print("WORD DETECTION TEST")
    print("=" * 80)

    common_words = ['the', 'and', 'data', 'plan', 'management', 'project',
                   'badania', 'danych', 'plan', 'projektu', 'oraz']

    garbled_words_found = sum(1 for word in common_words if word in garbled_text.lower())
    normal_words_found = sum(1 for word in common_words if word in normal_text.lower())

    print(f"Garbled text - common words found: {garbled_words_found}")
    print(f"Normal text - common words found: {normal_words_found}")

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_garbled_text_detection()
