"""
Factory functions for creating a document generator
"""

from typing import Dict, Optional, Type

from musicbingo.docgen.documentgenerator import DocumentGenerator

GENERATORS: Dict[str, Type[DocumentGenerator]] = {}

try:
    from musicbingo.docgen.pdfgen import PDFGenerator
    GENERATORS['pdf'] = PDFGenerator
except ImportError as err:
    print(err)

class DocumentFactory:
    """Class for creating DocumentGenerator instances"""

    @classmethod
    def create_generator(cls, generator: Optional[str] = None) -> DocumentGenerator:
        """
        Create an DocumentGenerator.
        If generator==None, the factory will pick the first one that
        is supported.
        """
        if generator is None:
            assert len(GENERATORS) > 0
            generator = list(GENERATORS.keys())[0]
            assert generator is not None
        try:
            return GENERATORS[generator.lower()]()
        except KeyError:
            raise NotImplementedError(f'Unknown document generator "{generator}"')
