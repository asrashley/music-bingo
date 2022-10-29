"""
Represents the length of something in real-world units
"""

import re
from typing import Union, cast

class Dimension:
    """
    Represents the length of something in real-world units
    """

    INCH: float = 25.4
    UNITS = {
        'in': INCH,
        'pt': INCH / 72.0,
        'px': INCH / 96.0,
        'cm': 10.0,
        'mm': 1.0
    }

    _re = re.compile(r'^([\d\.]+)\s*(\w+)$')

    def __init__(self, value: Union[float, str, "Dimension"]) -> None:
        self.absolute = True
        if isinstance(value, str):
            if value.endswith('%'):
                self.absolute = False
                value = float(value[:-1])
            else:
                match = self._re.match(value)
                if match is None:
                    raise ValueError(f'Failed to parse "{value}"')
                value = float(match.group(1)) * self.UNITS[match.group(2)]
        elif isinstance(value, Dimension):
            self.absolute = value.absolute
            value = value.value
        elif isinstance(value, int):
            value = float(value)
        self.value: float = value

    def points(self) -> float:
        """Convert dimension into points (1/72nd of an inch)"""
        if not self.absolute:
            raise ValueError(f'Cannot convert relative value {self.value}')
        return cast(float, self.value) / self.UNITS['pt']

    def points_or_relative(self) -> Union[float, str]:
        """
        Convert dimension into points unless relative, when the relative
        value is returned
        """
        if self.absolute:
            return self.value / self.UNITS['pt']
        return self.value

    def __float__(self) -> float:
        if not self.absolute:
            raise ValueError(f'Cannot convert relative value "{self.value}"')
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Dimension):
            return self.value == cast(Dimension, other).value
        if isinstance(other, (int, float)):
            return self.value == other
        if isinstance(other, str):
            return self.value == Dimension(other)
        raise NotImplementedError(f"Unable to compare {other} with {self}")

    def __truediv__(self, other: Union[float, str, "Dimension"]) -> "Dimension":
        if not self.absolute:
            raise NotImplementedError("Division of relative values not implemented")
        assert isinstance(self.value, float)
        if isinstance(other, Dimension):
            if not cast(Dimension, other).absolute:
                raise NotImplementedError("Division of relative values not implemented")
            return Dimension(self.value / cast(float, cast(Dimension, other).value))
        if isinstance(other, (int, float)):
            return Dimension(self.value / float(other))
        raise ValueError("Unsupprted division of {self.value} and {value}")

    def __floordiv__(self, other: Union[float, str, "Dimension"]) -> "Dimension":
        if not self.absolute:
            raise NotImplementedError("Division of relative values not implemented")
        assert isinstance(self.value, float)
        if isinstance(other, Dimension):
            if not cast(Dimension, other).absolute:
                raise NotImplementedError("Division of relative values not implemented")
            return Dimension(self.value // cast(float, cast(Dimension, other).value))
        if isinstance(other, (int, float)):
            return Dimension(self.value // float(other))
        raise ValueError("Unsupprted floor division of {self.value} and {value}")

    def __add__(self, other: Union["Dimension", float]) -> "Dimension":
        if not self.absolute:
            value = self.value + Dimension(other).value
            return Dimension(f'{value}%')
        value = self.value + float(other)
        return Dimension(value)

    def __sub__(self, other: Union["Dimension", float]) -> "Dimension":
        # print('value', type(self.value), self.value, type(other))
        if not self.absolute:
            value = self.value - Dimension(other).value
            return Dimension(f'{value}%')
        value = self.value - float(other)
        return Dimension(value)

    def __mul__(self, other: Union["Dimension", float]) -> "Dimension":
        if not self.absolute:
            value = self.value * float(other)
            return Dimension(f'{value}%')
        value = self.value * float(other)
        return Dimension(value)

    def __lt__(self, other: Union["Dimension", float]) -> bool:
        # pylint: disable=invalid-name
        def cmp_fn(a, b):
            return a < b
        return self.__compare(other, cmp_fn)

    def __gt__(self, other: Union["Dimension", float]) -> bool:
        # pylint: disable=invalid-name
        def cmp_fn(a, b):
            return a > b
        return self.__compare(other, cmp_fn)

    def __compare(self, other: Union["Dimension", float], cmp_fn) -> bool:
        other = Dimension(other)
        if self.absolute != other.absolute:
            raise ValueError("Cannot compare absolute and non-absolute dimensions")
        if not self.absolute:
            return cmp_fn(self.value, other.value)
        return cmp_fn(self.value, other.value)

    def __str__(self) -> str:
        if not self.absolute:
            return f'{self.value}%'
        #pts = self.points()
        #if abs(pts - round(pts)) < 0.1:
        #    return f'{pts}pt'
        value = round(self.value, 3)
        return f'{value}mm'

    def __repr__(self) -> str:
        if not self.absolute:
            return f'Dimension("{self.value}%")'
        return f'Dimension({self.value})'

RelaxedDimension = Union[Dimension, float, str]
