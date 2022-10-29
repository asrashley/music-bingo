"""
Collection of colour schemes that can be used when generating
Bingo tickets
"""
import enum
from typing import List, NamedTuple, Tuple

from musicbingo.assets import Assets
from musicbingo.docgen.colour import Colour, HexColour, FloatColour
from musicbingo.docgen.documentgenerator import Image
from musicbingo.docgen.sizes.dimension import Dimension, RelaxedDimension

class ColourScheme(NamedTuple):
    """tuple representing one colour scheme"""
    box_normal_bg: Colour
    box_alternate_bg: Colour
    title_bg: Colour
    logo: Tuple[str, int, int]
    colours: List[Colour] = []


class Palette(enum.Enum):
    """Available colour schemes"""

    BLUE = ColourScheme(
        box_normal_bg=HexColour(0xF0F8FF),
        box_alternate_bg=HexColour(0xDAEDFF),
        title_bg=HexColour(0xa4d7ff),
        logo=('logo_banner.jpg', 7370, 558),
    )

    RED = ColourScheme(
        box_normal_bg=HexColour(0xFFF0F0),
        box_alternate_bg=HexColour(0xffdada),
        title_bg=HexColour(0xffa4a4),
        logo=('logo_banner.jpg', 7370, 558),
    )

    GREEN = ColourScheme(
        box_normal_bg=HexColour(0xf0fff0),
        box_alternate_bg=HexColour(0xd9ffd9),
        title_bg=HexColour(0xa4ffa4),
        logo=('logo_banner.jpg', 7370, 558),
    )

    ORANGE = ColourScheme(
        box_normal_bg=HexColour(0xfff7f0),
        box_alternate_bg=HexColour(0xffecd9),
        title_bg=HexColour(0xffd1a3),
        logo=('logo_banner.jpg', 7370, 558),
    )

    PINK = ColourScheme(
        box_normal_bg=HexColour(0xffd2cb),
        box_alternate_bg=HexColour(0xffebe8),
        title_bg=HexColour(0xffe4e1),
        logo=('logo_banner.jpg', 7370, 558),
    )

    PURPLE = ColourScheme(
        box_normal_bg=HexColour(0xf8f0ff),
        box_alternate_bg=HexColour(0xeed9ff),
        title_bg=HexColour(0xd5a3ff),
        logo=('logo_banner.jpg', 7370, 558),
    )

    YELLOW = ColourScheme(
        box_normal_bg=HexColour(0xfffff0),
        box_alternate_bg=HexColour(0xfeffd9),
        title_bg=HexColour(0xfdffa3),
        logo=('logo_banner.jpg', 7370, 558),
    )

    GREY = ColourScheme(
        box_normal_bg=HexColour(0xf1f1f1),
        box_alternate_bg=HexColour(0xd9d9d9),
        title_bg=HexColour(0xbfbfbf),
        logo=('logo_banner.jpg', 7370, 558),
    )

    CYAN = ColourScheme(
        box_normal_bg=HexColour(0xecfdff),
        box_alternate_bg=HexColour(0xd9fdff),
        title_bg=HexColour(0xccfdff),
        logo=('logo_banner.jpg', 7370, 558),
    )

    MAGENTA = ColourScheme(
        box_normal_bg=HexColour(0xffe6ff),
        box_alternate_bg=HexColour(0xedc1e4),
        title_bg=HexColour(0xf9d6f2),
        logo=('logo_banner.jpg', 7370, 558),
    )

    PRIDE = ColourScheme(
        box_normal_bg=HexColour(0xf1f1f1),
        box_alternate_bg=HexColour(0xd9d9d9),
        title_bg=HexColour(0xbfbfbf),
        colours=[
            FloatColour(0.00, 0.00, 0.00, 0.25),  # black
            FloatColour(0.47, 0.31, 0.09, 0.25),  # brown
            FloatColour(0.94, 0.14, 0.14, 0.25),  # red
            FloatColour(0.93, 0.52, 0.13, 0.25),  # orange
            FloatColour(1.00, 0.90, 0.00, 0.25),  # yellow
            FloatColour(0.07, 0.62, 0.04, 0.25),  # green
            FloatColour(0.02, 0.27, 0.70, 0.25),  # blue
            FloatColour(0.76, 0.18, 0.86, 0.25),  # purple
        ],
        logo=('pride_logo_banner.png', 7370, 558),
    )

    @classmethod
    def names(cls) -> List[str]:
        """get list of colour schemes"""
        return sorted(cls.__members__.keys()) # type: ignore

    @classmethod
    def from_string(cls, name: str) -> "Palette":
        """
        convert name of colour into an entry from this enum
        """
        try:
            return cls[name.upper()]  # type: ignore
        except KeyError as exc:
            raise ValueError(name) from exc

    def logo_image(self, width: RelaxedDimension) -> Image:
        """filename of the Music Bingo logo"""
        width = Dimension(width)
        #pylint: disable=no-member
        filename, img_width, img_height = self.value.logo
        aspect: float = float(img_width) / float(img_height)
        width = Dimension(width)
        return Image(filename=Assets.get_data_filename(filename),
                     width=width, height=(width / aspect))

    @property
    def box_normal_bg(self) -> Colour:
        """primary background colour for a Bingo square"""
        #pylint: disable=no-member
        return self.value.box_normal_bg

    @property
    def box_alternate_bg(self) -> Colour:
        """alternate background colour for a Bingo square"""
        #pylint: disable=no-member
        return self.value.box_alternate_bg

    @property
    def title_bg(self) -> Colour:
        """background colour for title row"""
        #pylint: disable=no-member
        return self.value.title_bg

    @property
    def colours(self) -> List[Colour]:
        """list of colours for each Bingo square"""
        #pylint: disable=no-member
        return self.value.colours

    def __str__(self) -> str:
        return self.name
