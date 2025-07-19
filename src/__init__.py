"""
EfficacyLens: Clinical Trial Efficacy Comparison AI Agent

This package provides AI-powered comparison of pharmaceutical publications
using Google Gemini API to generate actionable insights for decision makers.
"""

from .efficacy_lens_agent import EfficacyLensAgent
from .pdf_processor import PDFProcessor

__version__ = "1.0.0"
__author__ = "EfficacyLens Team"
__description__ = "Clinical Trial Efficacy Comparison AI Agent"

__all__ = [
    "EfficacyLensAgent",
    "PDFProcessor"
] 