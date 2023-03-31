#!/usr/bin env python3

import unittest

from functools_too import *


class TestClassProperty(unittest.TestCase):

    def setUp(self):

        class Example:
            I_AM = 'The Example class'

            @class_property
            def example(cls):
                return cls.I_AM

        class ExampleSub(Example):
            I_AM = 'The ExampleSub class'

        self.Example = Example
        self.ExampleSub = ExampleSub

    def test_operates_in_target_base_class_context(self):
        self.assertEqual('The Example class', self.Example.example)

    def test_operates_in_target_subclass_context(self):
        self.assertEqual('The ExampleSub class', self.ExampleSub.example)
