"""
utils/extractor_v3_separated.py — Experimental: Separated slicing & cleaning

DIFFERENCE FROM v2:
- v2: DMPExtractor calls ContentCleaner during slicing (per-section)
- v3: DMPExtractor slices FIRST (all sections), then ContentCleaner processes all at once

BENEFITS:
✅ Better separation of concerns (slice vs clean)
✅ Easier debugging (can inspect raw slices)
✅ Independent unit testing
✅ Optional RAW cache export for development

TRADE-OFFS:
⚠️ Slightly higher memory usage (all raw slices in memory)
⚠️ More complex flow (two-phase)

Pipeline
--------
1. DocConverter   : document → List[TextBlock]
2. AnchorMatcher  : find section boundaries
3. DMPExtractor   : slice blocks into raw sections
4. ContentCleaner : clean all sections (batch)
5. Cache assembly : merge raw + cleaned (optional)
"""

import os
import json
import uuid
import logging
from typing import Dict, List, Tuple
from datetime import datetime

# Import components from extractor_v2
from utils.extractor_v2 import (
    DocConverter,
    AnchorMatcher,
    ContentCleaner,
    SkipTermsManager,
    TextBlock,
    SECTION_ORDER,
    SECTION_TITLES,
    SECTION_QUESTIONS,
    validate_docx_file,
    validate_pdf_file,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Separated DMPExtractor (v3)
# ─────────────────────────────────────────────────────────────────────────────

class DMPExtractorSeparated:
    """
    Anchor-based DMP extractor with separated slicing & cleaning phases.

    Constructor parameters:
        save_raw_slices (bool): If True, exports RAW slices to cache for debugging

    Usage:
        extractor = DMPExtractorSeparated(save_raw_slices=True)
        result = extractor.process_file(file_path, output_dir)

        # Cache structure with save_raw_slices=True:
        {
            "1.1": {
                "section": "...",
                "question": "...",
                "paragraphs": ["cleaned", "text"],      ← CLEANED
                "tagged_paragraphs": [...],
                "raw_blocks": ["raw", "text", "1.1"]    ← RAW (debug)
            },
            "_raw_sections": {                           ← RAW dump (debug)
                "1.1": ["raw text with numerations"],
                "1.2": [...]
            }
        }
    """

    def __init__(self, save_raw_slices: bool = False) -> None:
        self._anchors_cfg = self._load_anchors()
        self._converter = DocConverter()
        self._matcher = AnchorMatcher(self._anchors_cfg.get('sections', {}))
        self._cleaner = ContentCleaner()
        self._skip_mgr = SkipTermsManager()
        self.save_raw_slices = save_raw_slices  # NEW: debug flag

    # ── Public API ────────────────────────────────────────────────────────────

    def process_file(
        self,
        file_path: str,
        output_dir: str,
        progress_callback=None,
    ) -> dict:
        """
        Process DMP file through separated slicing & cleaning pipeline.

        Returns same format as extractor_v2 for compatibility:
            {'success': True, 'filename': str, 'cache_id': str, ...}
            {'success': False, 'message': str}
        """
        def cb(msg: str, pct: int) -> None:
            if progress_callback:
                progress_callback(msg, pct)

        try:
            # Validate file
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.docx':
                ok, msg = validate_docx_file(file_path)
            elif ext == '.pdf':
                ok, msg = validate_pdf_file(file_path)
            else:
                return {'success': False, 'message': f'Unsupported file type: {ext}'}
            if not ok:
                return {'success': False, 'message': msg}

            # PHASE 1: Convert document to blocks
            cb('Converting document to text blocks…', 10)
            blocks = self._converter.convert(file_path)
            logger.info(
                '[v3-separated] DocConverter produced %d blocks from %s',
                len(blocks), file_path
            )

            # PHASE 2: Find section boundaries
            cb('Locating section boundaries…', 30)
            boundaries = self._matcher.find_boundaries(blocks)
            logger.info(
                '[v3-separated] Found %d / %d section boundaries',
                len(boundaries), len(SECTION_ORDER),
            )

            # PHASE 3: Slice into RAW sections (NO cleaning yet)
            cb('Slicing sections (raw)…', 50)
            raw_sections = self._slice_sections(blocks, boundaries)
            logger.info(
                '[v3-separated] Sliced %d raw sections', len(raw_sections)
            )

            # PHASE 4: Clean ALL sections (batch processing)
            cb('Cleaning sections (batch)…', 70)
            skip_patterns = self._skip_mgr.compile()
            cleaned_sections = self._clean_sections(raw_sections, skip_patterns)
            logger.info(
                '[v3-separated] Cleaned %d sections', len(cleaned_sections)
            )

            # PHASE 5: Assemble final cache
            cb('Assembling cache…', 85)
            cache = self._build_cache(raw_sections, cleaned_sections, boundaries)

            # Save cache
            cb('Saving cache…', 90)
            cache_id = str(uuid.uuid4())
            cache_dir = os.path.join(output_dir, 'cache')
            os.makedirs(cache_dir, exist_ok=True)
            cache_path = os.path.join(cache_dir, f'cache_{cache_id}.json')
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)

            filled = sum(
                1 for sid in SECTION_ORDER
                if cache.get(sid, {}).get('paragraphs')
            )
            cb('Done.', 100)

            return {
                'success': True,
                'filename': self._smart_filename(file_path),
                'cache_id': cache_id,
                'cache_file': f'cache_{cache_id}.json',
                'message': f'[v3-separated] Extracted {filled} of {len(SECTION_ORDER)} sections',
            }

        except Exception as exc:
            logger.exception('[v3-separated] process_file failed for %s', file_path)
            return {'success': False, 'message': str(exc)}

    # ── Internal: NEW separated pipeline ──────────────────────────────────────

    def _slice_sections(
        self,
        blocks: List[TextBlock],
        boundaries: Dict[str, Tuple[int, int]],
    ) -> Dict[str, List[TextBlock]]:
        """
        PHASE 1: Slice blocks into raw sections (NO cleaning).

        Returns:
            {
                '1.1': [TextBlock, TextBlock, ...],  ← RAW blocks
                '1.2': [...],
                '_pre_anchor': [...]  ← text before first anchor
            }
        """
        raw_sections: Dict[str, List[TextBlock]] = {}

        if not boundaries:
            # No anchors found → everything is "unconnected"
            raw_sections['_pre_anchor'] = blocks
            return raw_sections

        # Sort sections by position
        ordered = sorted(boundaries.items(), key=lambda x: x[1][0])

        # Text BEFORE first anchor
        first_start_idx, _ = ordered[0][1]
        raw_sections['_pre_anchor'] = blocks[:first_start_idx]

        # Slice each section
        for rank, (sid, (start_idx, win_size)) in enumerate(ordered):
            # Content starts AFTER anchor window
            content_start = start_idx + win_size

            # Content ends at next anchor (or document end)
            if rank + 1 < len(ordered):
                next_start_idx, _ = ordered[rank + 1][1]
                content_end = next_start_idx
            else:
                content_end = len(blocks)

            # Store RAW blocks (includes numerations, questions, etc.)
            raw_sections[sid] = blocks[content_start:content_end]

            logger.debug(
                '[v3-slice] Section %s: anchor %d-%d, content %d-%d (%d raw blocks)',
                sid, start_idx, start_idx + win_size - 1,
                content_start, content_end - 1,
                len(raw_sections[sid])
            )

        return raw_sections

    def _clean_sections(
        self,
        raw_sections: Dict[str, List[TextBlock]],
        skip_patterns: list,
    ) -> Dict[str, List[str]]:
        """
        PHASE 2: Clean ALL raw sections (batch processing).

        Args:
            raw_sections: Dict[section_id, List[TextBlock]]
            skip_patterns: Compiled regex patterns for user skip terms

        Returns:
            {
                '1.1': ['cleaned', 'text', 'lines'],  ← CLEANED
                '1.2': [...],
                '_pre_anchor': [...]
            }
        """
        cleaned_sections: Dict[str, List[str]] = {}

        for sid, raw_blocks in raw_sections.items():
            # ContentCleaner.clean() removes:
            # - numerations (1.1, 2.2)
            # - formatting markers
            # - headers/footers
            # - structural noise
            # - user skip terms
            cleaned_lines = self._cleaner.clean(raw_blocks, skip_patterns)
            cleaned_sections[sid] = cleaned_lines

            logger.debug(
                '[v3-clean] Section %s: %d raw blocks → %d cleaned lines',
                sid, len(raw_blocks), len(cleaned_lines)
            )

            # Warn if section is empty
            if sid != '_pre_anchor' and len(cleaned_lines) == 0:
                logger.warning(
                    '[v3-clean] Section %s: NO content after cleaning! '
                    '(%d raw blocks → 0 lines)',
                    sid, len(raw_blocks)
                )

        return cleaned_sections

    def _build_cache(
        self,
        raw_sections: Dict[str, List[TextBlock]],
        cleaned_sections: Dict[str, List[str]],
        boundaries: Dict[str, Tuple[int, int]],
    ) -> dict:
        """
        PHASE 3: Assemble final cache from raw + cleaned sections.

        Cache structure (compatible with review.html):
            {
                "1.1": {
                    "section": "1. Data description...",
                    "question": "How will new data...",
                    "paragraphs": ["cleaned", "text"],
                    "tagged_paragraphs": [{text, tags, title}, ...],
                    "raw_blocks": ["raw", "text"]  ← IF save_raw_slices=True
                },
                "_unconnected_text": [{text, type}, ...],
                "_raw_sections": {...}  ← IF save_raw_slices=True
            }
        """
        cache: dict = {}

        # Build cache for found sections
        for sid in SECTION_ORDER:
            main = sid.split('.')[0]

            if sid in cleaned_sections:
                paragraphs = cleaned_sections[sid]
                tagged = [{'text': p, 'tags': [], 'title': ''} for p in paragraphs]

                cache[sid] = {
                    'section': SECTION_TITLES[main],
                    'question': SECTION_QUESTIONS[sid],
                    'paragraphs': paragraphs,
                    'tagged_paragraphs': tagged,
                }

                # DEBUG: Optionally include raw blocks
                if self.save_raw_slices and sid in raw_sections:
                    cache[sid]['raw_blocks'] = [
                        blk.text for blk in raw_sections[sid]
                    ]
            else:
                # Section not found → empty
                cache[sid] = self._empty_section(sid)

        # Unconnected text (before first anchor)
        pre_lines = cleaned_sections.get('_pre_anchor', [])
        cache['_unconnected_text'] = [
            {'text': t, 'type': 'no_section'} for t in pre_lines
        ]

        # DEBUG: Optionally export ALL raw sections
        if self.save_raw_slices:
            cache['_raw_sections'] = {
                sid: [blk.text for blk in blocks]
                for sid, blocks in raw_sections.items()
                if sid != '_pre_anchor'
            }

        return cache

    @staticmethod
    def _empty_section(sid: str) -> dict:
        """Create empty section structure."""
        main = sid.split('.')[0]
        return {
            'section': SECTION_TITLES[main],
            'question': SECTION_QUESTIONS[sid],
            'paragraphs': [],
            'tagged_paragraphs': [],
        }

    def _load_anchors(self) -> dict:
        """Load anchor configuration."""
        path = os.path.normpath(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '..', 'config', 'dmp_anchors.json',
            )
        )
        with open(path, encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def _smart_filename(file_path: str) -> str:
        """Generate smart filename for output."""
        import re
        base = os.path.splitext(os.path.basename(file_path))[0]
        safe = re.sub(r'[^\w\-]', '_', base)[:50]
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'DMP_{safe}_{ts}'
