#!/usr/bin env python3

import unittest

from functools_too import *


class TestCachedClassperty(unittest.TestCase):

    def setUp(self):

        self.call_count = 0

        class Example:
            @cached_class_property
            def example(cls):
                Example.test_instance.call_count += 1
                return Example.test_instance.call_count

        class ExampleSub(Example):
            pass

        Example.test_instance = self

        self.Example = Example
        self.ExampleSub = ExampleSub

    def test_is_cached_for_base_class(self):
        self.assertEqual(1, self.Example.example)
        self.assertEqual(1, self.Example.example)

    def test_is_cached_for_subclass(self):
        self.assertEqual(1, self.ExampleSub.example)
        self.assertEqual(1, self.ExampleSub.example)

    def test_does_not_share_cache_with_subclass(self):
        self.assertEqual(1, self.Example.example)
        self.assertEqual(2, self.ExampleSub.example)
