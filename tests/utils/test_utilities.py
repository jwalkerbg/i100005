# test_utilities.py

import unittest
import pytest   # needed for pytest decorators

from pymodule import utils

# unittest style
class TestUtils(unittest.TestCase):
    # unittest assertion
    def test_hello_from_utils(self):
        self.assertEqual(utils.hello_from_utils(),None)
