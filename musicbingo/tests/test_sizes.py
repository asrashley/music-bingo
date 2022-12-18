"""
Tests of the size classes
"""
import unittest

from musicbingo.docgen.sizes.dimension import Dimension

class TestDimension(unittest.TestCase):
    """
    tests of the Dimension class
    """

    def test_inch_to_mm(self):
        """
        Test inches to mm
        """
        dim = Dimension("1in")
        self.assertAlmostEqual(dim.value, 25.4)
        dim = Dimension("8.3in")
        self.assertAlmostEqual(dim.value, 210.82)
        dim = Dimension("11.7in")
        self.assertAlmostEqual(dim.value, 297.18)

    def test_inch_to_points(self):
        """
        Test inches to points
        """
        dim = Dimension("8.3in")
        self.assertAlmostEqual(dim.points(), 597.6)
        dim = Dimension("11.7in")
        self.assertAlmostEqual(dim.points(), 842.4)

    def test_cm_to_mm(self):
        """
        Test cm to mm
        """
        dim = Dimension("1cm")
        self.assertAlmostEqual(dim.value, 10)
        dim = Dimension("21cm")
        self.assertAlmostEqual(dim.value, 210)
        dim = Dimension("0.5cm")
        self.assertAlmostEqual(dim.value, 5)

    def test_mm_to_points(self):
        """
        Test mm to points
        """
        dim = Dimension(25.4)
        self.assertAlmostEqual(dim.points(), 72.0)
        dim = Dimension(210)
        self.assertAlmostEqual(dim.points(), 595.276, delta=0.00045)
        dim = Dimension(297)
        self.assertAlmostEqual(dim.points(), 841.89, delta=0.00045)

    def test_multiply(self):
        """
        Test dimension multiply
        """
        tests = [
            (123, 2, 246),
            (246, 0.5, 123),
            (50, 0.25, 12.5),
        ]
        for val, mul, expected in tests:
            dim = Dimension(val) * mul
            self.assertEqual(dim.value, expected)

    def test_add(self):
        """
        Test adding dimensions
        """
        tests = [
            (12, 23, 35),
            (246, 0.5, 246.5),
            (5, 0.25, 5.25),
        ]
        for val, add, expected in tests:
            dim = Dimension(val) + add
            self.assertEqual(dim.value, expected)
            dim = Dimension(val) + Dimension(add)
            self.assertEqual(dim.value, expected)

    def test_sub(self):
        """
        Test subtracting dimensions
        """
        tests = [
            (32, 12, 20),
            (246, 0.5, 245.5),
            (5, 6, -1),
        ]
        for val, sub, expected in tests:
            dim = Dimension(val) - sub
            self.assertEqual(dim.value, expected)
            dim = Dimension(val) - Dimension(sub)
            self.assertEqual(dim.value, expected)


if __name__ == "__main__":
    unittest.main()
