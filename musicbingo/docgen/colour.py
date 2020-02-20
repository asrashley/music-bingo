"""
RGBA colour that can be expressed as integers or a string using the
CSS colour notation.
"""
from typing import Dict, List, Tuple, Union, cast

CSS_COLOUR_NAMES: Dict[str, str] = {
    'white': '#FFFFFF',
    'silver': '#C0C0C0',
    'gray': '#808080',
    'black': '#000000',
    'red': '#FF0000',
    'maroon': '#800000',
    'yellow': '#FFFF00',
    'olive': '#808000',
    'lime': '#00FF00',
    'green': '#008000',
    'aqua': '#00FFFF',
    'teal': '#008080',
    'blue': '#0000FF',
    'navy': '#000080',
    'fuchsia': '#FF00FF',
    'purple': '#800080',
}

class Colour:
    """
    Class to represent RGBA colour that can be expressed as integers
    or a string
    """
    MAX_VALUE = 255

    def __init__(self, value: Union["Colour", int, str],
                 green: int = 0, blue: int = 0, alpha: int = MAX_VALUE):
        if isinstance(value, str):
            self.red, self.green, self.blue, self.alpha = Colour.parse_colour(value)
        elif isinstance(value, Colour):
            self.red = value.red
            self.green = value.green
            self.blue = value.blue
            self.alpha = value.alpha
        else:
            self.red = cast(int, value)
            self.green = green
            self.blue = blue
            self.alpha = alpha

    @classmethod
    def parse_colour(cls, value: str) -> Tuple[int, int, int, int]:
        """
        Parse a string into a colour tuple.
        Supports most of the CSS colour forms.
        """
        values: List[int] = []
        try:
            value = CSS_COLOUR_NAMES[value.lower()]
        except KeyError:
            pass
        if value[0] == '#':
            if len(value) == 4: # short RGB form
                red = int(value[0], 16)
                green = int(value[1], 16)
                blue = int(value[2], 16)
                red += red << 4
                green += green << 4
                blue += blue << 4
                alpha = cls.MAX_VALUE
            elif len(value) == 9: # RGBA
                red = int(value[1:3], 16)
                green = int(value[3:5], 16)
                blue = int(value[5:7], 16)
                alpha = int(value[7:9], 16)
            else: # RGB
                red = int(value[1:3], 16)
                green = int(value[3:5], 16)
                blue = int(value[5:7], 16)
                alpha = cls.MAX_VALUE
            return (red, green, blue, alpha)
        if value.startswith('rgb('):
            value = value[4:-1]
            for item in value.split(','):
                if '%' in item:
                    values.append(int(cls.MAX_VALUE * float(item[:-1]) / 100.0))
                else:
                    values.append(int(item))
            values.append(cls.MAX_VALUE)
            return cast(Tuple[int, int, int, int], tuple(values))
        if value.startswith('rgba('):
            value = value[5:-1]
            for item in value.split(','):
                if '%' in item:
                    values.append(int(cls.MAX_VALUE * float(item[:-1]) / 100.0))
                elif '.' in item:
                    values.append(int(cls.MAX_VALUE * float(item)))
                else:
                    values.append(int(item))
            return cast(Tuple[int, int, int, int], tuple(values))
        raise ValueError(f'Unsupported colour string {value}')

    def css(self) -> str:
        """convert this colour into a CSS style string"""
        if self.alpha == self.MAX_VALUE:
            return '#{0:02x}{1:02x}{2:02x}'.format(self.red, self.green,
                                                   self.blue)
        return '#{0:02x}{1:02x}{2:0x}{3:02x}'.format(self.red, self.green,
                                                     self.blue, self.alpha)

    def __repr__(self) -> str:
        return f'Colour({self.red}, {self.green}, {self.blue}, {self.alpha})'

    def __eq__(self, colour: object) -> bool:
        if isinstance(colour, str):
            colour = Colour(colour)
        if not isinstance(colour, Colour):
            return False
        return (self.red == colour.red and
                self.green == colour.green and
                self.blue == colour.blue and
                self.alpha == colour.alpha)

    @property
    def __key__(self) -> Tuple:
        return (self.red, self.green, self.blue, self.alpha)

    def __hash__(self) -> int:
        return hash(self.__key__)

class HexColour(Colour):
    """
    Represent an RGB colour using one integer
    """

    def __init__(self, hexcolour: int):
        red = (hexcolour >> 16) & 0xFF
        green = (hexcolour >> 8) & 0xFF
        blue = hexcolour & 0xFF
        super(HexColour, self).__init__(red, green, blue)

class FloatColour(Colour):
    """
    Represent an RGB or RGBA colour using floating point values
    """
    def __init__(self, red: float, green: float, blue: float, alpha: float = 1.0):
        red = int(Colour.MAX_VALUE * red)
        green = int(Colour.MAX_VALUE * green)
        blue = int(Colour.MAX_VALUE * blue)
        alpha = int(Colour.MAX_VALUE * alpha)
        super(FloatColour, self).__init__(red, green, blue, alpha)
