"""Compatibility wrapper for legacy extractor imports."""

from .extractor_v4 import DMPExtractor, HAS_OCR, SkipTermsManager

__all__ = ["DMPExtractor", "HAS_OCR", "SkipTermsManager"]
