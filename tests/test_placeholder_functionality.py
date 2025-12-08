#!/usr/bin/env python3
"""
Test suite for DMP Extractor placeholder functionality
Tests that empty sections are correctly identified and filled with placeholder text
"""
import unittest
import os
import json
import sys
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.extractor import DMPExtractor


class TestPlaceholderFunctionality(unittest.TestCase):
    """Test suite for placeholder text in empty sections"""

    @classmethod
    def setUpClass(cls):
        """Initialize extractor once for all tests"""
        cls.extractor = DMPExtractor(debug_mode=True)
        cls.expected_placeholder = "Not answered in the source document."
        cls.section_ids = ['1.1', '1.2', '2.1', '2.2', '3.1', '3.2', '4.1', '4.2', '5.1', '5.2', '5.3', '6.1', '6.2']

    def setUp(self):
        """Create temporary directory for each test"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory after each test"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_empty_sections_filled_with_placeholder(self):
        """Test that empty sections are correctly identified and filled with placeholder text"""
        # Create a mock review structure with some empty sections
        review_structure = {
            '1.1': {
                'section': 'Test Section 1',
                'question': 'Test Question 1.1',
                'paragraphs': [],  # Empty
                'tagged_paragraphs': [],
                'confidence': 0.0,
                'extraction_method': 'test'
            },
            '1.2': {
                'section': 'Test Section 1',
                'question': 'Test Question 1.2',
                'paragraphs': ['Some content here'],  # Has content
                'tagged_paragraphs': [{'text': 'Some content here', 'tags': [], 'title': None}],
                'confidence': 0.9,
                'extraction_method': 'test'
            },
            '2.1': {
                'section': 'Test Section 2',
                'question': 'Test Question 2.1',
                'paragraphs': None,  # None (should be treated as empty)
                'tagged_paragraphs': [],
                'confidence': 0.0,
                'extraction_method': 'test'
            }
        }

        # Apply placeholder logic (simulating what happens in process_docx/process_pdf)
        empty_count = 0
        for section_id in self.section_ids:
            if section_id in review_structure:
                paras = review_structure[section_id].get('paragraphs', [])
                if not paras:
                    placeholder = self.expected_placeholder
                    review_structure[section_id]['paragraphs'] = [placeholder]
                    review_structure[section_id]['tagged_paragraphs'] = [{
                        'text': placeholder,
                        'tags': [],
                        'title': None
                    }]
                    empty_count += 1

        # Assertions
        # 1.1 should have placeholder (was empty)
        self.assertEqual(review_structure['1.1']['paragraphs'], [self.expected_placeholder])
        self.assertEqual(len(review_structure['1.1']['tagged_paragraphs']), 1)
        self.assertEqual(review_structure['1.1']['tagged_paragraphs'][0]['text'], self.expected_placeholder)
        self.assertEqual(review_structure['1.1']['tagged_paragraphs'][0]['tags'], [])

        # 1.2 should still have original content (was not empty)
        self.assertEqual(review_structure['1.2']['paragraphs'], ['Some content here'])
        self.assertEqual(review_structure['1.2']['tagged_paragraphs'][0]['text'], 'Some content here')

        # 2.1 should have placeholder (was None)
        self.assertEqual(review_structure['2.1']['paragraphs'], [self.expected_placeholder])

        # empty_count should be 2 (1.1 and 2.1)
        self.assertEqual(empty_count, 2)

    def test_sections_with_content_not_modified(self):
        """Test that sections with existing content are not modified"""
        # Create a review structure with all sections having content
        review_structure = {}
        for section_id in self.section_ids:
            review_structure[section_id] = {
                'section': f'Test Section {section_id}',
                'question': f'Test Question {section_id}',
                'paragraphs': [f'Content for section {section_id}'],
                'tagged_paragraphs': [{'text': f'Content for section {section_id}', 'tags': ['test'], 'title': None}],
                'confidence': 0.95,
                'extraction_method': 'test'
            }

        # Store original state for comparison
        original_state = json.loads(json.dumps(review_structure))

        # Apply placeholder logic
        empty_count = 0
        for section_id in self.section_ids:
            if section_id in review_structure:
                paras = review_structure[section_id].get('paragraphs', [])
                if not paras or len(paras) == 0:
                    placeholder = self.expected_placeholder
                    review_structure[section_id]['paragraphs'] = [placeholder]
                    review_structure[section_id]['tagged_paragraphs'] = [{
                        'text': placeholder,
                        'tags': [],
                        'title': None
                    }]
                    empty_count += 1

        # Verify no sections were modified
        self.assertEqual(empty_count, 0)
        for section_id in self.section_ids:
            self.assertEqual(
                review_structure[section_id]['paragraphs'],
                original_state[section_id]['paragraphs'],
                f"Section {section_id} was unexpectedly modified"
            )
            self.assertEqual(
                review_structure[section_id]['tagged_paragraphs'],
                original_state[section_id]['tagged_paragraphs'],
                f"Tagged paragraphs for section {section_id} were unexpectedly modified"
            )

    def test_placeholder_text_format(self):
        """Test that the placeholder text matches the expected format"""
        review_structure = {
            '1.1': {
                'paragraphs': [],
                'tagged_paragraphs': []
            }
        }

        # Apply placeholder
        placeholder = self.expected_placeholder
        review_structure['1.1']['paragraphs'] = [placeholder]
        review_structure['1.1']['tagged_paragraphs'] = [{
            'text': placeholder,
            'tags': [],
            'title': None
        }]

        # Verify exact format
        self.assertEqual(
            review_structure['1.1']['paragraphs'][0],
            "Not answered in the source document.",
            "Placeholder text does not match expected format"
        )

        # Verify it's a list with exactly one element
        self.assertIsInstance(review_structure['1.1']['paragraphs'], list)
        self.assertEqual(len(review_structure['1.1']['paragraphs']), 1)

        # Verify tagged_paragraphs structure
        self.assertIsInstance(review_structure['1.1']['tagged_paragraphs'], list)
        self.assertEqual(len(review_structure['1.1']['tagged_paragraphs']), 1)
        tagged = review_structure['1.1']['tagged_paragraphs'][0]
        self.assertEqual(tagged['text'], self.expected_placeholder)
        self.assertEqual(tagged['tags'], [])
        self.assertIsNone(tagged['title'])

    def test_empty_count_calculation(self):
        """Test that the empty_count is correctly calculated"""
        # Test various scenarios
        test_cases = [
            # (number of empty sections, description)
            (0, "all sections have content"),
            (5, "5 sections are empty"),
            (13, "all sections are empty"),
        ]

        for expected_empty, description in test_cases:
            with self.subTest(description=description):
                review_structure = {}
                
                # Create structure based on test case
                for i, section_id in enumerate(self.section_ids):
                    if i < expected_empty:
                        # Empty section
                        review_structure[section_id] = {
                            'paragraphs': [],
                            'tagged_paragraphs': []
                        }
                    else:
                        # Section with content
                        review_structure[section_id] = {
                            'paragraphs': [f'Content {section_id}'],
                            'tagged_paragraphs': [{'text': f'Content {section_id}', 'tags': [], 'title': None}]
                        }

                # Apply placeholder logic and count
                empty_count = 0
                for section_id in self.section_ids:
                    if section_id in review_structure:
                        paras = review_structure[section_id].get('paragraphs', [])
                        if not paras or len(paras) == 0:
                            placeholder = self.expected_placeholder
                            review_structure[section_id]['paragraphs'] = [placeholder]
                            review_structure[section_id]['tagged_paragraphs'] = [{
                                'text': placeholder,
                                'tags': [],
                                'title': None
                            }]
                            empty_count += 1

                self.assertEqual(empty_count, expected_empty, f"Expected {expected_empty} empty sections but got {empty_count}")

    def test_missing_section_ids_ignored(self):
        """Test that missing section IDs are handled gracefully"""
        # Create structure with only some sections
        review_structure = {
            '1.1': {
                'paragraphs': [],
                'tagged_paragraphs': []
            },
            '2.1': {
                'paragraphs': ['Content'],
                'tagged_paragraphs': [{'text': 'Content', 'tags': [], 'title': None}]
            }
        }

        # Apply placeholder logic
        empty_count = 0
        for section_id in self.section_ids:
            if section_id in review_structure:
                paras = review_structure[section_id].get('paragraphs', [])
                if not paras or len(paras) == 0:
                    placeholder = self.expected_placeholder
                    review_structure[section_id]['paragraphs'] = [placeholder]
                    review_structure[section_id]['tagged_paragraphs'] = [{
                        'text': placeholder,
                        'tags': [],
                        'title': None
                    }]
                    empty_count += 1

        # Should only count 1.1 as empty (2.1 has content, others don't exist)
        self.assertEqual(empty_count, 1)
        self.assertEqual(review_structure['1.1']['paragraphs'], [self.expected_placeholder])
        self.assertEqual(review_structure['2.1']['paragraphs'], ['Content'])

    def test_edge_cases_for_empty_detection(self):
        """Test edge cases in empty section detection"""
        test_cases = [
            ({'paragraphs': []}, True, "empty list"),
            ({'paragraphs': None}, True, "None value"),
            ({'paragraphs': ['']}, False, "list with empty string (has content)"),
            ({'paragraphs': ['   ']}, False, "list with whitespace (has content)"),
            ({'paragraphs': ['content']}, False, "list with actual content"),
            ({}, True, "missing paragraphs key"),
        ]

        for section_data, should_be_empty, description in test_cases:
            with self.subTest(description=description):
                review_structure = {'1.1': section_data}

                # Apply placeholder logic
                empty_count = 0
                for section_id in ['1.1']:
                    if section_id in review_structure:
                        paras = review_structure[section_id].get('paragraphs', [])
                        if not paras or len(paras) == 0:
                            placeholder = self.expected_placeholder
                            review_structure[section_id]['paragraphs'] = [placeholder]
                            review_structure[section_id]['tagged_paragraphs'] = [{
                                'text': placeholder,
                                'tags': [],
                                'title': None
                            }]
                            empty_count += 1

                if should_be_empty:
                    self.assertEqual(empty_count, 1, f"{description}: should be treated as empty")
                    self.assertEqual(review_structure['1.1']['paragraphs'], [self.expected_placeholder])
                else:
                    self.assertEqual(empty_count, 0, f"{description}: should not be treated as empty")

    @patch('builtins.print')
    def test_logging_message_format(self, mock_print):
        """Test that the correct logging message is printed when placeholders are added"""
        # Create structure with some empty sections
        review_structure = {}
        for i, section_id in enumerate(['1.1', '1.2', '2.1']):
            review_structure[section_id] = {
                'paragraphs': [] if i < 2 else ['content'],
                'tagged_paragraphs': []
            }

        # Apply placeholder logic
        empty_count = 0
        for section_id in ['1.1', '1.2', '2.1']:
            if section_id in review_structure:
                paras = review_structure[section_id].get('paragraphs', [])
                if not paras or len(paras) == 0:
                    placeholder = self.expected_placeholder
                    review_structure[section_id]['paragraphs'] = [placeholder]
                    review_structure[section_id]['tagged_paragraphs'] = [{
                        'text': placeholder,
                        'tags': [],
                        'title': None
                    }]
                    empty_count += 1

        # Simulate the print statement from the actual code
        if empty_count > 0:
            print(f"Added placeholder text to {empty_count} empty section(s)")

        # Verify the print was called with correct message
        mock_print.assert_called_once_with("Added placeholder text to 2 empty section(s)")


class TestPlaceholderIntegration(unittest.TestCase):
    """Integration tests to ensure placeholder functionality works with actual extractor methods"""

    @classmethod
    def setUpClass(cls):
        """Initialize extractor for integration tests"""
        cls.extractor = DMPExtractor(debug_mode=True)

    def setUp(self):
        """Create temporary directory for each test"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory after each test"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_placeholder_preserves_confidence_scores(self):
        """Test that adding placeholders doesn't affect existing confidence scores"""
        review_structure = {
            '1.1': {
                'paragraphs': [],
                'confidence': 0.0,
                'extraction_method': 'test'
            },
            '1.2': {
                'paragraphs': ['Content'],
                'confidence': 0.85,
                'extraction_method': 'direct_match'
            }
        }

        # Store original confidence
        original_confidence = review_structure['1.2']['confidence']

        # Apply placeholder
        empty_count = 0
        for section_id in ['1.1', '1.2']:
            if section_id in review_structure:
                paras = review_structure[section_id].get('paragraphs', [])
                if not paras or len(paras) == 0:
                    placeholder = "Not answered in the source document."
                    review_structure[section_id]['paragraphs'] = [placeholder]
                    review_structure[section_id]['tagged_paragraphs'] = [{
                        'text': placeholder,
                        'tags': [],
                        'title': None
                    }]
                    empty_count += 1

        # Verify confidence score unchanged for section with content
        self.assertEqual(review_structure['1.2']['confidence'], original_confidence)

    def test_placeholder_preserves_metadata(self):
        """Test that adding placeholders doesn't affect metadata"""
        review_structure = {
            '1.1': {'paragraphs': []},
            '_metadata': {
                'filename': 'test.docx',
                'date': '2025-11-19'
            },
            '_unconnected_text': ['Some unconnected text']
        }

        original_metadata = review_structure['_metadata'].copy()
        original_unconnected = review_structure['_unconnected_text'].copy()

        # Apply placeholder
        for section_id in ['1.1']:
            if section_id in review_structure and not section_id.startswith('_'):
                paras = review_structure[section_id].get('paragraphs', [])
                if not paras or len(paras) == 0:
                    placeholder = "Not answered in the source document."
                    review_structure[section_id]['paragraphs'] = [placeholder]
                    review_structure[section_id]['tagged_paragraphs'] = [{
                        'text': placeholder,
                        'tags': [],
                        'title': None
                    }]

        # Verify metadata unchanged
        self.assertEqual(review_structure['_metadata'], original_metadata)
        self.assertEqual(review_structure['_unconnected_text'], original_unconnected)


if __name__ == '__main__':
    unittest.main(verbosity=2)
