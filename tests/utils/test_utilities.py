# test_utilities.py

import unittest
import pytest   # needed for pytest decorators

from pymodule import utils

# unittest style
class TestUtils(unittest.TestCase):
    # unittest assertion
    def test_hello_from_utils(self):
        self.assertEqual(utils.hello_from_utils(),None)

    def test_sumator_u(self):
        self.assertEqual(utils.sumator(4,5,6),15)

    # pytest assertion
    def test_sumator_p(self):
        assert utils.sumator(1,2,3) == 6

# unittest style, less informative on errors
class TestSumator_u(unittest.TestCase):
    def test_sumator_up(self):
        test_cases = [
            (1, 2, 3, 6),       # 1 + 2 + 3 = 6
            (10, 20, 30, 60),   # 10 + 20 + 30 = 60
            (-1, -1, -1, -3),   # -1 + -1 + -1 = -3
            (0, 0, 0, 0),       # 0 + 0 + 0 = 0
            (5, 5, 5, 15)       # 5 + 5 + 5 = 15
        ]

        for a, b, c, expected in test_cases:
            with self.subTest(a=a, b=b, c=c):
                self.assertEqual(utils.sumator(a, b, c), expected)

# pytest style, more informative on errors
class TestSumator_pp:
    @pytest.mark.parametrize(
        "a, b, c, expected", [
            (1, 2, 3, 6),       # 1 + 2 + 3 = 6
            (10, 20, 30, 60),   # 10 + 20 + 30 = 60
            (-1, -1, -1, -3),   # -1 + -1 + -1 = -3
            (0, 0, 0, 0),       # 0 + 0 + 0 = 0
            (5, 5, 5, 15)       # 5 + 5 + 5 = 15
        ]
    )
    def test_sumator_pp(self, a, b, c, expected):
        assert utils.sumator(a, b, c) == expected
