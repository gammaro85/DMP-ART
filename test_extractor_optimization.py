#!/usr/bin/env python3
"""
Comprehensive test suite for DMP Extractor optimization
Tests performance, accuracy, and edge cases
"""
import unittest
import time
import os
import json
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.extractor import DMPExtractor


class TestExtractorPerformance(unittest.TestCase):
    """Performance benchmarks for extractor methods"""

    @classmethod
    def setUpClass(cls):
        """Initialize extractor once for all tests"""
        cls.extractor = DMPExtractor()
        cls.sample_texts = {
            'section_polish': "1. Opis danych oraz pozyskiwanie lub ponowne wykorzystanie istniejących danych",
            'section_english': "1. Data description and collection or re-use of existing data",
            'subsection_polish': "Sposób pozyskiwania i opracowywania nowych danych i/lub ponownego wykorzystania dostępnych danych:",
            'subsection_english': "How will new data be collected or produced and/or how will existing data be re-used?",
            'header': "OSF, OPUS-29 Strona 41 ID: 651313, 2025-06-09 11:29:38",
            'content': "This research will collect survey data from 500 participants using validated questionnaires."
        }

    def test_text_similarity_performance(self):
        """Benchmark text similarity calculation"""
        text1 = "How will new data be collected or produced and/or how will existing data be re-used?"
        text2 = "Sposób pozyskiwania i opracowywania nowych danych"

        iterations = 1000
        start_time = time.time()

        for _ in range(iterations):
            self.extractor._text_similarity(text1, text2)

        elapsed = time.time() - start_time
        avg_time = (elapsed / iterations) * 1000  # Convert to ms

        print(f"\n[PERF] Text similarity: {avg_time:.4f}ms per call ({iterations} iterations)")
        self.assertLess(avg_time, 1.0, "Text similarity should be < 1ms per call")

    def test_section_detection_performance(self):
        """Benchmark section detection"""
        test_texts = [
            "1. Opis danych oraz pozyskiwanie",
            "2. Dokumentacja i jakość danych",
            "BOLD:3. Przechowywanie i tworzenie kopii zapasowych",
            "Regular content that is not a section"
        ]

        iterations = 500
        start_time = time.time()

        for _ in range(iterations):
            for text in test_texts:
                self.extractor.detect_section_from_text(text, is_pdf=False)

        elapsed = time.time() - start_time
        avg_time = (elapsed / (iterations * len(test_texts))) * 1000

        print(f"[PERF] Section detection: {avg_time:.4f}ms per call ({iterations * len(test_texts)} calls)")
        self.assertLess(avg_time, 5.0, "Section detection should be < 5ms per call")

    def test_subsection_detection_performance(self):
        """Benchmark subsection detection"""
        section = "1. Data description and collection or re-use of existing data"
        test_texts = [
            "How will new data be collected or produced?",
            "What data will be collected?",
            "Sposób pozyskiwania i opracowywania nowych danych",
            "Regular content not a subsection"
        ]

        iterations = 500
        start_time = time.time()

        for _ in range(iterations):
            for text in test_texts:
                self.extractor.detect_subsection_from_text(text, section, is_pdf=False)

        elapsed = time.time() - start_time
        avg_time = (elapsed / (iterations * len(test_texts))) * 1000

        print(f"[PERF] Subsection detection: {avg_time:.4f}ms per call ({iterations * len(test_texts)} calls)")
        self.assertLess(avg_time, 5.0, "Subsection detection should be < 5ms per call")

    def test_skip_text_performance(self):
        """Benchmark header/footer filtering"""
        test_texts = [
            "OSF, OPUS-29 Strona 41 ID: 651313, 2025-06-09 11:29:38",
            "Strona 5",
            "This is valid content about research data",
            "2024-12-01 09:15:22",
            "Some more valid content with project ID 123456"
        ]

        iterations = 1000
        start_time = time.time()

        for _ in range(iterations):
            for text in test_texts:
                self.extractor.should_skip_text(text, is_pdf=True)

        elapsed = time.time() - start_time
        avg_time = (elapsed / (iterations * len(test_texts))) * 1000

        print(f"[PERF] Skip text filtering: {avg_time:.4f}ms per call ({iterations * len(test_texts)} calls)")
        self.assertLess(avg_time, 2.0, "Skip text filtering should be < 2ms per call")


class TestExtractorAccuracy(unittest.TestCase):
    """Accuracy tests for extraction logic"""

    def setUp(self):
        """Initialize extractor for each test"""
        self.extractor = DMPExtractor()

    def test_section_mapping_completeness(self):
        """Verify all 6 sections are mapped"""
        self.assertEqual(len(self.extractor.section_mapping), 6,
                        "Should have 6 Polish-English section mappings")

    def test_subsection_mapping_completeness(self):
        """Verify all 14 subsections are mapped"""
        # Count unique English subsections
        unique_subsections = set(self.extractor.subsection_mapping.values())
        self.assertEqual(len(unique_subsections), 14,
                        "Should have 14 unique subsection mappings")

    def test_section_detection_polish(self):
        """Test Polish section detection"""
        test_cases = [
            ("1. Opis danych oraz pozyskiwanie", "1. Data description and collection or re-use of existing data"),
            ("2. Dokumentacja i jakość danych", "2. Documentation and data quality"),
            ("BOLD:3. Przechowywanie i tworzenie kopii zapasowych", "3. Storage and backup during the research process"),
        ]

        for polish_text, expected_section in test_cases:
            detected = self.extractor.detect_section_from_text(polish_text, is_pdf=False)
            self.assertEqual(detected, expected_section,
                           f"Failed to detect section from: {polish_text}")

    def test_section_detection_english(self):
        """Test English section detection"""
        test_cases = [
            "1. Data description and collection or re-use of existing data",
            "2. Documentation and data quality",
            "3. Storage and backup during the research process"
        ]

        for text in test_cases:
            detected = self.extractor.detect_section_from_text(text, is_pdf=False)
            self.assertEqual(detected, text,
                           f"Failed to detect English section: {text}")

    def test_subsection_detection_polish(self):
        """Test Polish subsection detection"""
        section = "1. Data description and collection or re-use of existing data"
        test_cases = [
            ("Sposób pozyskiwania i opracowywania nowych danych i/lub ponownego wykorzystania dostępnych danych",
             "How will new data be collected or produced and/or how will existing data be re-used?"),
            ("Pozyskiwane lub opracowywane dane (np. rodzaj, format, ilość)",
             "What data (for example the types, formats, and volumes) will be collected or produced?"),
        ]

        for polish_text, expected_subsection in test_cases:
            detected = self.extractor.detect_subsection_from_text(polish_text, section, is_pdf=False)
            self.assertEqual(detected, expected_subsection,
                           f"Failed to detect subsection from: {polish_text}")

    def test_header_footer_detection(self):
        """Test that headers/footers are correctly identified"""
        test_cases_skip = [
            "OSF, OPUS-29 Strona 41 ID: 651313, 2025-06-09 11:29:38",
            "Strona 5",
            "Page 10",
            "ID: 123456",
            "[wydruk roboczy]",
            "2024-12-01 09:15:22"
        ]

        test_cases_keep = [
            "This research will collect survey data from participants.",
            "Data will be stored in secure repositories.",
            "The project involves analysis of existing datasets."
        ]

        for text in test_cases_skip:
            self.assertTrue(self.extractor.should_skip_text(text, is_pdf=True),
                          f"Should skip header/footer: {text}")

        for text in test_cases_keep:
            self.assertFalse(self.extractor.should_skip_text(text, is_pdf=True),
                           f"Should NOT skip content: {text}")

    def test_text_similarity_exact_match(self):
        """Test similarity for identical strings"""
        similarity = self.extractor._text_similarity("test string", "test string")
        self.assertEqual(similarity, 1.0, "Identical strings should have similarity of 1.0")

    def test_text_similarity_no_match(self):
        """Test similarity for completely different strings"""
        similarity = self.extractor._text_similarity("abc", "xyz")
        self.assertEqual(similarity, 0.0, "Completely different strings should have similarity of 0.0")

    def test_text_similarity_partial_match(self):
        """Test similarity for partially matching strings"""
        similarity = self.extractor._text_similarity(
            "How will data be collected",
            "How will new data be collected or produced"
        )
        self.assertGreater(similarity, 0.5, "Partially matching strings should have high similarity")

    def test_clean_markup(self):
        """Test markup cleaning"""
        test_cases = [
            ("[text]{.underline}", "text"),
            ("**bold text**", "bold text"),
            ("__underlined__", "underlined"),
            ("{.mark}marked{.mark}", "marked"),
        ]

        for input_text, expected_output in test_cases:
            cleaned = self.extractor.clean_markup(input_text)
            self.assertIn(expected_output, cleaned,
                         f"Markup cleaning failed for: {input_text}")

    def test_metadata_extraction_from_filename(self):
        """Test metadata extraction from filenames"""
        test_cases = [
            ("DMP_Kowalski_J_OPUS_25_161125.docx", {
                'competition_name': 'OPUS',
                'competition_edition': '25',
                'researcher_surname': 'Kowalski'
            }),
            ("PRELUDIUM2025_plan.docx", {
                'competition_name': 'PRELUDIUM',
                'competition_edition': '2025'
            }),
        ]

        for filename, expected_fields in test_cases:
            metadata = self.extractor._extract_from_filename(filename)

            for field, expected_value in expected_fields.items():
                self.assertEqual(metadata.get(field), expected_value,
                               f"Failed to extract {field} from {filename}")


class TestExtractorIntegration(unittest.TestCase):
    """Integration tests with sample files"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.extractor = DMPExtractor()
        cls.test_dir = os.path.join(os.path.dirname(__file__), 'pzd')
        cls.output_dir = os.path.join(os.path.dirname(__file__), 'test_outputs')
        os.makedirs(cls.output_dir, exist_ok=True)

    def test_docx_file_validation(self):
        """Test DOCX file validation"""
        # Find a valid DOCX file
        for filename in os.listdir(self.test_dir):
            if filename.endswith('.docx'):
                file_path = os.path.join(self.test_dir, filename)
                is_valid, message = self.extractor.validate_docx_file(file_path)

                if is_valid:
                    print(f"\n[OK] Valid DOCX: {filename}")
                    self.assertTrue(is_valid, f"Expected {filename} to be valid")
                    break

    def test_full_extraction_docx(self):
        """Test full extraction process on a DOCX file"""
        # Find first DOCX file
        test_file = None
        for filename in os.listdir(self.test_dir):
            if filename.endswith('.docx'):
                test_file = os.path.join(self.test_dir, filename)
                break

        if not test_file:
            self.skipTest("No DOCX test files found")

        print(f"\n[TEST] Testing full extraction: {os.path.basename(test_file)}")

        start_time = time.time()
        result = self.extractor.process_file(test_file, self.output_dir)
        elapsed = time.time() - start_time

        print(f"[TIME]  Processing time: {elapsed:.2f}s")

        self.assertTrue(result.get('success'),
                       f"Extraction failed: {result.get('message')}")

        # Verify cache file was created
        if result.get('cache_id'):
            cache_file = os.path.join(self.output_dir, f"cache_{result['cache_id']}.json")
            self.assertTrue(os.path.exists(cache_file), "Cache file should be created")

            # Analyze extraction quality
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            sections_with_content = sum(
                1 for key, value in cache_data.items()
                if isinstance(value, dict) and value.get('paragraphs')
            )

            print(f"[PERF] Sections with content: {sections_with_content}/14")
            print(f"[PERF] Unconnected items: {len(cache_data.get('_unconnected_text', []))}")

            # Should extract at least some content
            self.assertGreater(sections_with_content, 0,
                             "Should extract content for at least one section")


class TestExtractorEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def setUp(self):
        """Initialize extractor for each test"""
        self.extractor = DMPExtractor()

    def test_empty_text_similarity(self):
        """Test similarity with empty strings"""
        similarity = self.extractor._text_similarity("", "test")
        self.assertEqual(similarity, 0.0, "Empty string should have 0 similarity")

        similarity = self.extractor._text_similarity("test", "")
        self.assertEqual(similarity, 0.0, "Empty string should have 0 similarity")

    def test_section_detection_with_none(self):
        """Test section detection with None current section"""
        result = self.extractor.detect_subsection_from_text("some text", None, is_pdf=False)
        self.assertIsNone(result, "Should return None when no current section")

    def test_very_long_text_performance(self):
        """Test performance with very long text"""
        long_text = "This is a test sentence. " * 1000  # ~5000 words

        start_time = time.time()
        self.extractor.should_skip_text(long_text, is_pdf=True)
        elapsed = time.time() - start_time

        print(f"\n[PERF] Long text filtering ({len(long_text)} chars): {elapsed*1000:.2f}ms")
        self.assertLess(elapsed, 0.1, "Should process long text in < 100ms")

    def test_special_characters_in_text(self):
        """Test handling of special characters"""
        test_texts = [
            "Dane będą przechowywane w bezpiecznym repozytorium",
            "Αυτή είναι ελληνική",  # Greek
            "数据管理计划",  # Chinese
            "Test with emojis",
        ]

        for text in test_texts:
            # Should not crash
            try:
                self.extractor.detect_section_from_text(text, is_pdf=False)
                self.extractor.clean_markup(text)
            except Exception as e:
                self.fail(f"Failed to handle special characters in: {text}\nError: {e}")


def run_performance_suite():
    """Run performance tests and generate report"""
    print("="*80)
    print("DMP EXTRACTOR: PERFORMANCE & OPTIMIZATION TEST SUITE")
    print("="*80)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestExtractorPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestExtractorAccuracy))
    suite.addTests(loader.loadTestsFromTestCase(TestExtractorIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestExtractorEdgeCases))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Generate report
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"[OK] Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"[FAIL] Failed: {len(result.failures)}")
    print(f"[WARN]  Errors: {len(result.errors)}")

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_performance_suite()
    sys.exit(0 if success else 1)
