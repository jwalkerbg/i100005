# tests/test_core_module_a.py

import unittest
from pymodule import core

class TestCore_a(unittest.TestCase):
    def test_hello_from_core_module_a(self):
        self.assertEqual(core.hello_from_core_module_a(),1)

    def test_goodbye_from_core_module_a(self):
        self.assertEqual(core.goodbye_from_core_module_a(),-1)
