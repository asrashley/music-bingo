"""
Mock impementation of DocumentGenerator for use in unit tests
"""
from pathlib import Path
from typing import Dict

from musicbingo.docgen import documentgenerator as DG
from musicbingo.progress import Progress

from .mock_base import MockBase


class MockDocumentGenerator(DG.DocumentGenerator, MockBase):
    """
    Mock impementation of DocumentGenerator for use in unit tests
    """

    def __init__(self):
        self.output: Dict[str, Dict] = {}

    def render(self, filename: str, document: DG.Document,
               progress: Progress) -> None:
        """Render the given document"""
        doc = document.as_dict()
        self.output[Path(filename).name] = self.flatten(doc)
