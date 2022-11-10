"""
A mixin for classes that adds additional asserts for tests
"""

import datetime
from unittest import mock

class TestCaseMixin:
    """
    A mixin for adding additional asserts for tests
    """

    real_datetime_class = datetime.datetime

    @classmethod
    def classname(cls):
        """name of this class"""
        if cls.__module__.startswith('__'):
            return cls.__name__
        return cls.__module__ + '.' + cls.__name__

    def _assert_true(self, result, one, two, msg, template):
        """assert result == true"""
        if not result:
            if msg is not None:
                raise AssertionError(msg)
            raise AssertionError(template.format(one, two))

    # pylint: disable=invalid-name
    def assertTrue(self, result, msg=None):
        """assert result == true"""
        self._assert_true(result, result, None, msg, r'{} not True')

    # pylint: disable=invalid-name
    def assertFalse(self, result, msg=None):
        """assert result == false"""
        self._assert_true(not result, result, None, msg, r'{} not False')

    # pylint: disable=invalid-name
    def assertEqual(self, a, b, msg=None):
        """assert a == b"""
        self._assert_true(a == b, a, b, msg, r'{} != {}')

    # pylint: disable=invalid-name
    def assertNotEqual(self, a, b, msg=None):
        """assert a != b"""
        self._assert_true(a != b, a, b, msg, r'{} == {}')

    # pylint: disable=invalid-name
    def assertAlmostEqual(self, a, b, places=7, msg=None, delta=None):
        """assert a roughly equals b"""
        if delta is not None:
            d = abs(a - b)
            self._assert_true(
                d <= delta,
                a,
                b,
                msg,
                f'{{}} !~= {{}} (delta {delta})')
        else:
            ar = round(a, places)
            br = round(b, places)
            self._assert_true(ar == br, a, b, msg, '{} !~= {}')

    # pylint: disable=invalid-name
    def assertObjectEqual(self, expected, actual, msg=None, strict=False):
        """assert objects expected == actual"""
        for key, value in expected.iteritems():
            if msg is None:
                key_name = key
            else:
                key_name = f'{msg}.{key}'
            if expected is None:
                self.assertIsNone(
                    actual, f'{key_name}: {actual} should be None')
            else:
                self.assertIsNotNone(
                    actual, f'{key_name}: {actual} should not be None')
            if isinstance(value, dict):
                self.assertObjectEqual(value, actual[key], key_name, strict=strict)
            elif isinstance(value, list):
                self.assertListEqual(value, actual[key], key_name)
            else:
                self.assertIn(key, actual,
                              f'{key_name}: missing key {key}')
                assert_msg = f'{key_name}: expected "{value}" got "{actual[key]}"'
                self.assertEqual(value, actual[key], msg=assert_msg)
        if strict:
            for key in actual.keys():
                self.assertIn(key, expected)

    # pylint: disable=invalid-name
    def assertListEqual(self, expected, actual, msg=None):
        """assert lists expected == actual"""
        if msg is None:
            msg = ''
        assert_msg = f'{msg}: expected length {len(expected)} got {len(actual)}'
        self.assertEqual(len(expected), len(actual), assert_msg)
        idx = 0
        for exp, act in zip(expected, actual):
            if isinstance(exp, list):
                self.assertListEqual(exp, act, f'{msg}[{idx}]')
            elif isinstance(exp, dict):
                self.assertObjectEqual(exp, act, f'{msg}[{idx}]')
            else:
                assert_msg = f'{msg}[{idx}] expected "{exp}" got "{act}"'
                self.assertEqual(exp, act, assert_msg)
            idx += 1

    # pylint: disable=invalid-name
    def assertGreaterThan(self, a, b, msg=None):
        """assert a > b"""
        self._assert_true(a > b, a, b, msg, r'{} <= {}')

    # pylint: disable=invalid-name
    def assertGreaterThanOrEqual(self, a, b, msg=None):
        """assert a >= b"""
        self._assert_true(a >= b, a, b, msg, r'{} < {}')

    # pylint: disable=invalid-name
    def assertLessThan(self, a, b, msg=None):
        """assert a < b"""
        self._assert_true(a < b, a, b, msg, r'{} >= {}')

    # pylint: disable=invalid-name
    def assertLessThanOrEqual(self, a, b, msg=None):
        """assert a <= b"""
        self._assert_true(a <= b, a, b, msg, r'{} > {}')

    # pylint: disable=invalid-name
    def assertIn(self, a, b, msg=None):
        """assert a in b"""
        self._assert_true(a in b, a, b, msg, r'{} not in {}')

    # pylint: disable=invalid-name
    def assertNotIn(self, a, b, msg=None):
        """assert a not in b"""
        self._assert_true(a not in b, a, b, msg, r'{} in {}')

    # pylint: disable=invalid-name
    def assertIsNone(self, a, msg=None):
        """assert a is None"""
        self._assert_true(a is None, a, None, msg, r'{} is not None')

    # pylint: disable=invalid-name
    def assertIsNotNone(self, a, msg=None):
        """assert a is not None"""
        self._assert_true(a is not None, a, None, msg, r'{} is None')

    # pylint: disable=invalid-name
    def assertStartsWith(self, a, b, msg=None):
        """assert string a starts with b"""
        self._assert_true(a.startswith(b), a, b, msg,
                          r'{} does not start with {}')

    # pylint: disable=invalid-name
    def assertEndsWith(self, a, b, msg=None):
        """assert string a ends with b"""
        self._assert_true(a.endswith(b), a, b, msg, r'{} does not end with {}')

    # pylint: disable=invalid-name
    def assertIsInstance(self, a, types, msg=None):
        """assert a is instance of b"""
        self._assert_true(isinstance(a, types), a, types,
                          msg, r'{} is not instance of {}')

    @classmethod
    def mock_datetime_now(cls, target):
        """
        Override ``datetime.datetime.now()`` with a custom target value.
        This creates a new datetime.datetime class, and alters its now()/utcnow()
        methods.
        Returns:
        A mock.patch context, can be used as a decorator or in a with.
        """
        # See http://bugs.python.org/msg68532
        # And
        # http://docs.python.org/reference/datamodel.html#customizing-instance-and-subclass-checks
        class DatetimeSubclassMeta(type):
            """
            We need to customize the __instancecheck__ method for isinstance().
            This must be performed at a metaclass level.
            """
            @classmethod
            def __instancecheck__(mcs, obj):
                return isinstance(obj, cls.real_datetime_class)

        class BaseMockedDatetime(cls.real_datetime_class):
            """
            base class for a mock DateTime
            """
            @classmethod
            def now(cls, tz=None):
                return target.replace(tzinfo=tz)

            @classmethod
            def utcnow(cls):
                return target

        # Python2 & Python3-compatible metaclass
        MockedDatetime = DatetimeSubclassMeta(
            'datetime', (BaseMockedDatetime,), {})
        return mock.patch.object(datetime, 'datetime', MockedDatetime)
