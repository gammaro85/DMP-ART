"""Compatibility wrapper for legacy v3 extractor imports."""

from .extractor_v4 import DMPExtractor as DMPExtractorSeparated

__all__ = ["DMPExtractorSeparated"]
