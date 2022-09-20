"""
Displays the discovered MP3 editors and parsers
"""

from .factory import MP3Factory

def main():
    """
    Displays the discovered MP3 editors and parsers
    """
    available_editors = ', '.join(MP3Factory.available_editors())
    print(f'Available MP3 editors: {available_editors}')
    if MP3Factory.EDITOR_ERRORS:
        print('MP3 editors that were not enabled:')
        for name, err in MP3Factory.EDITOR_ERRORS:
            print(f'{name}: {err}')
    available_parsers = ', '.join(MP3Factory.available_parsers())
    print(f'Available MP3 parsers: {available_parsers}')

    if MP3Factory.PARSER_ERRORS:
        print('MP3 parsers that were not enabled:')
        for name, err in MP3Factory.PARSER_ERRORS:
            print(f'{name}: {err}')

main()
