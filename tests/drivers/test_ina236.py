# test_utilities.py

import unittest

from pymodule import drivers

class TestDrivers(unittest.TestCase):
    def test_hello_from_ina236(self):
        self.assertEqual(drivers.hello_from_ina236(),None)