"""
Mock impementation of DocumentGenerator for use in unit tests
"""
from pathlib import Path
from typing import Dict

from musicbingo.docgen import documentgenerator as DG
from musicbingo.progress import Progress
from musicbingo import utils

class MockDocumentGenerator(DG.DocumentGenerator):
    """
    Mock impementation of DocumentGenerator for use in unit tests
    """

    def __init__(self) -> None:
        self.output: Dict[str, Dict] = {}

    def render(self, filename: str, document: DG.Document,
               progress: Progress, debug: bool = False, showBoundary: bool = False) -> None:
        """Render the given document"""
        doc = document.as_dict()
        self.output[Path(filename).name] = utils.flatten(doc)
