#!/usr/bin/env python3
"""Focused tests for the unified session-history JSON layout."""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import app as dmp_app


class SessionHistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix='dmp_art_sessions_')
        self.app = dmp_app.app
        self.original_config = {
            'CACHE_FOLDER': self.app.config['CACHE_FOLDER'],
            'ACTIVE_SESSIONS_FOLDER': self.app.config['ACTIVE_SESSIONS_FOLDER'],
            'SESSION_ARCHIVE_FOLDER': self.app.config['SESSION_ARCHIVE_FOLDER'],
            'ARCHIVES_FOLDER': self.app.config['ARCHIVES_FOLDER'],
        }

        self.app.config['CACHE_FOLDER'] = os.path.join(self.temp_dir, 'cache')
        self.app.config['ACTIVE_SESSIONS_FOLDER'] = os.path.join(self.temp_dir, 'sessions', 'active')
        self.app.config['SESSION_ARCHIVE_FOLDER'] = os.path.join(self.temp_dir, 'sessions', 'archive')
        self.app.config['ARCHIVES_FOLDER'] = os.path.join(self.temp_dir, 'legacy_archives')

        os.makedirs(self.app.config['CACHE_FOLDER'], exist_ok=True)
        os.makedirs(self.app.config['ACTIVE_SESSIONS_FOLDER'], exist_ok=True)
        os.makedirs(self.app.config['SESSION_ARCHIVE_FOLDER'], exist_ok=True)
        os.makedirs(self.app.config['ARCHIVES_FOLDER'], exist_ok=True)

        self.cache_id = '11111111-2222-3333-4444-555555555555'
        self.cache_path = os.path.join(self.app.config['CACHE_FOLDER'], f'cache_{self.cache_id}.json')

        cache_payload = {
            '1.1': {
                'section': '1. Data description and collection or re-use of existing data',
                'question': 'How will new data be collected?',
                'paragraphs': ['Paragraph one', 'Paragraph two'],
                'tagged_paragraphs': [{'text': 'Paragraph one', 'tags': [], 'title': ''}]
            },
            '_metadata': {
                'researcher_surname': 'Kowalski',
                'researcher_firstname': 'Jan',
                'competition_name': 'OPUS',
                'competition_edition': '29',
                'creation_date': '28-05-26',
                'filename_original': 'plan.docx'
            }
        }

        with open(self.cache_path, 'w', encoding='utf-8') as file_handle:
            json.dump(cache_payload, file_handle, ensure_ascii=False, indent=2)

        self.client = self.app.test_client()

    def tearDown(self):
        for key, value in self.original_config.items():
            self.app.config[key] = value
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_ensure_active_session_creates_split_json_files(self):
        bundle = dmp_app._ensure_active_session(
            self.cache_id,
            feedback_data={'1.1': 'Komentarz testowy'},
            compiled_feedback='1.1 Komentarz testowy'
        )

        paths = bundle['paths']
        self.assertTrue(os.path.exists(paths['dmp_path']))
        self.assertTrue(os.path.exists(paths['feedback_path']))
        self.assertTrue(os.path.exists(paths['metadata_path']))

        with open(paths['dmp_path'], 'r', encoding='utf-8') as file_handle:
            dmp_plan = json.load(file_handle)
        self.assertEqual(dmp_plan['cache_id'], self.cache_id)
        self.assertIn('1.1', dmp_plan['sections'])

        with open(paths['feedback_path'], 'r', encoding='utf-8') as file_handle:
            feedback = json.load(file_handle)
        self.assertEqual(feedback['sections']['1.1'], 'Komentarz testowy')
        self.assertEqual(feedback['compiled_feedback'], '1.1 Komentarz testowy')

        with open(paths['metadata_path'], 'r', encoding='utf-8') as file_handle:
            metadata = json.load(file_handle)
        self.assertEqual(metadata['status'], 'active')
        self.assertEqual(metadata['filename_original'], 'plan.docx')

    def test_archive_session_preserves_active_session_and_creates_archive_copy(self):
        dmp_app._ensure_active_session(
            self.cache_id,
            feedback_data={'1.1': 'Komentarz archiwizowany'},
            compiled_feedback='1.1 Komentarz archiwizowany'
        )

        response = self.client.post('/api/archive-session', json={
            'cache_id': self.cache_id,
            'feedback': {'1.1': 'Komentarz archiwizowany'}
        })

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['success'])

        archive_dir = os.path.join(self.app.config['SESSION_ARCHIVE_FOLDER'], payload['archive_id'])
        active_dir = os.path.join(self.app.config['ACTIVE_SESSIONS_FOLDER'], self.cache_id)

        self.assertTrue(os.path.exists(os.path.join(archive_dir, 'dmp_plan.json')))
        self.assertTrue(os.path.exists(os.path.join(archive_dir, 'feedback.json')))
        self.assertTrue(os.path.exists(os.path.join(archive_dir, 'metadata.json')))
        self.assertTrue(os.path.exists(active_dir))

        with open(os.path.join(active_dir, 'metadata.json'), 'r', encoding='utf-8') as file_handle:
            active_metadata = json.load(file_handle)

        self.assertTrue(active_metadata['preserved_after_archive'])
        self.assertEqual(active_metadata['last_archive_id'], payload['archive_id'])


if __name__ == '__main__':
    unittest.main()