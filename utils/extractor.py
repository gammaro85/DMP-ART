"""Backward-compatible wrapper around extractor_v2 for legacy tests and scripts."""

import os
import re
import shutil

from utils.extractor_v2 import (  # noqa: F401
    AnchorMatcher,
    ContentCleaner,
    DMPExtractor as _V2DMPExtractor,
    HAS_OCR,
    SECTION_ORDER,
    SECTION_QUESTIONS,
    SECTION_TITLES,
    SkipTermsManager,
    TextBlock,
    _BUILTIN_NOISE,
    normalize,
    strip_formatting,
    token_overlap,
    validate_docx_file,
    validate_pdf_file,
)

_POLISH_SECTION_TITLES = {
    '1': '1. Opis danych oraz pozyskiwanie lub ponowne wykorzystanie istniejacych danych',
    '2': '2. Dokumentacja i jakosc danych',
    '3': '3. Przechowywanie i tworzenie kopii zapasowych podczas badan',
    '4': '4. Wymogi prawne, kodeks postepowania',
    '5': '5. Udostepnianie i dlugotrwale przechowywanie danych',
    '6': '6. Zadania zwiazane z zarzadzaniem danymi oraz zasoby',
}

_LEGACY_SKIP_PATTERNS = (
    re.compile(r'^\s*strona\s+\d+\s*$', re.IGNORECASE),
    re.compile(r'^\s*page\s+\d+\s*$', re.IGNORECASE),
    re.compile(r'^\s*id:\s*\d+\s*$', re.IGNORECASE),
    re.compile(r'^\s*\[wydruk roboczy\]\s*$', re.IGNORECASE),
    re.compile(r'^\s*\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2}:\d{2})?\s*$', re.IGNORECASE),
    re.compile(r'^\s*osf,.*strona\s+\d+.*id:\s*\d+.*$', re.IGNORECASE),
)


class DMPExtractor(_V2DMPExtractor):
    """Compatibility facade preserving the old helper methods and attributes."""

    def __init__(self, debug_mode=False):
        super().__init__()
        self.debug_mode = debug_mode
        self.section_mapping = dict(SECTION_TITLES)
        self.subsection_mapping = dict(SECTION_QUESTIONS)
        self._compiled_skip_patterns = self._skip_mgr.compile()

    def _text_similarity(self, text_a, text_b):
        normalized_a = normalize(text_a or '')
        normalized_b = normalize(text_b or '')

        if not normalized_a or not normalized_b:
            return 0.0

        forward = token_overlap(normalized_a, normalized_b)
        backward = token_overlap(normalized_b, normalized_a)
        return (forward + backward) / 2

    def detect_section_from_text(self, text, is_pdf=False):
        normalized_text = normalize(text or '')
        if not normalized_text:
            return None

        best_section = None
        best_score = 0.0

        for main_id, english_title in SECTION_TITLES.items():
            candidates = [english_title, _POLISH_SECTION_TITLES.get(main_id, '')]

            for candidate in candidates:
                normalized_candidate = normalize(candidate)
                if not normalized_candidate:
                    continue

                score = max(
                    token_overlap(normalized_candidate, normalized_text),
                    token_overlap(normalized_text, normalized_candidate),
                )
                if score > best_score:
                    best_score = score
                    best_section = english_title

        return best_section if best_score >= 0.35 else None

    def detect_subsection_from_text(self, text, section, is_pdf=False):
        if not section:
            return None

        section_id = next(
            (main_id for main_id, title in SECTION_TITLES.items() if title == section),
            None,
        )
        if not section_id:
            return None

        normalized_text = normalize(text or '')
        if not normalized_text:
            return None

        best_subsection = None
        best_score = 0.0

        for subsection_id, question in SECTION_QUESTIONS.items():
            if not subsection_id.startswith(f'{section_id}.'):
                continue

            cfg = self._anchors_cfg.get('sections', {}).get(subsection_id, {})
            candidates = cfg.get('pl', []) + cfg.get('en', []) + [question]

            for candidate in candidates:
                normalized_candidate = normalize(candidate)
                score = max(
                    token_overlap(normalized_candidate, normalized_text),
                    token_overlap(normalized_text, normalized_candidate),
                )
                if score > best_score:
                    best_score = score
                    best_subsection = question

        return best_subsection if best_score >= 0.35 else None

    def should_skip_text(self, text, is_pdf=False):
        if not text or not text.strip():
            return True

        stripped = text.strip()
        if any(pattern.search(stripped) for pattern in _LEGACY_SKIP_PATTERNS):
            return True

        if any(pattern.search(stripped) for pattern in _BUILTIN_NOISE):
            return True

        cleaned = strip_formatting(stripped)
        return any(pattern.search(cleaned) for pattern in self._compiled_skip_patterns)

    def clean_markup(self, text):
        cleaned = (text or '').strip()
        cleaned = re.sub(r'^\[(.*?)\]\{[^}]+\}$', r'\1', cleaned)
        cleaned = re.sub(r'^\*\*(.*?)\*\*$', r'\1', cleaned)
        cleaned = re.sub(r'^__(.*?)__$', r'\1', cleaned)
        cleaned = cleaned.replace('{.mark}', '')
        cleaned = re.sub(r'\{[^}]+\}', '', cleaned)
        cleaned = cleaned.replace('**', '').replace('__', '')
        return re.sub(r'\s+', ' ', cleaned).strip()

    def _extract_from_filename(self, filename):
        name = os.path.splitext(os.path.basename(filename))[0]
        metadata = {}

        structured_match = re.match(
            r'^DMP_([^_]+)_([^_]+)_([A-Za-z]+)_([0-9]+)_\d+$',
            name,
        )
        if structured_match:
            metadata['researcher_surname'] = structured_match.group(1)
            metadata['researcher_firstname'] = structured_match.group(2)
            metadata['competition_name'] = structured_match.group(3).upper()
            metadata['competition_edition'] = structured_match.group(4)
            return metadata

        compact_match = re.match(r'^([A-Za-z]+)(\d+)_plan$', name, re.IGNORECASE)
        if compact_match:
            metadata['competition_name'] = compact_match.group(1).upper()
            metadata['competition_edition'] = compact_match.group(2)

        return metadata

    def validate_docx_file(self, path):
        return validate_docx_file(path)

    def validate_pdf_file(self, path):
        return validate_pdf_file(path)

    def process_file(self, file_path, output_dir, progress_callback=None):
        result = super().process_file(file_path, output_dir, progress_callback=progress_callback)
        if not result.get('success') or not result.get('cache_id'):
            return result

        cache_name = f"cache_{result['cache_id']}.json"
        nested_cache = os.path.join(output_dir, 'cache', cache_name)
        legacy_cache = os.path.join(output_dir, cache_name)

        if os.path.exists(nested_cache) and not os.path.exists(legacy_cache):
            shutil.copy2(nested_cache, legacy_cache)

        result['cache_file'] = cache_name
        return result
