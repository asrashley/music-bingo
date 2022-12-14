"""
Displays the discovered MP3 editors and parsers
"""

from .factory import MP3Factory

def main():
    """
    Displays the discovered MP3 editors and parsers
    """

    def display_engine(name, feature):
        available = ', '.join(feature.available_engines())
        print(f'MP3 {name}: default={feature.default_engine} available=[{available}]')
        if feature.errors:
            for errname, err in feature.errors:
                print(f'{errname}: {err}')

    MP3Factory._auto_probe()
    display_engine('editors', MP3Factory.EDITOR)
    display_engine('parsers', MP3Factory.PARSER)
    display_engine('players', MP3Factory.PLAYER)

main()
